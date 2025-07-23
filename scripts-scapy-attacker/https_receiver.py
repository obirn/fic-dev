#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os
import sys
from email.parser import BytesParser
from email.policy import HTTP
import io

# Configuration
output_dir = "received_files"
server_port = 443
server_host = "0.0.0.0"
ssl_cert = "server.pem"
ssl_key = "server.key"

class FileUploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Gère les requêtes POST pour l'upload de fichiers"""
        try:
            if self.path != '/stats':
                self.send_error(404, "Not Found")
                return
            
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Bad Request: Expected multipart/form-data")
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            msg = BytesParser(policy=HTTP).parsebytes(
                b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + post_data
            )
            
            file_part = None
            for part in msg.iter_parts():
                if part.get_content_disposition() == 'form-data':
                    name = part.get_param('name', header='content-disposition')
                    if name == 'fichier' and part.get_filename():
                        file_part = part
                        break
            
            if not file_part:
                self.send_error(400, "No file uploaded")
                return
            
            filename = os.path.basename(file_part.get_filename())
            file_content = file_part.get_payload(decode=True)
            
            if self.save_file(filename, file_content):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"File '{filename}' uploaded successfully ({len(file_content)} bytes)\n".encode())
            else:
                self.send_error(500, "Failed to save file")
                
        except Exception as e:
            print(f"Error processing upload: {str(e)}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def save_file(self, filename, content):
        """Sauvegarde le fichier reçu"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
            
            # Éviter les collisions
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                counter += 1
            
            with open(output_path, 'wb') as f:
                f.write(content)
            
            print(f"File saved: {output_path} ({len(content)} bytes)")
            print(f"Client: {self.client_address[0]}:{self.client_address[1]}")
            print("-" * 50)
            return True
            
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    def do_GET(self):
        """Gère les requêtes GET (optionnel, pour tester)"""
        if self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = """<!DOCTYPE html>
            <html><head><title>File Upload</title></head>
            <body>
                <h2>File Upload Test</h2>
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="fichier" required>
                    <button type="submit">Upload</button>
                </form>
            </body></html>"""
            self.wfile.write(html.encode())
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def start_server():
    try:
        server = HTTPServer((server_host, server_port), FileUploadHandler)
        
        # Configuration SSL/TLS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=ssl_cert, keyfile=ssl_key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        
        print(f"HTTPS Server started on {server_host}:{server_port}")
        print(f"Secure upload endpoint: https://{server_host}:{server_port}/stats")
        print(f"Output directory: {output_dir}")
        print("Waiting for secure file uploads... (Ctrl+C to stop)")
        print("-" * 50)
        server.serve_forever()
        
    except PermissionError:
        print(f"Permission denied: Cannot bind to port {server_port}")
        print("Try running with sudo or use a port > 1024")
        sys.exit(1)
    except FileNotFoundError:
        print("SSL certificate or key not found!")
        print(f"Expected files: {ssl_cert} and {ssl_key}")
        print("Generate them with:")
        print("openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.pem -days 365 -nodes")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Vérification des prérequis SSL
    if not os.path.exists(ssl_cert) or not os.path.exists(ssl_key):
        print("SSL certificate files missing!")
        print("Generate them first with this command:")
        print("openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.pem -days 365 -nodes")
        print("Or specify your own certificate in the configuration.")
        sys.exit(1)
    
    if server_port < 1024 and os.geteuid() != 0:
        print("Warning: Port 443 requires root privileges")
        print("Run with: sudo python3 script.py")
        print("Or change server_port to a value > 1024")
        sys.exit(1)
    
    start_server()
