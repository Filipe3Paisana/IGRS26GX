# T04 – Deregisto de utilizador não registado

**Cartão Trello:** #3 · **Módulo:** `src/registo.py` (`tratar`, `esta_registado`)

## Objetivo
Um pedido de deregisto de um AoR acme que não está na base de dados de registos é rejeitado.

## Passos
```bash
tests/capturar.sh T04-deregisto-nao-registado \
    register carlos acme.operador 0 --espera 404 ++ register bob acme.operador 0 --espera 404
```
O segundo passo corre depois do T03: o bob já fez o deregisto, por isso esta resposta prova que
o T03 apagou mesmo o registo da usrloc.

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | carlos → acme.operador | `REGISTER` · `Contact: <...>;expires=0` |
| F2 | acme.operador → carlos | `404 Not Found` |

## Resultado esperado
**404 Not Found** (RFC 3261, 21.4.5: o servidor tem informação definitiva de que o utilizador
não existe; aqui, o AoR não existe na base de dados de registos). KPI `deregistos_invalidos` +1.

## Captura
`captures/T04-deregisto-nao-registado.pcap`
