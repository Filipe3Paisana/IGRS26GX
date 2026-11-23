# T03 – Deregisto de utilizador registado

**Cartão Trello:** #3 · **Módulo:** `src/registo.py` (`tratar`, `obter_expires`)

## Objetivo
Um utilizador acme registado remove o seu registo (expires = 0).

## Passos
```bash
tests/capturar.sh T03-deregisto-ok \
    register bob acme.operador 3600 --espera 200 ++ register bob acme.operador 0 --espera 200
```

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | bob → acme.operador | `REGISTER` · `Contact: <...>;expires=3600` |
| F2 | acme.operador → bob | `200 OK` |
| F3 | bob → acme.operador | `REGISTER` · `Contact: <...>;expires=0` |
| F4 | acme.operador → bob | `200 OK` (sem contactos: o registo foi apagado) |

## Resultado esperado
**200 OK** nos dois pedidos (RFC 3261, 10.2.2: expires=0 remove o contacto). O tempo é lido do
parâmetro `expires` do Contact, que tem prioridade, ou do cabeçalho `Expires`. `Contact: *` também
é tratado como deregisto. KPI `deregistos` +1.

## Captura
`captures/T03-deregisto-ok.pcap`
