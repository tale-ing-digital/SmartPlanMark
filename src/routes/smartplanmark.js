/**
 * SmartPlanMark Router
 * Maneja la carga de archivos, procesamiento Python y generación de ZIP
 */

const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const archiver = require('archiver');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

// ========== CONFIGURACIÓN DE MULTER ==========

const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const sessionId = req.sessionId || uuidv4();
        req.sessionId = sessionId;
        
        const uploadDir = path.join(__dirname, '../../tmp/smartplanmark', sessionId);
        
        try {
            await fs.mkdir(uploadDir, { recursive: true });
            cb(null, uploadDir);
        } catch (error) {
            cb(error);
        }
    },
    filename: (req, file, cb) => {
        const fieldName = file.fieldname === 'pdf' ? 'plano_maestro.pdf' : 'asignaciones.csv';
        cb(null, fieldName);
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 50 * 1024 * 1024 // 50 MB
    },
    fileFilter: (req, file, cb) => {
        if (file.fieldname === 'pdf' && file.mimetype === 'application/pdf') {
            cb(null, true);
        } else if (file.fieldname === 'csv' && file.mimetype === 'text/csv') {
            cb(null, true);
        } else {
            cb(new Error(`Tipo de archivo no válido para ${file.fieldname}`));
        }
    }
});

// ========== ENDPOINT PRINCIPAL ==========

router.post('/api/smartplanmark/process', upload.fields([
    { name: 'pdf', maxCount: 1 },
    { name: 'csv', maxCount: 1 }
]), async (req, res) => {
    const sessionId = req.sessionId || uuidv4();
    const tmpDir = path.join(__dirname, '../../tmp/smartplanmark', sessionId);
    const outputDir = path.join(tmpDir, 'output');

    try {
        // Validar que ambos archivos fueron recibidos
        if (!req.files.pdf || !req.files.csv) {
            return res.status(400).json({ 
                error: 'Se requieren ambos archivos: PDF y CSV' 
            });
        }

        const pdfPath = req.files.pdf[0].path;
        const csvPath = req.files.csv[0].path;

        console.log(`[${sessionId}] PDF recibido: ${pdfPath}`);
        console.log(`[${sessionId}] CSV recibido: ${csvPath}`);

        // Crear directorio de salida
        await fs.mkdir(outputDir, { recursive: true });

        // ========== EJECUTAR SCRIPT PYTHON ==========
        
        // Ruta raíz del proyecto (donde está package.json)
        const projectRoot = path.join(__dirname, '../..');
        
        // Ejecutar como módulo Python: python -m src.main
        const pythonArgs = [
            '-m', 'src.main',
            '--pdf', pdfPath,
            '--csv', csvPath,
            '--output', outputDir
        ];

        console.log(`[${sessionId}] Ejecutando: python ${pythonArgs.join(' ')}`);
        console.log(`[${sessionId}] CWD: ${projectRoot}`);

        await new Promise((resolve, reject) => {
            const pythonProcess = spawn('python', pythonArgs, {
                cwd: projectRoot,  // ✅ Ejecutar desde la raíz del proyecto
                env: {
                    ...process.env,
                    PYTHONIOENCODING: 'utf-8',  // ✅ Forzar UTF-8 para evitar errores de codificación
                    PYTHONUNBUFFERED: '1'        // ✅ Deshabilitar buffering para logs en tiempo real
                }
            });

            let stdout = '';
            let stderr = '';

            pythonProcess.stdout.on('data', (data) => {
                const output = data.toString();
                stdout += output;
                console.log(`[${sessionId}] Python stdout: ${output}`);
            });

            pythonProcess.stderr.on('data', (data) => {
                const output = data.toString();
                stderr += output;
                console.error(`[${sessionId}] Python stderr: ${output}`);
            });

            pythonProcess.on('close', (code) => {
                if (code === 0) {
                    console.log(`[${sessionId}] Procesamiento Python exitoso`);
                    resolve();
                } else {
                    console.error(`[${sessionId}] Error en Python. Código: ${code}`);
                    reject(new Error(`Python process exited with code ${code}\n${stderr}`));
                }
            });

            pythonProcess.on('error', (error) => {
                console.error(`[${sessionId}] Error al ejecutar Python:`, error);
                reject(error);
            });
        });

        // ========== COMPRIMIR RESULTADOS EN ZIP ==========

        const zipPath = path.join(tmpDir, 'planos_marcados.zip');
        
        await createZip(outputDir, zipPath);

        console.log(`[${sessionId}] ZIP generado: ${zipPath}`);

        // ========== ENVIAR ZIP AL FRONTEND ==========

        res.download(zipPath, 'planos_marcados.zip', async (err) => {
            if (err) {
                console.error(`[${sessionId}] Error al enviar ZIP:`, err);
            }

            // Limpiar archivos temporales después de la descarga
            try {
                await fs.rm(tmpDir, { recursive: true, force: true });
                console.log(`[${sessionId}] Archivos temporales eliminados`);
            } catch (cleanupError) {
                console.error(`[${sessionId}] Error al limpiar:`, cleanupError);
            }
        });

    } catch (error) {
        console.error(`[${sessionId}] Error en procesamiento:`, error);

        // Limpiar archivos temporales en caso de error
        try {
            await fs.rm(tmpDir, { recursive: true, force: true });
        } catch (cleanupError) {
            console.error(`[${sessionId}] Error al limpiar después de fallo:`, cleanupError);
        }

        res.status(500).json({ 
            error: error.message || 'Error al procesar los archivos'
        });
    }
});

// ========== FUNCIÓN PARA CREAR ZIP ==========

function createZip(sourceDir, outputPath) {
    return new Promise(async (resolve, reject) => {
        const output = require('fs').createWriteStream(outputPath);
        const archive = archiver('zip', {
            zlib: { level: 9 } // Máxima compresión
        });

        output.on('close', () => {
            console.log(`ZIP creado: ${archive.pointer()} bytes`);
            resolve();
        });

        archive.on('error', (err) => {
            reject(err);
        });

        archive.pipe(output);

        // Añadir todos los archivos del directorio de salida
        archive.directory(sourceDir, false);

        await archive.finalize();
    });
}

// ========== EXPORTAR ROUTER ==========

module.exports = router;
