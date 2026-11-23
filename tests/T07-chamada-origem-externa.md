# T07 – Chamada de utilizador de domínio externo

**Cartão Trello:** #4 (usa a verificação de domínio do #3) · **Módulo:** `src/kamailio.py`

## Objetivo
`manel@outro.operador` não consegue ligar a utilizadores acme (nem usar qualquer outra funcionalidade).

## Passos
```bash
tests/capturar.sh T07-chamada-origem-externa pedido INVITE manel outro.operador sip:bob@acme.operador --espera 403
```

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | manel → proxy | `INVITE sip:bob@acme.operador` · From `<sip:manel@outro.operador>` |
| F2 | proxy → manel | `403 Forbidden` |
| F3 | manel → proxy | `ACK` (descartado) |

## Resultado esperado
**403 Forbidden** (RFC 3261, 21.4.4). Verifica-se o domínio do **From**, que identifica o
originador. KPI `pedidos_dominio_externo` +1.

## Captura
`captures/T07-chamada-origem-externa.pcap`
