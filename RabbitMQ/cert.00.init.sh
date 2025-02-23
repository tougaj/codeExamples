#!/usr/bin/env bash

# First let's create a directory for our test Certificate Authority:
mkdir testca
cd testca
mkdir certs private
chmod 700 private
echo 01 > serial
touch index.txt

# Now add the following OpenSSL configuration file, openssl.cnf, within the newly created testca directory:
cat << EOF > openssl.cnf
[ ca ]
default_ca = testca

[ testca ]
dir = .
certificate = \$dir/ca_certificate.pem
database = \$dir/index.txt
new_certs_dir = \$dir/certs
private_key = \$dir/private/ca_private_key.pem
serial = \$dir/serial

default_crl_days = 7
default_days = 3650
default_md = sha256

policy = testca_policy
x509_extensions = certificate_extensions

[ testca_policy ]
commonName = supplied
stateOrProvinceName = optional
countryName = optional
emailAddress = optional
organizationName = optional
organizationalUnitName = optional
domainComponent = optional

[ certificate_extensions ]
basicConstraints = CA:false

[ req ]
default_bits = 2048
default_keyfile = ./private/ca_private_key.pem
default_md = sha256
prompt = yes
distinguished_name = root_ca_distinguished_name
x509_extensions = root_ca_extensions

[ root_ca_distinguished_name ]
commonName = hostname

[ root_ca_extensions ]
basicConstraints = CA:true
keyUsage = keyCertSign, cRLSign

[ client_ca_extensions ]
basicConstraints = CA:false
keyUsage = digitalSignature,keyEncipherment
extendedKeyUsage = 1.3.6.1.5.5.7.3.2

[ server_ca_extensions ]
basicConstraints = CA:false
keyUsage = digitalSignature,keyEncipherment
extendedKeyUsage = 1.3.6.1.5.5.7.3.1
EOF

# Тут можна додати в кінці

# subjectAltName = @alt_names

# [ alt_names ]
# IP.1 = 127.0.0.1

# Замість 127.0.0.1 можна додати ip-адресу Вашого серверу, після цього можна буде використати для з'єднання:
# params = pika.ConnectionParameters(
#     host='127.0.0.1',
#     port=5671,
#     credentials=credentials,
#     ssl_options=pika.SSLOptions(context)
# )
# Інакше треба при з'єднанні обов'язково вказувати при з'єднанні:
# ssl_options=pika.SSLOptions(context, server_hostname='<your_hostname>')