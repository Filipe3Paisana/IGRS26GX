# Regras de trabalho

1. **Nunca fazer commit direto em `main`.** Cada pessoa trabalha num branch
   `feature/<area>` (ex.: `feature/sala-equipa`) e abre Pull Request para `main`.
2. **Commits pequenos, um por passo lógico**, com a mensagem no formato
   `[#N] area: descrição`, em que `N` é o número do cartão do Trello.
   Ex.: `[#3] registo: rejeitar domínios externos com 403`
3. **Cada cartão do Trello** tem dono e o link para o(s) commit(s)/PR correspondente(s).
4. **Só mexes no teu módulo.** Se precisares de alterar `kamailio.py`, `config.py` ou o
   módulo de outra pessoa, avisa no grupo primeiro.
5. **Constantes partilhadas** (domínio, AoR das salas, endereço do servidor de
   conferências) estão só em `src/config.py`. Não as repitas noutros ficheiros.
6. **KPIs:** qualquer módulo conta eventos com `kpi.inc("nome_do_kpi")`.
7. **Testes:** cada funcionalidade tem em `tests/` um `.md` com objetivo, passos,
   resultado esperado (código SIP) e o nome da captura `.pcap` em `tests/captures/`.
8. **Definition of Done:** uma tarefa só fecha no Trello quando tem código no `main`,
   diagramas em `docs/` e um teste com captura.
9. Comentários e documentação em português de Portugal.

## Fluxo Git básico

```bash
git checkout main && git pull
git checkout -b feature/minha-area
# ... trabalhar ...
git add <ficheiros> && git commit -m "[#N] area: o que fiz"
git push -u origin feature/minha-area
# abrir Pull Request no GitHub
```
