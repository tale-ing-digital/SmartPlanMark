import os
import sys
import argparse
import pandas as pd

# Configurar codificación UTF-8 para stdout/stderr (compatible con Windows)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.config import DATA_INPUT, DATA_OUTPUT
from src.core.ocr_engine import (
    detect_number_coordinates_pdf
)
from src.core.pdf_renderer import draw_highlight_box


# ==========================================
# Procesar una fila del CSV
# ==========================================
def process_assignment(row, pdf_master, output_dir=None):
    """
    Procesa una fila del CSV: busca el número en el PDF, dibuja y genera copia.
    
    Args:
        row: Fila del DataFrame con columnas 'depto' y 'estacionamiento'
        pdf_master: Ruta al PDF maestro
        output_dir: Directorio de salida (default: DATA_OUTPUT)
    """
    depto = str(row["depto"])
    estacionamiento = str(row["estacionamiento"])

    print(f">> Procesando Departamento: {depto} | Estacionamiento: {estacionamiento}")

    # --- Detección directa del PDF ---
    bbox = detect_number_coordinates_pdf(pdf_master, estacionamiento)

    # Nombre del PDF generado
    output_name = f"{depto}_EST_{estacionamiento}.pdf"

    if bbox:
        print(f"   [OK] Coordenadas detectadas: {bbox}")
        result = draw_highlight_box(pdf_master, bbox, output_name, output_dir=output_dir)
        print(f"   [OK] Archivo generado: {result}")
    else:
        print(f"   [WARN] No se pudo detectar el numero {estacionamiento}")
        return None

    return output_name


# ==========================================
# Función principal con argumentos CLI
# ==========================================
def main_with_args(pdf_path, csv_path, output_path):
    """
    Ejecuta el procesamiento con argumentos personalizados.
    """
    print("=== SmartPlanMark – Iniciando procesamiento ===")

    # Crear carpeta de salida si no existe
    os.makedirs(output_path, exist_ok=True)

    # Validaciones básicas
    if not os.path.exists(csv_path):
        print(f"[ERROR] No se encontro el CSV: {csv_path}")
        return

    if not os.path.exists(pdf_path):
        print(f"[ERROR] No se encontro el PDF maestro: {pdf_path}")
        return

    # Cargar CSV
    df = pd.read_csv(csv_path)

    print(f"CSV cargado. Filas: {len(df)}")
    print("Iniciando procesamiento...\n")

    # Procesar cada fila una por una
    for _, row in df.iterrows():
        process_assignment(row, pdf_path, output_dir=output_path)

    print(f"\n=== Finalizado. Archivos generados en {output_path} ===")
    return True


# ==========================================
# Programa principal (modo original)
# ==========================================
def main():
    print("=== SmartPlanMark – Iniciando procesamiento ===")

    # Crear carpeta de salida si no existe
    os.makedirs(DATA_OUTPUT, exist_ok=True)

    # Definir rutas de entrada
    csv_path = os.path.join(DATA_INPUT, "asignaciones.csv")
    pdf_master = os.path.join(DATA_INPUT, "plano_maestro.pdf")

    # Validaciones básicas
    if not os.path.exists(csv_path):
        print(f"[ERROR] No se encontro el CSV: {csv_path}")
        return

    if not os.path.exists(pdf_master):
        print(f"[ERROR] No se encontro el PDF maestro: {pdf_master}")
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
    # Parser de argumentos CLI
    parser = argparse.ArgumentParser(description='SmartPlanMark - Marcador Inteligente de Planos')
    parser.add_argument('--pdf', type=str, help='Ruta al PDF maestro')
    parser.add_argument('--csv', type=str, help='Ruta al archivo CSV de asignaciones')
    parser.add_argument('--output', type=str, help='Directorio de salida')
    
    args = parser.parse_args()

    # Si se proporcionan argumentos CLI, usar modo personalizado
    if args.pdf and args.csv and args.output:
        main_with_args(args.pdf, args.csv, args.output)
    else:
        # Modo original (usando DATA_INPUT y DATA_OUTPUT de config)
        main()
