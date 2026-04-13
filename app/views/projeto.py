from __future__ import annotations

import streamlit as st


def render_aba_projeto() -> None:
    st.header("Projeto — ENEM e Estrutura Social")

    # =========================================================
    # VISÃO GERAL
    # =========================================================
    st.markdown("### Quanto o contexto social influencia a nota no ENEM?")

    st.markdown(
        """
        Este projeto busca responder uma pergunta simples, mas muito importante:

        👉 **Até que ponto as condições de vida de um estudante influenciam seu desempenho no ENEM?**

        Para isso, analisamos fatores como:

        - renda familiar  
        - escolaridade dos responsáveis  
        - ocupação dos responsáveis  
        - tipo de escola  
        - acesso à tecnologia  

        A ideia é entender como essas condições, quando combinadas, ajudam a explicar as diferenças de desempenho entre os estudantes.

        Além da análise, foi desenvolvido um modelo que permite **estimar a nota média esperada**
        a partir de um perfil socioeconômico.

        Ou seja: é possível simular cenários e entender como diferentes contextos sociais estão associados ao desempenho educacional.

        ---
        
        🔗 **Quer ver os detalhes técnicos, metodologia e código completo?**  
        Acesse o projeto no GitHub:  
        https://github.com/flaviapaulinos/projeto_enem_2021_2024
        """
    )

    st.divider()

    # =========================================================
    # BASE DE DADOS
    # =========================================================
    st.markdown("### De onde vêm os dados?")

    st.markdown(
        """
        Os dados utilizados são os microdados oficiais do ENEM, disponibilizados pelo INEP.

        Foram utilizadas duas abordagens principais:

        - **Brasil (2024)** → visão geral do país  
        - **Minas Gerais (2021 a 2024)** → análise ao longo do tempo  

        Esses dados incluem informações como:

        - notas nas provas  
        - renda familiar  
        - escolaridade dos responsáveis  
        - tipo de escola  
        - características demográficas  

        ⚠️ Em 2024, os dados foram divulgados em bases separadas (perfil e desempenho).  
        Por isso, algumas análises são feitas de forma agregada, e não individual.
        """
    )

    st.divider()

    # =========================================================
    # MODELAGEM
    # =========================================================
    st.markdown("### Como funciona o modelo?")

    st.markdown(
        """
        O modelo desenvolvido neste projeto não tenta prever a nota de um aluno específico.

        Em vez disso, ele responde:

        👉 **Qual é a nota média esperada para um determinado perfil socioeconômico?**

        Isso significa que:

        - o foco não é o indivíduo  
        - mas sim grupos com características semelhantes  

        Por exemplo:

        - estudantes com determinada faixa de renda  
        - com pais com certo nível de escolaridade  
        - que estudam em escola pública ou privada  

        Essa abordagem ajuda a reduzir o “ruído” individual e permite enxergar padrões mais claros.

        O objetivo do modelo é:

        - entender quais fatores mais influenciam o desempenho  
        - quantificar essas diferenças  
        - permitir simulações de cenários  

        Mais do que prever, o foco é **explicar e interpretar**.
        """
    )

    st.divider()

    # =========================================================
    # PRINCIPAIS RESULTADOS
    # =========================================================
    st.markdown("### O que mais influencia o desempenho?")

    st.markdown(
        """
        Os dados mostram que o desempenho no ENEM não depende de um único fator,
        mas de uma combinação de condições sociais.
    
        Alguns fatores se destacam:
    
        - 🏫 **Tipo de escola**  
          Esse é o fator com maior impacto.  
          Diferenças entre escola pública e privada representam cerca de **40% do efeito total observado**.
    
        - 👨‍👩‍👧 **Contexto familiar**  
          Escolaridade e ocupação dos responsáveis juntos respondem por aproximadamente **25% da variação no desempenho**.
    
        - 📱💻 **Acesso à tecnologia**  
          Ter celular e computador está associado a melhores resultados, contribuindo com cerca de **15% do impacto total**.
    
        👉 Em resumo: o desempenho é resultado de uma **estrutura combinada de fatores**,
        e não de um único elemento isolado.
    """
    )
    st.caption(
    "Os percentuais apresentados foram estimados a partir da decomposição dos coeficientes do modelo preditivo."
)

    st.divider()

    # =========================================================
    # INTERPRETAÇÃO
    # =========================================================
    st.markdown("### Como interpretar esses resultados?")

    st.markdown(
        """
        É importante destacar:

        - os dados mostram **associações**, não causas diretas  
        - ou seja, não é possível afirmar que um fator isolado "causa" uma nota maior  

        O que o projeto evidencia é que:

        👉 **as condições socioeconômicas influenciam o desempenho de forma conjunta**

        Em geral:

        - fatores familiares e escola têm forte peso   
        - tecnologia atua como complemento  

        Isso reforça a ideia de que desigualdades educacionais são **estruturais**,
        e não resultado de um único fator isolado.
        """
    )

    st.divider()

    # =========================================================
    # LIMITAÇÕES
    # =========================================================
    st.markdown("## ⚠️ Limitações")

    st.markdown(
        """
        - Os dados são observacionais → não permitem inferência causal direta  
        - Em 2024, as bases foram divulgadas separadamente  
        - Algumas informações são autodeclaradas  
        - Nem todos os fatores relevantes podem ser medidos  

        Mesmo assim, os dados permitem uma análise consistente das desigualdades educacionais.
        """
    )

    st.divider()

    # =========================================================
    # FECHAMENTO
    # =========================================================
    st.info(
        "Este dashboard apresenta uma visão simplificada dos resultados. "
        "Para uma análise completa, metodologia detalhada e código do projeto, consulte o GitHub."
    )