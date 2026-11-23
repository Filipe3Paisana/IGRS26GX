# Constantes partilhadas por todos os módulos – Responsável: A
#
# Qualquer valor que mais do que um módulo precise de conhecer fica AQUI e só aqui.
# Se algum valor mudar, muda-se uma linha e todo o serviço acompanha.

# Domínio do operador (confirmado: acme.operador; o enunciado também escreve
# "acme.operator" por gralha).
DOMINIO = "acme.operador"

# Parte "user" dos AoR especiais do serviço (sip:<user>@DOMINIO)
SALA_COMUM = "common"      # sip:common@acme.operador
SALA_EQUIPA = "team"       # sip:team@acme.operador
VALIDAR = "validar"        # sip:validar@acme.operador (validação por PIN)
LEADER = "leader"          # sip:leader@acme.operador (confirmado; o enunciado escreve "leadear" por gralha)

# Servidor de conferências (SEMS do lab #5, ver compose.yaml e config/sems.conf).
# O SEMS (aplicação "conference") usa a parte user do R-URI como nome da sala,
# p.ex. sip:common@sipnet.sems:5050 -> sala "common".
SERVIDOR_CONF_HOST = "sipnet.sems"
SERVIDOR_CONF_PORTA = 5050

# Tabela usrloc onde o registrar guarda os registos (igual à dos labs)
TABELA_REGISTOS = "location"
