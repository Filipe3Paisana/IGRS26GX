# Sala de equipa sip:team@acme.operador – Responsável: C
# STUB: a implementar.
import KSR as KSR

import config
import kpi

sala_aberta = False         # estado da sala (o leader "abre" com o seu INVITE)
pedidos_pendentes = {}      # AoR do utilizador -> transação à espera da decisão do leader


def tratar(msg):
    """Pedidos relativos à sala de equipa (To ou From = sip:team@acme.operador).

    Comportamento esperado:
      - INVITE do leader (sip:<config.LEADER>@acme.operador) -> encaminhar para o
        servidor de conferências; a sala fica "aberta"
      - INVITE de outro utilizador acme:
          * sala fechada -> 503 Service Unavailable
          * sala aberta  -> suspender a transação e enviar SIP MESSAGE ao leader:
            "<AoR> pretende aceder à sala da equipa"; esperar pela resposta DTMF
      - BYE -> servidor de conferências; o BYE do leader fecha a sala
        (o leader é sempre o último a sair)
      - domínio externo -> 403 Forbidden (já garantido em kamailio.py)

    TODO (C): implementar. Até lá responde 501 Not Implemented.
    """
    if KSR.pv.get("$rm") != "ACK":      # nunca se responde a um ACK
        KSR.sl.send_reply(501, "Not Implemented")
    return 1


def tratar_dtmf(msg):
    """SIP INFO enviado pelo leader com a tecla premida.

    Comportamento esperado:
      - '#' -> aceita: o INVITE pendente segue para o servidor de conferências
      - '*' -> rejeita: o utilizador recebe 603 Decline, p.ex. kpi.inc("pedidos_recusados_leader")
      - responder 200 OK ao INFO

    TODO (C): implementar. Até lá responde 501 Not Implemented.
    """
    KSR.sl.send_reply(501, "Not Implemented")
    return 1
