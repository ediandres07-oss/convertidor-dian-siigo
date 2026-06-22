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

    // ============================================================
    // 4. LIQUIDACIONES DEFINITIVAS, VACACIONES Y PRIMAS
    // ============================================================
    let employees = [];

    function renderEmployeesTable() {
        const employeesTbody = document.getElementById('employees-tbody');
        if (!employeesTbody) return;

        employeesTbody.innerHTML = employees.map((emp, idx) => `
            <tr style="border-bottom:1px solid #e2e8f0;">
                <td style="border:1px solid #e2e8f0;padding:.5rem;"><input type="text" value="${emp.nombre}" placeholder="Nombre" style="width:100%;border:1px solid #e2e8f0;padding:.3rem;border-radius:3px;font-size:.8rem;" data-idx="${idx}" data-field="nombre" class="emp-input"></td>
                <td style="border:1px solid #e2e8f0;padding:.5rem;text-align:right;"><input type="number" value="${emp.salario}" placeholder="Salario" style="width:100%;border:1px solid #e2e8f0;padding:.3rem;border-radius:3px;text-align:right;font-size:.8rem;" data-idx="${idx}" data-field="salario" class="emp-input"></td>
                <td style="border:1px solid #e2e8f0;padding:.5rem;text-align:center;"><input type="date" value="${emp.fecha_ingreso}" style="width:100%;border:1px solid #e2e8f0;padding:.3rem;border-radius:3px;font-size:.8rem;" data-idx="${idx}" data-field="fecha_ingreso" class="emp-input"></td>
                <td style="border:1px solid #e2e8f0;padding:.5rem;text-align:center;"><input type="date" value="${emp.fecha_retiro}" style="width:100%;border:1px solid #e2e8f0;padding:.3rem;border-radius:3px;font-size:.8rem;" data-idx="${idx}" data-field="fecha_retiro" class="emp-input"></td>
                <td style="border:1px solid #e2e8f0;padding:.5rem;text-align:center;">
                    <select style="width:100%;border:1px solid #e2e8f0;padding:.3rem;border-radius:3px;font-size:.8rem;" data-idx="${idx}" data-field="tipo_retiro" class="emp-input">
                        <option value="retiro_voluntario" ${emp.tipo_retiro === 'retiro_voluntario' ? 'selected' : ''}>Retiro Voluntario</option>
                        <option value="despido_justificado" ${emp.tipo_retiro === 'despido_justificado' ? 'selected' : ''}>Despido Justificado</option>
                        <option value="despido_sin_causa" ${emp.tipo_retiro === 'despido_sin_causa' ? 'selected' : ''}>Despido Sin Causa</option>
                        <option value="jubilacion" ${emp.tipo_retiro === 'jubilacion' ? 'selected' : ''}>Jubilación</option>
                        <option value="muerte" ${emp.tipo_retiro === 'muerte' ? 'selected' : ''}>Muerte</option>
                    </select>
                </td>
                <td style="border:1px solid #e2e8f0;padding:.5rem;text-align:center;">
                    <button type="button" class="delete-btn" data-idx="${idx}" title="Eliminar" style="background:#ef4444;color:white;border:none;padding:4px 8px;border-radius:3px;cursor:pointer;font-size:.7rem;">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');

        // Attach input listeners
        document.querySelectorAll('.emp-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const idx = parseInt(e.target.dataset.idx);
                const field = e.target.dataset.field;
                let value;
                if (field === 'salario') {
                    value = parseFloat(e.target.value) || 0;
                } else {
                    value = e.target.value;
                }
                if (employees[idx]) employees[idx][field] = value;
            });
        });

        // Attach delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const idx = parseInt(e.target.dataset.idx);
                employees.splice(idx, 1);
                renderEmployeesTable();
            });
        });
    }

    const addEmployeeBtn = document.getElementById('add-employee-btn');
    if (addEmployeeBtn) {
        addEmployeeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const hoy = new Date().toISOString().split('T')[0];
            employees.push({
                nombre: '',
                salario: 0,
                fecha_ingreso: hoy,
                fecha_retiro: hoy,
                tipo_retiro: 'retiro_voluntario'
            });
            renderEmployeesTable();
        });
    }

    const generateLiquidacionBtn = document.getElementById('generate-liquidacion-btn');
    if (generateLiquidacionBtn) {
        generateLiquidacionBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (employees.length === 0) {
                showMsg('liquidacion-message', '⚠️ Agrega al menos un empleado.', true);
                return;
            }
            const msgLiq = document.getElementById('liquidacion-message');
            if (msgLiq) msgLiq.innerHTML = '';
            setLoading('generate-liquidacion-btn', 'spinner-liquidacion', true);
            try {
                const res = await fetch('/api/liquidaciones', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ empleados: employees })
                });
                if (!res.ok) {
                    const j = await res.json();
                    throw new Error(j.error || `Error ${res.status}`);
                }
                await downloadBlob(res, 'LIQUIDACIONES.xlsx');
                showMsg('liquidacion-message', '✅ Reporte de liquidaciones generado correctamente.', false);
            } catch (err) {
                showMsg('liquidacion-message', `❌ ${err.message}`, true);
            } finally {
                setLoading('generate-liquidacion-btn', 'spinner-liquidacion', false);
            }
        });
    }

    // ============================================================
    // DIAN - DESCARGAR REPORTES
    // ============================================================
    const dianBtn     = document.getElementById('dian-btn');
    const dianUser    = document.getElementById('dian-user');
    const dianPass    = document.getElementById('dian-pass');
    const spinnerDian = document.getElementById('spinner-dian');
    const msgDian     = document.getElementById('dian-message');

    dianBtn && dianBtn.addEventListener('click', async () => {
        if (!dianUser.value || !dianPass.value) {
            msgDian.innerHTML = '<span style="color:#b45309">⚠️ Ingresa tus credenciales de DIAN.</span>';
            return;
        }

        msgDian.innerHTML = '';
        setLoading('dian-btn', 'spinner-dian', true);
        try {
            const res = await fetch('/api/download-dian', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    usuario: dianUser.value,
                    password: dianPass.value
                })
            });

            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }

            await downloadBlob(res, `Reporte_DIAN_${new Date().toISOString().split('T')[0]}.xlsx`);
            showMsg('dian-message', '✅ Reporte descargado. Ahora sube el archivo a los planos.', false);
        } catch (err) {
            showMsg('dian-message', `❌ ${err.message}`, true);
        } finally {
            setLoading('dian-btn', 'spinner-dian', false);
        }
    });

    // ============================================================
    // SIIGO - SUBIR PLANOS AUTOMÁTICAMENTE
    // ============================================================
    const siigoBtn    = document.getElementById('siigo-btn');
    const siigoUser   = document.getElementById('siigo-user');
    const siigoPass   = document.getElementById('siigo-pass');
    const spinnerSiigo = document.getElementById('spinner-siigo');
    const msgSiigo    = document.getElementById('siigo-message');

    siigoBtn && siigoBtn.addEventListener('click', async () => {
        if (!fileInput || !fileInput.files.length) {
            msgSiigo.innerHTML = '<span style="color:#b45309">⚠️ Primero genera los planos.</span>';
            return;
        }
        if (!siigoUser.value || !siigoPass.value) {
            msgSiigo.innerHTML = '<span style="color:#b45309">⚠️ Ingresa tus credenciales de Siigo API.</span>';
            return;
        }

        msgSiigo.innerHTML = '';
        setLoading('siigo-btn', 'spinner-siigo', true);
        try {
            // Primero generar los planos
            const fd = new FormData(form);
            const planeRes = await fetch('/api/convert', { method: 'POST', body: fd });
            if (!planeRes.ok) {
                const j = await planeRes.json();
                throw new Error(j.error || 'Error generando planos');
            }
            const planeBlob = await planeRes.blob();

            // Luego subir a Siigo
            const siigoFd = new FormData();
            siigoFd.append('file', planeBlob, 'PLANOS.xlsx');
            siigoFd.append('siigo_user', siigoUser.value);
            siigoFd.append('siigo_pass', siigoPass.value);

            const res = await fetch('/api/upload-siigo', { method: 'POST', body: siigoFd });
            if (!res.ok) {
                const j = await res.json();
                throw new Error(j.error || `Error ${res.status}`);
            }
            const result = await res.json();
            showMsg('siigo-message', `✅ ${result.mensaje || 'Planos subidos a Siigo correctamente'}`, false);
            console.log('Detalles:', result.detalles);
        } catch (err) {
            showMsg('siigo-message', `❌ ${err.message}`, true);
        } finally {
            setLoading('siigo-btn', 'spinner-siigo', false);
        }
    });

});
