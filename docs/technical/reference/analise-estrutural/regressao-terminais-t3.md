# Regressão de terminais (T3)

**Data:** 2026-10-03
**Suíte:** `experiments/cuts/verify_t3_regressao_terminais.py`
**Commit:** o commit que introduz este arquivo (`git log -1 -- docs/technical/reference/regressao-terminais-t3.md`).

## Casos

| Caso | O que fixa |
|---|---|
| `StayPutIsolado` | `S=T={v}`, sem aresta. Permanência pura. OPT 0. |
| `Pura-2` | dois vértices isolados, `S=T={v1,v2}`. |
| `SharedTerminal` | estrela, sobreposição parcial no centro. OPT 1. |
| `StayPut` | `S=T={a,b}` com aresta `a–b`. Troca, não permanência isolada. OPT 0. |
| `TermRelay`, `TermRelayForced` | recarga em terminal. |
| `CaminhoABC` | caminho `a–b–c`, `S={a,b}`, `T={b,c}`, `r=1`. CE1: `C=∅` é viável. Cancelar `b` mudaria o ótimo. |
| `ST-igual-V` | `S=T=V={a,b}` no caminho de uma aresta. |
| `m0` | nenhum robô. Qualquer `C`, inclusive vazio, é viável. |

O caminho `a–b–c` está em `validacao-formulacao-base.md` (CE1) e no parecer §2.4. Não existia gabarito com esse nome; `make_CaminhoABC` o registra.

## Resultado

Cinco mecanismos em todo `C ⊆ V`: modelo base (Gurobi), `integer_oracle`, `separate_classical_fracs`, `is_valid_cut` e o validador independente.

Saída: `0 divergências`. Código de saída 0.

## A suíte pega o defeito antigo

`--sem-permanencia` troca o oráculo pela rede sem arco `v_out → v_in` e compara com o modelo base. A saída reproduz a falha em `StayPutIsolado` e em `Pura-2`, inclusive com `C={v}`: estação no vértice isolado não cria caminho de `v_out` a `v_in`. Código de saída 0 nesse modo significa que a falha foi reproduzida.

`make_StayPut` não aparece nessa falha. A aresta `a–b` permite troca e mascara a ausência do arco de permanência.

## Grafo desconexo

`ler_instancia` (`ms_utils.py`) não testa conectividade. O validador independente avisa em stderr quando o grafo é desconexo, exceto componentes que são um único vértice em `S∩T` (permanência pura, exigida por esta suíte). Não houve alteração do leitor de instâncias.
