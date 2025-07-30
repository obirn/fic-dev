#!/bin/bash

set -e

# Configuration de base
PKG_NAME="ntopng"
PKG_ORIGIN="net/ntopng"
PKG_VERSION="6.5.250611"
PKG_COMMENT="High speed network traffic monitor"
PKG_MAINTAINER="packager@ntop.org"
PKG_WWW="https://www.ntop.org"
PKG_ABI="FreeBSD:14:amd64"
PKG_ARCH="freebsd:14:x86:64"
PKG_PREFIX="/"
PKG_DESC="Web-based network traffic monitoring tool"
PKG_FREEBSD_VERSION="1400094"

# Dépendances (format compact)
DEPS_JSON='{"json-c":{"origin":"devel/json-c","version":"0.17"},"libmaxminddb":{"origin":"net/libmaxminddb","version":"1.10.0"},"libzmq4":{"origin":"net/libzmq4","version":"4.3.5_2"},"rrdtool":{"origin":"databases/rrdtool","version":"1.8.0_4"},"lua53":{"origin":"lang/lua53","version":"5.3.6_1"},"libsodium":{"origin":"security/libsodium","version":"1.0.19"},"sqlite3":{"origin":"databases/sqlite3","version":"3.46.0,1"},"hiredis":{"origin":"databases/hiredis","version":"1.2.0.15"},"zstd":{"origin":"archivers/zstd","version":"1.5.6"},"curl":{"origin":"ftp/curl","version":"8.9.1"},"socat":{"origin":"net/socat","version":"1.7.4.4"}}'

SHLIBS_REQUIRED='["librrd.so.8","libjson-c.so.5","libmaxminddb.so.0","libsqlite3.so.0","libexpat.so.1","libzmq.so.5","libsodium.so.26","libcurl.so.4"]'

SCRIPTS_JSON='{"post-install":"# Add missing libraries symlinks due to invalid shlib version\\nRES=`ldd /usr/local/bin/ntopng | grep \"not found\" | cut -d '\''='\'' -f 1 | sed '\''s/[[:blank:]]//g'\''`\\n\\nfor LIB in $RES; do\\n    BASELIB=`echo $LIB|cut -d '\''.'\'' -f 1`\\n    CMD=`ln -s /usr/local/lib/$BASELIB.so /usr/local/lib/$LIB`\\ndone","post-deinstall":"rm -rf /usr/local/share/ntopng"}'

# Vérification des arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <installation-directory>"
  exit 1
fi

INSTALL_DIR="$1"
MANIFEST_FILE="+MANIFEST"
COMPACT_MANIFEST_FILE="+COMPACT_MANIFEST"

# Vérification du répertoire
if [ ! -d "$INSTALL_DIR" ]; then
  echo "Error: Directory $INSTALL_DIR does not exist"
  exit 1
fi

# Calcul de la taille totale
PKG_FLATSIZE=$(find "$INSTALL_DIR" -type f -exec stat -c "%s" {} + | awk '{sum += $1} END {print sum}')

# Génération de la section fichiers (format compact)
echo "Generating files list with hashes..."
FILES_JSON=$(cd "$INSTALL_DIR" && find . -type f -exec sha256sum {} + | awk '{
  path = substr($2, 3);
  printf "%s\"/%s\":\"1$%s\"", (NR==1?"":","), path, $1
}')

# Construction des manifestes (format compact)
echo "Building compact manifests..."
# MANIFEST complet
echo -n '{"name":"'"$PKG_NAME"'","origin":"'"$PKG_ORIGIN"'","version":"'"$PKG_VERSION"'","comment":"'"$PKG_COMMENT"'","maintainer":"'"$PKG_MAINTAINER"'","www":"'"$PKG_WWW"'","abi":"'"$PKG_ABI"'","arch":"'"$PKG_ARCH"'","prefix":"'"$PKG_PREFIX"'","flatsize":'"$PKG_FLATSIZE"',"desc":"'"$PKG_DESC"'","deps":'"$DEPS_JSON"',"shlibs_required":'"$SHLIBS_REQUIRED"',"annotations":{"FreeBSD_version":"'"$PKG_FREEBSD_VERSION"'"},"scripts":'"$SCRIPTS_JSON"',"files":{'"$FILES_JSON"'}}' > "$INSTALL_DIR/$MANIFEST_FILE"

# COMPACT_MANIFEST
echo -n '{"name":"'"$PKG_NAME"'","origin":"'"$PKG_ORIGIN"'","version":"'"$PKG_VERSION"'","comment":"'"$PKG_COMMENT"'","maintainer":"'"$PKG_MAINTAINER"'","www":"'"$PKG_WWW"'","abi":"'"$PKG_ABI"'","arch":"'"$PKG_ARCH"'","prefix":"'"$PKG_PREFIX"'","flatsize":'"$PKG_FLATSIZE"',"desc":"'"$PKG_DESC"'","deps":'"$DEPS_JSON"',"shlibs_required":'"$SHLIBS_REQUIRED"',"annotations":{"FreeBSD_version":"'"$PKG_FREEBSD_VERSION"'"}}' > "$INSTALL_DIR/$COMPACT_MANIFEST_FILE"

echo "Package manifests generated: $MANIFEST_FILE and $COMPACT_MANIFEST_FILE (compact format)"