async function api(path, method='GET', body=null) {
  const opts = {method, headers: {}};
  if (body && !(body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  } else if (body instanceof FormData) {
    opts.body = body;
  }
  const res = await fetch(path, opts);
  return res.json();
}

function log(msg) {
  const area = document.getElementById('logArea');
  const now = new Date().toLocaleTimeString();
  area.textContent = `[${now}] ${msg}\n` + area.textContent;
}

// list files
async function loadFiles() {
  const list = document.getElementById('filesList');
  list.innerHTML = "<div class='small-muted'>Loading...</div>";
  const res = await api('/api/files');
  if (!res.ok) {
    log('Failed to list files');
    list.innerHTML = '';
    return;
  }
  list.innerHTML = '';
  res.files.forEach(f => {
    const item = document.createElement('div');
    item.className = 'list-group-item file-row';
    item.innerHTML = `
      <div style="flex:1">
        <input type="checkbox" class="sel-checkbox me-2" data-name="${f.name}">
        <strong>${f.name}</strong>
        <div class="small-muted">Size: ${Math.round(f.size/1024)} KB • Modified: ${new Date(f.mtime*1000).toLocaleString()}</div>
      </div>
      <div class="file-actions">
        <button class="btn btn-sm btn-outline-secondary btn-rename" data-name="${f.name}">Rename</button>
        <button class="btn btn-sm btn-outline-info btn-update" data-name="${f.name}">Update</button>
        <button class="btn btn-sm btn-outline-danger btn-delete" data-name="${f.name}">Delete</button>
        <a class="btn btn-sm btn-outline-dark" href="/files/${encodeURIComponent(f.name)}" download>Download</a>
      </div>
    `;
    list.appendChild(item);
  });

  // wire up buttons
  document.querySelectorAll('.btn-delete').forEach(btn =>
    btn.addEventListener('click', onDelete));
  document.querySelectorAll('.btn-rename').forEach(btn =>
    btn.addEventListener('click', onRename));
  document.querySelectorAll('.btn-update').forEach(btn =>
    btn.addEventListener('click', onUpdate));
}

async function onDelete(e) {
  const name = e.target.dataset.name;
  if (!confirm(`Delete ${name}?`)) return;
  const res = await api('/api/delete', 'POST', {name});
  if (res.ok) {
    log(`Deleted ${name}`);
    loadFiles();
  } else {
    log('Delete error: ' + (res.error||'unknown'));
  }
}

async function onRename(e) {
  const old = e.target.dataset.name;
  const newName = prompt("Enter new filename (include .pdf):", old);
  if (!newName) return;
  const res = await api('/api/rename', 'POST', {old_name: old, new_name: newName});
  if (res.ok) {
    log(`Renamed ${old} -> ${res.renamed.to}`);
    loadFiles();
  } else {
    log('Rename error: ' + (res.error||'unknown'));
  }
}

async function onUpdate(e) {
  const old = e.target.dataset.name;
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.pdf';
  fileInput.onchange = async () => {
    const file = fileInput.files[0];
    if (!file) return;
    const form = new FormData();
    form.append('filename', old);
    form.append('file', file);
    const res = await fetch('/api/update', {method:'POST', body: form});
    const json = await res.json();
    if (json.ok) {
      log(`Updated ${old}`);
      loadFiles();
    } else {
      log('Update error: ' + (json.error||'unknown'));
    }
  };
  fileInput.click();
}

// Upload
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const input = document.getElementById('fileInput');
  if (!input.files.length) {
    alert('Choose at least one PDF to upload');
    return;
  }
  const form = new FormData();
  for (const f of input.files) form.append('files', f);
  const res = await fetch('/api/upload', {method: 'POST', body: form});
  const json = await res.json();
  if (json.ok) {
    log(`Uploaded: ${json.saved.join(', ')}`);
    input.value = '';
    loadFiles();
  } else {
    log('Upload failed');
  }
});

// Merge selected
document.getElementById('mergeBtn').addEventListener('click', async () => {
  const checks = Array.from(document.querySelectorAll('.sel-checkbox:checked'));
  if (!checks.length) {
    alert('Select at least one file');
    return;
  }
  const files = checks.map(c => c.dataset.name);
  let out = document.getElementById('mergeName').value.trim() || 'merged.pdf';
  if (!out.toLowerCase().endsWith('.pdf')) out += '.pdf';
  const res = await api('/api/merge', 'POST', {files, output_name: out});
  if (res.ok) {
    log(`Merged into ${res.merged}`);
    loadFiles();
  } else {
    log('Merge error: ' + (res.error||'unknown'));
  }
});

// Organize by keyword
document.getElementById('organizeKeyword').addEventListener('click', async () => {
  let txt = document.getElementById('keywordMap').value.trim();
  try {
    const map = JSON.parse(txt);
    const res = await api('/api/organize', 'POST', {mode:'keyword', map});
    if (res.ok) {
      log('Organize by keyword done: ' + JSON.stringify(res.result));
    } else {
      log('Organize error: ' + (res.error||'unknown'));
    }
  } catch (err) {
    alert('Invalid JSON for mapping');
  }
});

// Organize by year
document.getElementById('organizeYear').addEventListener('click', async () => {
  const res = await api('/api/organize', 'POST', {mode: 'year'});
  if (res.ok) {
    log('Organized by year');
  } else {
    log('Organize error: ' + (res.error||'unknown'));
  }
});

// initial load
loadFiles();