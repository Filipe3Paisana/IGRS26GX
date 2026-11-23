# T06 – Chamada para utilizador acme não registado

**Cartão Trello:** #4 · **Módulo:** `src/registo.py` (`chamada_basica`)

## Objetivo
Uma chamada para um AoR acme sem registo na usrloc é rejeitada.

## Passos
```bash
tests/capturar.sh T06-chamada-destino-nao-registado chamada alice zeca --sem-registo-destino --espera 404
```

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | alice → proxy | `INVITE sip:zeca@acme.operador` |
| F2 | proxy → alice | `404 Not Found` (o lookup falhou) |
| F3 | alice → proxy | `ACK` (mesma transação do INVITE; o proxy descarta-o sem resposta) |

## Resultado esperado
**404 Not Found** (RFC 3261, 21.4.5), como no lab #4. Alternativa a discutir: `480 Temporarily
Unavailable` (21.4.18). Um INVITE para um domínio que não é `acme.operador` também recebe 404,
porque o RFC 3261 (21.4.5) prevê o 404 quando o domínio do R-URI não é servido pelo servidor.
KPI `chamadas_destino_nao_registado` +1.

## Captura
`captures/T06-chamada-destino-nao-registado.pcap`
