import http.server
import socketserver
import requests
import time
import json
from urllib.parse import urlparse, parse_qs

# Configuration Targets
PORT = 8080
TARGET_HOST = "https://ruby-network.net"

class RubyTrafficSniffer(http.server.BaseHTTPRequestHandler):
    
    # Suppress default server log strings to keep terminal output clean
    def log_message(self, format, *args):
        return

    def print_request_details(self, method, path, headers, body_data=None):
        """Prints full structural diagnostic metrics of the intercepted traffic."""
        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)
        
        print("\n" + "="*60)
        print(f"[{time.strftime('%H:%M:%S')}] 🚨 INTERCEPTED REQUEST: {method} -> {parsed_url.path}")
        print("="*60)
        
        print(f"[+] Client Address : {self.client_address[0]}:{self.client_address[1]}")
        
        # Log Query Parameters
        if query_params:
            print("[+] Query Strings  :")
            for k, v in query_params.items():
                print(f"    -> {k} = {v[0] if len(v)==1 else v}")
                
        # Log Complete Request Headers
        print("[+] Request Headers:")
        for key, val in headers.items():
            print(f"    {key}: {val}")
            
        # Log Incoming Body Data Payload
        if body_data:
            print("[+] Payload Data   :")
            try:
                # Attempt clear format printing if payload is structural JSON
                json_data = json.loads(body_data)
                print(json.dumps(json_data, indent=6))
            except ValueError:
                print(f"    {body_data}")
        print("="*60 + "\n")

    def forward_request(self, method, path, headers, data=None):
        """Forwards traffic seamlessly to the real server and mirrors responses."""
        target_url = f"{TARGET_HOST}{path}"
        
        # Clean headers to prevent proxy routing loops
        clean_headers = {k: v for k, v in headers.items() if k.lower() not in ['host', 'content-length']}
        
        try:
            if method == "GET":
                res = requests.get(target_url, headers=clean_headers, timeout=10)
            elif method == "POST":
                res = requests.post(target_url, headers=clean_headers, data=data, timeout=10)
            else:
                res = requests.request(method, target_url, headers=clean_headers, data=data, timeout=10)
                
            # Mirror the backend server response back to the client worker
            self.send_response(res.status_code)
            for k, v in res.headers.items():
                if k.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(res.content)
            
            print(f"[✓] Forwarded successfully. Backend responded with HTTP {res.status_code}")
            
        except Exception as e:
            print(f"[X] Forwarding error mapping back to core gateway: {e}")
            self.send_error(502, f"Bad Gateway: {e}")

    def do_GET(self):
        """Intercepts and documents GET inquiries."""
        self.print_request_details("GET", self.path, self.headers)
        self.forward_request("GET", self.path, self.headers)

    def do_POST(self):
        """Intercepts, parses, and documents payload-heavy POST interactions."""
        content_length = int(self.headers.get('Content-Length', 0))
        body_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else None
        
        self.print_request_details("POST", self.path, self.headers, body_data)
        self.forward_request("POST", self.path, self.headers, body_data)

def launch_sniffer():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RubyTrafficSniffer) as httpd:
        print(f"[*] Core API Traffic Sniffer Online.")
        print(f"[*] Listening on Local Port: {PORT}")
        print(f"[*] Intercepting and routing traffic continuously to: {TARGET_HOST}\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Deactivating sniffer engine safely.")

if __name__ == "__main__":
    launch_sniffer()
