from flask import Flask, render_template, send_file, abort, jsonify
import os
import json

app = Flask(__name__)

output_folder = "./output"
image_file = "epd_image.png"
image_path = os.path.join(output_folder, image_file)
online_ips_file = os.path.join(output_folder, "online_ips_ports.json")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/image")
def display_image():
    if os.path.exists(image_path) and os.path.isfile(image_path):
        return send_file(image_path, mimetype="image/png")
    abort(404, description="Image not found")

@app.route("/online_ips")
def online_ips():
    if os.path.exists(online_ips_file) and os.path.isfile(online_ips_file):
        with open(online_ips_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify([])

app.run(host="0.0.0.0", port=8080)
