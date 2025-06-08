import pandas as pd

# Lê o CSV
df = pd.read_csv("../data/clientes_inadimplentes.csv")

# Cria faixas de atraso
def categorizar_atraso(dias):
    if dias < 15:
        return "<15 dias"
    elif dias < 30:
        return "15-30 dias"
    elif dias < 60:
        return "30-60 dias"
    else:
        return ">60 dias"

df["faixa_atraso"] = df["dias_em_atraso"].apply(categorizar_atraso)

# Marca respostas positivas
df["resposta_positiva"] = df["resposta_cliente"].apply(
    lambda r: 1 if r in ["Prometeu pagar", "Negocia desconto"] else 0
)

# Agrupa canais
df["canal_grupo"] = df["canal_utilizado"].apply(
    lambda c: "Digital" if c in ["SMS", "WhatsApp"] else "Humano"
)

# Faixa de valor
df["valor_faixa"] = pd.cut(
    df["valor_divida"],
    bins=[0, 500, 1500, float("inf")],
    labels=["Baixo", "Médio", "Alto"]
)

# Mostra o dataframe
print(df)

# Exporta para um novo CSV para análise final
df.to_csv("../data/clientes_enriquecido.csv", index=False, encoding="utf-8")
print("✅ Base enriquecida salva com sucesso!")
