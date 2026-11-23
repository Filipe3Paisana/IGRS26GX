# T02 – Registo de utilizador de domínio externo

**Cartão Trello:** #3 · **Módulo:** `src/kamailio.py` (verificação de domínio)

## Objetivo
Um utilizador que não pertence a `acme.operador` (ex.: `sip:manel@outro.operador`) não se consegue registar.

## Passos
```bash
tests/capturar.sh T02-registo-dominio-externo register manel outro.operador 3600 --espera 403
```
(Com o Twinkle: perfil Manel → Registar.)

## Mensagens
| # | De → Para | Mensagem |
|---|---|---|
| F1 | manel → acme.operador | `REGISTER sip:outro.operador` · To `<sip:manel@outro.operador>` |
| F2 | acme.operador → manel | `403 Forbidden` |

## Resultado esperado
**403 Forbidden** (RFC 3261, 21.4.4: o servidor percebeu o pedido mas recusa-se a satisfazê-lo
e a autenticação não ajudaria). Verifica-se o domínio do **To**, porque no REGISTER o To é o AoR
a registar (RFC 3261, 10.2). Nada é guardado na usrloc. KPI `registos_rejeitados` +1.

## Captura
`captures/T02-registo-dominio-externo.pcap`
