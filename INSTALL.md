# 🚀 INSTALACIÓN RÁPIDA - SmartPlanMark

## Paso 1: Instalar dependencias de Node.js

```powershell
npm install
```

## Paso 2: Configurar Python

### Opción A: Con entorno virtual (recomendado)

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (PowerShell)
.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### Opción B: Sin entorno virtual

```powershell
pip install -r requirements.txt
```

## Paso 3: Verificar Tesseract OCR

```powershell
tesseract --version
```

Si no está instalado:
1. Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar en: `C:\Program Files\Tesseract-OCR\`
3. Agregar al PATH del sistema

## Paso 4: Iniciar el servidor

### Opción A: Usando el script de inicio

```powershell
.\start.bat
```

### Opción B: Manualmente

```powershell
npm start
```

## ✅ Listo!

Accede a: **http://localhost:3000**

---

## 🔧 Solución de Problemas

### Error: "Cannot find module 'express'"

```powershell
npm install
```

### Error: "Python no encontrado"

```powershell
# Verificar instalación
python --version

# O usar ruta completa en src/routes/smartplanmark.js
# Cambiar: spawn('python', ...)
# Por: spawn('C:\\Python39\\python.exe', ...)
```

### Error: "Tesseract no encontrado"

```powershell
# Editar src/config.py y ajustar:
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## 📦 Dependencias Instaladas

### Node.js
- express
- multer
- archiver
- cors
- uuid

### Python
- pytesseract
- PyMuPDF
- pandas
- opencv-python
- numpy
- pillow
