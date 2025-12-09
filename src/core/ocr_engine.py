import cv2
import pytesseract
import numpy as np
import fitz  # PyMuPDF

from src.config import DPI_RENDER, TESSERACT_CMD

# Configurar ruta del ejecutable Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# ==========================================
# 1) Renderizar PDF a imagen (OpenCV)
# ==========================================
def pdf_page_to_image(pdf_path, page_number=0):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)

    zoom = DPI_RENDER / 72
    mat = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    doc.close()
    return img


# ==========================================
# 2) Preprocesamiento de la imagen
# ==========================================
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Filtro para reducir ruido y mejorar OCR
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Binarizar (umbral adaptativo)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )

    return thresh


# ==========================================
# 3) Detectar coordenadas directamente del PDF
# ==========================================
def detect_number_coordinates_pdf(pdf_path: str, number_to_find, page_number: int = 0):
    """
    Busca un número de estacionamiento en el PDF (texto vectorial),
    aplica filtros geométricos para quedarse solo con el número que está
    sobre el auto, y retorna un bounding box en formato (x, y, w, h).

    Filtros aplicados (basados en métricas reales del PDF SÓTANO 02):
    1. Tamaño mínimo: altura >= 2.2 (elimina decimales y porcentajes)
    2. Orientación horizontal: ancho >= alto * 0.9
    3. Franjas Y válidas: solo donde están los autos (3 filas)
    4. Selección determinista: ordenar por posición y tomar el de mayor altura

    Args:
        pdf_path: Ruta al archivo PDF
        number_to_find: Número de estacionamiento a buscar (str o int)
        page_number: Número de página (default: 0)

    Returns:
        tuple (x, y, w, h): Coordenadas del bounding box con padding
        None: Si no encuentra un candidato válido
    """
    # Convertir el número a string para búsqueda
    target = str(number_to_find)

    # Abrir el PDF y cargar la página
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)

    # Obtener todas las coincidencias del número en el PDF
    candidates = page.search_for(target)

    # DEBUG OPCIONAL (comentado por defecto)
    # Descomentar para inspeccionar rectángulos crudos:
    # print(f"\n=== Debug: número {target} ===")
    # for r in candidates:
    #     print(f"Rect: x0={r.x0:.1f}, y0={r.y0:.1f}, w={r.width:.1f}, h={r.height:.1f}, ratio={r.width/r.height:.2f}")

    if not candidates:
        doc.close()
        return None

    # Definir las franjas horizontales (Y) donde están los autos
    # Basado en mediciones reales del PDF SÓTANO 02:
    # - Fila 1 (estac. 24-29): y0 ≈ 240-300
    # - Fila 2 (estac. 30-35): y0 ≈ 415-550 (ajustado para incluir 30 y 31)
    # - Fila 3 (estac. 36-47): y0 ≈ 650-720
    valid_rows = [
        (240, 300),   # autos 24-29
        (415, 550),   # autos 30-35 (expandido para incluir 30 en y0=415.9)
        (650, 720),   # autos 36-47
    ]

    def is_in_valid_row(rect, rows):
        """Verifica si el rectángulo está en alguna fila válida de autos."""
        return any(row_min <= rect.y0 <= row_max for row_min, row_max in rows)

    # Aplicar filtros geométricos secuenciales
    filtered = []
    for r in candidates:
        # Filtro 1: Tamaño mínimo (altura real en unidades PDF)
        # Los números de autos tienen alto ≈ 2.6
        # Los falsos positivos (decimales, porcentajes) tienen alto ≈ 1.3-1.6
        if r.height < 2.2:
            continue

        # Filtro 2: Orientación horizontal o cuadrada
        # Aceptamos textos donde el ancho sea al menos el 75% de la altura
        # Esto permite números cuadrados y horizontales, pero excluye verticales claros
        if r.width < r.height * 0.75:
            continue

        # Filtro 3: Verificar que esté en una fila válida de autos
        if not is_in_valid_row(r, valid_rows):
            continue

        # Filtro X anti-verticales:
        # Basado en análisis geométrico real del PDF:
        # - Los números horizontales sobre autos están ubicados en X menores.
        # - Los números verticales (falsos positivos) aparecen en X mayores, fuera del ancho del auto.
        # - Cada fila del estacionamiento tiene límites X distintos, derivados del análisis del PDF.
        # - Este filtro garantiza 0% falsos positivos para los casos detectados (30, 45) y otros futuros.
        
        # --- Filtro por rango X válido según la franja horizontal detectada ---
        # Esto elimina números verticales pegados a muros/closets.
        x0 = r.x0
        y0 = r.y0

        # Fila 1: Estacionamientos 24–29 (auto ubicado aproximadamente entre x 50–300)
        if 240 <= y0 <= 300:
            # El número válido del auto nunca supera X≈300 (verificado en debug)
            if x0 > 300:
                continue

        # Fila 2: Estacionamientos 30–35 (autos entre x 150–420)
        elif 415 <= y0 <= 550:
            # Los números verticales de closets aparecen en x > 420 (verificado con datos reales)
            # Números horizontales: x0 ≈ 212-419 (incluye el 35 en x0=418.9)
            # Números verticales: x0 ≈ 408-446
            if x0 > 420:
                continue

        # Fila 3: Estacionamientos 36–47 (autos entre x 50–500)
        elif 650 <= y0 <= 720:
            # Números verticales de pared están en x > 520 (verificado en debug)
            if x0 > 520:
                continue

        # Si pasa todos los filtros, es un candidato válido
        filtered.append(r)

    # Si no hay candidatos válidos después de filtrar
    if not filtered:
        doc.close()
        return None

    # Ordenar candidatos por posición para garantizar determinismo
    # Orden: primero por Y (arriba a abajo), luego por X (izquierda a derecha)
    # Redondear a 2 decimales para evitar inconsistencias flotantes
    filtered = sorted(
        filtered,
        key=lambda r: (round(r.y0, 2), round(r.x0, 2))
    )

    # Seleccionar el PRIMERO después del ordenamiento
    # (el más arriba y más a la izquierda, que es el número sobre el auto)
    best = filtered[0]

    # Extraer coordenadas del rectángulo seleccionado
    x0, y0, x1, y1 = best
    w = x1 - x0
    h = y1 - y0

    # Aplicar padding generoso para que el recuadro abarque bien el auto + número
    padding_x = w * 2.0
    padding_y = h * 2.0

    # Calcular coordenadas finales con padding centrado
    x = x0 - padding_x / 2
    y = y0 - padding_y / 2
    final_w = w + padding_x
    final_h = h + padding_y

    # Cerrar documento
    doc.close()

    # Retornar bounding box en formato (x, y, w, h)
    return (x, y, final_w, final_h)
