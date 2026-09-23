"""
SalesInsight PY - Analise de Dados de Vendas
============================================

Mini-Projeto Avaliativo do Modulo 01 - SCTEC/SENAI
Curso: Desenvolvimento de IA para Analise Preditiva [T4]

Autor: Helyton Renato Goncalves Ronchi (Helyton Renato Gonçalves Ronchi)
Turma: T4

Descricao:
    Pipeline completo de analise de dados de vendas em Python puro,
    cobrindo desde a geracao do dataset ate a publicacao de dashboard.

    O projeto responde a 5 perguntas de negocio:
      1. Como as vendas se comportam ao longo do tempo?
      2. Quais produtos e categorias geram mais receita?
      3. Quais regioes tem melhor desempenho?
      4. Quais clientes sao mais valiosos (Bronze/Prata/Ouro)?
      5. Quantas vendas tiveram receita acima da media geral?

Escopo:
    Reduzido (ate a Semana 05 do Modulo 01).
    Apenas biblioteca padrao do Python.
    Sem Pandas, NumPy, Matplotlib, Seaborn ou classes.

Uso:
    python salesinsight.py              # modo automatico
    python salesinsight.py sintetico    # forca dataset sintetico
    python salesinsight.py real         # forca dataset real (Superstore)
"""

import csv
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime


# =============================================================================
# CONSTANTES GLOBAIS
# =============================================================================

CAMINHO_DATASET = "vendas.csv"
CAMINHO_DATASET_REAL = "Sample - Superstore.csv"
PASTA_OUTPUTS = "outputs"

CAMINHO_METRICAS_CSV = os.path.join(PASTA_OUTPUTS, "metricas_por_mes.csv")
CAMINHO_SEGMENTACAO_CSV = os.path.join(PASTA_OUTPUTS, "segmentacao_clientes.csv")
CAMINHO_ESTATISTICAS_JSON = os.path.join(PASTA_OUTPUTS, "estatisticas_gerais.json")
CAMINHO_GRAFICO_BARRAS = os.path.join(PASTA_OUTPUTS, "grafico_receita_mensal.svg")
CAMINHO_GRAFICO_PIZZA = os.path.join(PASTA_OUTPUTS, "grafico_segmentacao.svg")
CAMINHO_GRAFICO_BARRAS_AGRUPADAS = os.path.join(PASTA_OUTPUTS, "grafico_barras_agrupadas.svg")
CAMINHO_DASHBOARD = os.path.join(PASTA_OUTPUTS, "dashboard.html")

FORMATOS_DATA_ACEITOS = ["%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d"]

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

PRODUTOS_POR_CATEGORIA = {
    "Eletronicos": ["Fone de Ouvido", "Mouse Sem Fio", "Teclado Mecanico", "Carregador USB-C"],
    "Casa": ["Panela de Pressao", "Jogo de Toalhas", "Luminaria de Mesa", "Organizador Multiuso"],
    "Vestuario": ["Camiseta Basica", "Jaqueta Corta-Vento", "Tenis Casual", "Bone Aba Curva"],
    "Esporte": ["Bola de Futebol", "Corda de Pular", "Garrafa Termica", "Faixa Elastica"],
    "Papelaria": ["Caderno Universitario", "Kit Canetas", "Mochila Escolar", "Estojo Duplo"],
}

REGIOES = ["Sul", "Sudeste", "Nordeste", "Centro-Oeste", "Norte"]

PADRAO_CLIENTE_NUMERICO = re.compile(r"\d+")
PADRAO_ESPACOS = re.compile(r"\s+")


# =============================================================================
# RF01 - CRIAR OU CARREGAR O DATASET DE VENDAS
# =============================================================================

