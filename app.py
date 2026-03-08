import os
import uuid
import subprocess
import threading
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)

# Armazena os jobs em memória (suficiente para uso pessoal)
jobs = {}

TEMP_DIR = "/tmp/yt_extractor"
os.makedirs(TEMP_DIR, exist_ok=True)


def extract_urls(job_id: str, playlist_url: str, output_file: str):
    """Roda yt-dlp em background e atualiza o status do job."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "url", playlist_url],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos de timeout
        )

        if result.returncode != 0:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = result.stderr.strip() or "Erro desconhecido ao processar a playlist."
            return

        urls = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

        if not urls:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "Nenhuma URL encontrada. Verifique se a playlist é pública."
            return

        with open(output_file, "w") as f:
            f.write("\n".join(urls))

        jobs[job_id]["status"] = "done"
        jobs[job_id]["count"] = len(urls)
        jobs[job_id]["file"] = output_file

    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = "Timeout: a playlist demorou demais para processar."
    except FileNotFoundError:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = "yt-dlp não encontrado. Instale com: pip install yt-dlp"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    playlist_url = (data or {}).get("url", "").strip()

    if not playlist_url:
        return jsonify({"error": "URL da playlist não informada."}), 400

    if "youtube.com/playlist" not in playlist_url and "youtu.be" not in playlist_url:
        return jsonify({"error": "URL inválida. Use uma URL de playlist do YouTube."}), 400

    job_id = str(uuid.uuid4())
    output_file = os.path.join(TEMP_DIR, f"urls_{job_id}.txt")

    jobs[job_id] = {"status": "processing", "file": None, "error": None, "count": 0}

    thread = threading.Thread(target=extract_urls, args=(job_id, playlist_url, output_file))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job não encontrado."}), 404
    return jsonify({
        "status": job["status"],
        "count": job.get("count", 0),
        "error": job.get("error"),
    })


@app.route("/download/<job_id>")
def download(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "Arquivo não disponível."}), 404
    return send_file(
        job["file"],
        as_attachment=True,
        download_name="playlist_urls.txt",
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
