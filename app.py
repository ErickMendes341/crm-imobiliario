import streamlit as st
from supabase import create_client
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CRM Imobiliário | Match & Vendas",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONEXÃO SUPABASE ---
SUPABASE_URL = "https://dsnamhmffvjxcfqtlzet.supabase.co"
SUPABASE_KEY = "sb_publishable_XVO9PLxpxWBnr32_UYt_UA_HSdspi16"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- FUNÇÕES DE DADOS ---
def carregar_imoveis():
    res = supabase.table("imoveis").select("*").execute()
    return res.data if res.data else []

def carregar_leads():
    res = supabase.table("leads").select("*").execute()
    return res.data if res.data else []

def gerar_codigo_imovel_auto():
    imoveis = carregar_imoveis()
    proximo_num = len(imoveis) + 1
    return f"IMO-{proximo_num:03d}"  # Exemplo: IMO-001, IMO-002, etc.

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stCard {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .price-badge {
        background-color: #0284c7;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
imoveis_data = carregar_imoveis()
leads_data = carregar_leads()

# --- MENU LATERAL ---
st.sidebar.image("https://img.icons8.com/color/96/real-estate.png", width=70)
st.sidebar.title("CRM Imobiliário")
st.sidebar.caption("Gestão Inteligente de Leads & Imóveis")

menu = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📋 Imóveis Cadastrados", "📝 Novo Imóvel", "👤 Novo Lead", "🎯 Encontrar Matches"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("💡 **Sistema Ativo 24/7** — Dados sincronizados no Supabase.")

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Painel Geral de Vendas")
    st.write("Métricas em tempo real sobre seu inventário e clientes.")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    
    imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
    leads_ativos = [l for l in leads_data if l.get('status', 'Em busca') == 'Em busca']
    
    with col1:
        st.metric(label="🏠 Imóveis Disponíveis", value=len(imoveis_disponiveis))
    with col2:
        st.metric(label="👥 Leads Ativos (Em Busca)", value=len(leads_ativos))
    with col3:
        imoveis_vendidos = len(imoveis_data) - len(imoveis_disponiveis)
        st.metric(label="✅ Imóveis Vendidos", value=imoveis_vendidos)
    with col4:
        # Cálculo de matches para leads ativos com imóveis disponíveis
        total_matches = 0
        for lead in leads_ativos:
            orc = lead.get('orcamento_maximo', 0)
            bairros = lead.get('bairros_interesse', [])
            q_min = lead.get('quartos_minimos', 1)
            for im in imoveis_disponiveis:
                if im.get('valor_venda', 0) <= orc and ((not bairros) or im.get('bairro') in bairros) and im.get('quartos', 0) >= q_min:
                    total_matches += 1
        st.metric(label="🔥 Matches Ativos", value=total_matches)

# ==========================================
# 📋 ABA 2: IMÓVEIS CADASTRADOS
# ==========================================
elif menu == "📋 Imóveis Cadastrados":
    st.title("📋 Inventário de Imóveis")
    st.write("Gerencie a disponibilidade e visualize seus imóveis cadastrados.")
    
    if st.button("🔄 Atualizar Lista"):
        st.rerun()

    st.divider()

    if not imoveis_data:
        st.info("Nenhum imóvel cadastrado no momento.")
    else:
        for imovel in imoveis_data:
            status_atual = imovel.get('status', 'Disponível')
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2.5])
                
                with col1:
                    fotos_urls = imovel.get("fotos_urls")
                    if fotos_urls and len(fotos_urls) > 0:
                        st.image(fotos_urls[0], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/400x300?text=Sem+Foto", use_container_width=True)
                
                with col2:
                    c_title, c_badge = st.columns([3, 1])
                    with c_title:
                        st.subheader(f"{imovel.get('tipo')} — Cod: **{imovel.get('codigo_imovel')}**")
                    with c_badge:
                        st.markdown(f'<span class="price-badge">R$ {imovel.get("valor_venda", 0):,.2f}</span>', unsafe_allow_html=True)
                    
                    st.write(f"📍 **Bairro:** {imovel.get('bairro')} | 🛏️ **Quartos:** {imovel.get('quartos')}")
                    st.write(f"📝 {imovel.get('descricao', 'Sem descrição.')}")
                    
                    # Alterar Status
                    novo_status = st.radio(
                        "Status do Imóvel:",
                        ["Disponível", "Vendido"],
                        index=0 if status_atual == "Disponível" else 1,
                        key=f"status_imovel_{imovel.get('id')}",
                        horizontal=True
                    )
                    
                    if novo_status != status_atual:
                        supabase.table("imoveis").update({"status": novo_status}).eq("id", imovel.get("id")).execute()
                        st.success(f"Status atualizado para: **{novo_status}**!")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📝 ABA 3: NOVO IMÓVEL (CÓDIGO AUTO)
# ==========================================
elif menu == "📝 Novo Imóvel":
    st.title("📝 Cadastrar Novo Imóvel")
    st.write("O código do imóvel é gerado automaticamente para evitar duplicidades.")
    st.divider()

    codigo_gerado = gerar_codigo_imovel_auto()

    with st.form("form_imovel", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Código do Imóvel (Automático)", value=codigo_gerado, disabled=True)
            tipo = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura"])
            bairro = st.text_input("Bairro *", "Centro")
        with col2:
            valor = st.number_input("Valor de Venda (R$) *", min_value=0.0, value=350000.0, step=10000.0)
            quartos = st.slider("Quantidade de Quartos", 1, 6, 3)
            descricao = st.text_area("Descrição / Detalhes do Imóvel")
        
        fotos = st.file_uploader("📷 Fotos do Imóvel (JPG ou PNG)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        submitted = st.form_submit_button("💾 Salvar Imóvel", use_container_width=True)
        
        if submitted:
            urls_fotos = []
            if fotos:
                for foto in fotos:
                    caminho_storage = f"imoveis/{codigo_gerado}_{foto.name}"
                    res = supabase.storage.from_("fotos-imoveis").upload(caminho_storage, foto.getvalue(), {"content-type": foto.type})
                    url_publica = supabase.storage.from_("fotos-imoveis").get_public_url(caminho_storage)
                    urls_fotos.append(url_publica)
            
            dados_imovel = {
                "codigo_imovel": codigo_gerado,
                "tipo": tipo,
                "bairro": bairro,
                "valor_venda": valor,
                "quartos": quartos,
                "descricao": descricao,
                "fotos_urls": urls_fotos,
                "status": "Disponível"
            }
            supabase.table("imoveis").insert(dados_imovel).execute()
            st.success(f"✅ Imóvel **{codigo_gerado}** cadastrado com sucesso!")

# ==========================================
# 👤 ABA 4: NOVO LEAD
# ==========================================
elif menu == "👤 Novo Lead":
    st.title("👤 Cadastrar Novo Lead")
    st.write("Registre potenciais compradores para o Match Automático.")
    st.divider()

    with st.form("form_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Cliente *")
            whatsapp = st.text_input("WhatsApp com DDD *", "+5511999999999")
        with col2:
            bairro_interesse = st.text_input("Bairro de Interesse *", "Centro")
            orcamento = st.number_input("Orçamento Máximo (R$) *", min_value=0.0, value=500000.0, step=10000.0)
        
        quartos_min = st.slider("Mínimo de Quartos Desejados", 1, 6, 2)
        
        submitted_lead = st.form_submit_button("💾 Salvar Lead", use_container_width=True)
        if submitted_lead:
            dados_lead = {
                "nome": nome,
                "whatsapp": whatsapp,
                "bairros_interesse": [bairro_interesse],
                "orcamento_maximo": orcamento,
                "quartos_minimos": quartos_min,
                "status": "Em busca"
            }
            supabase.table("leads").insert(dados_lead).execute()
            st.success(f"✅ Lead **{nome}** cadastrado com sucesso!")

# ==========================================
# 🎯 ABA 5: MATCH INTELIGENTE
# ==========================================
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Automação de Match Imobiliário")
    st.write("Cruza apenas imóveis **Disponíveis** com clientes **Em busca**.")
    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado para realizar o cruzamento.")
    else:
        for lead in leads_data:
            status_lead = lead.get('status', 'Em busca')
            
            st.subheader(f"👤 Cliente: {lead.get('nome', 'Sem nome')}")
            
            # Atualizar Status do Lead
            novo_status_lead = st.radio(
                "Status do Cliente:",
                ["Em busca", "Já comprou"],
                index=0 if status_lead == "Em busca" else 1,
                key=f"status_lead_{lead.get('id')}",
                horizontal=True
            )
            
            if novo_status_lead != status_lead:
                supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead.get("id")).execute()
                st.success(f"Status do Lead atualizado para: **{novo_status_lead}**!")
                st.rerun()

            if novo_status_lead == "Já comprou":
                st.success("🎉 Cliente com compra concluída! Não serão exibidos novos matches.")
                st.divider()
                continue

            whatsapp_num = lead.get('whatsapp', '').replace("+", "").replace(" ", "").replace("-", "")
            orcamento = lead.get('orcamento_maximo', 0)
            bairros = lead.get('bairros_interesse', [])
            quartos_min = lead.get('quartos_minimos', 1)
            
            st.caption(f"💰 Orçamento Máx: **R$ {orcamento:,.2f}** | 📍 Bairro: **{', '.join(bairros)}** | 🛏️ Mín. Quartos: **{quartos_min}**")
            
            # Filtra somente imóveis que estão Disponíveis
            imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
            
            matches = []
            for imovel in imoveis_disponiveis:
                preco_ok = imovel.get('valor_venda', 0) <= orcamento
                bairro_ok = (not bairros) or (imovel.get('bairro') in bairros)
                quartos_ok = imovel.get('quartos', 0) >= quartos_min
                
                if preco_ok and bairro_ok and quartos_ok:
                    matches.append(imovel)
            
            if matches:
                for m in matches:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"🏠 **{m.get('tipo')} [{m.get('codigo_imovel')}]** — R$ {m.get('valor_venda'):,.2f} ({m.get('quartos')} quartos no {m.get('bairro')})")
                    with c2:
                        foto_link = m.get('fotos_urls')[0] if m.get('fotos_urls') else 'Sem foto'
                        texto_msg = f"Olá {lead.get('nome')}! Encontrei o imóvel ideal para você: {m.get('tipo')} no {m.get('bairro')} por R$ {m.get('valor_venda'):,.2f}. Confira fotos aqui: {foto_link}"
                        link_wa = f"https://wa.me/{whatsapp_num}?text={urllib.parse.quote(texto_msg)}"
                        st.markdown(f"[📲 **Enviar WhatsApp**]({link_wa})")
            else:
                st.warning("Nenhum imóvel disponível compatível no momento.")
            st.divider()
