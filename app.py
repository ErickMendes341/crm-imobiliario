import os
import urllib.parse
import streamlit as st
from supabase import create_client

# --- CONFIGURAÇÃO DA PÁGINA & PWA ---
st.set_page_config(
    page_title="CRM Imobiliário | Match & Vendas",
    page_icon="logo.png" if os.path.exists("logo.png") else "🏢",
    layout="wide",
    initial_sidebar_state="collapsed"  # Ideal para navegação em celulares
)

# --- LOGO NA BARRA LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

# --- LISTA DE BAIRROS DE PASSOS - MG (ORDEM ALFABÉTICA) ---
BAIRROS_PASSOS = sorted([
    "Aclimação", "Alto dos Maias", "Alvorada", "Antenas", "Aroeiras",
    "Bela Vista 1 e 2", "Belo Horizonte", "Califórnia", "Canadá 1, 2 e 3",
    "Canjeranus", "Carmelo", "Centro", "Cohab 4", "Cohab 5", "Coimbras",
    "Condomínio da Nações", "Condomínio Monte Belo", "Eldorado", "Exposição",
    "Flamboyant", "Jacarandá", "Jardim América", "Jardim Cidade",
    "Jardim Colégio de Passos", "Jardim Europa", "Jardim Florença",
    "Jardim dos Lagos", "Mirante do Vale", "Muarama", "Nossa Senhora das Graças",
    "Nova Califórnia", "Nova Passos", "Novo Horizonte", "Nsa de Fátima",
    "Olímpico", "Penha", "Planalto", "Rancho Alegre", "Recreio",
    "Rochas", "Saci", "Santa Luzia", "São Benedito", "São Francisco",
    "São João", "São Luís", "São Pedro", "Vila Agreny", "Vila Esperança",
    "Vila Manganelli", "Vila Rica"
])

# Adicione aqui o restante das suas funções de conexão com Supabase e lógica do CRM...
