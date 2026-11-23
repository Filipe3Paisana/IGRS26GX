# T08 – Método não suportado

**Cartão Trello:** #4 · **Módulo:** `src/registo.py` (`chamada_basica`)

## Objetivo
Pedidos fora de diálogo com métodos que o serviço não trata (ex.: OPTIONS, SUBSCRIBE, PUBLISH,
que o Twinkle envia) recebem uma resposta conforme o RFC.

## Passos
```bash
tests/capturar.sh T08-metodo-nao-suportado pedido OPTIONS alice acme.operador sip:bob@acme.operador --espera 405
```

## Resultado esperado
**405 Method Not Allowed** com o cabeçalho `Allow: INVITE, ACK, BYE, CANCEL, REGISTER, MESSAGE, INFO`
(RFC 3261, 21.4.6: o 405 tem de incluir Allow). Os labs usavam `403 Forbiden method`.

## Captura
`captures/T08-metodo-nao-suportado.pcap`
