from __future__ import annotations

from typing import Optional
import pandas as pd
import streamlit as st


def opcoes_ordenadas(df: pd.DataFrame, coluna: str) -> list[str]:
    """
    Retorna valores únicos ordenados de uma coluna.
    """
    if coluna not in df.columns:
        return []

    return sorted(
        df[coluna]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )


def valor_escola_para_funcao(escola: Optional[str]) -> Optional[str]:
    """
    Normaliza valor de escola para funções de gráfico.
    """
    if escola in (None, "Todas"):
        return None
    return escola


def materia_boxplot(materia_global: str) -> str:
    """
    Boxplot não suporta 'Média Geral'.
    Usa fallback para Matemática.
    """
    return "Matemática" if materia_global == "Média Geral" else materia_global


def plot(fig, key: str) -> None:
    """
    Wrapper padrão para plotly no Streamlit.
    """
    if fig is None:
        st.warning("Gráfico indisponível.")
        return

    st.plotly_chart(fig, width="stretch", key=key)

def txt_distribuicao():
    st.caption(
        "A composição dos participantes revela um padrão estrutural: regiões com menor renda concentram maior proporção de alunos da rede pública, "
        "reforçando a associação entre condição socioeconômica e acesso educacional."
    )


def txt_escolaridade_escola():
    st.caption(
        "A escolaridade dos responsáveis apresenta forte associação com o tipo de escola frequentada. "
        "Níveis mais elevados de escolaridade parental estão correlacionados a maior presença em escolas privadas, "
        "indicando o papel do capital familiar na trajetória educacional."
    )


def txt_renda_pais():
    st.caption(
        "O aumento da escolaridade dos responsáveis está associado a níveis mais elevados de renda familiar, "
        "evidenciando a transmissão intergeracional de capital socioeconômico como fator relevante no desempenho educacional."
    )


def txt_bubble_relacao():
    st.caption(
        "A análise multivariada evidencia uma relação positiva entre renda média e desempenho, com variação explicativa elevada. "
        "A dispersão observada sugere que, embora a renda seja um fator dominante, outros elementos — como acesso à infraestrutura "
        "e características institucionais — também influenciam os resultados."
    )


def txt_renda_nota_simples():
    st.caption(
        "Regiões com menor renda média apresentam, de forma consistente, desempenho médio inferior."
    )


def txt_desigualdade():
    st.caption(
        "As diferenças de desempenho entre faixas de renda permanecem estáveis ao longo do tempo, caracterizando um padrão estrutural de desigualdade educacional. "
        "Mesmo dentro da mesma faixa de renda, estudantes de escolas privadas apresentam desempenho superior, sugerindo efeito adicional de fatores institucionais."
    )


def txt_tecnologia():
    st.caption(
        "O acesso a recursos tecnológicos, como celulares e computadores, apresenta associação positiva com o desempenho médio. "
        "Esse padrão é consistente entre Minas Gerais e o Brasil, indicando que infraestrutura digital pode atuar como fator complementar ao aprendizado."
    )


def txt_r2():
    st.caption(
        "A relação entre renda e desempenho apresenta alta correlação (R² elevado), indicando forte associação entre variáveis. "
        "Ainda assim, trata-se de relação não causal, podendo ser influenciada por fatores não observados."
    )


def txt_renda_nota_mg():
    st.caption(
        "Embora a renda média em Minas Gerais seja inferior à de estados mais ricos, o desempenho médio se mantém elevado. "
        "Esse resultado sugere a presença de fatores estruturais adicionais — como qualidade da rede educacional — "
        "que mitigam parcialmente os efeitos da renda sobre o desempenho."
    )


def txt_consumo():
    st.caption(
        "O índice de consumo foi construído a partir da normalização de bens e infraestrutura domiciliar (ex.: eletrodomésticos, veículos e acesso a serviços), "
        "agregados em uma métrica única entre 0 e 1. Esse indicador atua como proxy de nível socioeconômico, "
        "permitindo capturar dimensões de bem-estar não refletidas diretamente pela renda declarada."
    )


def txt_conclusao():
    st.markdown(
        """#### Conclusão

Os resultados indicam que o desempenho no ENEM está fortemente associado a fatores socioeconômicos, 
especialmente renda familiar, escolaridade dos responsáveis e acesso a recursos.

Entretanto, diferenças regionais sugerem que fatores institucionais e estruturais também desempenham papel relevante, 
indicando que políticas públicas podem mitigar — ainda que parcialmente — desigualdades de origem.
"""
    )