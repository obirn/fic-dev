#!/bin/sh

# =============================================
# Script d'installation de ntopng sur pfSense - Version avec package local
# =============================================


# 1. Installation des dépendances uniquement
echo "[+] Installation des dépendances requises..."
pkg install -y redis ndpi mysql80-client lua53 libmaxminddb libzmq4 hiredis bash socat librdkafka pfSense-kernel-symbols-pfSense-2.7.2

# 2. Installation du package local
echo "[+] Installation du package ntopng local..."
ln -sf /usr/local/lib/libhiredis.so.1.0.0 /usr/local/lib/libhiredis.so.1.2.1
ln -sf /usr/local/lib/libsodium.so.23.3.0 /usr/local/lib/libsodium.so.26
ldconfig -m /usr/local/lib

pkg add -f /tmp/ntopng-6.5.250611.pkg

# Installation du paquet d'interface pfSense
echo "[+] Installation de l'interface pfSense pour ntopng..."
pkg install -y pfSense-pkg-ntopng

# 3. Configuration de Redis
echo "[+] Configuration de Redis..."
sysrc redis_enable="YES"

echo "[+] Démarrage de Redis..."
service redis start

# 4. Configuration de ntopng
echo "[+] Création du répertoire de configuration ntopng..."
mkdir -p /usr/local/etc/ntopng

echo "[+] Création du fichier de configuration ntopng..."
cat > /usr/local/etc/ntopng/ntopng.conf << 'EOL'
# Interface à surveiller (remplacez em0 par votre interface LAN/WAN)
-i=em0
# Port web de ntopng
-W=3000
# Désactiver la vérification des identifiants (pour la 1ère connexion)
--disable-login=1
EOL

# 5. Activation au démarrage
echo "[+] Activation de ntopng au boot..."
sysrc ntopng_enable="YES"

# 6. Démarrage de ntopng
echo "[+] Démarrage de ntopng..."
service ntopng start

# 7. Redémarrage de l'interface web pfSense
echo "[+] Redémarrage de l'interface web pfSense..."
/etc/rc.restart_webgui

# 8. Ouverture du port dans le pare-feu (optionnel)
echo "[+] Ajout d'une règle de pare-feu pour le port 3000..."
cat > /tmp/ntopng_rule.xml << 'EOL'
<rule>
    <type>pass</type>
    <interface>lan</interface>
    <ipprotocol>inet</ipprotocol>
    <protocol>tcp</protocol>
    <source>any</source>
    <destination>
        <address>172.16.2.137</address>
    </destination>
    <destination>
        <port>3000</port>
    </destination>
    <descr>Accès à ntopng</descr>
</rule>
EOL

# Import de la règle - Méthode corrigée
echo "[+] Application de la règle de pare-feu..."
(
echo "exec"
echo "load /tmp/ntopng_rule.xml"
echo "write rules"
echo "exit"
) | php /usr/local/sbin/pfSsh.php

# 9. Nettoyage
rm -f /tmp/ntopng_rule.xml

# 10. Résumé
echo "[+] Installation terminée !"
echo "----------------------------------------"
echo "Accès possibles :"
echo "1. Via l'interface pfSense : Services > ntopng"
echo "2. Directement via : http://[VOTRE_IP_PFSENSE]:3000"
echo "Identifiants par défaut : admin/admin"