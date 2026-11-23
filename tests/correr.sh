#!/bin/sh
# Corre o cliente de teste num contentor na rede sipnet.
# Uso: tests/correr.sh register alice acme.operador 3600 --espera 200
exec docker run --rm --network sipnet -v "$(cd "$(dirname "$0")" && pwd):/tests:ro" \
    nicolaka/netshoot:latest python3 /tests/sip_teste.py "$@"