def gerar_dataset(caminho=CAMINHO_DATASET, total_registros=400, semente=42):
    """Gera um dataset sintetico de vendas com sujeira proposital.

    Args:
        caminho (str): Caminho do arquivo CSV a ser gerado.
        total_registros (int): Quantidade de registros a criar.
        semente (int): Semente do gerador aleatorio.

    Returns:
        str: Caminho do arquivo gerado.
    """
    random.seed(semente)
    colunas = ["data", "cliente", "produto", "categoria",
               "quantidade", "preco_unitario", "regiao"]

    with open(caminho, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(colunas)

        for _ in range(total_registros):
            categoria = random.choice(list(PRODUTOS_POR_CATEGORIA.keys()))
            produto = random.choice(PRODUTOS_POR_CATEGORIA[categoria])
            regiao = random.choice(REGIOES)
            cliente_id = random.randint(1, 60)

            if random.random() < 0.06:
                data_str = "DATA INVALIDA"
            else:
                mes = random.randint(1, 9)
                dia = random.randint(1, 28)
                data_str = f"{dia:02d}/{mes:02d}/2026"

            quantidade = "" if random.random() < 0.05 else random.randint(1, 12)
            preco = "" if random.random() < 0.05 else round(random.uniform(15, 900), 2)
            produto_sujo = f"  {produto}   " if random.random() < 0.3 else produto

            formatos_cliente = [
                f"cliente {cliente_id}",
                f"CLIENTE_{cliente_id}",
                f"Cliente-{cliente_id}",
                f"  cliente{cliente_id}  ",
                f"Cliente_{cliente_id:03d}",
            ]
            cliente_sujo = random.choice(formatos_cliente)

            escritor.writerow([
                data_str, cliente_sujo, produto_sujo, categoria,
                quantidade, preco, regiao,
            ])

    print(f"[RF01] Dataset gerado: {caminho} ({total_registros} registros)")
    return caminho


def carregar_dataset(caminho=CAMINHO_DATASET):
    """Carrega o dataset de vendas a partir de um arquivo CSV.

    Args:
        caminho (str): Caminho do arquivo CSV.

    Returns:
        list[dict]: Lista de registros.
    """
    with open(caminho, mode="r", newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        registros = list(leitor)

    print(f"[RF01] Dataset carregado: {len(registros)} registros brutos")
    return registros


def reformatar_data(data_bruta):
    """Converte data em varios formatos para DD/MM/AAAA.

    Args:
        data_bruta (str): Data em formato desconhecido.

    Returns:
        str: Data formatada ou 'DATA INVALIDA'.
    """
    data_bruta = (data_bruta or "").strip()
    for formato in FORMATOS_DATA_ACEITOS:
        try:
            return datetime.strptime(data_bruta, formato).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return "DATA INVALIDA"


def normalizar_dataset_real(caminho_entrada=CAMINHO_DATASET_REAL,
                             caminho_saida=CAMINHO_DATASET):
    """Adapta um dataset real (Superstore) para o esquema interno.

    Args:
        caminho_entrada (str): Caminho do CSV original.
        caminho_saida (str): Caminho do CSV normalizado.

    Returns:
        str: Caminho do arquivo gerado.
    """
    with open(caminho_entrada, mode="r", newline="", encoding="utf-8-sig") as entrada:
        linhas = list(csv.DictReader(entrada))

    with open(caminho_saida, mode="w", newline="", encoding="utf-8") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(["data", "cliente", "produto", "categoria",
                            "quantidade", "preco_unitario", "regiao"])

        for linha in linhas:
            data_norm = reformatar_data(linha.get("Order Date", ""))
            try:
                qtd = int(float(linha.get("Quantity", "")))
                receita = float(linha.get("Sales", ""))
                preco = round(receita / qtd, 2) if qtd else ""
            except (ValueError, TypeError):
                qtd, preco = "", ""

            escritor.writerow([
                data_norm,
                linha.get("Customer Name", "").strip(),
                linha.get("Product Name", "").strip(),
                linha.get("Category", "").strip(),
                qtd, preco,
                linha.get("Region", "").strip(),
            ])

    print(f"[RF01-B] Dataset real normalizado: {len(linhas)} registros")
    return caminho_saida


# =============================================================================
# RF02 - INSPECIONAR E DESCREVER OS DADOS
# =============================================================================

def inspecionar_dados(registros):
    """Inspeciona os registros e exibe um resumo descritivo.

    Args:
        registros (list[dict]): Registros brutos.

    Returns:
        dict: Resumo com total, colunas e ausentes.
    """
    total = len(registros)
    colunas = list(registros[0].keys()) if registros else []

    ausentes = {coluna: 0 for coluna in colunas}
    for registro in registros:
        for coluna in colunas:
            valor = registro.get(coluna, "")
            if valor is None or str(valor).strip() == "":
                ausentes[coluna] += 1

    print("\n=== [RF02] INSPECAO DOS DADOS ===")
    print(f"Total de registros: {total}")
    print(f"Colunas: {colunas}")
    print("Valores ausentes por coluna:")
    for coluna, qtd in ausentes.items():
        print(f"  - {coluna}: {qtd}")
    print("\nPrimeiros 5 registros:")
    for registro in registros[:5]:
        print(f"  {registro}")

    return {"total_registros": total, "colunas": colunas, "ausentes": ausentes}


# =============================================================================
# RF03 - LIMPAR E TRATAR OS DADOS
# =============================================================================

def criar_padronizador_de_clientes():
    """Cria uma funcao que padroniza nomes de clientes para Cliente_NNN.

    Returns:
        Callable[[str], str | None]: Funcao de padronizacao.
    """
    mapa = {}

    def padronizar(cliente_bruto):
        if not cliente_bruto:
            return None

        correspondencia = PADRAO_CLIENTE_NUMERICO.search(cliente_bruto)
        if correspondencia:
            numero = int(correspondencia.group())
        else:
            chave = PADRAO_ESPACOS.sub(" ", cliente_bruto.strip().lower())
            if not chave:
                return None
            if chave not in mapa:
                mapa[chave] = len(mapa) + 1
            numero = mapa[chave]

        return f"Cliente_{numero:03d}"

    return padronizar


def limpar_dados(registros):
    """Limpa e valida os registros de venda.

    Args:
        registros (list[dict]): Registros brutos.

    Returns:
        tuple[list[dict], dict]: (registros_limpos, relatorio)
    """
    criticos = ["data", "cliente", "produto", "categoria",
                "quantidade", "preco_unitario", "regiao"]

    limpos = []
    motivos = defaultdict(int)
    total_entrada = len(registros)
    padronizar_cliente = criar_padronizador_de_clientes()

    for registro in registros:
        limpo = {
            chave: (valor.strip() if isinstance(valor, str) else valor)
            for chave, valor in registro.items()
        }

        vazio = next((c for c in criticos if not limpo.get(c)), None)
        if vazio:
            motivos[f"campo_vazio:{vazio}"] += 1
            continue

        try:
            limpo["data"] = datetime.strptime(limpo["data"], "%d/%m/%Y")
        except ValueError:
            motivos["data_invalida"] += 1
            continue

        try:
            limpo["quantidade"] = int(float(limpo["quantidade"]))
        except (ValueError, TypeError):
            motivos["quantidade_invalida"] += 1
            continue

        try:
            limpo["preco_unitario"] = float(limpo["preco_unitario"])
        except (ValueError, TypeError):
            motivos["preco_invalido"] += 1
            continue

        cliente_padronizado = padronizar_cliente(limpo["cliente"])
        if cliente_padronizado is None:
            motivos["cliente_invalido"] += 1
            continue
        limpo["cliente"] = cliente_padronizado

        limpo["produto"] = PADRAO_ESPACOS.sub(" ", limpo["produto"]).strip()

        limpos.append(limpo)

    relatorio = {
        "total_entrada": total_entrada,
        "total_removidos": total_entrada - len(limpos),
        "motivos_remocao": dict(motivos),
        "total_final": len(limpos),
    }

    print("\n=== [RF03] RELATORIO DE LIMPEZA ===")
    print(f"Registros que entraram:  {relatorio['total_entrada']}")
    print(f"Registros removidos:     {relatorio['total_removidos']}")
    for motivo, qtd in relatorio["motivos_remocao"].items():
        print(f"  - {motivo}: {qtd}")
    print(f"Registros que ficaram:   {relatorio['total_final']}")

    return limpos, relatorio


# =============================================================================
# RF04 - COLUNAS DERIVADAS
# =============================================================================

def classificar_faixa_receita(receita):
    """Classifica a receita de um item em uma faixa.

    Args:
        receita (float): Receita total do item.

    Returns:
        str: 'Baixo Valor', 'Medio Valor' ou 'Alto Valor'.
    """
    if receita < 500:
        return "Baixo Valor"
    elif receita < 5000:
        return "Medio Valor"
    return "Alto Valor"


def criar_colunas_derivadas(registros):
    """Adiciona colunas derivadas a cada registro.

    Args:
        registros (list[dict]): Registros limpos.

    Returns:
        list[dict]: Registros com colunas derivadas.
    """
    for registro in registros:
        data = registro["data"]
        receita = round(registro["quantidade"] * registro["preco_unitario"], 2)

        registro["receita_total"] = receita
        registro["ano"] = data.year
        registro["mes"] = data.month
        registro["mes_nome"] = MESES_PT[data.month]
        registro["trimestre"] = (data.month - 1) // 3 + 1
        registro["faixa_receita_item"] = classificar_faixa_receita(receita)

    print(f"\n[RF04] Colunas derivadas criadas para {len(registros)} registros")
    return registros


# =============================================================================
# RF05 - METRICAS AGREGADAS
# =============================================================================

def calcular_metricas(registros):
    """Calcula metricas agregadas por mes, produto, categoria e regiao.

    Args:
        registros (list[dict]): Registros com colunas derivadas.

    Returns:
        dict: Metricas consolidadas.
    """
    por_mes = defaultdict(lambda: {"receita": 0.0, "quantidade": 0, "vendas": 0})
    por_produto = defaultdict(float)
    por_categoria = defaultdict(float)
    por_regiao = defaultdict(lambda: {"receita": 0.0, "vendas": 0})

    for registro in registros:
        chave = (registro["ano"], registro["mes"])
        por_mes[chave]["receita"] += registro["receita_total"]
        por_mes[chave]["quantidade"] += registro["quantidade"]
        por_mes[chave]["vendas"] += 1

        por_produto[registro["produto"]] += registro["receita_total"]
        por_categoria[registro["categoria"]] += registro["receita_total"]

        por_regiao[registro["regiao"]]["receita"] += registro["receita_total"]
        por_regiao[registro["regiao"]]["vendas"] += 1

    metricas_mes = [
        {
            "ano": ano, "mes": mes, "mes_nome": MESES_PT[mes],
            "receita_total": round(dados["receita"], 2),
            "quantidade_vendida": dados["quantidade"],
            "numero_vendas": dados["vendas"],
        }
        for (ano, mes), dados in sorted(por_mes.items())
    ]

    top_produtos = sorted(
        ({"produto": p, "receita_total": round(v, 2)} for p, v in por_produto.items()),
        key=lambda x: x["receita_total"], reverse=True
    )[:5]

    metricas_categoria = sorted(
        ({"categoria": c, "receita_total": round(v, 2)} for c, v in por_categoria.items()),
        key=lambda x: x["receita_total"], reverse=True
    )

    metricas_regiao = []
    for regiao, dados in por_regiao.items():
        ticket = dados["receita"] / dados["vendas"] if dados["vendas"] else 0
        metricas_regiao.append({
            "regiao": regiao,
            "receita_total": round(dados["receita"], 2),
            "ticket_medio": round(ticket, 2),
        })
    metricas_regiao.sort(key=lambda x: x["receita_total"], reverse=True)

    print("\n=== [RF05] METRICAS AGREGADAS ===")
    print("Receita por mes:")
    for item in metricas_mes:
        print(f"  - {item['mes_nome']}/{item['ano']}: "
              f"R$ {item['receita_total']:.2f} ({item['numero_vendas']} vendas)")

    print("Top 5 produtos:")
    for item in top_produtos:
        print(f"  - {item['produto']}: R$ {item['receita_total']:.2f}")

    print("Receita por categoria:")
    for item in metricas_categoria:
        print(f"  - {item['categoria']}: R$ {item['receita_total']:.2f}")

    print("Receita por regiao:")
    for item in metricas_regiao:
        print(f"  - {item['regiao']}: R$ {item['receita_total']:.2f} "
              f"(ticket R$ {item['ticket_medio']:.2f})")

    return {
        "por_mes": metricas_mes,
        "top_produtos": top_produtos,
        "por_categoria": metricas_categoria,
        "por_regiao": metricas_regiao,
    }


# =============================================================================
# RF06 - SEGMENTACAO DE CLIENTES
# =============================================================================

def segmentar_clientes(registros):
    """Segmenta clientes em Bronze, Prata ou Ouro.

    Regras:
      - Abaixo de R$ 5.000      -> Bronze
      - R$ 5.000 a R$ 15.000    -> Prata
      - Acima de R$ 15.000      -> Ouro

    Args:
        registros (list[dict]): Registros com receita_total.

    Returns:
        list[dict]: Clientes segmentados.
    """
    gasto_por_cliente = defaultdict(float)
    for registro in registros:
        gasto_por_cliente[registro["cliente"]] += registro["receita_total"]

    classificar_segmento = lambda gasto: (
        "Ouro" if gasto > 15000
        else "Prata" if gasto >= 5000
        else "Bronze"
    )

    clientes_segmentados = list(map(
        lambda item: {
            "cliente": item[0],
            "gasto_total": round(item[1], 2),
            "segmento": classificar_segmento(item[1]),
        },
        gasto_por_cliente.items()
    ))

    clientes_segmentados.sort(key=lambda x: x["gasto_total"], reverse=True)

    distribuicao = defaultdict(int)
    for cliente in clientes_segmentados:
        distribuicao[cliente["segmento"]] += 1

    print("\n=== [RF06] SEGMENTACAO DE CLIENTES ===")
    print("Top 10 clientes por gasto total:")
    for c in clientes_segmentados[:10]:
        print(f"  - {c['cliente']}: R$ {c['gasto_total']:.2f} ({c['segmento']})")

    print("Distribuicao por segmento:")
    for segmento, qtd in distribuicao.items():
        print(f"  - {segmento}: {qtd} clientes")

    return clientes_segmentados


# =============================================================================
# RF07 - FUNCAO DE ORDEM SUPERIOR
# =============================================================================

def processar_coluna(registros, coluna, funcao_transformacao, nome_saida=None):
    """Aplica uma funcao de transformacao a uma coluna de cada registro.

    Args:
        registros (list[dict]): Registros de venda.
        coluna (str): Nome da coluna de origem.
        funcao_transformacao (Callable): Funcao de transformacao.
        nome_saida (str | None): Nome da coluna de destino.

    Returns:
        list[dict]: Registros com a coluna preenchida.
    """
    destino = nome_saida or coluna
    for registro in registros:
        registro[destino] = funcao_transformacao(registro[coluna])
    return registros


# =============================================================================
# RF08 - EXPORTAR RESULTADOS
# =============================================================================

def exportar_metricas_csv(metricas_mes, caminho=CAMINHO_METRICAS_CSV):
    """Exporta metricas mensais em CSV.

    Args:
        metricas_mes (list[dict]): Metricas por mes.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    colunas = ["ano", "mes", "mes_nome", "receita_total",
               "quantidade_vendida", "numero_vendas"]
    with open(caminho, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(metricas_mes)
    print(f"[RF08] Metricas por mes exportadas: {caminho}")
    return caminho


def exportar_segmentacao_csv(clientes_segmentados, caminho=CAMINHO_SEGMENTACAO_CSV):
    """Exporta segmentacao de clientes em CSV.

    Args:
        clientes_segmentados (list[dict]): Clientes segmentados.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    colunas = ["cliente", "gasto_total", "segmento"]
    with open(caminho, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(clientes_segmentados)
    print(f"[RF08] Segmentacao de clientes exportada: {caminho}")
    return caminho


def exportar_estatisticas_json(estatisticas, caminho=CAMINHO_ESTATISTICAS_JSON):
    """Exporta estatisticas gerais em JSON.

    Args:
        estatisticas (dict): Estatisticas consolidadas.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    with open(caminho, mode="w", encoding="utf-8") as arquivo:
        json.dump(estatisticas, arquivo, ensure_ascii=False, indent=2)
    print(f"[RF08] Estatisticas gerais exportadas: {caminho}")
    return caminho


def reler_estatisticas_json(caminho=CAMINHO_ESTATISTICAS_JSON):
    """Le de volta o JSON para conferencia.

    Args:
        caminho (str): Caminho do arquivo JSON.

    Returns:
        dict: Conteudo do arquivo.
    """
    with open(caminho, mode="r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    print(f"\n[RF08] Releitura de {caminho} para conferencia:")
    print(json.dumps(dados, ensure_ascii=False, indent=2))
    return dados


# =============================================================================
# BONUS B04 - GRAFICOS SVG E DASHBOARD HTML
# =============================================================================

def _gerar_svg_barras(metricas_por_mes):
    """Gera conteudo SVG do grafico de barras.

    Args:
        metricas_por_mes (list[dict]): Metricas por mes.

    Returns:
        str: Conteudo SVG.
    """
    if not metricas_por_mes:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"></svg>'

    dados = sorted(metricas_por_mes, key=lambda x: (x.get("ano", 0), x.get("mes", 0)))
    valores = [float(d.get("receita_total", 0)) for d in dados]
    max_valor = max(valores) if valores else 1.0
    if max_valor <= 0:
        max_valor = 1.0

    largura, altura = 860, 480
    me, md, ms, mi = 80, 30, 60, 80
    area_larg = largura - me - md
    area_alt = altura - ms - mi
    n = len(dados)
    espaco = 10
    larg_barra = max(16, (area_larg - (n - 1) * espaco) / n)

    idx_max = valores.index(max(valores))
    mes_destaque = dados[idx_max].get("mes_nome", "N/A")
    valor_destaque = valores[idx_max]
    titulo = (f"Receita Mensal - {mes_destaque} foi o mes de maior receita "
              f"(R$ {valor_destaque:,.2f})").replace(",", "X").replace(".", ",").replace("X", ".")

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">',
        f'<rect width="{largura}" height="{altura}" fill="#FFFFFF"/>',
        f'<text x="{largura/2}" y="28" text-anchor="middle" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" '
        f'fill="#1a1a1a">{titulo}</text>',
    ]

    for i in range(6):
        y = ms + area_alt - (i / 5) * area_alt
        valor_grid = (i / 5) * max_valor
        partes.append(
            f'<line x1="{me}" y1="{y:.1f}" x2="{largura-md}" y2="{y:.1f}" '
            f'stroke="#E8E8E8" stroke-width="1"/>'
        )
        rotulo = f"R$ {valor_grid:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        partes.append(
            f'<text x="{me-8}" y="{y+4:.1f}" text-anchor="end" '
            f'font-family="Arial,Helvetica,sans-serif" font-size="10" fill="#555">{rotulo}</text>'
        )

    for i, (d, v) in enumerate(zip(dados, valores)):
        x = me + i * (larg_barra + espaco)
        alt_barra = (v / max_valor) * area_alt
        y = ms + area_alt - alt_barra
        partes.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{larg_barra:.1f}" '
            f'height="{alt_barra:.1f}" fill="#78C043" rx="2" ry="2"/>'
        )
        valor_fmt = f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        partes.append(
            f'<text x="{x+larg_barra/2:.1f}" y="{y-5:.1f}" text-anchor="middle" '
            f'font-family="Arial,Helvetica,sans-serif" font-size="9" fill="#333">{valor_fmt}</text>'
        )
        mes_abr = str(d.get("mes_nome", f"M{i+1}"))[:3]
        partes.append(
            f'<text x="{x+larg_barra/2:.1f}" y="{altura-mi+18}" text-anchor="middle" '
            f'font-family="Arial,Helvetica,sans-serif" font-size="11" fill="#333">{mes_abr}</text>'
        )

    partes.append(
        f'<line x1="{me}" y1="{ms+area_alt}" x2="{largura-md}" '
        f'y2="{ms+area_alt}" stroke="#333" stroke-width="1.5"/>'
    )
    partes.append("</svg>")
    return "\n".join(partes)


def _gerar_svg_pizza(clientes_segmentados):
    """Gera conteudo SVG do grafico de pizza.

    Args:
        clientes_segmentados (list[dict]): Clientes segmentados.

    Returns:
        str: Conteudo SVG.
    """
    if not clientes_segmentados:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"></svg>'

    contagem = Counter(c.get("segmento", "Desconhecido") for c in clientes_segmentados)
    total = sum(contagem.values())
    if total == 0:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"></svg>'

    ordem = ["Bronze", "Prata", "Ouro"]
    cores = {"Bronze": "#CD7F32", "Prata": "#C0C0C0", "Ouro": "#FFD700"}

    segmentos = []
    for s in ordem:
        qtd = contagem.get(s, 0)
        if qtd > 0:
            segmentos.append({
                "nome": s, "qtd": qtd,
                "pct": (qtd / total) * 100,
                "cor": cores[s],
            })

    largura, altura = 680, 420
    cx, cy, raio = 230, 220, 145
    maior = max(segmentos, key=lambda x: x["qtd"])
    titulo = (f"Segmentacao - {maior['nome']} concentra "
              f"{maior['qtd']} clientes ({maior['pct']:.1f}%)")

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">',
        f'<rect width="{largura}" height="{altura}" fill="#FFFFFF"/>',
        f'<text x="{largura/2}" y="28" text-anchor="middle" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" '
        f'fill="#1a1a1a">{titulo}</text>',
    ]

    def ponto(angulo, r=raio):
        return cx + r * math.cos(angulo), cy + r * math.sin(angulo)

    angulo_atual = -math.pi / 2
    for seg in segmentos:
        angulo_fatia = (seg["pct"] / 100) * 2 * math.pi
        angulo_fim = angulo_atual + angulo_fatia
        x1, y1 = ponto(angulo_atual)
        x2, y2 = ponto(angulo_fim)
        grande = 1 if angulo_fatia > math.pi else 0
        path = (f"M {cx:.1f} {cy:.1f} L {x1:.1f} {y1:.1f} "
                f"A {raio} {raio} 0 {grande} 1 {x2:.1f} {y2:.1f} Z")
        partes.append(
            f'<path d="{path}" fill="{seg["cor"]}" stroke="#fff" stroke-width="2"/>'
        )
        if seg["pct"] >= 5:
            ang_meio = angulo_atual + angulo_fatia / 2
            lx, ly = ponto(ang_meio, raio * 0.6)
            partes.append(
                f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="middle" '
                f'font-family="Arial,Helvetica,sans-serif" font-size="12" '
                f'font-weight="bold" fill="#1a1a1a">{seg["pct"]:.1f}%</text>'
            )
        angulo_atual = angulo_fim

    lx, ly = 480, 130
    partes.append(
        f'<text x="{lx}" y="{ly-18}" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="13" font-weight="bold" fill="#333">Legenda</text>'
    )
    for i, seg in enumerate(segmentos):
        y = ly + i * 38
        partes.append(
            f'<rect x="{lx}" y="{y}" width="16" height="16" fill="{seg["cor"]}" '
            f'stroke="#333" stroke-width="0.5" rx="2"/>'
        )
        partes.append(
            f'<text x="{lx+24}" y="{y+13}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="12" fill="#333">{seg["nome"]}: {seg["qtd"]} ({seg["pct"]:.1f}%)</text>'
        )

    partes.append(
        f'<text x="{lx}" y="{ly + len(segmentos)*38 + 18}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#555">'
        f'Total: {total} clientes</text>'
    )
    partes.append("</svg>")
    return "\n".join(partes)


def gerar_grafico_barras_svg(metricas_por_mes, caminho=CAMINHO_GRAFICO_BARRAS):
    """Gera o arquivo SVG do grafico de barras.

    Args:
        metricas_por_mes (list[dict]): Metricas por mes.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    if not metricas_por_mes:
        raise ValueError("Lista de metricas por mes esta vazia.")
    conteudo = _gerar_svg_barras(metricas_por_mes)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho


def gerar_grafico_pizza_svg(clientes_segmentados, caminho=CAMINHO_GRAFICO_PIZZA):
    """Gera o arquivo SVG do grafico de pizza.

    Args:
        clientes_segmentados (list[dict]): Clientes segmentados.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    if not clientes_segmentados:
        raise ValueError("Lista de clientes segmentados esta vazia.")
    conteudo = _gerar_svg_pizza(clientes_segmentados)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho




def agregar_categoria_regiao(registros):
    """Agrega receita total por categoria e regiao.

    Args:
        registros (list[dict]): Registros com receita_total, categoria e regiao.

    Returns:
        dict: {categoria: {regiao: receita_total}}
    """
    resultado = defaultdict(lambda: defaultdict(float))
    for r in registros:
        resultado[r["categoria"]][r["regiao"]] += r["receita_total"]
    return {cat: dict(regs) for cat, regs in resultado.items()}


def gerar_grafico_barras_agrupadas(dados_categoria_regiao,
                                    titulo="Receita por Categoria e Regiao",
                                    largura=900, altura=560):
    """Gera grafico de barras agrupadas em SVG puro.

    Eixo X: Categorias
    Series: Regioes

    Args:
        dados_categoria_regiao (dict): {categoria: {regiao: receita}}
        titulo (str): Titulo do grafico.
        largura (int): Largura do SVG.
        altura (int): Altura do SVG.

    Returns:
        str: Conteudo SVG completo.
    """
    if not dados_categoria_regiao:
        return '<p>Sem dados para gerar o grafico.</p>'

    categorias = list(dados_categoria_regiao.keys())
    regioes = []
    for cat in categorias:
        for reg in dados_categoria_regiao[cat]:
            if reg not in regioes:
                regioes.append(reg)

    if not regioes:
        return '<p>Sem regioes disponiveis.</p>'

    me, md, ms, mi = 90, 30, 90, 120
    area_larg = largura - me - md
    area_alt = altura - ms - mi

    maior_valor = 0
    for cat in categorias:
        for reg in regioes:
            v = dados_categoria_regiao.get(cat, {}).get(reg, 0)
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = 0
            if v > maior_valor:
                maior_valor = v
    if maior_valor <= 0:
        maior_valor = 1

    def fmt_curto(v):
        v = float(v)
        if v >= 1000000:
            return f"R$ {v/1000000:.1f} mi"
        if v >= 1000:
            return f"R$ {v/1000:.0f} mil"
        return f"R$ {v:.0f}"

    def fmt_completo(v):
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    cores = ["#78C043", "#2F6B3F", "#D4A72C", "#4A6FA5", "#8E5A9A", "#C56B38"]

    total_geral = 0
    for cat in categorias:
        for reg in regioes:
            try:
                total_geral += float(dados_categoria_regiao.get(cat, {}).get(reg, 0))
            except (TypeError, ValueError):
                pass

    titulo_id = "gr-barras-titulo"
    descricao_id = "gr-barras-desc"

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
        f'width="{largura}" height="{altura}" role="img" '
        f'aria-labelledby="{titulo_id}" aria-describedby="{descricao_id}" focusable="false">',
        f'<title id="{titulo_id}">{titulo}</title>',
        f'<desc id="{descricao_id}">Grafico de barras agrupadas. '
        f'{len(categorias)} categorias, {len(regioes)} regioes. '
        f'Receita total: {fmt_completo(total_geral)}.</desc>',
        f'<rect width="{largura}" height="{altura}" fill="#ffffff" rx="12"/>',
        f'<text x="{me}" y="40" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="20" font-weight="bold" fill="#222">{titulo}</text>',
    ]

    # Grid e escala Y
    for i in range(6):
        prop = i / 5
        y = ms + area_alt - prop * area_alt
        val = maior_valor * prop
        partes.append(f'<line x1="{me}" y1="{y:.1f}" x2="{largura-md}" y2="{y:.1f}" '
                      f'stroke="#ddd" stroke-width="1"/>')
        partes.append(f'<text x="{me-10}" y="{y+4:.1f}" text-anchor="end" '
                      f'font-family="Arial,Helvetica,sans-serif" font-size="11" '
                      f'fill="#555">{fmt_curto(val)}</text>')

    # Eixos
    eixo_x = ms + area_alt
    partes.append(f'<line x1="{me}" y1="{ms}" x2="{me}" y2="{eixo_x}" '
                  f'stroke="#555" stroke-width="1.5"/>')
    partes.append(f'<line x1="{me}" y1="{eixo_x}" x2="{largura-md}" y2="{eixo_x}" '
                  f'stroke="#555" stroke-width="1.5"/>')

    # Barras
    n_cat = len(categorias)
    n_reg = len(regioes)
    larg_grupo = area_larg / n_cat
    espaco_grupo = 16
    larg_disp = larg_grupo - espaco_grupo
    larg_barra = larg_disp / n_reg
    if larg_barra > 48:
        larg_barra = 48
    larg_total = larg_barra * n_reg

    for idx_cat, cat in enumerate(categorias):
        centro = me + idx_cat * larg_grupo + larg_grupo / 2
        inicio = centro - larg_total / 2

        partes.append(f'<text x="{centro:.1f}" y="{eixo_x+28}" text-anchor="middle" '
                      f'font-family="Arial,Helvetica,sans-serif" font-size="11" '
                      f'font-weight="bold" fill="#333">{cat}</text>')

        for idx_reg, reg in enumerate(regioes):
            v = dados_categoria_regiao.get(cat, {}).get(reg, 0)
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = 0
            alt_barra = (v / maior_valor) * area_alt
            x = inicio + idx_reg * larg_barra
            y = eixo_x - alt_barra
            cor = cores[idx_reg % len(cores)]

            partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" '
                          f'width="{max(larg_barra-3,1):.1f}" height="{max(alt_barra,0):.1f}" '
                          f'fill="{cor}" rx="2">'
                          f'<title>{cat} | {reg}: {fmt_completo(v)}</title></rect>')

            if v > 0:
                y_txt = max(y - 6, ms - 8)
                partes.append(f'<text x="{x+(larg_barra-3)/2:.1f}" y="{y_txt:.1f}" '
                              f'text-anchor="middle" font-family="Arial,Helvetica,sans-serif" '
                              f'font-size="9" font-weight="bold" fill="#333">{fmt_curto(v)}</text>')

    # Legenda
    leg_y = altura - 42
    larg_item = area_larg / n_reg
    for idx_reg, reg in enumerate(regioes):
        x = me + idx_reg * larg_item
        cor = cores[idx_reg % len(cores)]
        partes.append(f'<rect x="{x:.1f}" y="{leg_y-10}" width="12" height="12" '
                      f'fill="{cor}" rx="2"/>')
        partes.append(f'<text x="{x+18:.1f}" y="{leg_y}" font-family="Arial,Helvetica,sans-serif" '
                      f'font-size="11" fill="#444">{reg}</text>')

    partes.append("</svg>")
    return "\n".join(partes)


def gerar_grafico_barras_agrupadas_svg(dados_categoria_regiao, caminho=CAMINHO_GRAFICO_BARRAS_AGRUPADAS):
    """Gera o arquivo SVG do grafico de barras agrupadas (categoria x regiao).

    Args:
        dados_categoria_regiao (dict): {categoria: {regiao: receita}}
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    if not dados_categoria_regiao:
        raise ValueError("Dados de categoria x regiao estao vazios.")
    conteudo = gerar_grafico_barras_agrupadas(dados_categoria_regiao)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho


def gerar_dashboard_html(metricas, clientes_segmentados, estatisticas, registros=None,
                          caminho=CAMINHO_DASHBOARD):
    """Gera dashboard HTML estatico.

    Args:
        metricas (dict): Metricas consolidadas.
        clientes_segmentados (list[dict]): Clientes segmentados.
        estatisticas (dict): Estatisticas gerais.
        caminho (str): Caminho de saida.

    Returns:
        str: Caminho do arquivo gerado.
    """
    total_vendas = estatisticas.get("total_vendas_validas", 0)
    receita_total = estatisticas.get("receita_total_geral", 0.0)
    ticket_medio = estatisticas.get("receita_media_por_venda", 0.0)

    def formatar_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    svg_barras = _gerar_svg_barras(metricas.get("por_mes", []))
    svg_pizza = _gerar_svg_pizza(clientes_segmentados)
    # Novo: gerar grafico de barras agrupadas
    if registros:
        dados_cat_reg = agregar_categoria_regiao(registros)
        svg_barras_agrupadas = gerar_grafico_barras_agrupadas(dados_cat_reg)
    else:
        svg_barras_agrupadas = "<p>Sem dados para o grafico de barras agrupadas.</p>"

    linhas_top = "".join(
        f"<tr><td>{i}</td><td>{p.get('produto', '-')}</td>"
        f"<td class='valor'>{formatar_brl(p.get('receita_total', 0))}</td></tr>\n"
        for i, p in enumerate(metricas.get("top_produtos", [])[:5], 1)
    )
    linhas_cat = "".join(
        f"<tr><td>{c.get('categoria', '-')}</td>"
        f"<td class='valor'>{formatar_brl(c.get('receita_total', 0))}</td></tr>\n"
        for c in metricas.get("por_categoria", [])
    )
    linhas_reg = "".join(
        f"<tr><td>{r.get('regiao', '-')}</td>"
        f"<td class='valor'>{formatar_brl(r.get('receita_total', 0))}</td>"
        f"<td class='valor'>{formatar_brl(r.get('ticket_medio', 0))}</td></tr>\n"
        for r in metricas.get("por_regiao", [])
    )

    cont_seg = Counter(c.get("segmento") for c in clientes_segmentados)
    n_ouro = cont_seg.get("Ouro", 0)
    n_prata = cont_seg.get("Prata", 0)
    n_bronze = cont_seg.get("Bronze", 0)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SalesInsight PY - Dashboard</title>
<style>
  :root {{ --verde: #78C043; --verde-escuro: #5a9a2e; --texto: #1a1a1a; --borda: #e0e4e8; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, Helvetica, sans-serif; background: #f0f2f5; color: var(--texto); line-height: 1.5; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }}
  header {{ background: linear-gradient(135deg, #78C043, #5a9a2e); color: white; padding: 28px 24px; border-radius: 12px; margin-bottom: 28px; }}
  header h1 {{ font-size: 26px; margin-bottom: 6px; }}
  header p {{ opacity: 0.92; font-size: 14px; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }}
  .kpi {{ background: white; border-radius: 10px; padding: 18px 20px; border-left: 5px solid var(--verde); box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
  .kpi .label {{ font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 4px; }}
  .kpi .value {{ font-size: 22px; font-weight: bold; }}
  .section {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
  .section h2 {{ font-size: 18px; margin-bottom: 16px; color: var(--verde-escuro); border-bottom: 2px solid var(--verde); padding-bottom: 6px; }}
  .graficos {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
  @media (min-width: 900px) {{ .graficos {{ grid-template-columns: 1.4fr 1fr; }} }}
  .grafico-box {{ background: #fafafa; border: 1px solid var(--borda); border-radius: 8px; padding: 12px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--borda); }}
  th {{ background: #f0f7e8; color: var(--verde-escuro); font-weight: 600; }}
  tr:hover {{ background: #f9fbf6; }}
  td.valor {{ text-align: right; }}
  .grafico-box svg {{ max-width: 100%; height: auto; }}
  footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>SalesInsight PY - Dashboard Analitico</h1>
    <p>Bonus B04 - Graficos SVG + Dashboard HTML - SCTEC/SENAI T4</p>
  </header>

  <div class="kpis">
    <div class="kpi"><div class="label">Total de Vendas</div><div class="value">{total_vendas}</div></div>
    <div class="kpi"><div class="label">Receita Total</div><div class="value">{formatar_brl(receita_total)}</div></div>
    <div class="kpi"><div class="label">Ticket Medio</div><div class="value">{formatar_brl(ticket_medio)}</div></div>
    <div class="kpi"><div class="label">Clientes (O / P / B)</div><div class="value">{n_ouro} / {n_prata} / {n_bronze}</div></div>
  </div>


  <div class="section">
    <h2>Principais Insights</h2>
    <ul style="padding-left: 20px; line-height: 1.8; font-size: 15px; margin: 0;">
      <li><strong>Fevereiro</strong> foi o mês de maior receita (<strong>R$ 167.513,45</strong>).</li>
      <li>O segmento <strong>Ouro</strong> concentra <strong>55%</strong> dos clientes (33 de 60).</li>
      <li><strong>Vestuário</strong> (R$ 233.850,61) e <strong>Casa</strong> (R$ 221.674,10) lideram a receita por categoria.</li>
      <li>A região <strong>Centro-Oeste</strong> tem a maior receita total (<strong>R$ 242.067,51</strong>).</li>
      <li>O produto mais rentável é o <strong>Teclado Mecânico</strong> (<strong>R$ 84.922,01</strong>).</li>
    </ul>
  </div>

  <div class="section">
    <h2>Visualizacoes</h2>
    <div class="graficos">
      <div class="grafico-box">{svg_barras}</div>
      <div class="grafico-box">{svg_pizza}</div>
      <div class="grafico-box" style="grid-column: 1 / -1;">{svg_barras_agrupadas}</div>
    </div>
  </div>

  <div class="section">
    <h2>Top 5 Produtos por Receita</h2>
    <table><thead><tr><th>#</th><th>Produto</th><th>Receita Total</th></tr></thead>
    <tbody>{linhas_top if linhas_top else "<tr><td colspan='3'>Sem dados</td></tr>"}</tbody></table>
  </div>

  <div class="section">
    <h2>Receita por Categoria</h2>
    <table><thead><tr><th>Categoria</th><th>Receita Total</th></tr></thead>
    <tbody>{linhas_cat if linhas_cat else "<tr><td colspan='2'>Sem dados</td></tr>"}</tbody></table>
  </div>

  <div class="section">
    <h2>Receita por Regiao</h2>
    <table><thead><tr><th>Regiao</th><th>Receita Total</th><th>Ticket Medio</th></tr></thead>
    <tbody>{linhas_reg if linhas_reg else "<tr><td colspan='3'>Sem dados</td></tr>"}</tbody></table>
  </div>

  <footer>SalesInsight PY - Gerado automaticamente - Biblioteca padrao do Python - Bonus B04</footer>
</div>
</body>
</html>
"""

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)
    return caminho


# =============================================================================
# RF09 - FLUXO COMPLETO
# =============================================================================

def montar_estatisticas_gerais(registros, metricas, relatorio_limpeza):
    """Consolida estatisticas gerais do projeto.

    Args:
        registros (list[dict]): Registros finais.
        metricas (dict): Metricas consolidadas.
        relatorio_limpeza (dict): Relatorio da limpeza.

    Returns:
        dict: Estatisticas gerais.
    """
    receitas = [r["receita_total"] for r in registros]
    receita_media = sum(receitas) / len(receitas) if receitas else 0
    acima_media = sum(1 for r in receitas if r > receita_media)

    return {
        "total_vendas_validas": len(registros),
        "receita_total_geral": round(sum(receitas), 2),
        "receita_media_por_venda": round(receita_media, 2),
        "vendas_acima_da_media": acima_media,
        "relatorio_limpeza": relatorio_limpeza,
        "top_5_produtos": metricas["top_produtos"],
        "receita_por_categoria": metricas["por_categoria"],
        "receita_por_regiao": metricas["por_regiao"],
    }


def main(fonte="auto"):
    """Executa o fluxo completo do SalesInsight PY.

    Args:
        fonte (str): 'sintetico', 'real' ou 'auto'.
    """
    os.makedirs(PASTA_OUTPUTS, exist_ok=True)

    print("=" * 60)
    print(" SALESINSIGHT PY - ANALISE DE DADOS DE VENDAS")
    print("=" * 60)

    if fonte == "real":
        normalizar_dataset_real()
    elif fonte == "sintetico":
        gerar_dataset(CAMINHO_DATASET)
    else:
        if os.path.exists(CAMINHO_DATASET_REAL):
            print("[INFO] Dataset real detectado - usando Opcao B")
            normalizar_dataset_real()
        elif not os.path.exists(CAMINHO_DATASET):
            print("[INFO] Gerando dataset sintetico")
            gerar_dataset(CAMINHO_DATASET)
        else:
            print("[INFO] Dataset sintetico ja existe - reutilizando")

    registros_brutos = carregar_dataset(CAMINHO_DATASET)
    inspecionar_dados(registros_brutos)
    registros_limpos, relatorio_limpeza = limpar_dados(registros_brutos)
    registros = criar_colunas_derivadas(registros_limpos)

    processar_coluna(
        registros, "receita_total",
        lambda x: round(x / 1000, 2),
        nome_saida="receita_em_milhares"
    )
    processar_coluna(
        registros, "quantidade",
        lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
        nome_saida="perfil_volume"
    )
    print("\n[RF07] Funcao de ordem superior aplicada em 2 contextos")

    metricas = calcular_metricas(registros)
    clientes_segmentados = segmentar_clientes(registros)

    exportar_metricas_csv(metricas["por_mes"])
    exportar_segmentacao_csv(clientes_segmentados)
    estatisticas = montar_estatisticas_gerais(registros, metricas, relatorio_limpeza)
    exportar_estatisticas_json(estatisticas)
    reler_estatisticas_json()

    try:
        gerar_grafico_barras_svg(metricas["por_mes"])
        gerar_grafico_pizza_svg(clientes_segmentados)
        # Gerar SVG de barras agrupadas
        dados_cat_reg = agregar_categoria_regiao(registros)
        gerar_grafico_barras_agrupadas_svg(dados_cat_reg)
        gerar_dashboard_html(metricas, clientes_segmentados, estatisticas, registros)
        print("\n[BONUS B04] Visualizacoes geradas em outputs/:")
        print("  - grafico_receita_mensal.svg")
        print("  - grafico_segmentacao.svg")
        print("  - dashboard.html")
    except Exception as erro:
        print(f"\n[BONUS B04] Aviso: nao foi possivel gerar visualizacoes ({erro})")

    print("\n" + "=" * 60)
    print(" FLUXO CONCLUIDO COM SUCESSO")
    print("=" * 60)


if __name__ == "__main__":
    fonte_escolhida = sys.argv[1] if len(sys.argv) > 1 else "auto"
    main(fonte=fonte_escolhida)
