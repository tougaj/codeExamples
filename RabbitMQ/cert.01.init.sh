#!/usr/bin/env bash

# Next we need to generate the key and certificates that our test Certificate Authority will use within the testca directory:
cd testca
openssl req -x509 -config openssl.cnf -newkey rsa:2048 -days 3650 \
    -out ca_certificate.pem -outform PEM -subj /CN=MyTestCA/ -nodes
openssl x509 -in ca_certificate.pem -out ca_certificate.cer -outform DER