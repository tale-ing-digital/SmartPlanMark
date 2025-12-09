# ============================
# Configuración Global
# ============================

import os

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_INPUT = os.path.join(BASE_DIR, "data", "input")
DATA_OUTPUT = os.path.join(BASE_DIR, "data", "output")

# DPI para renderizar PDFs en OCR
DPI_RENDER = 300

# Color de resaltado (RGB normalizado para PyMuPDF)
BOX_COLOR = (1, 0, 0)   # Rojo

# Grosor del rectángulo
BOX_THICKNESS = 3

# Ruta del ejecutable de Tesseract (Windows)
# (Normalmente detecta automáticamente si está en PATH)
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

