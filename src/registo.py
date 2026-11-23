# Registo/deregisto e chamadas básicas – Responsável: A
import KSR as KSR

import config
import kpi


def tratar(msg):
    """REGISTER: registo (expires>0) ou deregisto (expires=0).
    TODO (#3): guardar em usrloc e responder 200 OK; deregisto de quem não está
    registado -> 404 Not Found."""
    KSR.sl.send_reply(501, "Not Implemented")
    return 1


def chamada_basica(msg):
    """INVITE/ACK/BYE/CANCEL entre utilizadores acme.
    TODO (#4): lookup do destino; não registado -> 404 Not Found; senão relay."""
    if KSR.pv.get("$rm") != "ACK":
        KSR.sl.send_reply(501, "Not Implemented")
    return 1
