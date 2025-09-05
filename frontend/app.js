// Set backend base URL. If frontend is served from same origin as backend, set to ''
const API_BASE = 'https://probable-waffle-g4596x4wp7j93r77-8000.app.github.dev'; // or window.location.origin

const extractForm = document.getElementById('extractForm');
const results = document.getElementById('results');
const fieldsDiv = document.getElementById('fields');
const submittedFieldsInput = document.getElementById('submittedFields');
const verifyForm = document.getElementById('verifyForm');
const qualityDiv = document.getElementById('quality');
const verifyOut = document.getElementById('verifyOut');

let lastFile = null;
let lastDocType = 'generic';
let lastLang = 'eng';
extractForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(extractForm);
  lastFile = document.getElementById('file').files[0];
  lastDocType = form.get('docType');
  lastLang = form.get('language');
  try {
    const res = await fetch(API_BASE + '/api/ocr/extract', { method: 'POST', body: form });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Server ${res.status}: ${text}`);
    }
    const data = await res.json();
    results.style.display = 'block';
    fieldsDiv.innerHTML = '';
    (data.fields || []).forEach(f => {
      const row = document.createElement('div');
      row.className = 'field-row';
      row.innerHTML = `
        <label>${f.name}</label>
        <input type="text" value="${(f.value||'')}" data-name="${f.name}"/>
        <span class="conf">conf: ${(f.confidence||0).toFixed(2)}</span>
      `;
      fieldsDiv.appendChild(row);
    });
    qualityDiv.innerText = `Avg blur: ${data.quality?.avgBlur?.toFixed(1)} | Avg brightness: ${data.quality?.avgBrightness?.toFixed(2)}`;
  } catch (err) {
    console.error('Extract failed', err);
    alert('Extract failed: ' + err.message);
  }
});

verifyForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const inputs = [...fieldsDiv.querySelectorAll('input[type="text"]')];
  const payload = inputs.map(inp => ({ name: inp.dataset.name, value: inp.value }));
  submittedFieldsInput.value = JSON.stringify(payload);
  const form = new FormData();
  form.append('file', lastFile);
  form.append('submittedFields', submittedFieldsInput.value);
  form.append('docType', lastDocType);
  form.append('language', lastLang);
  form.append('prefer_trocr', 'true');
  const res = await fetch(API_BASE + '/api/ocr/verify', { method: 'POST', body: form });
  const data = await res.json();
  verifyOut.textContent = JSON.stringify(data, null, 2);
});