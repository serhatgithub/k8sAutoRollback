from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI()
TARGET_URL = os.getenv("TARGET_URL", "http://app-service:8080")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <html>
    <head><title>Chaos</title></head>
    <body style="background-color: #ffcccc; font-family: monospace; text-align: center; padding-top: 50px;">
        <div style="border: 3px solid black; display: inline-block; padding: 40px; background: white;">
            <h1> CHAOS CONTROL</h1>
            <label>Hata (%):</label> <input type="number" id="rate" value="0"><br><br>
            <label>Gecikme (ms):</label> <input type="number" id="latency" value="0"><br><br>
            <button onclick="apply()" style="background: red; color: white; padding: 10px;">SALDIR</button>
            <p id="status"></p>
        </div>
        <script>
            function apply() {
                var r = document.getElementById("rate").value;
                var l = document.getElementById("latency").value;
                fetch("/inject?rate=" + r + "&latency=" + l)
                .then(res => res.text()).then(t => document.getElementById("status").innerText = t);
            }
        </script>
    </body>
    </html>
    """

@app.get("/inject")
def inject(rate: int, latency: int):
    try:
        requests.get(f"{TARGET_URL}/set-chaos?rate={rate}&latency={latency}", timeout=2)
        return f"OK -> Hata: %{rate}, Gecikme: {latency}ms"
    except Exception as e:
        return f"Hata: {e}"