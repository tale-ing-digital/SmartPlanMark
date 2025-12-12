# SmartPlanMark 🎯

**Marcador Inteligente de Planos** - Sistema automatizado para marcar estacionamientos en planos PDF usando OCR y procesamiento inteligente.

Desarrollado por **TalePlanHub - Mesa de Ayuda TI** © 2025

---

## 🚀 Características

- ✅ **Interfaz Web Moderna** - Diseño corporativo TalePlanHub con modo oscuro
- ✅ **Procesamiento Inteligente** - OCR con Tesseract para detección precisa
- ✅ **Carga por Lotes** - Procesa múltiples asignaciones desde CSV
- ✅ **Descarga ZIP** - Todos los planos marcados en un solo archivo
- ✅ **API REST** - Backend Express con Python integrado

---

## 📋 Requisitos Previos

### Software Necesario

1. **Node.js** >= 18.0.0
2. **Python** >= 3.8
3. **Tesseract OCR** - [Descargar aquí](https://github.com/tesseract-ocr/tesseract)

### Instalación de Tesseract (Windows)

```powershell
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en: C:\Program Files\Tesseract-OCR\
# Agregar al PATH del sistema
```

---

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tale-ing-digital/SmartPlanMark.git
cd SmartPlanMark
```

### 2. Instalar dependencias de Node.js

```bash
npm install
```

### 3. Instalar dependencias de Python

```bash
# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar entorno virtual
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Verificar instalación de Tesseract

```bash
# Debe mostrar la versión instalada
tesseract --version
```

---

## 🎮 Uso

### Iniciar el servidor

```bash
npm start
```

El servidor estará disponible en: **http://localhost:3000**

### Modo desarrollo (con auto-reload)

```bash
npm run dev
```

---

## 📂 Estructura del Proyecto

```
SmartPlanMark/
├── app.js                      # Servidor Express principal
├── package.json                # Dependencias Node.js
├── requirements.txt            # Dependencias Python
├── public/                     # Frontend
│   ├── smartplanmark.html     # Interfaz web
│   └── smartplanmark.js       # Lógica del cliente
├── src/                       # Backend Python
│   ├── main.py               # Script principal
│   ├── config.py             # Configuración
│   ├── routes/               # Rutas Express
│   │   └── smartplanmark.js # API endpoint
│   ├── core/                 # Procesamiento OCR
│   │   ├── ocr_engine.py
│   │   └── pdf_renderer.py
│   └── utils/                # Utilidades
│       ├── file_manager.py
│       └── validators.py
├── data/
│   ├── input/                # Archivos de entrada
│   └── output/               # Planos generados
└── tmp/                      # Archivos temporales
```

---

## 🔧 Configuración

### Ajustar ruta de Tesseract

Editar `src/config.py`:

```python
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Cambiar puerto del servidor

```bash
# Windows
$env:PORT=8080; npm start

# Linux/Mac
PORT=8080 npm start
```

---

## 📊 Formato del CSV

El archivo CSV debe contener las siguientes columnas:

| depto | estacionamiento |
|-------|----------------|
| 101   | E-15          |
| 102   | E-16          |
| 103   | E-17          |

---

## 🔌 API Endpoints

### `POST /api/smartplanmark/process`

Procesa un PDF maestro con asignaciones CSV.

**Parámetros (multipart/form-data):**
- `pdf` - Archivo PDF maestro (max 50MB)
- `csv` - Archivo CSV con asignaciones (max 5MB)

**Respuesta:**
- Archivo ZIP con planos marcados

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:3000/api/smartplanmark/process \
  -F "pdf=@plano_maestro.pdf" \
  -F "csv=@asignaciones.csv" \
  --output planos_marcados.zip
```

---

## 🎨 Estilo Corporativo

Este proyecto sigue las **Directrices de Estilo Corporativo TalePlanHub**:

- 🎨 **Colores**: Cyan (#00C9FF) + Navy (#01053A)
- 🌙 **Modo Oscuro**: Completo y persistente
- 📱 **Responsive**: Compatible con todos los dispositivos
- ♿ **Accesibilidad**: Cumple con estándares WCAG

---

## 🐛 Troubleshooting

### Error: "Tesseract no encontrado"

```bash
# Verificar instalación
tesseract --version

# Agregar al PATH (Windows)
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"
```

### Error: "Python no encontrado"

Asegurarse de que Python está en el PATH del sistema o actualizar `src/routes/smartplanmark.js`:

```javascript
const pythonProcess = spawn('python3', pythonArgs, {
    // ... o usar ruta absoluta: 'C:\\Python39\\python.exe'
});
```

---

## 📞 Soporte

**Mesa de Ayuda TI - Tale Inmobiliaria**

📧 Email: [soporte@taleconstructora.com](mailto:soporte@taleconstructora.com)

---

## 📄 Licencia

MIT License - © 2025 Tale Inmobiliaria

---

## 🙏 Créditos

Desarrollado con ❤️ por el equipo de **TalePlanHub**

- **OCR**: Tesseract
- **PDF Processing**: PyMuPDF
- **Backend**: Express.js
- **Frontend**: Vanilla JS (sin frameworks)
