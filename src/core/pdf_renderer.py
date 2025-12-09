import fitz  # PyMuPDF
from src.config import BOX_COLOR, BOX_THICKNESS, DATA_OUTPUT
import os


# ==========================================
# 1) Exportar página con recuadro (SIN REFLOW)
# ==========================================
def draw_highlight_box(pdf_path, bbox, output_name="output.pdf", page_number=0):
    """
    Dibuja un rectángulo en las coordenadas exactas detectadas por OCR.
    
    SOLUCIÓN AL PROBLEMA DE COORDENADAS:
    - Usa insertPDF() para importar la página manteniendo geometría original
    - Las coordenadas se aplican en el mismo espacio que la detección
    - Evita transformaciones que desplacen el recuadro
    - El recuadro se dibuja EXACTAMENTE donde fue detectado
    
    NOTA: is_wrapped=True es normal en páginas copiadas con PyMuPDF.
    Esto NO afecta la precisión de coordenadas ni la calidad vectorial.
    
    Args:
        pdf_path: Ruta al PDF maestro original
        bbox: Tupla (x, y, w, h) con coordenadas detectadas
        output_name: Nombre del archivo de salida
        page_number: Número de página (default: 0)
    
    Returns:
        str: Ruta del PDF generado
        None: Si no hay bbox válido
    """

    if bbox is None:
        print("⚠ No se recibió ninguna coordenada para dibujar.")
        return None

    # Extraer coordenadas del bounding box
    x, y, w, h = bbox

    # Abrir PDF maestro
    master_doc = fitz.open(pdf_path)
    page = master_doc[page_number]

    # Crear nuevo PDF destino (vacío)
    out = fitz.open()

    # Importar la página completa del documento maestro
    # insertPDF mantiene mejor la estructura original que show_pdf_page
    out.insert_pdf(master_doc, from_page=page_number, to_page=page_number)
    
    # Obtener la página importada
    new_page = out[0]

    # Crear rectángulo usando coordenadas crudas (sin transformación)
    r = fitz.Rect(x, y, x + w, y + h)

    # Dibujar el rectángulo sobre la página importada
    # overlay=True asegura que se dibuje encima del contenido
    new_page.draw_rect(
        r,
        color=BOX_COLOR,      # borde rojo (desde config)
        width=BOX_THICKNESS,  # grosor (desde config)
        fill=None,            # sin relleno
        overlay=True          # dibujar encima del contenido
    )

    # Guardar sin wrap ni optimización que modifique la estructura interna
    # clean=False evita reorganización que causa is_wrapped=True
    output_path = os.path.join(DATA_OUTPUT, output_name)
    out.save(
        output_path,
        deflate=True,       # comprime sin pérdida
        incremental=False,  # PDF completo (no incremental)
        clean=False,        # NO limpiar (evita reflow)
        garbage=0           # NO optimizar estructura (mantiene coordenadas)
    )
    
    # Cerrar documentos
    out.close()
    master_doc.close()

    return output_path


# ==========================================
# 2) Función de conveniencia para guardar copias
# ==========================================
def save_copy(pdf_path, new_name):
    """
    Clona el PDF original y guarda una copia con nuevo nombre.
    Mantiene el contenido 100% vectorial sin degradación.
    """

    doc = fitz.open(pdf_path)
    output_path = os.path.join(DATA_OUTPUT, new_name)
    
    # Guardar con parámetros que preservan estructura original
    doc.save(
        output_path,
        deflate=True,       # comprime sin rasterizar
        clean=False,        # NO limpiar (evita reflow)
        garbage=0,          # NO optimizar (mantiene estructura)
        incremental=False   # asegura PDF final íntegro
    )
    doc.close()

    return output_path




