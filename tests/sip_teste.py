#!/usr/bin/env python3
"""Cliente SIP mínimo para testar o ConferenceControl 2.0 sem interface gráfica.

Só usa a biblioteca padrão. Corre num contentor ligado à rede "sipnet":

    docker run --rm --network sipnet -v "$PWD/tests:/tests" nicolaka/netshoot \
        python3 /tests/sip_teste.py <comando> [argumentos]

Comandos:
    register <user> <dominio> [expires]       REGISTER (expires=0 -> deregisto)
    chamada  <user_origem> <user_destino> [--sem-registo-destino] [--dominio-destino D]
             INVITE de origem para destino; o destino (se registado) atende
             automaticamente; depois ACK e BYE.
    pedido   <metodo> <user_origem> <dominio_origem> <uri_destino>
             envia um pedido fora de diálogo (ex.: MESSAGE, INVITE) e mostra a resposta.

Cada comando imprime as respostas recebidas e termina com código de saída 0 se a
resposta final for a esperada (opção --espera <codigo>).

As mensagens são construídas à mão de propósito, para se ver cada cabeçalho
exigido pelo RFC 3261 (secção 8.1.1: To, From, CSeq, Call-ID, Max-Forwards, Via).
"""
import argparse
import random
import socket
import sys
import threading

PROXY = ("acme.operador", 5060)
DOMINIO = "acme.operador"


def aleatorio(n=8):
    return "".join(random.choice("abcdef0123456789") for _ in range(n))


def ip_local():
    # IP desta máquina na rede sipnet (o "connect" de UDP não envia nada)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(PROXY)
    ip = s.getsockname()[0]
    s.close()
    return ip


class Mensagem:
    """Pedido ou resposta SIP já recebido, com os cabeçalhos num dicionário."""

    def __init__(self, texto):
        cabecalho, _, self.corpo = texto.partition("\r\n\r\n")
        linhas = cabecalho.split("\r\n")
        self.primeira = linhas[0]
        self.hdrs = []                       # lista de (nome_minúsculas, valor)
        for linha in linhas[1:]:
            nome, _, valor = linha.partition(":")
            self.hdrs.append((nome.strip().lower(), valor.strip()))
        partes = self.primeira.split(" ", 2)
        self.resposta = partes[0].startswith("SIP/")
        self.codigo = int(partes[1]) if self.resposta else None
        self.metodo = None if self.resposta else partes[0]

    def get(self, nome):
        for n, v in self.hdrs:
            if n == nome:
                return v
        return None

    def todos(self, nome):
        return [v for n, v in self.hdrs if n == nome]


