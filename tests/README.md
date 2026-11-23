# Testes

Um ficheiro por cenário (`T01-registo-ok.md`, `T02-registo-dominio-externo.md`, ...), cada um
com objetivo, passos, resultado esperado (código SIP) e a captura em `captures/`.

## Ferramentas

- `sip_teste.py`: cliente SIP mínimo, sem dependências, para testar sem o Twinkle.
- `correr.sh`: corre o `sip_teste.py` num contentor (`nicolaka/netshoot`) ligado à rede `sipnet`.
- `capturar.sh`: corre um ou mais passos (separados por `++`) e grava o tráfego visto pelo
  Kamailio em `captures/<nome>.pcap` (abre-se no Wireshark).

```bash
docker compose up -d kamailio
tests/correr.sh register alice acme.operador 3600 --espera 200
tests/capturar.sh T01-registo-ok register alice acme.operador 3600 --espera 200
```

## Índice

| Teste | Cenário | Esperado | Cartão |
|---|---|---|---|
| [T01](T01-registo-ok.md) | registo acme | 200 | #3 |
| [T02](T02-registo-dominio-externo.md) | registo de domínio externo | 403 | #3 |
| [T03](T03-deregisto-ok.md) | deregisto de registado | 200 | #3 |
| [T04](T04-deregisto-nao-registado.md) | deregisto de não registado | 404 | #3 |
