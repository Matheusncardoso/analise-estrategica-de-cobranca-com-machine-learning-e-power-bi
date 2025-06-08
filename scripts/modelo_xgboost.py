import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                             classification_report, roc_curve, auc)
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier
import numpy as np

# Caminho dos arquivos gerados pelo pipeline ETL
CAMINHO_BASE = r"C:\\Users\\Matheus\\OneDrive\\Desktop\\Data_Analyst\\projeto2_analise_cobranca"
PASTA_MODELO = os.path.join(CAMINHO_BASE, 'modelo_xgboost')
os.makedirs(PASTA_MODELO, exist_ok=True)

# Carregar dados
X_treino = pd.read_csv(os.path.join(CAMINHO_BASE, 'X_treino.csv'))
X_teste = pd.read_csv(os.path.join(CAMINHO_BASE, 'X_teste.csv'))
y_treino = pd.read_csv(os.path.join(CAMINHO_BASE, 'y_treino.csv')).values.ravel()
y_teste = pd.read_csv(os.path.join(CAMINHO_BASE, 'y_teste.csv')).values.ravel()

# Identificar colunas categóricas e numéricas
features_categoricas = ['canal_utilizado', 'faixa_risco', 'faixa_atraso', 'canal_grupo', 'valor_faixa']
features_numericas = ['dias_em_atraso', 'valor_divida']

# Pipeline de pré-processamento
preprocessor = ColumnTransformer(transformers=[
    ('cat', Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first', sparse_output=False))
    ]), features_categoricas)
], remainder='passthrough')

# Pipeline completo
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('xgboost', XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42))
])

# Treinar modelo
pipeline.fit(X_treino, y_treino)

# Avaliar desempenho
y_pred = pipeline.predict(X_teste)
y_prob = pipeline.predict_proba(X_teste)[:, 1]

print("Relatório de Classificação:\n")
print(classification_report(y_teste, y_pred))

# Matriz de Confusão
cm = confusion_matrix(y_teste, y_pred)
ConfusionMatrixDisplay(cm).plot()
plt.title("Matriz de Confusão - XGBoost")
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
plt.title('Curva ROC - XGBoost')
plt.legend(loc="lower right")
plt.savefig(os.path.join(PASTA_MODELO, 'curva_roc.png'))
plt.close()

# Importância das Features
modelo = pipeline.named_steps['xgboost']
ohe = pipeline.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
ohe_features = ohe.get_feature_names_out(features_categoricas)
nomes_features = np.concatenate([ohe_features, features_numericas])

importancias = modelo.feature_importances_
impacto = pd.DataFrame({
    'feature': nomes_features,
    'importancia': importancias
}).sort_values(by='importancia', ascending=True)

impacto.to_csv(os.path.join(PASTA_MODELO, 'impacto_features.csv'), index=False)
plt.figure(figsize=(10, 6))
plt.barh(impacto['feature'], impacto['importancia'], color='teal')
plt.xlabel('Importância na Decisão (Gain)')
plt.title('Importância das Variáveis - XGBoost')
plt.tight_layout()
plt.savefig(os.path.join(PASTA_MODELO, 'impacto_features.png'))
plt.close()

# Salvar modelo
joblib.dump(pipeline, os.path.join(PASTA_MODELO, 'modelo.pkl'))
print("Modelo salvo com sucesso em 'modelo_xgboost/modelo.pkl'.")
