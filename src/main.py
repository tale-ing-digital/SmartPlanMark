import os
import pandas as pd

from src.config import DATA_INPUT, DATA_OUTPUT
from src.core.ocr_engine import (
    detect_number_coordinates_pdf
)
from src.core.pdf_renderer import draw_highlight_box


# ==========================================
# Procesar una fila del CSV
# ==========================================
def process_assignment(row, pdf_master):
    """
    Procesa una fila del CSV: busca el número en el PDF, dibuja y genera copia.
    """
    depto = str(row["depto"])
    estacionamiento = str(row["estacionamiento"])

    print(f"➡ Procesando Departamento: {depto} | Estacionamiento: {estacionamiento}")

    # --- Detección directa del PDF ---
    bbox = detect_number_coordinates_pdf(pdf_master, estacionamiento)

    # Nombre del PDF generado
    output_name = f"{depto}_EST_{estacionamiento}.pdf"

    if bbox:
        print(f"   ✔ Coordenadas detectadas: {bbox}")
        result = draw_highlight_box(pdf_master, bbox, output_name)
        print(f"   ✔ Archivo generado: {result}")
    else:
        print(f"   ⚠ No se pudo detectar el número {estacionamiento}")
        return None

    return output_name


# ==========================================
# Programa principal
# ==========================================
def main():
    print("=== SmartPlanMark – Iniciando procesamiento ===")

    # Definir rutas de entrada
    csv_path = os.path.join(DATA_INPUT, "asignaciones.csv")
    pdf_master = os.path.join(DATA_INPUT, "plano_maestro.pdf")

    # Validaciones básicas
    if not os.path.exists(csv_path):
        print(f"❌ No se encontró el CSV: {csv_path}")
        return

    if not os.path.exists(pdf_master):
        print(f"❌ No se encontró el PDF maestro: {pdf_master}")
        return

    # Cargar CSV
    df = pd.read_csv(csv_path)

    print(f"CSV cargado. Filas: {len(df)}")
    print("Iniciando procesamiento...\n")

    # Procesar cada fila una por una
    for _, row in df.iterrows():
        process_assignment(row, pdf_master)

    print("\n=== Finalizado. Archivos generados en data/output ===")


if __name__ == "__main__":
    main()
