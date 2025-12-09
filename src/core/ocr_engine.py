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

    # Todas las apariciones del número en la página
    text_instances = page.search_for(target)

    if not text_instances:
        doc.close()
        return None

    # Elegimos el rectángulo con mayor altura (normalmente el del auto)
    best_rect = max(text_instances, key=lambda r: r.height)

    doc.close()

    x0, y0, x1, y1 = best_rect

    # --- Agregamos margen para que no sea tan chiquito ---
    width = x1 - x0
    height = y1 - y0

    padding_x = width * 1.2   # 20% a cada lado
    padding_y = height * 1.5  # más alto que el texto

    x = x0 - padding_x / 2
    y = y0 - padding_y / 2
    w = width + padding_x
    h = height + padding_y

    return (x, y, w, h)
