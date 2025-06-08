import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                             classification_report, roc_curve, auc)
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Caminho base e pasta do modelo
CAMINHO_BASE = r"C:\\Users\\Matheus\\OneDrive\\Desktop\\Data_Analyst\\projeto2_analise_cobranca"
PASTA_MODELO = os.path.join(CAMINHO_BASE, 'modelo_random_forest')
os.makedirs(PASTA_MODELO, exist_ok=True)

# Carregar dados pré-processados
X_treino = pd.read_csv(os.path.join(CAMINHO_BASE, 'X_treino.csv'))
X_teste = pd.read_csv(os.path.join(CAMINHO_BASE, 'X_teste.csv'))
y_treino = pd.read_csv(os.path.join(CAMINHO_BASE, 'y_treino.csv')).values.ravel()
y_teste = pd.read_csv(os.path.join(CAMINHO_BASE, 'y_teste.csv')).values.ravel()

# Identificar colunas categóricas e numéricas
features_categoricas = ['canal_utilizado', 'faixa_risco', 'faixa_atraso', 'canal_grupo', 'valor_faixa']
features_numericas = ['dias_em_atraso', 'valor_divida']

# Pipeline de pré-processamento e modelo
preprocessor = ColumnTransformer(transformers=[
    ('cat', Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop='first'))
    ]), features_categoricas)
], remainder='passthrough')

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('random_forest', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Treinar modelo
pipeline.fit(X_treino, y_treino)

# Avaliar desempenho
y_pred = pipeline.predict(X_teste)
y_prob = pipeline.predict_proba(X_teste)[:, 1]

print("Relatório de Classificação:\n")
relatorio = classification_report(y_teste, y_pred, output_dict=False)
print(relatorio)

# Matriz de Confusão
cm = confusion_matrix(y_teste, y_pred)
ConfusionMatrixDisplay(cm).plot()
plt.title("Matriz de Confusão - Random Forest")
plt.savefig(os.path.join(PASTA_MODELO, 'matriz_confusao.png'))
plt.close()

# Curva ROC
fpr, tpr, thresholds = roc_curve(y_teste, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label='Curva ROC (área = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos')
plt.ylabel('Taxa de Verdadeiros Positivos')
plt.title('Curva ROC - Random Forest')
plt.legend(loc="lower right")
plt.savefig(os.path.join(PASTA_MODELO, 'curva_roc.png'))
plt.close()

# Importância das Features (Gini Importance)
modelo = pipeline.named_steps['random_forest']
nomes_features = pipeline.named_steps['preprocessor'].get_feature_names_out()
importancias = modelo.feature_importances_
impacto = pd.DataFrame({
    'feature': nomes_features,
    'importancia': importancias
}).sort_values(by='importancia', ascending=True)

# Salvar CSV e gráfico
impacto.to_csv(os.path.join(PASTA_MODELO, 'impacto_features.csv'), index=False)
plt.figure(figsize=(10, 6))
plt.barh(impacto['feature'], impacto['importancia'], color='darkgreen')
plt.xlabel('Importância na Decisão (Gini)')
plt.title('Importância das Variáveis - Random Forest')
plt.tight_layout()
plt.savefig(os.path.join(PASTA_MODELO, 'impacto_features.png'))
plt.close()

# Salvar modelo treinado
joblib.dump(pipeline, os.path.join(PASTA_MODELO, 'modelo.pkl'))
print("Modelo salvo com sucesso em 'modelo.pkl'.")
