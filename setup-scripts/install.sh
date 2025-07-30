#!/usr/bin/env bash

FREEBSD_HOSTNAME=192.168.2.137
PFSENSE_HOSTNAME=192.168.2.135

# define colors for logger
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Step 1: Copy the custom ntpng package to the FreeBSD host

log_info "Copying ntopng changes on the host..."
cp ntopng/ntopng-orig ntopng/ntopng-infected -r
cp ntopng/ntopng-changes ntopng/ntopng-infected -r
log_success "Copied ntopng changes to ntopng-infected directory."

# Step 2: Copy the whole 