import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import os

# Caminho local para a base de dados
CAMINHO_BASE = r"C:\\Users\\Matheus\\OneDrive\\Desktop\\Data_Analyst\\projeto2_analise_cobranca\\clientes_enriquecido.csv"
CAMINHO_SAIDA = r"C:\\Users\\Matheus\\OneDrive\\Desktop\\Data_Analyst\\projeto2_analise_cobranca"

# Carregar a base de dados
df = pd.read_csv(CAMINHO_BASE)

# Definir variável alvo
df['resposta_positiva'] = df['resposta_positiva'].astype(int)
y = df['resposta_positiva']

# Selecionar features relevantes
X = df[[
    'dias_em_atraso',
    'valor_divida',
    'canal_utilizado',
    'faixa_risco',
    'faixa_atraso',
    'canal_grupo',
    'valor_faixa'
]]

# Separar variáveis numéricas e categóricas
features_numericas = ['dias_em_atraso', 'valor_divida']
features_categoricas = ['canal_utilizado', 'faixa_risco', 'faixa_atraso', 'canal_grupo', 'valor_faixa']

# Pré-processamento para variáveis categóricas
transformador_categorico = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop='first'))
])

# Pré-processamento completo
preprocessor = ColumnTransformer(transformers=[
    ('cat', transformador_categorico, features_categoricas)
], remainder='passthrough')

# Separar dados de treino e teste
X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Ajustar e transformar os dados com o pré-processador
X_treino_transformado = preprocessor.fit_transform(X_treino)
X_teste_transformado = preprocessor.transform(X_teste)

# Recuperar os nomes das colunas após one-hot encoding
onehot_columns = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(features_categoricas)
colunas_finais = list(onehot_columns) + features_numericas

# Converter para DataFrame com nomes das colunas
X_treino_df = pd.DataFrame(X_treino_transformado, columns=colunas_finais)
X_teste_df = pd.DataFrame(X_teste_transformado, columns=colunas_finais)

# Salvar conjuntos de treino e teste transformados
os.makedirs(CAMINHO_SAIDA, exist_ok=True)
X_treino_df.to_csv(os.path.join(CAMINHO_SAIDA, 'X_treino_transformado.csv'), index=False)
X_teste_df.to_csv(os.path.join(CAMINHO_SAIDA, 'X_teste_transformado.csv'), index=False)
y_treino.to_csv(os.path.join(CAMINHO_SAIDA, 'y_treino.csv'), index=False)
y_teste.to_csv(os.path.join(CAMINHO_SAIDA, 'y_teste.csv'), index=False)

# Salvar também os arquivos não transformados, se desejar
X_treino.to_csv(os.path.join(CAMINHO_SAIDA, 'X_treino.csv'), index=False)
X_teste.to_csv(os.path.join(CAMINHO_SAIDA, 'X_teste.csv'), index=False)

print("Pipeline de ETL executado com sucesso. Dados transformados e salvos com nomes de colunas expandidos.")