class UA:
    """User Agent SIP simples (UAC e, opcionalmente, UAS que atende chamadas)."""

    def __init__(self, user, dominio, porta):
        self.user, self.dominio = user, dominio
        self.ip = ip_local()
        self.porta = porta
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", porta))
        self.sock.settimeout(5)
        self.cseq = 0
        self.aor = "sip:%s@%s" % (user, dominio)
        self.contact = "<sip:%s@%s:%d>" % (user, self.ip, porta)

    # ---------- envio / receção ----------
    def enviar(self, texto, destino=PROXY):
        print("  >>> %s" % texto.split("\r\n", 1)[0])
        self.sock.sendto(texto.encode(), destino)

    def receber(self):
        dados, origem = self.sock.recvfrom(65535)
        m = Mensagem(dados.decode(errors="replace"))
        print("  <<< %s" % m.primeira)
        return m, origem

    def via(self, branch):
        return "SIP/2.0/UDP %s:%d;branch=z9hG4bK%s;rport" % (self.ip, self.porta, branch)

    def pedido(self, metodo, ruri, to, call_id, from_tag, branch,
               to_tag=None, extra=(), corpo="", tipo=None, cseq=None):
        if cseq is None:
            self.cseq += 1
            cseq = self.cseq
        linhas = [
            "%s %s SIP/2.0" % (metodo, ruri),
            "Via: " + self.via(branch),
            "Max-Forwards: 70",
            "From: <%s>;tag=%s" % (self.aor, from_tag),
            "To: <%s>%s" % (to, ";tag=" + to_tag if to_tag else ""),
            "Call-ID: " + call_id,
            "CSeq: %d %s" % (cseq, metodo),
            "Contact: " + self.contact,
        ]
        linhas += list(extra)
        if tipo:
            linhas.append("Content-Type: " + tipo)
        linhas.append("Content-Length: %d" % len(corpo.encode()))
        return "\r\n".join(linhas) + "\r\n\r\n" + corpo

    def esperar_final(self):
        """Espera pela resposta final (>=200) ignorando as provisórias (1xx)."""
        while True:
            m, _ = self.receber()
            if m.resposta and m.codigo >= 200:
                return m

    # ---------- REGISTER ----------
    def register(self, expires):
        call_id = aleatorio(12) + "@" + self.ip
        # RFC 3261, 10.2: R-URI = domínio do registrar; To = AoR a registar;
        # o tempo de registo pode ir no parâmetro expires do Contact (como o Twinkle faz).
        texto = self.pedido("REGISTER", "sip:" + self.dominio, self.aor, call_id,
                            aleatorio(), aleatorio())
        texto = texto.replace("Contact: " + self.contact,
                              "Contact: %s;expires=%d" % (self.contact, expires))
        self.enviar(texto)
        return self.esperar_final()

    # ---------- chamada (INVITE / ACK / BYE) ----------
    def invite(self, destino):
        call_id = aleatorio(12) + "@" + self.ip
        from_tag, branch = aleatorio(), aleatorio()
        sdp = ("v=0\r\no=%s 1 1 IN IP4 %s\r\ns=-\r\nc=IN IP4 %s\r\nt=0 0\r\n"
               "m=audio 8000 RTP/AVP 0\r\na=rtpmap:0 PCMU/8000\r\n") % (self.user, self.ip, self.ip)
        self.enviar(self.pedido("INVITE", destino, destino, call_id, from_tag, branch,
                                corpo=sdp, tipo="application/sdp"))
        final = self.esperar_final()
        to_tag = (final.get("to") or "").partition("tag=")[2] or None
        if final.codigo >= 300:
            # RFC 3261, 17.1.1.3: resposta negativa -> ACK na MESMA transação
            # (mesmo branch e CSeq), enviado salto-a-salto ao proxy.
            self.enviar(self.pedido("ACK", destino, destino, call_id, from_tag, branch,
                                    to_tag=to_tag, cseq=self.cseq))
            return final, None
        # 2xx: o ACK é um pedido novo, dentro do diálogo (RFC 3261, 13.2.2.4),
        # dirigido ao Contact do destino e com o route set (Record-Route invertido).
        alvo = final.get("contact").strip("<>").split(">")[0]
        rotas = [r for v in reversed(final.todos("record-route")) for r in v.split(",")]
        extra = ["Route: " + r.strip() for r in rotas]
        dialogo = dict(alvo=alvo, to=destino, call_id=call_id, from_tag=from_tag,
                       to_tag=to_tag, extra=extra)
        self.enviar(self.pedido("ACK", alvo, destino, call_id, from_tag, aleatorio(),
                                to_tag=to_tag, extra=extra, cseq=self.cseq))
        return final, dialogo

    def bye(self, d):
        self.enviar(self.pedido("BYE", d["alvo"], d["to"], d["call_id"], d["from_tag"],
                                aleatorio(), to_tag=d["to_tag"], extra=d["extra"]))
        return self.esperar_final()

    # ---------- UAS: atender automaticamente ----------
    def responder(self, m, origem, codigo, razao, to_tag, corpo=""):
        linhas = ["SIP/2.0 %d %s" % (codigo, razao)]
        linhas += ["Via: " + v for v in m.todos("via")]
        linhas += ["Record-Route: " + v for v in m.todos("record-route")]
        to = m.get("to")
        if "tag=" not in to and codigo > 100:
            to += ";tag=" + to_tag
        linhas += ["From: " + m.get("from"), "To: " + to,
                   "Call-ID: " + m.get("call-id"), "CSeq: " + m.get("cseq"),
                   "Contact: " + self.contact]
        if corpo:
            linhas.append("Content-Type: application/sdp")
        linhas.append("Content-Length: %d" % len(corpo.encode()))
        texto = "\r\n".join(linhas) + "\r\n\r\n" + corpo
        print("  [%s] >>> %s" % (self.user, linhas[0]))
        self.sock.sendto(texto.encode(), origem)

    def atender_em_fundo(self):
        def ciclo():
            to_tag = aleatorio()
            self.sock.settimeout(None)
            while True:
                dados, origem = self.sock.recvfrom(65535)
                m = Mensagem(dados.decode(errors="replace"))
                print("  [%s] <<< %s" % (self.user, m.primeira))
                if m.resposta or m.metodo == "ACK":
                    continue
                if m.metodo == "INVITE":
                    self.responder(m, origem, 180, "Ringing", to_tag)
                    self.responder(m, origem, 200, "OK", to_tag, corpo=m.corpo)
                else:                       # BYE, CANCEL, ...
                    self.responder(m, origem, 200, "OK", to_tag)
        threading.Thread(target=ciclo, daemon=True).start()


