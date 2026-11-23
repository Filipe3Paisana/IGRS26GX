# T01 – Registo de utilizador acme

**Cartão Trello:** #3 · **Módulo:** `src/registo.py` (`tratar`)

## Objetivo
Um utilizador do domínio `acme.operador` regista-se e fica na base de dados de registos (usrloc).

## Pré-condições
`docker compose up -d kamailio`

## Passos
```bash
tests/capturar.sh T01-registo-ok register alice acme.operador 3600 --espera 200
```
(Com o Twinkle: perfil Alice → Registar.)

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | alice → acme.operador | `REGISTER sip:acme.operador` · To `<sip:alice@acme.operador>` · `Contact: <sip:alice@IP:5070>;expires=3600` |
| F2 | acme.operador → alice | `200 OK` com o Contact registado |

## Resultado esperado
**200 OK** (RFC 3261, 10.3 passo 8: o registrar devolve 200 com a lista atual de contactos).
KPI `registos` +1.

## Captura
`captures/T01-registo-ok.pcap`
