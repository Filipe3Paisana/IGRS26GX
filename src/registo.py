# Registo/deregisto e chamadas básicas – Responsável: A
#
# Quando chegamos aqui, kamailio.py já garantiu que o pedido vem de acme.operador
# (domínio externo -> 403 Forbidden).
import re

import KSR as KSR

import config
import kpi


# ---------------------------------------------------------------------------
# REGISTER
# ---------------------------------------------------------------------------

def obter_expires():
    """Devolve o tempo de registo pedido (segundos) ou None se não for indicado.

    RFC 3261, 10.2.1.1 e 10.2.2:
      - "Contact: *" (todos os contactos) só é válido com Expires: 0 -> deregisto total;
      - o parâmetro ";expires=" do Contact tem prioridade sobre o cabeçalho Expires;
      - se nenhum dos dois existir, o registrar escolhe o valor por omissão.
    O Twinkle (terminais dos labs) envia o tempo no parâmetro do Contact
    (registration_time_in_contact=yes), mas outros terminais usam o cabeçalho.
    """
    contact = KSR.hdr.get("Contact")
    if contact is not None and contact.strip() == "*":
        return 0
    if contact is not None:
        m = re.search(r";\s*expires\s*=\s*(\d+)", contact, re.IGNORECASE)
        if m:
            return int(m.group(1))
    expires = KSR.hdr.get("Expires")
    if expires is not None and expires.strip().isdigit():
        return int(expires.strip())
    return None


def esta_registado(aor):
    """True se o AoR tem pelo menos um contacto na base de dados de registos (usrloc)."""
    return KSR.registrar.registered_uri(config.TABELA_REGISTOS, aor) == 1


def tratar(msg):
    """REGISTER de um utilizador acme: registo (expires>0) ou deregisto (expires=0).

    - Registo: KSR.registrar.save() guarda o Contact na tabela usrloc "location"
      e responde ele próprio 200 OK com os contactos atuais (RFC 3261, 10.3 passo 8).
    - Deregisto de quem está registado: save() com expires=0 apaga o contacto e
      responde 200 OK.
    - Deregisto de quem NÃO está registado: 404 Not Found. Pelo RFC 3261 (21.4.5)
      o 404 indica que o servidor tem informação definitiva de que o utilizador não
      existe; aqui significa que o AoR não existe na base de dados de registos e,
      portanto, não há nada para remover.
    """
    aor = KSR.pv.get("$tu")
    expires = obter_expires()

    if expires == 0 and not esta_registado(aor):
        KSR.info("  deregisto de %s, que nao esta registado: 404\n" % aor)
        kpi.inc("deregistos_invalidos")
        KSR.sl.send_reply(404, "Not Found")
        return 1

    # flags=0: o próprio registrar envia a resposta (200 OK ou o erro adequado).
    if KSR.registrar.save(config.TABELA_REGISTOS, 0) < 0:
        KSR.err("  erro ao guardar o registo de %s\n" % aor)
        return 1

    if expires == 0:
        KSR.info("  deregisto de %s: 200\n" % aor)
        kpi.inc("deregistos")
    else:
        KSR.info("  registo de %s (expires=%s): 200\n" % (aor, expires))
        kpi.inc("registos")
    return 1


# ---------------------------------------------------------------------------
# Chamadas básicas
# ---------------------------------------------------------------------------

METODOS_SUPORTADOS = "INVITE, ACK, BYE, CANCEL, REGISTER, MESSAGE, INFO"


def relay():
    """Encaminha com estado (módulo tm), como no lab #4. Se o encaminhamento
    falhar logo (ex.: destino impossível de resolver), o tm responde com erro."""
    if KSR.tm.t_relay() < 0:
        KSR.sl.send_reply(500, "Server Internal Error")
    return 1


