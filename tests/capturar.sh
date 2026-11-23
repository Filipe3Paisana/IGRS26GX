#!/bin/sh
# Corre um teste e grava o tráfego SIP visto pelo Kamailio em tests/captures/<nome>.pcap
# Uso: tests/capturar.sh T01-registo-ok register alice acme.operador 3600 --espera 200
#      (pode receber vários testes separados por " ++ ", ex.: register ... ++ register ...)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
NOME="$1"; shift
docker run -d --rm --name captura_igrs --network container:kamailio \
    -v "$DIR/captures:/captures" nicolaka/netshoot:latest \
    tcpdump -i any -U -w "/captures/$NOME.pcap" udp port 5060 or udp port 5050 >/dev/null
sleep 2
RC=0
# separa os vários passos pelo marcador "++"
PASSO=""
for arg in "$@" "++"; do
    if [ "$arg" = "++" ]; then
        echo "== $PASSO"
        # shellcheck disable=SC2086
        "$DIR/correr.sh" $PASSO || RC=1
        PASSO=""
    else
        PASSO="$PASSO $arg"
    fi
done
sleep 1
docker stop captura_igrs >/dev/null
echo "captura: tests/captures/$NOME.pcap"
exit $RC
