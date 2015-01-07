#!/bin/bash

set -e

ctx logger info "Installing HAProxy"
ctx logger debug "${COMMAND}"

apt-get udpate || exit 1
apt-get -y install haproxy || exit 1

ctx logger info "Installed HAProxy"
