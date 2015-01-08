#!/bin/bash

set -e

ctx logger debug "Setting ENABLED=1 in /etc/default/haproxy"

sudo /bin/sed -i 's/ENABLED=0/ENABLED=1/' /etc/default/haproxy || exit 1

COMMAND="/etc/init.d/haproxy start"

logger info "Starting HAProxy"
ctx logger debug "${COMMAND}"

er=1
while [[ $er != 0 ]]
do
    sudo nohup ${COMMAND} /dev/null 2>&1 &
    er=$?
    sleep 10
done

ctx logger info "Started HAProxy"
