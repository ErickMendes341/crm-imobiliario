import os
import urllib.parse
import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração padrão da página
st.set_page_config(
    page_title="CRM Imobiliário | Match & Vendas",
    layout="wide"
)

# Exibe a logo na barra lateral se o arquivo logo.png existir
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

# LISTA DE BAIRROS DE PASSOS - MG
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

# CONEXÃO COM SUPABASE
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if url and key:
        return create_client(url, key)
    return None

supabase = init_supabase()

# CARREGAR DADOS
def carregar_imoveis():
    if supabase:
        try:
            res = supabase.table("imoveis").select("*").execute()
            return pd.DataFrame(res.data)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def carregar_leads():
    if supabase:
        try:
            res = supabase.table("leads").select("*").execute()
            return pd.DataFrame(res.data)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# TÍTULO PRINCIPAL
st.title("🏢 CRM Imobiliário - Match & Vendas")

# ABA DE NAVEGAÇÃO PRINCIPAL
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
            
        with col2:
            valor = st.number_input("Valor do Imóvel (R$)", min_value=0.0, step=10000.0, format="%.2f")
            
        observacoes = st.text_area("Observações / Detalhes do Imóvel")
        btn_salvar_imovel = st.form_submit_button("Salvar Imóvel")
        
        if btn_salvar_imovel:
            dados_imovel = {
                "tipo": tipo_imovel,
                "bairro": bairro,
                "valor": valor,
                "observacoes": observacoes
            }
            
            if supabase:
                try:
                    supabase.table("imoveis").insert(dados_imovel).execute()
                    st.success("Imóvel cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco de dados: {e}")
            else:
                st.success("Imóvel cadastrado com sucesso (Modo Demonstração)!")

    st.divider()
    st.subheader("📋 Imóveis Cadastrados")
    df_imoveis = carregar_imoveis()
    if not df_imoveis.empty:
        st.dataframe(df_imoveis, use_container_width=True)
    else:
        st.info("Nenhum imóvel cadastrado no momento.")

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
                    "tipo_interesse": tipo_interesse,
                    "bairro_interesse": bairro_interesse,
                    "orcamento_max": orcamento_max
                }
                
                if supabase:
                    try:
                        supabase.table("leads").insert(dados_lead).execute()
                        st.success("Lead cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco de dados: {e}")
                else:
                    st.success("Lead cadastrado com sucesso (Modo Demonstração)!")

    st.divider()
    st.subheader("👥 Leads Cadastrados")
    df_leads = carregar_leads()
    if not df_leads.empty:
        st.dataframe(df_leads, use_container_width=True)
    else:
        st.info("Nenhum lead cadastrado no momento.")

# ==========================================
# 3. ABA: MATCH & OPORTUNIDADES
# ==========================================
with aba_selecionada[2]:
    st.header("Match de Imóveis e Leads")
    
    df_imoveis = carregar_imoveis()
    df_leads = carregar_leads()
    
    if df_imoveis.empty or df_leads.empty:
        st.warning("Cadastre imóveis e leads para visualizar os cruzamentos de oportunidades.")
    else:
        matches = []
        for _, lead in df_leads.iterrows():
            imoveis_compativeis = df_imoveis[
                (df_imoveis["tipo"] == lead["tipo_interesse"]) &
                (df_imoveis["bairro"] == lead["bairro_interesse"]) &
                (df_imoveis["valor"] <= lead["orcamento_max"])
            ]
            
            for _, imovel in imoveis_compativeis.iterrows():
                tel_limpo = "".join(filter(str.isdigit, str(lead.get("telefone", ""))))
                msg = f"Olá {lead['nome']}, tudo bem? Encontrei um(a) {imovel['tipo']} no bairro {imovel['bairro']} no valor de R$ {imovel['valor']:,.2f} que combina com o seu perfil!"
                link_wa = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}" if tel_limpo else "#"
                
                matches.append({
                    "Cliente (Lead)": lead["nome"],
                    "Telefone": lead.get("telefone", ""),
                    "Tipo": imovel["tipo"],
                    "Bairro": imovel["bairro"],
                    "Valor Imóvel": f"R$ {imovel['valor']:,.2f}",
                    "Contato WhatsApp": link_wa
                })
        
        if matches:
            df_match = pd.DataFrame(matches)
            st.success(f"Foram encontradas **{len(matches)} oportunidades de negócio**!")
            st.dataframe(
                df_match,
                column_config={
                    "Contato WhatsApp": st.column_config.LinkColumn("Enviar WhatsApp", display_text="📱 Chamar no WhatsApp")
                },
                use_container_width=True
            )
        else:
            st.info("Nenhum match direto encontrado entre os imóveis e leads atuais.")
