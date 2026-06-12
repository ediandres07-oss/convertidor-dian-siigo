// ============================================================
// Convertidor DIAN → Siigo Nube — script principal
// ============================================================

// ── Helpers ──────────────────────────────────────────────────
function showMsg(containerId, text, isError) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div style="padding:.6rem 1rem;border-radius:6px;
        background:${isError ? '#fee2e2' : '#d1fae5'};
        color:${isError ? '#991b1b' : '#065f46'};
        border:1px solid ${isError ? '#fca5a5' : '#6ee7b7'}">
        ${text}</div>`;
}

function setLoading(btnId, spinnerId, loading) {
    const btn = document.getElementById(btnId);
    const sp  = document.getElementById(spinnerId);
    if (btn) btn.disabled = loading;
    if (sp)  sp.style.display = loading ? 'inline-block' : 'none';
}

async function downloadBlob(response, fallbackName) {
    const cd = response.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : fallbackName;
    const blob = await response.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
}

// ============================================================
// 1. FORMULARIO PRINCIPAL — Convertir a Planos
// ============================================================
document.addEventListener('DOMContentLoaded', () => {

    const dropZone   = document.getElementById('drop-zone');
    const fileInput  = document.getElementById('file-input');
    const browseBtn  = document.getElementById('browse-btn');
    const fileSelected = document.getElementById('file-selected');
    const fileName   = document.getElementById('file-name');
    const removeBtn  = document.getElementById('remove-file-btn');
    const submitBtn  = document.getElementById('submit-btn');
    const ivaBtn     = document.getElementById('iva-btn');
    const form       = document.getElementById('upload-form');
    const msgBox     = document.getElementById('message-container');
    const spinner    = document.getElementById('spinner');
    const spinnerIva = document.getElementById('spinner-iva');

    function setFile(file) {
        if (!file) return;
        fileName.textContent = file.name;
        fileSelected.style.display = 'flex';
        dropZone.querySelector('.upload-content').style.display = 'none';
        submitBtn.disabled = false;
        ivaBtn.disabled    = false;
        // mantener el file en el input
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
    }

    function clearFile() {
        fileInput.value = '';
        fileSelected.style.display = 'none';
        dropZone.querySelector('.upload-content').style.display = '';
        submitBtn.disabled = true;
        ivaBtn.disabled    = true;
        msgBox.innerHTML   = '';
    }

    browseBtn && browseBtn.addEventListener('click', e => {
        e.stopPropagation();   // evitar que el clic burbujee al drop-zone y abra el diálogo dos veces
        fileInput.click();
    });
    fileInput  && fileInput.addEventListener('change', () => {
        if (fileInput.files.length) setFile(fileInput.files[0]);
    });
    removeBtn  && removeBtn.addEventListener('click', clearFile);

    // Drag & drop
    if (dropZone) {
        dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
        });
        dropZone.addEventListener('click', e => {
            if (e.target === dropZone || e.target.closest('.upload-content')) fileInput.click();
        });
    }

    // Submit → Convertir
    form && form.addEventListener('submit', async e => {
        e.preventDefault();
        if (!fileInput.files.length) return;
        msgBox.innerHTML = '';
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        try {
            const fd = new FormData(form);
            const res = await fetch('/api/convert', { method: 'POST', body: fd });
            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }
            await downloadBlob(res, 'PLANOS.xlsx');
            showMsg('message-container', '✅ Planos generados correctamente.', false);
        } catch (err) {
            showMsg('message-container', `❌ ${err.message}`, true);
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });

    // Liquidar IVA
    ivaBtn && ivaBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) return;
        msgBox.innerHTML = '';
        ivaBtn.disabled  = true;
        spinnerIva.style.display = 'inline-block';
        try {
            const fd = new FormData();
            fd.append('file', fileInput.files[0]);
            const res = await fetch('/api/liquidar-iva', { method: 'POST', body: fd });
            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }
            await downloadBlob(res, 'LIQUIDACION_IVA.xlsx');
            showMsg('message-container', '✅ Liquidación de IVA generada.', false);
        } catch (err) {
            showMsg('message-container', `❌ ${err.message}`, true);
        } finally {
            ivaBtn.disabled = false;
            spinnerIva.style.display = 'none';
        }
    });

    // ============================================================
    // 2. BALANCE DE PRUEBA POR TERCERO
    // ============================================================
    const balancePruebaInput = document.getElementById('balance-prueba-input');
    const balancePruebaBtn   = document.getElementById('balance-prueba-btn');
    const spinnerBalP        = document.getElementById('spinner-balance-prueba');
    const msgBalP            = document.getElementById('balance-prueba-message');

    balancePruebaBtn && balancePruebaBtn.addEventListener('click', async () => {
        if (!balancePruebaInput || !balancePruebaInput.files.length) {
            msgBalP.innerHTML = '<span style="color:#b45309">⚠️ Selecciona el archivo de Balance primero.</span>';
            return;
        }
        msgBalP.innerHTML = '';
        setLoading('balance-prueba-btn', 'spinner-balance-prueba', true);
        try {
            const fd = new FormData();
            fd.append('file', balancePruebaInput.files[0]);
            const res = await fetch('/api/balance', { method: 'POST', body: fd });
            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }
            await downloadBlob(res, 'BALANCE_TERCERO.xlsx');
            showMsg('balance-prueba-message', '✅ Balance generado correctamente.', false);
        } catch (err) {
            showMsg('balance-prueba-message', `❌ ${err.message}`, true);
        } finally {
            setLoading('balance-prueba-btn', 'spinner-balance-prueba', false);
        }
    });

    // ============================================================
    // 3. NÓMINA
    // ============================================================
    const nominaBtn    = document.getElementById('nomina-btn');
    const balanceInput = document.getElementById('balance-input');
    const consecNomina = document.getElementById('consec_nomina');
    const spinnerNom   = document.getElementById('spinner-nomina');
    const msgNom       = document.getElementById('nomina-message');

    nominaBtn && nominaBtn.addEventListener('click', async () => {
        if (!balanceInput || !balanceInput.files.length) {
            msgNom.innerHTML = '<span style="color:#b45309">⚠️ Selecciona el archivo de Balance primero.</span>';
            return;
        }
        msgNom.innerHTML = '';
        setLoading('nomina-btn', 'spinner-nomina', true);
        try {
            const fd = new FormData();
            fd.append('balance', balanceInput.files[0]);
            fd.append('consec_nomina', consecNomina ? consecNomina.value : '1');
            const res = await fetch('/api/nomina', { method: 'POST', body: fd });
            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }
            await downloadBlob(res, 'PLANO_NOMINA.xlsx');
            showMsg('nomina-message', '✅ Plano de nómina generado correctamente.', false);
        } catch (err) {
            showMsg('nomina-message', `❌ ${err.message}`, true);
        } finally {
            setLoading('nomina-btn', 'spinner-nomina', false);
        }
    });

});
