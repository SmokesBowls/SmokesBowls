# zw_mcp/zw_mcp_daemon.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
import os
import threading
import subprocess  # ← Add this line
import time  # ← Add this line
from pathlib import Path
from datetime import datetime
from ollama_handler import query_ollama

LOG_PATH = Path("zw_mcp/logs/daemon.log")
BUFFER_SIZE = 4096
PORT = 7421
HOST = "127.0.0.1"  # Change to "0.0.0.0" for LAN

class ZWHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/process_zw':
            # Enable CORS
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Get ZW data from request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            zw_content = data.get('zw_data', '')
            
            # Process with Ollama (same as TCP handler)
            response = query_ollama(zw_content)
            log(zw_content, response)
            
            # Return response
            self.wfile.write(json.dumps({'status': 'success', 'response': response}).encode())
        
        # In your HTTP handler, add option for direct Blender routing
        if data.get('route_to_blender', False):
            temp_file = f'/tmp/web_zw_{int(time.time())}.zw'
            with open(temp_file, 'w') as f:
                f.write(zw_content)
            # Then change the subprocess call to:
            project_root = os.path.dirname(os.path.abspath(__file__)).replace('/zw_mcp', '')
            subprocess.run(['python3', 'tools/engain_orbit.py', temp_file], 
               cwd=project_root)

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_http_server():
    server = HTTPServer(('localhost', 1111), ZWHTTPHandler)
    print(f"🌐 ZW MCP HTTP Server listening on localhost:1111")
    server.serve_forever()

# In start_server(), add:
def start_server():
    # ... existing TCP code ...
    
    # Start HTTP server in separate thread
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()

def log(prompt: str, response: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n--- Incoming [{datetime.now()}] ---\n{prompt}\n")
        f.write(f"\n--- Response ---\n{response}\n")

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    data = []
    try:
        while True:
            chunk = conn.recv(BUFFER_SIZE).decode("utf-8")
            if not chunk:
                # Connection closed by client before sending "///" or anything
                print(f"[-] Connection from {addr} closed prematurely.")
                return
            data.append(chunk)
            if chunk.strip().endswith("///"):
                break
    except ConnectionResetError:
        print(f"[!] Connection reset by {addr} during receive.")
        return
    except Exception as e:
        print(f"[!] Error receiving data from {addr}: {e}")
        return


    prompt = "".join(data).strip()
    prompt = prompt.rstrip("///").strip()
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

def start_server():
    # Ensure log directory exists at startup
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Start HTTP server in separate thread
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # ... rest of your existing TCP code ...
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
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True # Allow main program to exit even if threads are running
                thread.start()
            except KeyboardInterrupt:
                print("\n[!] Server shutting down...")
                break
            except Exception as e:
                print(f"[!] Error accepting connection: {e}")
                # Potentially add a small delay here if errors are too frequent

if __name__ == "__main__":
    start_server()
