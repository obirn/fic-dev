#!/bin/sh

# create directories
mkdir -p ntopng-build/usr/local/bin 
mkdir -p ntopng-build/usr/local/etc/ntopng 
mkdir -p ntopng-build/usr/local/etc/rc.d 
mkdir -p ntopng-build/usr/local/share/man/man8 
mkdir -p ntopng-build/usr/local/share/ntopng

# ntopng exe
cp ntopng/ntopng ntopng-build/usr/local/bin/ntopng

# ntopng.conf.sample
cp ntopng/packages/etc/ntopng/ntopng.conf ntopng-build/usr/local/etc/ntopng/ntopng.conf.sample

# rc.d/ntopng
cp ntopng/packages/FreeBSD/usr/local/etc/rc.d/ntopng ntopng-build/usr/local/etc/rc.d/ntopng

# ntopng-config
cp ntopng/packages/wizard/ntopng-config ntopng-build/usr/local/bin/ntopng-config

# ntopng.8
cp ntopng/ntopng.8 ntopng-build/usr/local/share/man/man8/ntopng.8

# scripts
cp -r ntopng/scripts ntopng-build/usr/local/share/ntopng/

# httpdocs
cp -r ntopng/httpdocs ntopng-build/usr/local/share/ntopng/
