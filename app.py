import subprocess
import random
import platform
import sqlite3
import psutil
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
def predict_risk(cpu, ram):
    risk = (cpu * 0.6) + (ram * 0.4)
    return round(min(risk, 99), 1)

app = Flask(__name__)
app.secret_key = "devops_ultra_secret_2026"

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("SELECT * FROM users")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'devops2026')")
    conn.commit()
    conn.close()

init_db()

@app.before_request
def require_login():
    allowed = ['login', 'static']
    if 'logged_in' not in session and request.endpoint not in allowed:
        return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                  (data.get("username"), data.get("password")))
        user = c.fetchone()
        conn.close()
        if user:
            session["logged_in"] = True
            return jsonify({"status": "success"})
        return jsonify({"status": "error"}), 401
    return render_template("login.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update-profile", methods=["POST"])
def update_profile():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET username=?, password=? WHERE id=1", 
              (data.get("username"), data.get("password")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/execute", methods=["POST"])
def execute():
    cmd_raw = request.json.get("command", "").strip()
    
    if cmd_raw == "/check-health":
        res = "SYSTEM: All clusters reporting 100% health. Latency stable."
        
    elif cmd_raw == "/system-info":
       try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        boot_time = datetime.datetime.fromtimestamp(
            psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        res = f"""--- OS METRICS ---
    OS: {platform.system()} {platform.release()}
    CPU Usage: {cpu_usage}%
    RAM Usage: {ram.percent}% ({round(ram.used / (1024**3), 2)} GB used)
    Last Boot: {boot_time}
    ------------------"""
       except Exception as e:
           res = f"System info error: {str(e)}"
        
    elif cmd_raw == "/list-files":
        cmd = "dir" if platform.system() == "Windows" else "ls"
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout

    elif cmd_raw == "/deploy":
         res = "✅ Deployment triggered → payment-api:v2.1 | Pods: 3→6 | ETA: 45s"

    elif cmd_raw == "/rollback":
         res = "⏪ Rollback initiated → payment-api:v2.0 | Previous stable build restored"

    elif cmd_raw == "/scale":
         res = "⚡ Auto-scaling → DB Cluster pods scaled 2→5 replicas | Load balanced"

    elif cmd_raw == "/status":
         cpu = psutil.cpu_percent(interval=1)
         ram = psutil.virtual_memory().percent
         res = f"🟢 Services: UP | CPU: {cpu}% | RAM: {ram}% | Nodes: 4/4 Healthy"

    elif cmd_raw == "/help":
        res = "Commands: /deploy /rollback /scale /status /check-health /system-info /list-files"
    else:
        res = f"Command execution failed: '{cmd_raw}' not in whitelist."
        
    return jsonify({"response": res})

@app.route("/stats")
def stats():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    return jsonify({
        "latency": f"{random.randint(28, 55)}ms",
        "deployments": random.randint(12, 18),
        "errors": "OPTIMAL" if cpu < 70 else "HIGH LOAD",
        "cpu": cpu,
        "ram": ram
    })

@app.route('/predict')
def predict():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    risk = predict_risk(cpu, ram)
    status = "CRITICAL" if risk > 70 else "WARNING" if risk > 40 else "STABLE"
    return jsonify({"risk": risk, "status": status, "cpu": cpu, "ram": ram})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)