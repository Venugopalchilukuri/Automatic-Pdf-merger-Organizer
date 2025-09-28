import os
import shutil
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename
from pypdf import PdfReader, PdfWriter
from pdfminer.high_level import extract_text

import config

# ensure folders exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.ORGANIZED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# ---- Utilities ----

def allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in config.ALLOWED_EXTENSIONS

def file_path(filename):
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def compute_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def list_uploaded_files():
    files = []
    for fname in sorted(os.listdir(app.config['UPLOAD_FOLDER'])):
        if not allowed_file(fname):
            continue
        p = file_path(fname)
        stat = os.stat(p)
        try:
            pdf = PdfReader(p)
            meta = pdf.metadata
            title = meta.title if meta and hasattr(meta, 'title') and meta.title else fname
        except Exception:
            title = fname
        files.append({
            "name": fname,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "hash": compute_hash(p)
        })
    return files

def ensure_safe_filename(name):
    return secure_filename(name)

# ---- Routes ----

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/files", methods=["GET"])
def api_list_files():
    files = list_uploaded_files()
    for f in files:
        f["mtime_iso"] = datetime.fromtimestamp(f["mtime"]).isoformat()
    return jsonify({"ok": True, "files": files})

@app.route("/files/<path:filename>", methods=["GET"])
def serve_file(filename):
    if not allowed_file(filename):
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if 'files' not in request.files:
        return jsonify({"ok": False, "error": "No files part"}), 400

    uploaded = request.files.getlist("files")
    saved = []
    for f in uploaded:
        if f and allowed_file(f.filename):
            orig = f.filename
            safe = ensure_safe_filename(orig)
            dest = file_path(safe)
            counter = 1
            base, ext = os.path.splitext(safe)
            while os.path.exists(dest):
                safe = f"{base}_{counter}{ext}"
                dest = file_path(safe)
                counter += 1
            f.save(dest)
            saved.append(safe)
    return jsonify({"ok": True, "saved": saved})

@app.route("/api/update", methods=["POST"])
def api_update():
    existing = request.form.get("filename", "")
    if not existing:
        return jsonify({"ok": False, "error": "Missing filename"}), 400
    if 'file' not in request.files:
        return jsonify({"ok": False, "error": "Missing file"}), 400
    if not allowed_file(existing):
        return jsonify({"ok": False, "error": "Invalid file"}), 400
    uploaded = request.files['file']
    if not allowed_file(uploaded.filename):
        return jsonify({"ok": False, "error": "Uploaded file not a PDF"}), 400
    dest = file_path(existing)
    if not os.path.exists(dest):
        return jsonify({"ok": False, "error": "Existing file not found"}), 404
    uploaded.save(dest)
    return jsonify({"ok": True, "replaced": existing})

@app.route("/api/rename", methods=["POST"])
def api_rename():
    data = request.json or {}
    old = data.get("old_name")
    new = data.get("new_name")
    if not old or not new:
        return jsonify({"ok": False, "error": "old_name/new_name required"}), 400
    if not allowed_file(old) or not allowed_file(new):
        return jsonify({"ok": False, "error": "Wrong extension; must be .pdf"}), 400
    oldp = file_path(old)
    new_safe = ensure_safe_filename(new)
    newp = file_path(new_safe)
    if not os.path.exists(oldp):
        return jsonify({"ok": False, "error": "File not found"}), 404
    if os.path.exists(newp):
        return jsonify({"ok": False, "error": "Target filename exists"}), 400
    os.rename(oldp, newp)
    return jsonify({"ok": True, "renamed": {"from": old, "to": new_safe}})

@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"ok": False, "error": "name required"}), 400
    p = file_path(name)
    if not os.path.exists(p):
        return jsonify({"ok": False, "error": "File not found"}), 404
    os.remove(p)
    return jsonify({"ok": True, "deleted": name})

@app.route("/api/merge", methods=["POST"])
def api_merge():
    data = request.json or {}
    files = data.get("files", [])
    output_name = data.get("output_name", "merged.pdf")
    if not files:
        return jsonify({"ok": False, "error": "No files selected"}), 400
    output_name = ensure_safe_filename(output_name)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)

    writer = PdfWriter()
    try:
        for fname in files:
            p = file_path(fname)
            if not os.path.exists(p):
                return jsonify({"ok": False, "error": f"File missing: {fname}"}), 404
            writer.append(p)

        with open(output_path, "wb") as f:
            writer.write(f)

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    return jsonify({"ok": True, "merged": output_name})

@app.route("/api/organize", methods=["POST"])
def api_organize():
    data = request.json or {}
    mode = data.get("mode")
    if not mode:
        return jsonify({"ok": False, "error": "mode required"}), 400

    if mode == "keyword":
        mapping = data.get("map", {})
        if not mapping:
            return jsonify({"ok": False, "error": "map required for keyword mode"}), 400
        results = []
        for keyword, folder_name in mapping.items():
            folder_path = os.path.join(config.ORGANIZED_FOLDER, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            writer = PdfWriter()
            found_any = False
            for fname in os.listdir(app.config['UPLOAD_FOLDER']):
                if not allowed_file(fname):
                    continue
                p = file_path(fname)
                text = ""
                try:
                    text = extract_text(p) or ""
                except Exception:
                    text = ""
                if keyword.lower() in fname.lower() or (text and keyword.lower() in text.lower()):
                    dest = os.path.join(folder_path, fname)
                    if not os.path.exists(dest):
                        shutil.copy(p, dest)
                    writer.append(p)
                    found_any = True
            if found_any:
                out = os.path.join(folder_path, f"{folder_name}_Merged.pdf")
                with open(out, "wb") as f:
                    writer.write(f)
                results.append({"category": folder_name, "merged": os.path.basename(out)})
        return jsonify({"ok": True, "result": results})

    elif mode == "year":
        for fname in os.listdir(app.config['UPLOAD_FOLDER']):
            if not allowed_file(fname):
                continue
            p = file_path(fname)
            year = None
            try:
                pdf = PdfReader(p)
                meta = pdf.metadata
                if meta and meta.creation_date:
                    cd = meta.creation_date
                    digits = ''.join(ch for ch in str(cd) if ch.isdigit())
                    if len(digits) >= 4:
                        year = digits[:4]
            except Exception:
                year = None
            if not year:
                year = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y")
            folder_path = os.path.join(config.ORGANIZED_FOLDER, year)
            os.makedirs(folder_path, exist_ok=True)
            dest = os.path.join(folder_path, fname)
            if not os.path.exists(dest):
                shutil.copy(p, dest)
        return jsonify({"ok": True, "message": "Organized by year"})

    else:
        return jsonify({"ok": False, "error": "Invalid mode"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
