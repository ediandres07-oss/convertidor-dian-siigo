document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadContent = document.querySelector('.upload-content');
    const fileSelected = document.getElementById('file-selected');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const submitBtn = document.getElementById('submit-btn');
    const ivaBtn = document.getElementById('iva-btn');
    const uploadForm = document.getElementById('upload-form');
    const spinner = document.getElementById('spinner');
    const spinnerIva = document.getElementById('spinner-iva');
    const messageContainer = document.getElementById('message-container');

    let currentFile = null;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle click to browse
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    dropZone.addEventListener('click', (e) => {
        // Prevent triggering file input if clicking on remove button
        if (!e.target.closest('#remove-file-btn') && !e.target.closest('#browse-btn')) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        // Validate file type (simple extension check)
        const validExtensions = ['.xlsx', '.xls'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(fileExtension)) {
            showMessage('Por favor, selecciona un archivo Excel válido (.xlsx o .xls)', 'error');
            return;
        }

        currentFile = file;
        updateUIForFile(file.name);
    }

    function updateUIForFile(name) {
        uploadContent.style.display = 'none';
        fileSelected.style.display = 'flex';
        fileName.textContent = name;
        submitBtn.disabled = false;
        ivaBtn.disabled = false;
        messageContainer.innerHTML = ''; // Clear any previous messages
    }

    // Handle remove file
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering dropZone click
        currentFile = null;
        fileInput.value = ''; // Reset input
        uploadContent.style.display = 'block';
        fileSelected.style.display = 'none';
        submitBtn.disabled = true;
        ivaBtn.disabled = true;
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentFile) {
            showMessage('Por favor, selecciona un archivo primero', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('consec_compras', document.getElementById('consec_compras').value);
        formData.append('consec_nc', document.getElementById('consec_nc').value);
        formData.append('consec_gastos', document.getElementById('consec_gastos').value);

        setLoadingState(true);
        messageContainer.innerHTML = '';

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                // Try to parse error JSON
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Error del servidor: ${response.status}`);
            }

            // Get filename from Content-Disposition header if available
            let filename = `PLANOS_${currentFile.name}`;
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/["']/g, '');
            }

            // Convert blob to downloadable link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showMessage('¡Archivo convertido y descargado con éxito!', 'success');
            
            // Optionally reset form
            // currentFile = null;
            // uploadContent.style.display = 'block';
            // fileSelected.style.display = 'none';
            // submitBtn.disabled = true;
            
        } catch (error) {
            console.error('Error:', error);
            showMessage(error.message, 'error');
        } finally {
            setLoadingState(false);
        }
    });

    // Handle IVA liquidation button
    ivaBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('file', currentFile);

        setIvaLoadingState(true);
        messageContainer.innerHTML = '';

        try {
            const response = await fetch('/api/liquidar-iva', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Error del servidor: ${response.status}`);
            }

            let filename = `LIQUIDACION_IVA_${currentFile.name}`;
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/["']/g, '');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showMessage('¡Liquidación de IVA generada y descargada con éxito!', 'success');
        } catch (error) {
            console.error('Error:', error);
            showMessage(error.message, 'error');
        } finally {
            setIvaLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            ivaBtn.disabled = true;
            submitBtn.querySelector('span').style.opacity = '0';
            spinner.style.display = 'block';
            spinner.style.position = 'absolute';
        } else {
            submitBtn.disabled = false;
            ivaBtn.disabled = !currentFile;
            submitBtn.querySelector('span').style.opacity = '1';
            spinner.style.display = 'none';
        }
    }

    function setIvaLoadingState(isLoading) {
        if (isLoading) {
            ivaBtn.disabled = true;
            submitBtn.disabled = true;
            ivaBtn.querySelector('span').style.opacity = '0';
            spinnerIva.style.display = 'block';
            spinnerIva.style.position = 'absolute';
        } else {
            ivaBtn.disabled = false;
            submitBtn.disabled = !currentFile;
            ivaBtn.querySelector('span').style.opacity = '1';
            spinnerIva.style.display = 'none';
        }
    }

    function showMessage(text, type) {
        const icon = type === 'error' 
            ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`
            : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22 11.08V12C21.9988 14.1564 21.3001 16.2547 20.0093 17.9818C18.7185 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13632 4.39828 5.49706C5.79935 3.8578 7.69279 2.71537 9.79619 2.24014C11.8996 1.76491 14.1003 1.98233 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 4L12 14.01L9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
            
        messageContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${icon}
                <span>${text}</span>
            </div>
        `;
    }
});
