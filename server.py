import http.server
import socketserver
import json
import os
import subprocess

PORT = 8080

class SovereignHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
            return

        if self.path == '/api/save':
            files = data.get('files', {})
            for filename, content in files.items():
                safe_name = os.path.basename(filename)
                with open(safe_name, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Files saved to local disk."}).encode())
            print(f"[DISK] Workspace files synchronized successfully.")

        elif self.path == '/api/commit':
            msg = data.get('message', 'Automated PSA Sovereign Commit')
            try:
                subprocess.run(['git', 'add', '.'], check=True)
                result = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True, check=True)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success", 
                    "output": result.stdout.strip()
                }).encode())
                print(f"[GIT] Commit executed: {msg}")
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error", 
                    "output": e.stderr.strip() if e.stderr else str(e)
                }).encode())

        elif self.path == '/api/push':
            try:
                result = subprocess.run(['git', 'push'], capture_output=True, text=True, check=True)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success", 
                    "output": result.stdout.strip() or "Successfully pushed to remote."
                }).encode())
                print(f"[GIT] Push executed successfully.")
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error", 
                    "output": e.stderr.strip() if e.stderr else str(e)
                }).encode())

        elif self.path == '/api/vercel':
            try:
                result = subprocess.run(['vercel', '--prod', '--yes'], capture_output=True, text=True, check=True)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success", 
                    "output": result.stdout.strip() or "Successfully deployed to Vercel production."
                }).encode())
                print(f"[VERCEL] Production deployment executed.")
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error", 
                    "output": e.stderr.strip() if e.stderr else str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

Handler = SovereignHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"PSA Sovereign Backend active at http://localhost:{PORT}")
    print(f"Inventor/Founder: Rean Van Aswegen")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Shutting down PSA Sovereign Backend.")
