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

def chamada_basica(msg):
    """INVITE/ACK/BYE/CANCEL entre utilizadores acme.
    TODO (#4): lookup do destino; não registado -> 404 Not Found; senão relay."""
    if KSR.pv.get("$rm") != "ACK":
        KSR.sl.send_reply(501, "Not Implemented")
    return 1
