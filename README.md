# 📊 ENEM, Estrutura Socioeconômica e Desempenho Educacional

![banner](relatorios/imagens/banner_projeto.png)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Model-green)
![Status](https://img.shields.io/badge/status-active-success)

<p align="center">
  <sub>
    Análise estrutural da desigualdade educacional com base nos microdados do ENEM
  </sub>
</p>

---

## 📌 Visão Geral

Este projeto investiga a relação entre **estrutura socioeconômica** e o desempenho dos participantes no ENEM, com foco em **Minas Gerais** e no **Brasil**.

A proposta vai além da análise descritiva, adotando uma abordagem **estrutural e interpretável**, com o objetivo de responder:

> Qual é a nota média esperada dado um perfil socioeconômico?

A análise integra múltiplas dimensões:

- renda familiar  
- escolaridade dos responsáveis  
- ocupação dos responsáveis  
- tipo de escola  
- acesso à tecnologia  

Os resultados indicam que o desempenho educacional está associado a uma **estrutura multidimensional persistente**, e não a fatores isolados.

![projeto](relatorios/imagens/projeto.png)

---

## 🔍 Contexto

Os dados utilizados são os microdados oficiais do ENEM (INEP).

Abordagens utilizadas:

- **Brasil (2024)** → análise agregada nacional  
- **Minas Gerais (2021–2024)** → análise temporal e estrutural  

⚠️ Em 2024, as bases foram disponibilizadas separadamente (perfil e desempenho), impossibilitando análise individual direta.

---

## 📊 Principais Insights

![grafico_1](relatorios/imagens/participacao_renda_nota.png)

A análise revelou padrões estruturais consistentes:

- 📈 **Renda**: diferença de até ~200 pontos entre extremos  
- 🏫 **Tipo de escola**: efeito institucional relevante  
- 👨‍👩‍👧 **Capital familiar**: forte preditor de desempenho  
- 💻 **Tecnologia**: fator complementar ao aprendizado  
- 🌍 **Desigualdade regional**: persistente entre regiões  

![grafico_2](relatorios/imagens/rendaxdesempenho.png)

---

## ⚙️ Pipeline de Dados

Estruturado com foco em reprodutibilidade:

1. **Ingestão**
   - CSV → Parquet  
   - Padronização de schema  

2. **Transformação**
   - Agregações com DuckDB  
   - Bases intermediárias  

3. **Consolidação**
   - Merge socioeconômico + desempenho  
   - Base analítica final  

✔ Performance  
✔ Rastreabilidade  
✔ Reuso  

---

## Engenharia de Features

- Faixas de renda (salários mínimos)  
- Escolaridade dos pais (ordinal)  
- Ocupação dos pais  
- Tipo de escola  
- Indicadores regionais  

✔ Tratamento de missing  
✔ Padronização categórica  
✔ Pronto para modelagem  

---

## Modelagem Preditiva

### Objetivo
Estimar a **nota média esperada** dado um perfil socioeconômico.

### Estratégia

- Aprendizado supervisionado  
- Unidade: grupos socioeducacionais  
- Foco em interpretabilidade  

### Hipótese

> O desempenho é majoritariamente explicado por fatores estruturais socioeconômicos.

### 📊 Base de treino

- Minas Gerais (2021–2023)  
- Dados agregados  

### Resultado

O modelo permite:

- estimar desempenho esperado  
- interpretar desigualdades  
- simular cenários  

![grafico_3](relatorios/imagens/mapa_estrutural_regiao.png)

---

## 🔬 Experimentos

Uso de MLflow para:

- métricas (RMSE, R²)  
- versionamento de modelos  
- comparação entre abordagens  

---

## 📊 Dashboard Interativo

![socioeconomico_app](relatorios/imagens/socioeconomico_app.gif)

![desempenho_app](relatorios/imagens/desempenho_app.gif)

![modelo_app](relatorios/imagens/modelo_app.gif)

O dashboard permite:

- exploração interativa  
- análise regional  
- simulação com modelo  

👉 **[Acesse o dashboard](https://projetoenem.streamlit.app/)**


##  Estrutura do Projeto

```
├── dados/                  # Dados brutos e tratados
├── notebooks/              # Pipeline analítico completo
│   ├── 00_preprocessamento
│   ├── 01_consolidacao
│   ├── 02_features_ml
│   ├── 03_eda
│   ├── 04_modelagem
│   └── dashboard
├── src/                     # Código estruturado (pipeline + modelagem)
│   ├── dados/
│   ├── ingestao/
│   ├── modelos/
│   ├── preprocessamento/
│   └── utils/
│   └── visualizacao/
├── scripts/               # Execução e treinamento
├── relatorios/            # Imagens e outputs
├── referências            # Dicionários
├── resultados/            # Modelos treinados, métricas, tabelas
├── app/                   # Aplicação Streamlit
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── utils/
│
└── README.md
```


### Limitações
* Dados observacionais → não permitem inferência causal
* Base 2024 fragmentada (perfil vs desempenho)
* Possível viés de autodeclaração
* Fatores não observáveis não capturados

Apesar disso, o projeto permite uma análise robusta das desigualdades estruturais educacionais.

### Conclusão

O desempenho no ENEM não é determinado por um único fator, mas por uma estrutura socioeconômica integrada e persistente.

Os resultados mostram que:

* desigualdades educacionais são estruturais
* renda é importante, mas não isoladamente
* capital familiar e escola amplificam diferenças
* tecnologia atua como mediador

Este projeto contribui para uma leitura mais ampla do sistema educacional, alinhada à literatura de economia da educação.

##### Tecnologias Utilizadas
* Python (pandas, numpy)
* DuckDB
* Streamlit
* Plotly
* Scikit-learn
* MLflow (experimentos e rastreamento de modelos — ambiente local

## Contato

🔗 [GitHub: https://github.com/flaviapaulinos](https://github.com/flaviapaulinos)  
🔗 [LinkedIn: https://www.linkedin.com/in/fl%C3%A1via-paulino-a5654831/](https://www.linkedin.com/in/fl%C3%A1via-paulino-a5654831/)

# 📊 ENEM, Socioeconomic Structure and Educational Performance
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-purple)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Model-green)
![Status](https://img.shields.io/badge/status-active-success)

![banner](relatorios/imagens/banner_dashboard_mg.png)

<p align="center">
  <sub>
    Structural analysis of educational inequality based on ENEM microdata
  </sub>
</p>

---

## 📌 Overview

This project investigates the relationship between **socioeconomic structure** and student performance in Brazil’s national high school exam (ENEM), with a focus on Minas Gerais and national-level patterns.

Beyond a purely descriptive analysis, the project adopts a **structural and interpretable approach**, aiming to answer:

> What is the expected average score given a socioeconomic profile?

The analysis integrates multiple structural dimensions:

- household income  
- parents’ education  
- parents’ occupation  
- type of school (public vs private)  
- access to technology  

Results show that educational performance is driven by a **persistent and multidimensional social structure**, rather than isolated variables.

---

## 🔍 Context

The dataset is based on official **ENEM microdata**, provided by the Brazilian Institute for Educational Studies (INEP).

Two main analytical approaches were used:

- **Brazil (2024)** → aggregated national analysis  
- **Minas Gerais (2021–2024)** → structural and temporal analysis  

⚠️ In 2024, the data was released in separate datasets (socioeconomic profile vs performance), preventing individual-level linkage. This limitation is explicitly addressed in the project.

---

## 📊 Key Insights

The exploratory analysis reveals consistent structural patterns:

### 📈 Income and performance
- Higher-income students consistently achieve higher scores  
- Gap of up to **~200 points** between lowest and highest income groups  

### 🏫 Type of school
- Private school students outperform public school students even within the same income bracket  
- Strong evidence of institutional effects  

### 👨‍👩‍👧 Family capital
- Parents’ education and occupation are strong predictors of performance  
- These variables act as proxies for cultural capital  

### 💻 Technology access
- Higher access to computers and mobile devices correlates with better performance  
- Technology acts as a mediating factor  

### 🌍 Regional inequality
- Persistent regional disparities within Minas Gerais  
- Notable contrast between metropolitan and low-income regions  

---

## ⚙️ Data Pipeline

The project is structured with a strong focus on **reproducibility and layered architecture**:

### 1. Ingestion
- CSV → Parquet conversion  
- Schema standardization  

### 2. Transformation
- Aggregations using DuckDB  
- Creation of intermediate datasets  

### 3. Consolidation
- Merging socioeconomic and performance data  
- Building analytical datasets  

✔ Improved performance  
✔ Traceability  
✔ Reusability  

---

## 🧠 Feature Engineering

Structural variables were created with a focus on interpretability:

- Income brackets (minimum wages)  
- Parents’ education (ordinal encoding)  
- Parents’ occupation  
- School type  
- Regional aggregated indicators  

✔ Missing data handling  
✔ Category standardization  
✔ Model-ready structure  

---

## 🤖 Predictive Modeling

The project adopts an **aggregated and interpretable modeling approach**, focusing on structural relationships.

### 🎯 Objective
Estimate the **expected average score** based on a socioeconomic profile.

### 🧩 Strategy

- Supervised learning  
- Unit of analysis: **aggregated socio-educational profiles (not individuals)**  
- Emphasis on interpretability  

### 🧠 Core hypothesis

> Performance variation is primarily explained by structural socioeconomic factors rather than individual noise.

### 📊 Training data

- Minas Gerais (2021–2023)  
- Aggregated dataset (`DADOS_AGG_MG_ML`)  

### 🏆 Outcome

The model enables:

- estimation of expected performance  
- interpretation of structural drivers  
- simulation of socioeconomic scenarios  

---

## 📊 Interactive Dashboard

The project includes a **Streamlit dashboard** with:

- interactive visualizations  
- regional and socioeconomic filtering  
- structural inequality analysis  
- integration with the predictive model  

### 🔗 App link

👉 *(add your deployment link here)*

---

## 🧩 Project Structure

projeto_enem_ml/

├── dados/ # Raw and processed data
├── modelos/ # Trained models
├── notebooks/ # Full analytical pipeline
│ ├── preprocessing
│ ├── consolidation
│ ├── feature_engineering
│ ├── eda
│ ├── modeling
│ └── dashboards
│
├── app/ # Streamlit application
│ ├── pages/
│ ├── components/
│ ├── services/
│ └── utils/
│
├── src/ # Core project code
│ ├── preprocessing/
│ ├── modeling/
│ └── visualization/
│
├── scripts/ # Training and execution
├── relatorios/ # Reports and images
└── README.md

## ⚠️ Limitations

- Observational data → no causal inference  
- 2024 dataset split (profile vs performance)  
- Self-reported socioeconomic variables  
- Unobserved factors not captured (e.g., school quality, individual traits)  

Despite these limitations, the project provides a robust analysis of **structural educational inequality**.

---

## 📌 Conclusion

Educational performance in ENEM is not driven by a single factor, but by a **persistent and interconnected socioeconomic structure**.

Key findings:

- inequality is structural and stable over time  
- income matters, but is not sufficient alone  
- family capital plays a central role  
- school type amplifies disparities  
- technology access mediates outcomes  

This project contributes to a broader understanding of educational inequality, aligned with the literature in **economics of education**, and provides insights that may support more targeted public policies.

---

## 🚀 Technologies

- Python (pandas, numpy)  
- DuckDB  
- Streamlit  
- Plotly  
- Scikit-learn  
- MLflow  

---

## 📬 Contact

*(add your LinkedIn / GitHub here)*