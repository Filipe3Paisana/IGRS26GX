# Sala comum sip:common@acme.operador – Responsável: B
# STUB: a implementar.
import KSR as KSR

import config
import kpi


def tratar(msg):
    """Pedidos relativos à sala comum (To ou From = sip:common@acme.operador).

    Comportamento esperado:
      - INVITE de utilizador acme -> encaminhar para o servidor de conferências
        (R-URI sip:common@<config.SERVIDOR_CONF_HOST>:<config.SERVIDOR_CONF_PORTA>,
        Record-Route e t_relay), p.ex. kpi.inc("conferencias_comum")
      - ACK/BYE/CANCEL do diálogo -> encaminhar (loose_route + t_relay)
      - utilizador de domínio externo -> 403 Forbidden (já garantido pela
        verificação de domínio em kamailio.py)
      - servidor de conferências não responde -> contar falha,
        p.ex. kpi.inc("conferencias_falhadas")

    TODO (B): implementar. Até lá responde 501 Not Implemented.
    """
    if KSR.pv.get("$rm") != "ACK":      # nunca se responde a um ACK
        KSR.sl.send_reply(501, "Not Implemented")
    return 1
