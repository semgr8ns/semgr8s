[ req ]
default_bits       = 2048
distinguished_name = req_distinguished_name
req_extensions     = req_ext
prompt             = no
[ req_distinguished_name ]
countryName                 = IN
stateOrProvinceName         = KAR
localityName                = BGL
organizationName            = ACME INC
commonName                  = __WEBHOOK__ __VERSION__
[ req_ext ]
subjectAltName = @alt_names
[alt_names]
DNS.1   = __WEBHOOK__-svc.__NAMESPACE__.svc
