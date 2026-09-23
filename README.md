# SalesInsight PY — Análise de Dados de Vendas

Mini-Projeto Avaliativo do Módulo 01
**Curso:** Desenvolvimento de IA para Análise Preditiva [T4] — SCTEC/SENAI

## 🎯 Objetivo

Simular o trabalho de um Analista de Dados Júnior em uma empresa de varejo:
receber um CSV de vendas com sujeira proposital, limpar e transformar os dados,
calcular métricas de negócio e segmentar clientes.

O projeto responde a 5 perguntas de negócio:

1. Como as vendas se comportam ao longo do tempo (mês e trimestre)?
2. Quais produtos e categorias geram mais receita?
3. Quais regiões têm melhor desempenho?
4. Quais clientes são mais valiosos (Bronze / Prata / Ouro)?
5. Quantas vendas tiveram receita acima da média geral?

## 🚀 Como executar

1. Abra o notebook `M.p.Avaliativo_SCTEC.ipynb` no Google Colab.
2. Execute as células na ordem (1 → 5).
3. O notebook gera o dataset sintético, executa todo o pipeline e exporta os resultados na pasta `outputs/`.

O código utiliza **apenas a biblioteca padrão do Python** (sem Pandas, NumPy, Matplotlib ou Seaborn).


### Alternativa - Script Python puro

Também é possível rodar como script Python puro (sem Colab):

```bash
python salesinsight.py              # modo automatico
python salesinsight.py sintetico    # forca dataset sintetico
python salesinsight.py real         # forca dataset real (Superstore)
```

O arquivo `salesinsight.py` e a versao standalone do notebook,
com toda a logica em funcoes documentadas e comentadas.

## 🌐 Dashboard Publicado

O dashboard está disponível online:

**https://deegpnini.github.io/salesinsight-py/**

Ele mostra os 3 gráficos (barras, pizza e barras agrupadas), os KPIs e os principais insights.

## 📂 Estrutura do projeto

```
salesinsight-py/
├── M.p.Avaliativo_SCTEC.ipynb   ← notebook principal
├── salesinsight.py               ← script Python puro (alternativa)
├── vendas.csv                    ← dataset gerado
├── README.md
├── CHANGELOG.md
├── KANBAN.md
├── index.html
├── outputs/
│   ├── metricas_por_mes.csv
│   ├── segmentacao_clientes.csv
│   ├── estatisticas_gerais.json
│   ├── grafico_receita_mensal.svg
│   ├── grafico_segmentacao.svg
│   ├── grafico_barras_agrupadas.svg
│   └── dashboard.html
└── docs/
    ├── grafico_receita_mensal.svg
    ├── grafico_segmentacao.svg
    ├── grafico_barras_agrupadas.svg
    └── index.html
```

## 📋 Requisitos Funcionais (RF01–RF09)

| RF   | Descrição                              | Status |
|------|----------------------------------------|--------|
| RF01 | Criar / carregar dataset               | ✅     |
| RF02 | Inspecionar dados                      | ✅     |
| RF03 | Limpar dados (datetime + regex)        | ✅     |
| RF04 | Criar colunas derivadas                | ✅     |
| RF05 | Calcular métricas agregadas            | ✅     |
| RF06 | Segmentação de clientes (lambda)       | ✅     |
| RF07 | Função de ordem superior               | ✅     |
| RF08 | Exportar CSV e JSON                    | ✅     |
| RF09 | Fluxo completo (main)                  | ✅     |

## 🌟 Bônus B04 — Gráficos SVG + Dashboard HTML

Como Matplotlib e Seaborn são proibidos pelo edital, os gráficos foram gerados em **SVG puro** com Python (apenas strings) e o dashboard em **HTML estático** (sem JavaScript e sem dependências externas).

Arquivos gerados:
- `outputs/grafico_receita_mensal.svg` — receita por mês (barras)
- `outputs/grafico_segmentacao.svg` — distribuição de clientes por segmento (pizza)
- `outputs/grafico_barras_agrupadas.svg` — receita por categoria e região (barras agrupadas)
- `outputs/dashboard.html` — painel com KPIs, gráficos e tabelas

## 🛠️ Tecnologias utilizadas

- Python 3.10+
- Biblioteca padrão: `csv`, `json`, `math`, `os`, `random`, `re`, `collections`, `datetime`
- Google Colab (recomendado para o notebook)
- Python 3.10+ local (para `salesinsight.py`, sem dependencias externas)

## 🎥 Vídeo de demonstração

[Link do vídeo — a ser preenchido após a gravação]

## 📜 Declaração de Autoria

Projeto desenvolvido individualmente para fins avaliativos.
Nenhuma solução externa foi copiada; o autor é capaz de explicar integralmente o código entregue.

---
**Helyton Renato Gonçalves Ronchi**
SCTEC/SENAI — Turma T4