# Validação por PIN (MESSAGE para sip:validar@acme.operador) – Responsável: B
# STUB: a implementar no Sprint 2. Neste momento a segurança do serviço é
# garantida pela verificação de domínio em kamailio.py.
import KSR as KSR

import config
import kpi

PIN_VALIDO = "0000"


def tratar(msg):
    """Recebe uma SIP MESSAGE dirigida a sip:validar@acme.operador.

    Comportamento esperado:
      - corpo da MESSAGE ($rb, sem espaços/quebras de linha) igual a PIN_VALIDO
        -> 200 OK
      - outro corpo -> 403 Forbidden
      - (opcional) contar com kpi.inc("pin_validos") / kpi.inc("pin_invalidos")

    TODO (B): implementar. Até lá responde 501 Not Implemented
    (RFC 3261, 21.5.2: o servidor não suporta a funcionalidade pedida).
    """
    KSR.sl.send_reply(501, "Not Implemented")
    return 1
