# T05 – Chamada de voz entre utilizadores acme

**Cartão Trello:** #4 · **Módulo:** `src/registo.py` (`chamada_basica`, `pedido_em_dialogo`)

## Objetivo
`alice@acme.operador` liga a `bob@acme.operador` (registado), a chamada é estabelecida e terminada.

## Passos
```bash
tests/capturar.sh T05-chamada-ok chamada alice bob --espera 200
```
O cliente regista o bob, que atende automaticamente; a alice envia INVITE, ACK e BYE.
(Com o Twinkle: registar Alice e Bob; a Alice liga para `bob`.)

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | alice → proxy | `INVITE sip:bob@acme.operador` (SDP) |
| F2 | proxy → alice | `100 Trying` (tm) |
| F3 | proxy → bob | `INVITE sip:bob@<IP:porta>`: o R-URI foi trocado pelo Contact registado (lookup) e foi acrescentado `Record-Route: <sip:proxy;lr>` |
| F4–F5 | bob → proxy → alice | `180 Ringing` |
| F6–F7 | bob → proxy → alice | `200 OK` (SDP) com o Record-Route |
| F8–F9 | alice → proxy → bob | `ACK` com `Route: <sip:proxy;lr>` (loose_route) |
| F10–F11 | alice → proxy → bob | `BYE` com `Route` |
| F12–F13 | bob → proxy → alice | `200 OK` |

Diálogo: Call-ID + tag do From (alice) + tag do To (bob), criado no 200 OK do INVITE e terminado no
200 OK do BYE. Transações: INVITE (F1–F7), ACK (F8–F9, sem resposta) e BYE (F10–F13).

## Resultado esperado
**200 OK** ao INVITE e ao BYE. KPI `chamadas` +1.

## Captura
`captures/T05-chamada-ok.pcap`
