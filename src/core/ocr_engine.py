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
def detect_number_coordinates_pdf(pdf_path, number_to_find, page_number=0):
    """
    Busca el número directamente en el PDF sin OCR.
    Retorna las coordenadas (x, y, w, h) donde se detecta el número buscado.
    """
    target = str(number_to_find)

    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)

    text_instances = page.search_for(target)

    if not text_instances:
        doc.close()
        return None

    # Dimensiones de la página
    page_w = page.rect.x1
    page_h = page.rect.y1

    # 1. Filtrar por zona donde están los autos
    zone_filtered = [
        r for r in text_instances
        if (r.y0 > page_h * 0.20 and r.y1 < page_h * 0.88 and
            r.x0 >= page_w * 0.05 and
            r.x1 < page_w * 0.85)  # 85% para incluir auto 36
    ]

    if not zone_filtered:
        doc.close()
        return None

    # 2. Filtrar números verticales y casi cuadrados problemáticos
    # El 30 vertical tiene dimensiones casi iguales (w≈h)
    horizontal = [
        r for r in zone_filtered
        if r.width > r.height * 0.98  # Solo aceptar si width >= height
    ]

    if not horizontal:
        horizontal = zone_filtered

    # 3. Filtrar por tamaño mínimo
    min_height = 3.5
    sized_filtered = [
        r for r in horizontal
        if r.height >= min_height
    ]

    if not sized_filtered:
        sized_filtered = horizontal

    # 4. Verificar que NO sea parte de un decimal
    valid_numbers = []
    for rect in sized_filtered:
        x_margin = rect.width * 2
        search_rect = fitz.Rect(
            rect.x0 - x_margin, rect.y0,
            rect.x1 + x_margin, rect.y1
        )
        context_text = page.get_textbox(search_rect)
        
        if context_text and not any(char in context_text for char in ['.', '%', ',']):
            valid_numbers.append(rect)
    
    if not valid_numbers:
        valid_numbers = sized_filtered

    # 5. Elegir el rectángulo más grande (el del auto)
    best_rect = max(valid_numbers, key=lambda r: r.height)

    if not horizontal:
        horizontal = zone_filtered

    # 3. Filtrar por tamaño mínimo (eliminar números pequeños de porcentajes)
    # Los números de autos tienen altura mínima de ~4-5 puntos
    min_height = 3.5
    sized_filtered = [
        r for r in horizontal
        if r.height >= min_height
    ]

    if not sized_filtered:
        sized_filtered = horizontal

    # 4. Verificar que NO sea parte de un decimal (5.43%, 5.45%)
    # Buscamos el contexto del texto alrededor
    valid_numbers = []
    for rect in sized_filtered:
        # Expandir búsqueda para ver si hay un punto decimal cerca
        x_margin = rect.width * 2
        search_rect = fitz.Rect(
            rect.x0 - x_margin, rect.y0,
            rect.x1 + x_margin, rect.y1
        )
        context_text = page.get_textbox(search_rect)
        
        # Si el contexto contiene punto decimal o porcentaje, descartar
        if context_text and not any(char in context_text for char in ['.', '%', ',']):
            valid_numbers.append(rect)
    
    if not valid_numbers:
        valid_numbers = sized_filtered

    # 5. Elegir el rectángulo más grande (el del auto)
    best_rect = max(valid_numbers, key=lambda r: r.height)

    x0, y0, x1, y1 = best_rect

    # 4. Padding para ampliar el recuadro
    width = x1 - x0
    height = y1 - y0

    padding_x = width * 1.6
    padding_y = height * 1.6

    x = x0 - padding_x / 2
    y = y0 - padding_y / 2
    w = width + padding_x
    h = height + padding_y

    doc.close()
    return (x, y, w, h)
