# Changelog

## [1.0.0] — 2026-09-15

### Adicionado
- RF01: Geração de dataset sintético com sujeira proposital
- RF02: Inspeção de dados (total, colunas, ausentes, primeiros)
- RF03: Limpeza com datetime e expressões regulares
- RF04: Colunas derivadas (receita_total, mês, trimestre, ano, faixa)
- RF05: Métricas agregadas por mês, produto, categoria, região
- RF06: Segmentação de clientes (Bronze, Prata, Ouro) com lambda
- RF07: Função de ordem superior (processar_coluna)
- RF08: Exportação em CSV e JSON com releitura
- RF09: Fluxo completo via main()

### Bônus B04
- Gráfico de barras SVG (receita por mês)
- Gráfico de pizza SVG (distribuição por segmento)
- Dashboard HTML estático (sem JavaScript)

### Notas
- Escopo reduzido: apenas biblioteca padrão do Python
- Sem Pandas, NumPy, Matplotlib ou Seaborn
- Projeto avaliativo do Módulo 01 — SCTEC/SENAI T4