# IGRS 2026/27 – ConferenceControl 2.0 (Grupo 10)

Serviço suplementar de conferência sobre SIP, implementado em Python para Kamailio
(KEMI, módulo `app_python3`), com KPIs modelados em YANG e expostos via gNMI.

Enunciado: [docs/enunciado.pdf](docs/enunciado.pdf)

## Equipa e responsabilidades

| Pessoa | Área | Módulo |
|---|---|---|
| A – Filipe | Infra, registo, chamadas básicas, coordenação | `src/kamailio.py`, `src/registo.py`, `src/config.py` |
| B – Leonel | Sala comum, validação por PIN, GRL | `src/sala_comum.py`, `src/pin.py` |
| C – Tchang | Sala de equipa (leader, MESSAGE, DTMF) | `src/sala_equipa.py` |
| D – Sérgio | KPIs, YANG, gNMI | `src/kpi.py`, `docs/yang/`, `gnmi/` |

## Estrutura

```
compose.yaml    ambiente Docker do projeto (baseado nos labs #3/#4 + SEMS do lab #5)
config/         kamailio.cfg, sems.conf e perfis Twinkle dos terminais
src/            código Python KEMI (um módulo por funcionalidade)
  config.py     constantes partilhadas (DOMINIO, AoR das salas, servidor de conferências)
docs/grl/       diagrama GRL
docs/backlog/   Product Backlog (User Stories + Story Points)
docs/sprintN/   Sprint Backlog, Definition of Ready/Done, diagramas
docs/yang/      modelo YANG dos KPIs
gnmi/           servidor gNMI
tests/          descrição dos testes (.md), cliente SIP de teste e capturas .pcap
labs/           ficheiros originais dos labs #3, #4 e #5 (referência)
```

## Ambiente de desenvolvimento

Pré-requisitos: Docker Desktop, as imagens `twinkle:igrs_2026` e `sems:igrs_2026`
(construída com `docker build -f labs/lab5/sems.dockerfile -t sems:igrs_2026 labs/lab5`) e,
para os terminais Twinkle, um servidor X (XQuartz) como nos labs.

```bash
docker compose up -d kamailio sems          # proxy/registrar + servidor de conferências
docker compose logs -f kamailio             # ver os logs do script Python
docker compose restart kamailio             # recarregar depois de alterar src/
docker compose --profile terminais up -d    # (opcional) terminais Twinkle alice/bob/manel
```

| Contentor | Hostname | Papel |
|---|---|---|
| `kamailio` | `acme.operador` | registrar + proxy, executa `src/kamailio.py` (UDP 5060) |
| `sems` | `sipnet.sems` | servidor de conferências (UDP 5050) |
| `terminal_*` | `sipnet.<nome>` | terminais Twinkle (alice e bob em acme, manel em outro.operador) |

Testes automáticos sem interface gráfica: ver [tests/README.md](tests/README.md).

## Sprints

| Sprint | Datas | Objetivo |
|---|---|---|
| 1 | 26 nov → 6 dez | Registo, chamadas básicas, sala comum, modelo YANG |
| 2 | 7 dez → 20 dez | Sala de equipa, PIN, gNMI, testes finais |

## Regras de trabalho

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
