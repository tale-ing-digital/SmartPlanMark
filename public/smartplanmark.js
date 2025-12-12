/**
 * SmartPlanMark - Cliente JavaScript
 * TalePlanHub © 2025
 * Gestión de carga, procesamiento y descarga de planos marcados
 */

(function() {
    'use strict';

    // ========== ELEMENTOS DEL DOM ==========
    const pdfInput = document.getElementById('pdfInput');
    const csvInput = document.getElementById('csvInput');
    const pdfUploadArea = document.getElementById('pdfUploadArea');
    const csvUploadArea = document.getElementById('csvUploadArea');
    const pdfFileName = document.getElementById('pdfFileName');
    const csvFileName = document.getElementById('csvFileName');
    const processBtn = document.getElementById('processBtn');
    const logsSection = document.getElementById('logsSection');
    const logsContainer = document.getElementById('logsContainer');
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');

    // ========== VARIABLES DE ESTADO ==========
    let pdfFile = null;
    let csvFile = null;
    let downloadBlob = null;

    // ========== CONFIGURACIÓN ==========
    const MAX_PDF_SIZE = 50 * 1024 * 1024; // 50 MB
    const MAX_CSV_SIZE = 5 * 1024 * 1024;  // 5 MB
    const API_ENDPOINT = '/api/smartplanmark/process';

    // ========== MANEJO DE SUBIDA DE ARCHIVOS ==========

    // PDF Upload Area - Click
    pdfUploadArea.addEventListener('click', () => {
        pdfInput.click();
    });

    // PDF Input Change
    pdfInput.addEventListener('change', (e) => {
        handlePdfUpload(e.target.files[0]);
    });

    // PDF Upload Area - Drag & Drop
    pdfUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        pdfUploadArea.style.borderColor = 'var(--color-cyan-hover)';
    });

    pdfUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        pdfUploadArea.style.borderColor = 'var(--color-primary-cyan)';
    });

    pdfUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        pdfUploadArea.style.borderColor = 'var(--color-primary-cyan)';
        const file = e.dataTransfer.files[0];
        handlePdfUpload(file);
    });

    // CSV Upload Area - Click
    csvUploadArea.addEventListener('click', () => {
        csvInput.click();
    });

    // CSV Input Change
    csvInput.addEventListener('change', (e) => {
        handleCsvUpload(e.target.files[0]);
    });

    // CSV Upload Area - Drag & Drop
    csvUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        csvUploadArea.style.borderColor = 'var(--color-cyan-hover)';
    });

    csvUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        csvUploadArea.style.borderColor = 'var(--color-primary-cyan)';
    });

    csvUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        csvUploadArea.style.borderColor = 'var(--color-primary-cyan)';
        const file = e.dataTransfer.files[0];
        handleCsvUpload(file);
    });

    // ========== VALIDACIÓN DE ARCHIVOS ==========

    function handlePdfUpload(file) {
        if (!file) return;

        // Validar extensión
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError('El archivo debe ser un PDF válido (.pdf)');
            pdfFile = null;
            pdfFileName.textContent = '';
            checkFormValidity();
            return;
        }

        // Validar tamaño
        if (file.size > MAX_PDF_SIZE) {
            showError(`El PDF excede el tamaño máximo permitido (${formatFileSize(MAX_PDF_SIZE)})`);
            pdfFile = null;
            pdfFileName.textContent = '';
            checkFormValidity();
            return;
        }

        // Archivo válido
        pdfFile = file;
        pdfFileName.textContent = `✅ ${file.name} (${formatFileSize(file.size)})`;
        addLog(`PDF cargado: ${file.name}`, 'success');
        checkFormValidity();
    }

    function handleCsvUpload(file) {
        if (!file) return;

        // Validar extensión
        if (!file.name.toLowerCase().endsWith('.csv')) {
            showError('El archivo debe ser un CSV válido (.csv)');
            csvFile = null;
            csvFileName.textContent = '';
            checkFormValidity();
            return;
        }

        // Validar tamaño
        if (file.size > MAX_CSV_SIZE) {
            showError(`El CSV excede el tamaño máximo permitido (${formatFileSize(MAX_CSV_SIZE)})`);
            csvFile = null;
            csvFileName.textContent = '';
            checkFormValidity();
            return;
        }

        // Validar contenido básico
        validateCsvContent(file);
    }

    function validateCsvContent(file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const content = e.target.result;
            const lines = content.split('\n');
            
            if (lines.length < 2) {
                showError('El CSV debe contener al menos una fila de encabezados y una fila de datos');
                csvFile = null;
                csvFileName.textContent = '';
                checkFormValidity();
                return;
            }

            // Validar encabezados
            const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
            const hasDepto = headers.some(h => h.includes('depto'));
            const hasEstacionamiento = headers.some(h => h.includes('estacionamiento'));

            if (!hasDepto || !hasEstacionamiento) {
                showError('El CSV debe contener las columnas: "depto" y "estacionamiento"');
                csvFile = null;
                csvFileName.textContent = '';
                checkFormValidity();
                return;
            }

            // Archivo válido
            csvFile = file;
            csvFileName.textContent = `✅ ${file.name} (${formatFileSize(file.size)})`;
            addLog(`CSV cargado: ${file.name} - ${lines.length - 1} registros`, 'success');
            checkFormValidity();
        };

        reader.onerror = function() {
            showError('Error al leer el archivo CSV');
            csvFile = null;
            csvFileName.textContent = '';
            checkFormValidity();
        };

        reader.readAsText(file);
    }

    // ========== VALIDACIÓN DEL FORMULARIO ==========

    function checkFormValidity() {
        if (pdfFile && csvFile) {
            processBtn.disabled = false;
            addLog('✅ Archivos listos. Puedes procesar los planos.', 'info');
        } else {
            processBtn.disabled = true;
        }
    }

    // ========== PROCESAMIENTO ==========

    processBtn.addEventListener('click', async () => {
        if (!pdfFile || !csvFile) return;

        try {
            // Deshabilitar botón
            processBtn.disabled = true;
            processBtn.textContent = '⏳ Procesando...';

            // Ocultar sección de descarga previa
            downloadSection.classList.remove('active');
            downloadBlob = null;

            // Mostrar logs
            logsSection.classList.add('active');
            clearLogs();
            addLog('🚀 Iniciando procesamiento...', 'info');

            // Crear FormData
            const formData = new FormData();
            formData.append('pdf', pdfFile);
            formData.append('csv', csvFile);

            addLog('📤 Enviando archivos al servidor...', 'info');

            // Enviar solicitud
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Error del servidor: ${response.status} ${response.statusText}`);
            }

            addLog('✅ Archivos recibidos por el servidor', 'success');
            addLog('🔄 Procesando planos...', 'info');

            // Obtener blob
            downloadBlob = await response.blob();

            addLog('✅ Procesamiento completado exitosamente', 'success');
            addLog(`📦 Archivo ZIP generado (${formatFileSize(downloadBlob.size)})`, 'success');

            // Mostrar sección de descarga
            downloadSection.classList.add('active');

            // Resetear botón
            processBtn.textContent = 'Procesar Planos';
            processBtn.disabled = false;

        } catch (error) {
            console.error('Error en procesamiento:', error);
            addLog(`❌ Error: ${error.message}`, 'error');
            showError(`Error al procesar: ${error.message}`);

            // Resetear botón
            processBtn.textContent = 'Procesar Planos';
            processBtn.disabled = false;
        }
    });

    // ========== DESCARGA ==========

    downloadBtn.addEventListener('click', () => {
        if (!downloadBlob) {
            showError('No hay archivo disponible para descargar');
            return;
        }

        try {
            const url = window.URL.createObjectURL(downloadBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `planos_marcados_${Date.now()}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            addLog('✅ Descarga iniciada', 'success');
        } catch (error) {
            console.error('Error en descarga:', error);
            showError('Error al descargar el archivo');
        }
    });

    // ========== UTILIDADES DE LOGS ==========

    function addLog(message, type = 'info') {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${getCurrentTime()}] ${message}`;
        logsContainer.appendChild(logEntry);

        // Auto-scroll al último log
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function clearLogs() {
        logsContainer.innerHTML = '';
    }

    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    }

    // ========== MANEJO DE ERRORES ==========

    function showError(message) {
        // Crear info-box de error si no existe
        let errorBox = document.querySelector('.error-box');
        
        if (!errorBox) {
            errorBox = document.createElement('div');
            errorBox.className = 'error-box';
            errorBox.style.cssText = `
                background: #FEE2E2;
                border-left: 4px solid #EF4444;
                padding: 1rem 1.25rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                color: #991B1B;
                font-weight: 500;
                transition: all 0.3s ease;
            `;
            
            // Insertar después del título
            const container = document.querySelector('.container');
            const title = container.querySelector('h2');
            title.parentNode.insertBefore(errorBox, title.nextSibling);
        }

        errorBox.textContent = `⚠️ ${message}`;
        errorBox.style.display = 'block';

        // Adaptar al modo oscuro
        if (document.body.classList.contains('dark-mode')) {
            errorBox.style.background = '#7F1D1D';
            errorBox.style.color = '#FEE2E2';
        } else {
            errorBox.style.background = '#FEE2E2';
            errorBox.style.color = '#991B1B';
        }

        // Añadir al log
        addLog(message, 'error');

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            errorBox.style.display = 'none';
        }, 5000);
    }

    // ========== UTILIDADES ==========

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    // ========== OBSERVER PARA DARK MODE ==========

    // Observar cambios en el modo oscuro para actualizar error boxes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const errorBox = document.querySelector('.error-box');
                if (errorBox && errorBox.style.display !== 'none') {
                    if (document.body.classList.contains('dark-mode')) {
                        errorBox.style.background = '#7F1D1D';
                        errorBox.style.color = '#FEE2E2';
                    } else {
                        errorBox.style.background = '#FEE2E2';
                        errorBox.style.color = '#991B1B';
                    }
                }
            }
        });
    });

    observer.observe(document.body, { attributes: true });

    // ========== INICIALIZACIÓN ==========

    console.log('SmartPlanMark JS cargado correctamente');
    addLog('Sistema iniciado. Esperando archivos...', 'info');

})();
