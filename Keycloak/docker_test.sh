#!/usr/bin/env bash

docker run -it --rm \
    --name keycloak_test \
    -p 9090:8080 \
    -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
    -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
    quay.io/keycloak/keycloak:26.1.2 \
    start-dev