def pedido_em_dialogo(metodo):
    """ACK, BYE, re-INVITE, ... de uma chamada já estabelecida (o To tem tag).

    Como no pedido inicial fizemos record_route(), os pedidos seguintes do diálogo
    trazem um cabeçalho Route a apontar para este proxy e o R-URI é o Contact do
    outro terminal (RFC 3261, 12.2.1.1 e 16.12). O loose_route() consome o Route
    e basta reencaminhar.
    """
    if KSR.rr.loose_route() > 0:
        return relay()

    if metodo == "ACK":
        # ACK de uma resposta negativa (ex.: 404) que pertence a uma transação
        # já conhecida: o tm absorve-o ou encaminha-o. Se não pertencer a nenhuma
        # (p.ex. ACK a um 404 gerado aqui pelo sl), descarta-se: um ACK nunca tem
        # resposta (RFC 3261, 17.1.1.3).
        if KSR.tm.t_check_trans() > 0:
            KSR.tm.t_relay()
        return 1

    # Sem Route (o terminal não respeitou o Record-Route): comportamento do lab #4,
    # localizar o destino pelo R-URI.
    if KSR.registrar.lookup(config.TABELA_REGISTOS) == 1:
        return relay()
    KSR.sl.send_reply(404, "Not Found")
    return 1


def chamada_basica(msg):
    """Chamadas de voz entre utilizadores acme (INVITE / ACK / BYE / CANCEL).

    Pedido inicial INVITE para sip:<user>@acme.operador:
      - destino registado -> o lookup() troca o R-URI pelo Contact registado,
        record_route() mantém o proxy no caminho do diálogo e t_relay() encaminha;
        as respostas (180, 200, ...) voltam pelo mesmo caminho (cabeçalhos Via).
      - destino não registado -> 404 Not Found.
        Escolha do enunciado/CLAUDE.md. Pelo RFC 3261 (21.4.5) o 404 indica que o
        utilizador não existe no domínio; a alternativa seria 480 Temporarily
        Unavailable (21.4.18: utilizador existe mas não está contactável).
      - destino de outro domínio -> 404 Not Found. O RFC 3261 (21.4.5) diz
        explicitamente que o 404 também se usa quando o domínio do R-URI não é
        servido por quem recebe o pedido.
    """
    metodo = KSR.pv.get("$rm")

    # Pedidos dentro de um diálogo já existente (o To tem tag)
    if KSR.pv.get("$tt") is not None:
        return pedido_em_dialogo(metodo)

    # CANCEL: cancela um INVITE ainda sem resposta final. O tm associa-o à
    # transação do INVITE e propaga-o ao destino (RFC 3261, 9.2 e 16.10).
    if metodo == "CANCEL":
        if KSR.tm.t_check_trans() > 0:
            return relay()
        KSR.sl.send_reply(481, "Call/Transaction Does Not Exist")
        return 1

    if metodo == "ACK":            # ACK fora de diálogo sem transação: descartar
        if KSR.tm.t_check_trans() > 0:
            KSR.tm.t_relay()
        return 1

    if metodo != "INVITE":
        # 405 Method Not Allowed (RFC 3261, 21.4.6): o método não é permitido para
        # este R-URI; a resposta TEM de incluir o cabeçalho Allow.
        KSR.hdr.append_to_reply("Allow: %s\r\n" % METODOS_SUPORTADOS)
        KSR.sl.send_reply(405, "Method Not Allowed")
        return 1

    # INVITE inicial
    if KSR.pv.get("$rd") != config.DOMINIO:
        KSR.info("  destino fora de %s: 404\n" % config.DOMINIO)
        kpi.inc("chamadas_destino_inexistente")
        KSR.sl.send_reply(404, "Not Found")
        return 1

    if KSR.registrar.lookup(config.TABELA_REGISTOS) != 1:
        KSR.info("  destino %s nao registado: 404\n" % KSR.pv.get("$ru"))
        kpi.inc("chamadas_destino_nao_registado")
        KSR.sl.send_reply(404, "Not Found")
        return 1

    KSR.info("  lookup: R-URI passou a %s\n" % KSR.pv.get("$ru"))
    kpi.inc("chamadas")
    KSR.rr.record_route()
    return relay()