def verificar(obtido, esperado):
    if esperado is None:
        return 0
    ok = obtido == esperado
    print("RESULTADO: %s (obtido %s, esperado %s)" % ("OK" if ok else "FALHOU", obtido, esperado))
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register")
    r.add_argument("user"); r.add_argument("dominio"); r.add_argument("expires", nargs="?", type=int, default=3600)
    c = sub.add_parser("chamada")
    c.add_argument("origem"); c.add_argument("destino")
    c.add_argument("--sem-registo-destino", action="store_true")
    c.add_argument("--dominio-destino", default=DOMINIO)
    q = sub.add_parser("pedido")
    q.add_argument("metodo"); q.add_argument("user"); q.add_argument("dominio"); q.add_argument("uri")
    q.add_argument("--corpo", default="")
    for s in (r, c, q):
        s.add_argument("--espera", type=int, help="código SIP final esperado")
    a = p.parse_args()

    if a.cmd == "register":
        ua = UA(a.user, a.dominio, 5070)
        return verificar(ua.register(a.expires).codigo, a.espera)

    if a.cmd == "pedido":
        ua = UA(a.user, a.dominio, 5070)
        call_id = aleatorio(12) + "@" + ua.ip
        corpo = a.corpo
        ua.enviar(ua.pedido(a.metodo, a.uri, a.uri, call_id, aleatorio(), aleatorio(),
                            corpo=corpo, tipo="text/plain" if corpo else None))
        final = ua.esperar_final()
        if a.metodo == "INVITE" and final.codigo >= 300:
            to_tag = (final.get("to") or "").partition("tag=")[2] or None
            branch = final.get("via").split("branch=z9hG4bK")[1].split(";")[0]
            ua.enviar(ua.pedido("ACK", a.uri, a.uri, call_id,
                                final.get("from").split("tag=")[1], branch,
                                to_tag=to_tag, cseq=ua.cseq))
        return verificar(final.codigo, a.espera)

    # chamada: origem e destino no mesmo processo, em portas diferentes
    origem = UA(a.origem, DOMINIO, 5070)
    destino_uri = "sip:%s@%s" % (a.destino, a.dominio_destino)
    if not a.sem_registo_destino:
        dest = UA(a.destino, DOMINIO, 5072)
        print("-- registo do destino (%s)" % a.destino)
        dest.register(3600)
        dest.atender_em_fundo()
    print("-- INVITE %s -> %s" % (origem.aor, destino_uri))
    final, dialogo = origem.invite(destino_uri)
    if dialogo is None:
        return verificar(final.codigo, a.espera)
    print("-- chamada estabelecida; BYE")
    fim = origem.bye(dialogo)
    rc = verificar(final.codigo, a.espera)
    print("BYE -> %d" % fim.codigo)
    return rc or (0 if fim.codigo == 200 else 1)


if __name__ == "__main__":
    sys.exit(main())
