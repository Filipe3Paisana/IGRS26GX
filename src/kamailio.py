# Ponto de entrada KEMI (Python) do Kamailio – ConferenceControl 2.0
# Responsável: A
#
# Este ficheiro só DECIDE para que módulo vai cada pedido SIP.
# A lógica de cada funcionalidade está no módulo de cada pessoa:
#   registo.py      REGISTER e chamadas básicas entre utilizadores acme   (A)
#   sala_comum.py   sip:common@acme.operador                              (B)
#   pin.py          MESSAGE para sip:validar@acme.operador                (B)
#   sala_equipa.py  sip:team@acme.operador, MESSAGE ao leader, DTMF       (C)
#   kpi.py          contadores: kpi.inc("nome")                           (D)
#
# Estrutura obrigatória do KEMI (igual à dos labs): mod_init() devolve um
# objeto com child_init, ksr_request_route, ksr_reply_route e ksr_onsend_route.

import KSR as KSR

import config
import registo
import sala_comum
import sala_equipa
import pin
import kpi


def mod_init():
    KSR.info("===== ConferenceControl 2.0: init (dominio %s) =====\n" % config.DOMINIO)
    return kamailio()


def sala_do_pedido():
    """Devolve o nome da sala de conferências a que o pedido diz respeito, ou None.

    Usamos o cabeçalho To ($tU) e não o Request-URI ($rU) porque:
      - num pedido inicial (INVITE) os dois coincidem (sip:common@acme.operador);
      - num pedido dentro do diálogo (BYE, ACK, INFO) o R-URI passa a ser o Contact
        do servidor de conferências, mas o To/From mantêm-se (RFC 3261, 12.2.1.1).
    Se o pedido vier do lado do servidor de conferências (ex.: BYE do SEMS), a sala
    aparece no From ($fU), por isso também verificamos esse campo.
    """
    salas = (config.SALA_COMUM, config.SALA_EQUIPA)
    for pv in ("$tU", "$fU"):
        user = KSR.pv.get(pv)
        if user in salas:
            return user
    return None


class kamailio:
    def __init__(self):
        KSR.info("===== kamailio.__init__\n")
        kpi.init()

    def child_init(self, rank):
        return 0

    def ksr_request_route(self, msg):
        metodo = KSR.pv.get("$rm")
        KSR.info("%s %s  From: %s  To: %s\n" % (
            metodo, KSR.pv.get("$ru"), KSR.pv.get("$fu"), KSR.pv.get("$tu")))

        # 1) REGISTER: registo / deregisto
        if metodo == "REGISTER":
            return registo.tratar(msg)

        # 2) MESSAGE para sip:validar@...: validação por PIN
        if metodo == "MESSAGE" and KSR.pv.get("$rU") == config.VALIDAR:
            return pin.tratar(msg)

        # 3) INFO enviado pelo leader: resposta DTMF (# aceita, * rejeita)
        if metodo == "INFO" and KSR.pv.get("$fU") == config.LEADER:
            return sala_equipa.tratar_dtmf(msg)

        # 4) Salas de conferência (pedidos iniciais e dentro do diálogo)
        sala = sala_do_pedido()
        if sala == config.SALA_COMUM:
            return sala_comum.tratar(msg)
        if sala == config.SALA_EQUIPA:
            return sala_equipa.tratar(msg)

        # 5) Tudo o resto: chamadas normais entre utilizadores acme
        return registo.chamada_basica(msg)

    def ksr_reply_route(self, msg):
        return 1

    def ksr_onsend_route(self, msg):
        return 1
