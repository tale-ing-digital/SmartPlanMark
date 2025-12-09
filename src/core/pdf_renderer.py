import fitz  # PyMuPDF
from src.config import BOX_COLOR, BOX_THICKNESS, DATA_OUTPUT
import os


# ==========================================
# 1) Dibujar rectángulo en la página del PDF
# ==========================================
def draw_highlight_box(pdf_path, bbox, output_name="output.pdf", page_number=0):
    """
    Dibuja un rectángulo basado en coordenadas (x, y, w, h) en la página del PDF.
    """

    if bbox is None:
        print("⚠ No se recibió ninguna coordenada para dibujar.")
        return None

    x, y, w, h = bbox

    doc = fitz.open(pdf_path)
    page = doc[page_number]

    # Crear la caja final
    rect = fitz.Rect(x, y, x + w, y + h)

    # Rectángulo con borde más grueso y SIN rellenar todo de rojo
    page.draw_rect(
        rect,
        color=BOX_COLOR,   # borde
        width=BOX_THICKNESS,
        fill=None          # evita cuadrado sólido rojo
    )

    # Guardar el nuevo PDF
    output_path = os.path.join(DATA_OUTPUT, output_name)
    doc.save(output_path)
    doc.close()

    return output_path


# ==========================================
# 2) Función de conveniencia para guardar copias
# ==========================================
def save_copy(pdf_path, new_name):
    """
    Clona el PDF original y guarda una copia con nuevo nombre.
    """

    doc = fitz.open(pdf_path)
    output_path = os.path.join(DATA_OUTPUT, new_name)
    doc.save(output_path)
    doc.close()

    return output_path


