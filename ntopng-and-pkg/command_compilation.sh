#!/bin/sh

# Exit immediately if any command fails
set -e

# Define variables for versions and repositories
PF_RING_VERSION="3fa234918ad7ad4698aa1b98eb6c299919660572"
NDPI_VERSION="aba60ac354e234935f35103dfa83e5090b6e7e2a"
NTOPNG_VERSION="a527c19bda9bb96f8db1ba82a9e0de21f4b4ef5a"

# Update package database first
pkg update -y

# Install all dependencies in a single command to reduce build time
pkg install -y \
    git gmake cmake pkgconf autoconf automake libtool rename sudo \
    redis libmaxminddb lua54 ndpi sqlite3 libgcrypt libxslt libxml2 libpcap \
    bash gcc11 libzmq4 hiredis redis \
    gettext flex bison json-c pcre2 rrdtool \
    libsodium lua53 zip librdkafka socat

# Set gmake as default make
alias make=gmake

# Clone and build PF_RING
echo "Building PF_RING..."
git clone https://github.com/ntop/PF_RING.git
cd PF_RING/userland/libpcap
git checkout $PF_RING_VERSION
./configure
make
cd -

# Clone and build nDPI
echo "Building nDPI..."
git clone https://github.com/ntop/nDPI.git
cd nDPI
git checkout $NDPI_VERSION
./autogen.sh
./configure
make
cd ..

# Clone and build ntopng
echo "Building ntopng..."
git clone https://github.com/ntop/ntopng.git
cd ntopng
git checkout $NTOPNG_VERSION
./autogen.sh
./configure
make

echo "Installation completed successfully!"