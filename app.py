import os
import urllib.parse
import streamlit as st
from supabase import create_client

# --- CONFIGURAÇÃO DA PÁGINA & PWA ---
st.set_page_config(
    page_title="CRM Imobiliário | Match & Vendas",
    page_icon="logo.png" if os.path.exists("logo.png") else "🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOGO NA BARRA LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

# --- CORRETORES ---
CORRETORES = ["Erick Mendes", "Pedro Siqueira"]

# --- LISTA DE BAIRROS DE PASSOS - MG ---
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

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if url and key:
        return create_client(url, key)
    return None

supabase = init_supabase()

# --- ABA DE NAVEGAÇÃO PRINCIPAL ---
st.title("🏢 CRM Imobiliário - Mendes & Soares")
aba_selecionada = st.tabs(["🏠 Cadastro de Imóveis", "👤 Cadastro de Leads", "🤝 Match & Oportunidades"])

# ==========================================
# 1. ABA: CADASTRO DE IMÓVEIS
# ==========================================
with aba_selecionada[0]:
    st.header("Cadastrar Novo Imóvel")
    
    with st.form("form_imovel", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_imovel = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Comercial", "Rural"])
            bairro = st.selectbox("Bairro (Passos - MG)", BAIRROS_PASSOS)
            endereco = st.text_input("Endereço Completo (Rua, Número, Complemento)")
            valor = st.number_input("Valor do Imóvel (R$)", min_value=0.0, step=10000.0, format="%.2f")
            
        with col2:
            proprietario_nome = st.text_input("Nome do Proprietário")
            proprietario_telefone = st.text_input("Telefone do Proprietário (com DDD)")
            corretor_captacao = st.selectbox("Corretor Responsável pela Captação", CORRETORES)
            observacoes = st.text_area("Observações / Detalhes do Imóvel")
            
        btn_salvar_imovel = st.form_submit_button("Salvar Imóvel")
        
        if btn_salvar_imovel:
            if not endereco or not proprietario_nome:
                st.error("Por favor, preencha o endereço e o nome do proprietário.")
            else:
                dados_imovel = {
                    "tipo": tipo_imovel,
                    "bairro": bairro,
                    "endereco": endereco,
                    "valor": valor,
                    "proprietario_nome": proprietario_nome,
                    "proprietario_telefone": proprietario_telefone,
                    "corretor_captacao": corretor_captacao,
                    "observacoes": observacoes
                }
                
                if supabase:
                    try:
                        supabase.table("imoveis").insert(dados_imovel).execute()
                        st.success("Imóvel cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco de dados: {e}")
                else:
                    st.success("Imóvel cadastrado com sucesso (Modo demonstração/Local)!")

# ==========================================
# 2. ABA: CADASTRO DE LEADS (CLIENTES)
# ==========================================
with aba_selecionada[1]:
    st.header("Cadastrar Novo Lead (Cliente)")
    
    with st.form("form_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_lead = st.text_input("Nome do Cliente")
            telefone_lead = st.text_input("Telefone do Cliente (com DDD)")
            corretor_lead = st.selectbox("Corretor que Encontrou o Lead", CORRETORES)
            
        with col2:
            tipo_interesse = st.selectbox("Interesse", ["Casa", "Apartamento", "Terreno", "Comercial", "Rural"])
            bairro_interesse = st.selectbox("Bairro de Preferência", BAIRROS_PASSOS)
            orcamento_max = st.number_input("Orçamento Máximo (R$)", min_value=0.0, step=10000.0, format="%.2f")
            
        btn_salvar_lead = st.form_submit_button("Salvar Lead")
        
        if btn_salvar_lead:
            if not nome_lead:
                st.error("Por favor, preencha o nome do cliente.")
            else:
                dados_lead = {
                    "nome": nome_lead,
                    "telefone": telefone_lead,
                    "corretor_lead": corretor_lead,
                    "tipo_interesse": tipo_interesse,
                    "bairro_interesse": bairro_interesse,
                    "orcamento_max": orcamento_max
                }
                
                if supabase:
                    try:
                        supabase.table("leads").insert(dados_lead).execute()
                        st.success("Lead cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco de dados: {e}")
                else:
                    st.success("Lead cadastrado com sucesso (Modo demonstração/Local)!")

# ==========================================
# 3. ABA: MATCH & OPORTUNIDADES
# ==========================================
with aba_selecionada[2]:
    st.header("Match de Imóveis e Leads")
    st.info("Esta aba cruza automaticamente os interesses dos clientes com os imóveis cadastrados pelos corretores.")
