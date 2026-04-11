![banner](relatorios/imagens/banner_dashboard.png)
## ENEM, Estrutura Socioeconômica e Desempenho Educacional

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![ML](https://img.shields.io/badge/Machine%20Learning-Model-green)
![Status](https://img.shields.io/badge/status-active-success)

<p align="center"> <sub> Análise estrutural da desigualdade educacional com base nos microdados do ENEM </sub> </p>
📌 Visão Geral

Este projeto investiga a relação entre estrutura socioeconômica e o desempenho dos participantes no ENEM, com foco no estado de Minas Gerais e no Brasil.

A proposta vai além da análise descritiva, incorporando uma abordagem estrutural e interpretável, com o objetivo de responder:

Qual é a nota média esperada dado um perfil socioeconômico?

A análise integra múltiplas dimensões:

* renda familiar
* escolaridade dos responsáveis
* ocupação dos responsáveis
* tipo de escola
* acesso à tecnologia

Os resultados indicam que o desempenho educacional está associado a uma estrutura multidimensional persistente, e não a fatores isolados.

![projeto](relatorios/imagens/projeto.png)

### Contexto

Os dados utilizados são os microdados oficiais do ENEM, disponibilizados pelo INEP.

Foram utilizadas duas abordagens principais:

Brasil (2024) → análise agregada nacional
Minas Gerais (2021–2024) → análise temporal e estrutural

⚠️ Em 2024, as bases foram disponibilizadas separadamente (perfil e desempenho), impossibilitando análise individual direta — o projeto trata essa limitação explicitamente.

### Principais Insights

![grafico_1](relatorios/imagens/participacao_renda_nota.png)

A análise exploratória revelou padrões estruturais consistentes:

📈 Renda e desempenho
A nota média dos participantes de maior renda apresentam notas significativamente superiores
Diferença de até ~200 pontos entre extremos de renda
🏫 Tipo de escola
Escolas privadas apresentam desempenho médio superior mesmo dentro da mesma faixa de renda
Evidência de efeito institucional relevante
👨‍👩‍👧 Capital familiar
Escolaridade e ocupação dos pais são fortes preditores de desempenho
Funcionam como proxy de capital cultural
💻 Tecnologia
Maior acesso a computador e celular está associado a melhor desempenho
Atua como fator de mediação
🌍 Desigualdade regional
Diferenças persistentes entre regiões de Minas Gerais
Destaque para contraste entre RMBH e regiões como Jequitinhonha

![grafico_2](relatorios/imagens/rendaxdesempenho.png)

### ⚙️ Pipeline de Dados

O projeto foi estruturado com foco em reprodutibilidade e organização em camadas:

1. Ingestão
Conversão de CSV → Parquet
Padronização de schemas
2. Transformações
Agregações via DuckDB
Criação de bases intermediárias
3. Consolidação
Merge entre dados socioeconômicos e desempenho
Construção de bases analíticas

✔ Melhor performance
✔ Rastreabilidade
✔ Reuso de dados

#### Engenharia de Features

Foram criadas variáveis estruturais com foco em interpretabilidade:

Faixas de renda (salários mínimos)
Escolaridade dos pais (ordenada)
Ocupação dos pais
Tipo de escola
Indicadores agregados regionais

✔ Tratamento de valores ausentes
✔ Padronização categórica
✔ Estrutura pronta para modelagem

#### Modelagem Preditiva

O projeto utiliza uma abordagem agregada e interpretável, focada em estrutura social.

#### Objetivo

Estimar a nota média esperada dado um perfil socioeconômico.

#### Estratégia

Modelagem supervisionada
Unidade de análise: grupos socioeducacionais (não indivíduos)
Foco em interpretabilidade

#### Hipótese central

A variação do desempenho é predominantemente explicada por fatores estruturais socioeconômicos.

#### Base de treino
Minas Gerais (2021–2023)
Dados agregados (DADOS_AGG_MG_ML)

#### Resultado

O modelo permite:

quantificar impacto de variáveis socioeconômicas
simular cenários educacionais
interpretar desigualdades estruturais

![grafico_3](relatorios/imagens/mapa_estrutural_regiao.png)

### Experimentos e Rastreamento

O treinamento dos modelos foi conduzido com uso de MLflow para:

- registro de métricas (RMSE, R², CV)
- versionamento de modelos
- comparação entre abordagens (analítica vs produto)

O deploy do dashboard utiliza os artefatos finais exportados, sem dependência direta do MLflow.

### Dashboard Interativo

O projeto inclui um dashboard desenvolvido em Streamlit, com:

visualizações interativas
análise por região e perfil
exploração de desigualdades
integração com modelo preditivo
🔗 Acesso ao app

👉 (adicione aqui o link do seu deploy)

</> Markdown
```bash
## Estrutura do Projeto

projeto_enem_ml/

├── dados/                  # Dados brutos e tratados
├── modelos/                # Modelos treinados
├── notebooks/              # Pipeline analítico completo
│   ├── 00_preprocessamento
│   ├── 01_consolidacao
│   ├── 02_features_ml
│   ├── 03_eda
│   ├── 04_modelagem
│   └── dashboard
│
├── app/                    # Aplicação Streamlit
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── utils/
│
├── src/                    # Código estruturado (pipeline + modelagem)
│   ├── preprocessamento/
│   ├── modelos/
│   └── visualizacao/
│
├── scripts/                # Execução e treinamento
├── relatorios/             # Imagens e outputs
└── README.md
---
![home_app](relatorios/imagens/home_app.gif)
![home_app](relatorios/imagens/socioeconomico_app.gif)

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
* renda é importante, mas não isolada
* capital familiar e escola amplificam diferenças
* tecnologia atua como mediador

Este projeto contribui para uma leitura mais ampla do sistema educacional, alinhada à literatura de economia da educação.

##### Tecnologias Utilizadas
* Python (pandas, numpy)
* DuckDB
* Streamlit
* Plotly
* Scikit-learn
* MLflow (experimentos e rastreamento de modelos — ambiente local)

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