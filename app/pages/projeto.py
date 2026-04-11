from __future__ import annotations

import streamlit as st


def render_aba_projeto() -> None:
    st.header("Projeto — ENEM e Estrutura Social")

    # =========================================================
    # VISÃO GERAL
    # =========================================================
    st.markdown("### Visão Geral")

    st.markdown(
        """
        Este projeto tem como objetivo analisar a relação entre **estrutura socioeconômica** e o desempenho dos participantes no ENEM, com foco especial no estado de Minas Gerais.
        
        A proposta vai além da análise descritiva, buscando também construir um **modelo preditivo interpretável** capaz de estimar:
        
        > Qual é a nota média esperada de um estudante dado seu perfil socioeconômico?
        
        O projeto foi estruturado em três pilares:
        
        - **Tratamento e estruturação de dados**
        - **Análise exploratória (EDA)**
        - **Modelagem preditiva interpretável**
        
        Os gráficos desenvolvidos para a análise dos dados investigam a relação entre estrutura socioeconômica e desempenho educacional no ENEM, com foco no estado de Minas Gerais e no Brasil.
        
        A análise integra diferentes dimensões estruturais — renda, escolaridade e ocupação dos responsáveis, tipo de escola e acesso à tecnologia — permitindo compreender como essas variáveis se combinam na explicação das desigualdades educacionais.
        
        Diferenças de desempenho entre grupos socioeconômicos permanecem estáveis ao longo do tempo, indicando que a desigualdade educacional possui caráter estrutural. Mesmo dentro da mesma faixa de renda, observam-se diferenças relevantes associadas ao tipo de escola e ao acesso a recursos tecnológicos.
        
        A análise foi conduzida com dados agregados, priorizando interpretabilidade estrutural em detrimento de previsão individual. Os resultados devem ser interpretados como relações associativas, não causais.
        
        Este projeto busca contribuir para a compreensão da desigualdade educacional a partir de uma abordagem integrada, alinhada à literatura de economia da educação, e oferecer evidências que possam subsidiar políticas públicas mais direcionadas.

    """
    )

    st.divider()

    # =========================================================
    # BASE DE DADOS
    # =========================================================
    st.markdown("### Base de Dados")

    st.markdown(
        """
    Foram utilizados os microdados do ENEM, abrangendo:
    
    - **Brasil (2024)** — utilizado para análise nacional
    - **Minas Gerais (2021 a 2024)** — utilizado para análise temporal
    
    As bases incluem informações como:
    
    - notas por área do conhecimento
    - renda familiar
    - escolaridade dos responsáveis
    - ocupação dos responsáveis
    - tipo de escola
    - características demográficas
    
    Os dados foram organizados em diferentes camadas:
    
    - **Brutos (CSV)**
    - **Intermediários (Parquet)**
    - **Analíticos (agregações e features)**
    """
    )

    st.divider()

    # =========================================================
    # PIPELINE
    # =========================================================
    st.markdown("### Pipeline de Dados")

    st.markdown(
        """
    O pipeline foi estruturado com foco em reprodutibilidade e organização em camadas:
    
    #### 1. Ingestão
    - Conversão de CSV para Parquet
    - Padronização de tipos e colunas
    
    #### 2. Transformações SQL (DuckDB)
    - Criação de views intermediárias
    - Agregações por:
      - região
      - escola
      - perfil socioeconômico
    
    #### 3. Consolidação
    - Merge de dados demográficos e de desempenho
    - Criação de bases analíticas finais
    
    Essa abordagem permite:
    - melhor performance
    - rastreabilidade
    - reutilização dos dados
    """
    )

    st.divider()

    # =========================================================
    # FEATURES
    # =========================================================
    st.markdown("### Engenharia de Features")

    st.markdown(
        """
    Foram construídas variáveis estruturais com base em categorias socioeconômicas:
    
    - Faixas de renda (em salários mínimos)
    - Escolaridade dos pais
    - Ocupação dos pais
    - Tipo de escola (pública/privada)
    - Indicadores agregados por região
    
    Além disso:
    
    - categorias foram **padronizadas e ordenadas**
    - valores ausentes foram tratados
    - variáveis categóricas foram transformadas para uso no modelo
    
    O foco foi manter **interpretabilidade**, evitando transformações excessivamente complexas.
    """
    )

    st.divider()

    # =========================================================
    # MODELAGEM
    # =========================================================
    st.markdown("### Modelagem Preditiva")

    st.markdown(
        """
    O modelo desenvolvido neste projeto tem como objetivo estimar a **nota média esperada**
    a partir de um perfil socioeconômico, com foco em interpretação estrutural.
    
    #### Abordagem conceitual
    
    Diferentemente de abordagens tradicionais centradas em previsão individual, este projeto adota uma perspectiva **estrutural e agregada**, na qual:
    
    - a unidade de análise não é o indivíduo
    - mas sim **perfis socioeducacionais agregados**
    
    Cada observação do modelo representa um grupo definido por:
    
    - ano do exame
    - faixa de renda familiar (em salários mínimos)
    - escolaridade dos responsáveis
    - ocupação dos responsáveis
    - tipo de escola frequentada
    - características demográficas
    
    Essa agregação reduz o ruído individual e permite analisar relações mais estáveis entre contexto social e desempenho educacional.
    
    ---
    
    #### Base utilizada
    
    A modelagem foi construída exclusivamente com dados de **Minas Gerais entre 2021 e 2023**, onde é possível relacionar diretamente:
    
    - perfil socioeconômico
    - desempenho nas provas
    
    Os dados foram transformados em uma base agregada (`DADOS_AGG_MG_ML`), contendo:
    
    - médias de desempenho
    - proporções populacionais
    - indicadores estruturais por perfil
    
    A base de 2024 não foi utilizada na modelagem devido à impossibilidade de vincular individualmente participantes e resultados.
    
    ---
    
    ### Hipótese central
    
    A hipótese do modelo é que:
    
    > A variabilidade da nota média é predominantemente explicada por fatores socioeconômicos estruturais, e não por ruído individual.
    
    ---
    
    #### Estratégia de modelagem
    
    - modelo supervisionado
    - foco em **interpretabilidade**
    - decomposição dos efeitos socioeconômicos
    - análise associativa com aproximação estrutural
    
    A modelagem prioriza:
    
    - compreensão dos efeitos das variáveis
    - estabilidade dos coeficientes
    - leitura analítica dos resultados
    
    em detrimento de ganhos marginais de acurácia.
    
    ---
    
    #### Evidências empíricas (EDA)
    
    A análise exploratória indicou padrões consistentes:
    
    - **Tipo de escola**  
      Diferença significativa entre pública e privada, sugerindo forte efeito institucional.
    
    - **Ocupação dos pais**  
      Gradiente crescente, funcionando como proxy de capital cultural.
    
    - **Região**  
      Diferenças persistentes, indicando desigualdade territorial.
    
    - **Raça/Cor**  
      Padrões estáveis entre grupos, refletindo desigualdades estruturais históricas.
    
    Esses resultados sustentam a utilização de um modelo interpretável focado em estrutura social.
    
    ---
    
    #### Objetivo do modelo
    
    - estimar a nota média esperada dado um perfil socioeconômico
    - quantificar a contribuição relativa de cada dimensão estrutural
    - identificar padrões sistêmicos de desigualdade educacional
    
    O modelo final está integrado à aplicação, permitindo simulações a partir de perfis definidos pelo usuário.

    A abordagem adotada aproxima-se de uma modelagem estrutural, permitindo interpretar o sistema educacional como função de condicionantes socioeconômicos agregados.
    """
    )

    # =========================================================
    # INTERPRETAÇÃO
    # =========================================================
    st.markdown("### Interpretação dos Resultados")

    st.markdown(
        """
    O projeto prioriza a leitura interpretável dos resultados.
    
    Os principais padrões observados incluem:
    
    - forte relação entre **renda familiar e desempenho**
    - impacto relevante da **escolaridade dos pais**
    - diferenças consistentes entre **escola pública e privada**
    - desigualdades regionais dentro de Minas Gerais
    
    A análise permite identificar não apenas diferenças médias,
    mas também **estruturas sociais associadas ao desempenho educacional**.
    """
    )

    st.divider()

    # =========================================================
    # LIMITAÇÕES
    # =========================================================
    st.markdown("## ⚠️ Limitações")

    st.markdown(
    """
    - Os dados são **observacionais**, não permitindo inferência causal direta.
    
    - As bases do ENEM de **2024 foram disponibilizadas de forma segmentada**, separando:
      - dados socioeconômicos (participantes)
      - dados de desempenho (resultados)
    
      Como não há uma chave única que permita o vínculo direto entre essas bases, **não é possível relacionar individualmente o perfil socioeconômico às notas dos participantes em 2024**.
    
    - Em função dessa limitação:
      - análises que exigem relação direta entre perfil e desempenho foram realizadas utilizando a série histórica de **2021 a 2023**, onde essa integração é possível;
      - as análises de 2024 são predominantemente **agregadas**, focadas em padrões estruturais.
    
    - Possíveis vieses adicionais:
      - autodeclaração das informações socioeconômicas
      - não resposta em variáveis relevantes
    
    - O modelo não captura fatores não observáveis, como:
      - qualidade específica da escola
      - características individuais não mensuradas
    
    Apesar dessas limitações, os dados permitem uma análise robusta das **desigualdades estruturais associadas ao desempenho educacional**.
    """
    )