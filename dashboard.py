import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(page_title="Dashboard de Assinaturas", layout="wide")

# ==================================================
# CORES E CONFIG
# ==================================================
COR_PRIMARIA = "#1E3A8A"
COR_SUCESSO = "#10B981"
COR_CHURN = "#EF4444"

# ==================================================
# CARREGA OS DADOS
# ==================================================
with open("dados_formatados.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

df = pd.DataFrame(dados)

datas = ["created_at", "inicio_ciclo", "fim_ciclo", "proximo_ciclo"]
for d in datas:
    df[d] = pd.to_datetime(df[d], errors="coerce")

hoje = datetime.today().date()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.header("Filtros de Período")
inicio = st.sidebar.date_input("Início:", df["created_at"].min().date())
fim = st.sidebar.date_input("Fim:", df["created_at"].max().date())
mask = (df["created_at"].dt.date >= inicio) & (df["created_at"].dt.date <= fim)
df = df[mask]

# ==================================================
# KPIs GERAIS
# ==================================================
vigentes = df[df["status_assinatura"] == "active"].shape[0]
entradas_dia = df[df["created_at"].dt.date == hoje].shape[0]
entradas_mes = df[df["created_at"].dt.month == hoje.month].shape[0]
entradas_ano = df[df["created_at"].dt.year == hoje.year].shape[0]

churn_dia = df[(df["status_assinatura"].str.contains("cancel")) & (df["created_at"].dt.date == hoje)].shape[0]
churn_mes = df[(df["status_assinatura"].str.contains("cancel")) & (df["created_at"].dt.month == hoje.month)].shape[0]
churn_ano = df[(df["status_assinatura"].str.contains("cancel")) & (df["created_at"].dt.year == hoje.year)].shape[0]

st.markdown(f"## Dashboard de Assinaturas")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Assinaturas Vigentes", vigentes)
k2.metric("Entradas (Dia)", entradas_dia)
k3.metric("Entradas (Mês)", entradas_mes)
k4.metric("Entradas (Ano)", entradas_ano)
k5.metric("Churn (Mês)", churn_mes)
k6.metric("Churn (Ano)", churn_ano)

# ==================================================
# EMPRESAS PARA DERRUBAR HOJE (+7 DIAS)
# ==================================================
st.markdown("### Empresas para derrubar hoje (+7 dias para expirar): ")
d7 = datetime.today() + timedelta(days=7)
empresas_derrubar = df[(df["fim_ciclo"].dt.date <= d7.date()) & (df["status_assinatura"] == "active")]
st.dataframe(empresas_derrubar[["nome_cliente", "nome_produto", "fim_ciclo", "metodo_pagamento", "status_assinatura"]])

# ==================================================
# RENDA RETIDA e PERCENTUAL DE RENOVAÇÃO
# ==================================================
st.markdown("### Renda Retida e Percentual de Renovação")
renovacoes_hoje = df[(df["inicio_ciclo"].dt.date == hoje) & (df["status_assinatura"].str.contains("active"))]
renovacoes_mes = df[(df["inicio_ciclo"].dt.month == hoje.month) & (df["status_assinatura"].str.contains("active"))]

st.metric("Renda Retida (Mês)", f"R$ {renovacoes_mes['total'].sum():,.2f}")

percentual_renovacao = (renovacoes_mes.shape[0] / df.shape[0]) * 100 if df.shape[0] > 0 else 0
st.metric("Percentual de Renovação (%)", f"{percentual_renovacao:.2f}")

# ==================================================
# RENOVAÇÕES E CANCELAMENTOS NO DIA E NO MÊS
# ==================================================
st.markdown("### Renovações e Cancelamentos por Dia e por Mês")
renovadas_dia = df[(df["status_assinatura"].str.contains("active")) & (df["inicio_ciclo"].dt.date == hoje)].shape[0]
canceladas_dia = df[(df["status_assinatura"].str.contains("cancel")) & (df["created_at"].dt.date == hoje)].shape[0]
atrasadas_dia = df[(df["status_assinatura"].str.contains("overdue")) & (df["created_at"].dt.date == hoje)].shape[0]

renovadas_mes = df[(df["status_assinatura"].str.contains("active")) & (df["inicio_ciclo"].dt.month == hoje.month)].shape[0]
canceladas_mes = df[(df["status_assinatura"].str.contains("cancel")) & (df["created_at"].dt.month == hoje.month)].shape[0]
atrasadas_mes = df[(df["status_assinatura"].str.contains("overdue")) & (df["created_at"].dt.month == hoje.month)].shape[0]

k7, k8, k9 = st.columns(3)
k7.metric("Renovadas (Dia)", renovadas_dia)
k8.metric("Canceladas (Dia)", canceladas_dia)
k9.metric("Atrasadas (Dia)", atrasadas_dia)

k10, k11, k12 = st.columns(3)
k10.metric("Renovadas (Mês)", renovadas_mes)
k11.metric("Canceladas (Mês)", canceladas_mes)
k12.metric("Atrasadas (Mês)", atrasadas_mes)

# ==================================================
# FORMAS DE PAGAMENTO
# ==================================================
st.markdown("### Assinaturas por Forma de Pagamento e Status")
metodo_contagem = df.groupby(["metodo_pagamento", "status_assinatura"]).size().reset_index(name="count")
st.dataframe(metodo_contagem)

metodos_count = df["metodo_pagamento"].value_counts()
st.plotly_chart(px.pie(values=metodos_count, names=metodos_count.index,
                      title="Assinaturas por método de pagamento",
                      color_discrete_sequence=["#1E3A8A", "#3B82F6", "#10B981", "#EF4444"]))

# ==================================================
# ASSINATURAS POR ESTADO E CIDADE
# ==================================================
st.markdown("### Assinaturas por Estado e Cidade")
estado_count = df["estado"].value_counts()
st.plotly_chart(px.bar(estado_count, title="Assinaturas por Estado",
                      color_discrete_sequence=["#1E3A8A"]))
cidade_count = df["cidade"].value_counts()
st.plotly_chart(px.bar(cidade_count, title="Assinaturas por Cidade",
                      color_discrete_sequence=["#3B82F6"]))

# ==================================================
# OFERTAS E ASSINATURAS FALSAS
# ==================================================
st.markdown("### Ofertas e Falsas Assinaturas")
ofertas_count = df["nome_oferta"].value_counts()
st.plotly_chart(px.bar(ofertas_count, title="Ofertas por Assinatura",
                      color_discrete_sequence=["#10B981"]))
falsas_count = df["assinatura_falsa"].value_counts()
st.plotly_chart(px.pie(values=falsas_count, names=falsas_count.index,
                      title="Falsas Assinaturas",
                      color_discrete_sequence=["#EF4444", "#1E3A8A"]))

# ==================================================
# DADOS DE CLIENTES
# ==================================================
st.markdown("### Dados de Clientes")
st.dataframe(df[["email", "nome_cliente", "created_at", "codigo_assinatura", "ciclo"]])

# ==================================================
# RECEITA DE ENTRADA
# ==================================================
st.markdown("### Receita de Entrada por Mês")
faturamento_mensal = df.groupby(df["created_at"].dt.to_period("M"))["total"].sum()
st.line_chart(faturamento_mensal)

# ==================================================
# ESTADO COM MENOR RENOVAÇÃO
# ==================================================
st.markdown("### Estado com Menor Taxa de Renovação")
renovacoes_por_estado = df.groupby("estado")["status_assinatura"].apply(lambda x: (x == "active").sum() / len(x) * 100).sort_values()
st.dataframe(renovacoes_por_estado)

# ==================================================
# RENOVAÇÃO DIÁRIA E MENSAL (GRÁFICO DE PIZZA)
# ==================================================
st.markdown("### Renovação Diária e Mensal (Pizza) ")
renovacoes_hoje = df[(df["inicio_ciclo"].dt.date == hoje) & (df["status_assinatura"].str.contains("active"))].shape[0]
pendentes_hoje = df[(df["inicio_ciclo"].dt.date == hoje) & (~df["status_assinatura"].str.contains("active"))].shape[0]

st.plotly_chart(px.pie(values=[renovacoes_hoje, pendentes_hoje], names=["Feitas", "Pendentes"],
                      title="Renovação - Hoje",
                      color_discrete_sequence=["#10B981", "#EF4444"]))

renovacoes_mes_count = df[(df["inicio_ciclo"].dt.month == hoje.month) & (df["status_assinatura"].str.contains("active"))].shape[0]
pendentes_mes_count = df[(df["inicio_ciclo"].dt.month == hoje.month) & (~df["status_assinatura"].str.contains("active"))].shape[0]

st.plotly_chart(px.pie(values=[renovacoes_mes_count, pendentes_mes_count], names=["Feitas", "Pendentes"],
                      title="Renovação - Mês",
                      color_discrete_sequence=["#10B981", "#EF4444"]))

# ==================================================
# FIM
# ==================================================
st.markdown("---")
st.markdown("*Dashboard Profissional de Assinaturas e Análises Avançadas.*")
