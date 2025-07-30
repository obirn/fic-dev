#!/bin/sh

# Exit immediately if any command fails
set -e

alias make=gmake

cd ntopng
# No need to autogen or configure, as we assume the environment is already set up
make
cd -

echo "Installation completed successfully!"