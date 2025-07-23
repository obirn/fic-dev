#!/usr/bin/env python3
"""
Script Scapy unifié pour générer des trames DNS avec domaine personnalisable
Format du domaine: X.webserver.iaa.org (où X est fourni par l'utilisateur)
IP destination: 172.16.2.137 (ntopng)
IP source: 172.16.2.1
Envoi automatique toutes les 10 secondes
"""

from scapy.all import *
import sys
import time
import signal
import os

def create_dns_query(domain_prefix):
    """
    Crée une requête DNS pour le domaine '[prefix].webserver.iaa.org'
    """
    # Construction du domaine complet
    domain = f"{domain_prefix}.webserver.iaa.org"

    # Définition des adresses IP
    src_ip = "172.16.2.1"
    dst_ip = "172.16.2.137"

    # Couche IP
    ip = IP(src=src_ip, dst=dst_ip)

    # Couche UDP (DNS utilise généralement le port 53)
    udp = UDP(sport=RandShort(), dport=53)

    # Couche DNS - Requête A (IPv4)
    dns_query = DNS(
            id=RandShort(),           # ID aléatoire
            qr=0,                     # Query (0) ou Response (1)
            opcode=0,                 # Standard query
            aa=0,                     # Authoritative Answer
            tc=0,                     # Truncated
            rd=1,                     # Recursion Desired
            ra=0,                     # Recursion Available
            z=0,                      # Reserved
            rcode=0,                  # Response Code
            qdcount=1,                # Question Count
            ancount=0,                # Answer Count
            nscount=0,                # Authority Count
            arcount=0,                # Additional Count
            qd=DNSQR(qname=domain, qtype="A", qclass="IN")
            )

    # Assemblage du paquet complet
    packet = ip / udp / dns_query

    return packet

def create_dns_response(domain_prefix):
    """
    Crée une réponse DNS pour le domaine '[prefix].webserver.iaa.org'
    """
    # Construction du domaine complet
    domain = f"{domain_prefix}.webserver.iaa.org"

    # Définition des adresses IP (inversées pour la réponse)
    src_ip = "172.16.2.137"
    dst_ip = "172.16.2.1"
    resolved_ip = "192.168.1.100"  # IP fictive pour la résolution

    # Couche IP
    ip = IP(src=src_ip, dst=dst_ip)

    # Couche UDP
    udp = UDP(sport=53, dport=RandShort())

    # Couche DNS - Réponse
    dns_response = DNS(
            id=12345,                 # Même ID que la requête
            qr=1,                     # Response
            opcode=0,                 # Standard query
            aa=1,                     # Authoritative Answer
            tc=0,                     # Truncated
            rd=1,                     # Recursion Desired
            ra=1,                     # Recursion Available
            z=0,                      # Reserved
            rcode=0,                  # No error
            qdcount=1,                # Question Count
            ancount=1,                # Answer Count
            nscount=0,                # Authority Count
            arcount=0,                # Additional Count
            qd=DNSQR(qname=domain, qtype="A", qclass="IN"),
            an=DNSRR(rrname=domain, type="A", rclass="IN", ttl=300, rdata=resolved_ip)
            )

    # Assemblage du paquet complet
    packet = ip / udp / dns_response

    return packet

def main():
    # Demander à l'utilisateur le préfixe du domaine
    domain_prefix = input("Entrez le préfixe du domaine: ").strip()
    if not domain_prefix:
        print("Erreur: Vous devez spécifier un préfixe de domaine")
        sys.exit(1)

    # Variable globale pour contrôler l'arrêt
    global running
    running = True

    # Gestionnaire de signal pour arrêt propre (Ctrl+C)
    def signal_handler(sig, frame):
        global running
        print("\n\n=== Arrêt du script demandé ===")
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("=== Script Scapy - Génération trame DNS automatique ===")
    print(f"Domaine: {domain_prefix}.webserver.iaa.org")
    print(f"IP source: 172.16.2.1")
    print(f"IP destination: 172.16.2.137")
    print("=" * 55)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n[{timestamp}] Envoi du paquet DNS")

    # Création de la requête DNS
    dns_query_packet = create_dns_query(domain_prefix)

    try:
        # Envoi du paquet
        send(dns_query_packet, verbose=0)
        print("✓ Paquet DNS envoyé avec succès")

        # Affichage optionnel des détails (décommentez si souhaité)
        # print("Détails du paquet:")
        # dns_query_packet.show()

    except Exception as e:
        print(f"✗ Erreur lors de l'envoi du paquet: {e}")
        if "Operation not permitted" in str(e):
            print("Note: Exécutez le script avec sudo pour envoyer des paquets")

    print("Script terminé.")

if __name__ == "__main__":
    print("ATTENTION: Ce script nécessite des privilèges root pour envoyer des paquets")
    print("Utilisez: sudo python3 dns_script_unifie.py")
    print()

    # Vérification des privilèges
    if os.geteuid() != 0:
        print("⚠️  Attention: Le script n'est pas exécuté en tant que root")
        print("   L'envoi de paquets peut échouer")
        print("   Utilisez 'sudo python3 dns_script_unifie.py' pour des privilèges complets")
        print()

        choice = input("Continuer quand même? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(1)

    main()
