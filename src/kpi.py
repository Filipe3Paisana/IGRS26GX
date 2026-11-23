# KPIs do serviço – Responsável: D
#
# API usada pelos outros módulos:
#     kpi.inc("nome_do_kpi")        incrementa um contador
#     kpi.ler_todos()               dicionário {nome: valor}
#
# STUB FUNCIONAL: por agora só há a versão NÃO persistente (dicionário em memória).
# Atenção: o Kamailio corre vários processos filhos (children=4 em kamailio.cfg);
# cada processo tem a sua cópia deste dicionário. A versão final deve usar memória
# partilhada ($shv) e/ou uma base de dados (ex.: Redis, como no lab #5).

_contadores = {}   # versão não persistente (memória do processo)


def init():
    """TODO (D): carregar os valores persistentes (Redis/ficheiro/SQLite)."""
    pass


def inc(nome, valor=1):
    """Incrementa o KPI `nome`. TODO (D): guardar também de forma persistente."""
    _contadores[nome] = _contadores.get(nome, 0) + valor


def ler_todos():
    return dict(_contadores)
