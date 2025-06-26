import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Replace with a secure key in production
os.makedirs("uploads", exist_ok=True)

TOGETHER_API_KEY = "your_actual_together_api_key_here"

# Simple in-memory user store
USERS = {
    "admin": "password123",
    "user": "code123"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if USERS.get(username) == password:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="❌ Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS:
            return render_template("register.html", error="⚠️ User already exists.")
        USERS[username] = password
        session["user"] = username
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_code():
    if "user" not in session:
        return redirect(url_for("login"))

    uploaded_file = request.files.get("code_file")
    if not uploaded_file or uploaded_file.filename == "":
        return "⚠️ No file selected.", 400

    path = os.path.join("uploads", uploaded_file.filename)
    uploaded_file.save(path)

    with open(path, "r") as f:
        code = f.read()

    try:
        fixed_code = debug_code(code)
        return f"<h2>✅ Uploaded Code:</h2><pre>{code}</pre><h2>🛠️ Fixed Code:</h2><pre>{fixed_code}</pre>"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Error while debugging:<br><pre>{str(e)}</pre>", 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    code = data.get("text", "")
    if not code:
        return jsonify({"error": "No text provided."}), 400

    try:
        fixed_code = debug_code(code)
        return jsonify({"fixed_code": fixed_code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def debug_code(code):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that debugs code."},
            {"role": "user", "content": f"Fix this code and return the corrected version:\n\n{code}"}
        ],
        "temperature": 0.2,
        "max_tokens": 512
    }
    response = requests.post(url, headers=headers, json=data)
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.text)
    response.raise_for_status()
    result = response.json()
    return result['choices'][0]['message']['content']

if __name__ == "__main__":
    app.run(debug=True)
