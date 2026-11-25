import streamlit as st


def render():
    st.markdown('<div class="eyebrow">CONHE&Ccedil;A A SOLU&Ccedil;&Atilde;O</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Sobre o projeto</h1>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Alimenta Escola &mdash; tecnologia a servi&ccedil;o da alimenta&ccedil;&atilde;o escolar.</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <div class="info-heading">&#127919; Objetivo</div>
        <div class="info-text">Apoiar o planejamento da merenda por meio da estimativa da demanda, ajudando a reduzir sobras e desperd&iacute;cio de alimentos.</div>
    </div>
    <div class="info-card">
        <div class="info-heading">&#129504; Intelig&ecirc;ncia artificial</div>
        <div class="info-text">
            O projeto prev&ecirc; a integra&ccedil;&atilde;o de um modelo de Machine Learning
            para estimar a quantidade de refei&ccedil;&otilde;es necess&aacute;rias.
            A previs&atilde;o depende da integra&ccedil;&atilde;o do modelo e dos dados preparados pela equipe.
        </div>
    </div>
    <div class="info-card">
        <div class="info-heading">&#128187; Tecnologias</div>
        <div class="info-text">Python &middot; Streamlit &middot; Pandas &middot; Scikit-learn</div>
    </div>
    """, unsafe_allow_html=True)
