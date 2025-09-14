from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
import os
import threading
import subprocess
import time
from pathlib import Path
from datetime import datetime
from ollama_handler import query_ollama

# --- Config / Paths ---
LOG_PATH = Path("zw_mcp/logs/daemon.log")
BUFFER_SIZE = 4096

# TCP server (client_example.py talks to this)
HOST = os.getenv("ZW_MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("ZW_MCP_PORT", "7421"))

# HTTP server (browser / local tools can POST here)
HTTP_HOST = os.getenv("ZW_MCP_HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.getenv("ZW_MCP_HTTP_PORT", "1111"))

# --- Logging ---
def log(prompt: str, response: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n--- Incoming [{datetime.now()}] ---\n{prompt}\n")
        f.write(f"\n--- Response ---\n{response}\n")

# --- HTTP Handler ---
class ZWHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_OPTIONS(self):
        # CORS preflight
        self._send_json(200, {"ok": True})

    def do_POST(self):
        if self.path != "/process_zw":
            self._send_json(404, {"error": "not found"})
            return

        # Read body safely
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"error": f"bad json: {e}"})
            return

        zw_content = data.get("zw_data", "")
        if not isinstance(zw_content, str) or not zw_content.strip():
            self._send_json(400, {"error": "missing or empty 'zw_data'"})
            return

        # Call Ollama and (optionally) route to Blender BEFORE we reply
        try:
            response_text = query_ollama(zw_content)
            log(zw_content, response_text)
        except Exception as e:
            self._send_json(502, {"error": f"ollama: {e}"})
            return

        if data.get("route_to_blender"):
            try:
                temp_file = f"/tmp/web_zw_{int(time.time())}.zw"
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(zw_content)

                project_root = Path(__file__).resolve().parents[1]  # repo root
                # Fire-and-forget; if you want to block, use run(..., check=True)
                subprocess.Popen(
                    ["python3", "tools/engain_orbit.py", temp_file],
                    cwd=str(project_root)
                )
            except Exception as e:
                # Non-fatal: return response but include routing error
                self._send_json(200, {"status": "success", "response": response_text, "blender_error": str(e)})
                return

        self._send_json(200, {"status": "success", "response": response_text})

# --- HTTP server thread ---
def start_http_server():
    # allow quick rebinds after crash
    HTTPServer.allow_reuse_address = True
    server = HTTPServer((HTTP_HOST, HTTP_PORT), ZWHTTPHandler)
    print(f"🌐 ZW MCP HTTP Server listening on {HTTP_HOST}:{HTTP_PORT}")
    server.serve_forever()

# --- TCP client handling ---
def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    data_chunks = []
    try:
        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                print(f"[-] Connection from {addr} closed prematurely.")
                return
            decoded = chunk.decode("utf-8", errors="replace")
            data_chunks.append(decoded)
            if decoded.strip().endswith("///"):
                break
    except ConnectionResetError:
        print(f"[!] Connection reset by {addr} during receive.")
        return
    except Exception as e:
        print(f"[!] Error receiving data from {addr}: {e}")
        return

    prompt = "".join(data_chunks).strip().rstrip("///").strip()
    if not prompt:
        print(f"[-] Empty prompt received from {addr} after stripping '///'. Closing connection.")
        conn.close()
        return

    print(f"[>] Received prompt from {addr}:\n{prompt}\n")

    try:
        response = query_ollama(prompt)
        conn.sendall(response.encode("utf-8"))
    except Exception as e:
        print(f"[!] Error processing or sending response to {addr}: {e}")
    finally:
        conn.close()
        print(f"[✔] Responded to {addr} and closed connection.")

    log(prompt, response if 'response' in locals() else "ERROR: No response generated")

# --- TCP accept loop + HTTP thread ---
def start_server():
    # Ensure log dir exists once
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # HTTP in background
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((HOST, PORT))
        except OSError as e:
            print(f"[!] Failed to bind to {HOST}:{PORT}: {e}")
            return

        server.listen()
        print(f"🌐 ZW MCP Daemon listening on {HOST}:{PORT} ...")
        print(f"ℹ️ Logging interactions to: {LOG_PATH.resolve()}")

        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except KeyboardInterrupt:
                print("\n[!] Server shutting down...")
                break
            except Exception as e:
                print(f"[!] Error accepting connection: {e}")

if __name__ == "__main__":
    start_server()
