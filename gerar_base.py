import pandas as pd
import random

# Dados auxiliares
nomes = [
    "Carlos", "Julia", "Fernanda", "Rafael", "Marina", "João", "Bianca", "André",
    "Lucas", "Paula", "Renata", "Diego", "Tatiane", "Gabriel", "Luana", "Vinicius",
    "Roberta", "Felipe", "Patrícia", "Leonardo", "Amanda", "Gustavo", "Camila", "Eduardo"
]

canais = ["SMS", "WhatsApp", "Ligação", "Assessoria"]
respostas = ["Sem resposta", "Prometeu pagar", "Negocia desconto", "Ignorou", "Recusou contato"]
riscos = ["Baixo", "Médio", "Alto", "Muito Alto"]

# Gerar lista de dicionários simulando clientes
registros = []

for i in range(1, 251):
    nome = random.choice(nomes)
    dias_atraso = random.randint(1, 120)
    valor = round(random.uniform(100, 30000), 2)
    canal = random.choice(canais)

    # Resposta mais positiva tende a aparecer em canais humanos ou até 60 dias
    if canal in ["Ligação", "Assessoria"] and dias_atraso <= 60:
        resposta = random.choices(
            respostas,
            weights=[1, 2, 3, 1, 1],  # mais chances de "Negocia desconto"
            k=1
        )[0]
    else:
        resposta = random.choices(respostas, k=1)[0]

    # Faixa de risco por valor e dias em atraso
    if dias_atraso > 90 or valor > 20000:
        risco = "Muito Alto"
    elif dias_atraso > 60 or valor > 10000:
        risco = "Alto"
    elif dias_atraso > 30 or valor > 5000:
        risco = "Médio"
    else:
        risco = "Baixo"

    registros.append({
        "cliente_id": i,
        "nome": nome,
        "dias_em_atraso": dias_atraso,
        "valor_divida": valor,
        "canal_utilizado": canal,
        "resposta_cliente": resposta,
        "faixa_risco": risco
    })

# Criar DataFrame e salvar como CSV
df = pd.DataFrame(registros)
df.to_csv("../data/clientes_inadimplentes.csv", index=False, encoding="utf-8")
print("✅ Base fake gerada com sucesso com", len(df), "registros.")
