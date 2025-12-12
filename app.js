/**
 * SmartPlanMark - Servidor Express
 * TalePlanHub © 2025
 */

const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// ========== MIDDLEWARES ==========

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos desde la carpeta public
app.use(express.static(path.join(__dirname, 'public')));

// Logging de peticiones
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// ========== RUTAS ==========

// Importar router de SmartPlanMark
app.use(require('./src/routes/smartplanmark'));

// Ruta principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'smartplanmark.html'));
});

// Ruta de health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        service: 'SmartPlanMark API',
        timestamp: new Date().toISOString()
    });
});

// ========== MANEJO DE ERRORES ==========

// Ruta no encontrada
app.use((req, res) => {
    res.status(404).json({ error: 'Ruta no encontrada' });
});

// Error handler global
app.use((err, req, res, next) => {
    console.error('Error:', err);
    
    if (err instanceof multer.MulterError) {
        return res.status(400).json({ 
            error: `Error de carga: ${err.message}` 
        });
    }
    
    res.status(500).json({ 
        error: err.message || 'Error interno del servidor' 
    });
});

// ========== INICIAR SERVIDOR ==========

app.listen(PORT, () => {
    console.log('════════════════════════════════════════════════');
    console.log('   SmartPlanMark - TalePlanHub');
    console.log('════════════════════════════════════════════════');
    console.log(`✅ Servidor ejecutándose en http://localhost:${PORT}`);
    console.log(`✅ Interfaz web: http://localhost:${PORT}`);
    console.log(`✅ API endpoint: http://localhost:${PORT}/api/smartplanmark/process`);
    console.log('════════════════════════════════════════════════\n');
});

module.exports = app;
