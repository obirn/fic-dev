#!/usr/bin/env bash

FREEBSD_HOSTNAME=192.168.158.137
PFSENSE_HOSTNAME=192.168.158.135

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

test_connectivity() {
    ip=$1
    ssh_user=$2

    # Test ping
    ping -c 1 $ip > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_error "Cannot ping $ip. Please check the network connection."
        exit 1
    fi
    # Test ssh 
    ssh -o BatchMode=yes -o ConnectTimeout=5 $ssh_user@$ip "exit" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_error "Cannot SSH into $ip as $ssh_user. Please ensure that you copied your SSH key to the remote host."
        exit 1
    fi
    log_success "Connectivity to $ip as $ssh_user is successful."
}

# Step : Check connectivity to FreeBSD host
log_info "Checking connectivity to FreeBSD host..."
test_connectivity $FREEBSD_HOSTNAME root
log_info "Checking connectivity to Pfsense host..."
test_connectivity $PFSENSE_HOSTNAME root

# Step : Setup the compilation of ntopng on the FreeBSD host
log_info "Running freebsd_setup_compilation.sh on the FreeBSD host..."
ssh root@$FREEBSD_HOSTNAME 'sh -s' < setup-scripts/freebsd_setup_compilation.sh
if [ $? -ne 0 ]; then
    log_error "Failed to run freebsd_setup_compilation.sh on the FreeBSD host."
    exit 1
fi

# Step : Copy ntopng changes on freebsd host
log_info "Copying ntopng changes on the host..."
scp -r ntopng/ntopng-changes/* root@$FREEBSD_HOSTNAME:ntopng/
log_success "Copied ntopng changes to ntopng-infected directory."

# Step : Compile ntopng on the FreeBSD host
log_info "Compiling ntopng on the FreeBSD host..."
ssh root@$FREEBSD_HOSTNAME 'sh -s' < setup-scripts/freebsd_compile_ntopng.sh
