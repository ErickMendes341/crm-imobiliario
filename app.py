import streamlit as st
from supabase import create_client
import urllib.parse
import os
from datetime import date, datetime

# ==========================================
# 🎨 PALETA DE CORES MENDES & SOARES
# ==========================================
COR_AZUL_MARINHO = "#181e29"  # Fundo da logo / Sidebar / Títulos
COR_DOURADO = "#c59b27"       # Dourado vibrante dos botões e destaques
COR_DOURADO_HOVER = "#a37f1e" # Dourado mais escuro para efeito ao passar o mouse
COR_FUNDO_PAGINA = "#f4f6f8"   # Cinza suave premium para leitura agradável
COR_CARD = "#ffffff"          # Fundo branco para os cards
COR_TEXTO = "#101620"          # Texto escuro refinado

# --- LISTA DE CORRETORES ---
CORRETORES = ["Erick Mendes", "Pedro Siqueira"]

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Mendes & Soares | Engenharia e Imóveis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LISTA DE BAIRROS DE PASSOS - MG ---
BAIRROS_PASSOS = sorted([
    "Aclimação", "Alto dos Maias", "Alvorada", "Antenas", "Aroeiras",
    "Bela Vista 1 e 2", "Belo Horizonte", "Califórnia", "Canadá 1, 2 e 3",
    "Canjeranus", "Carmelo", "Centro", "Cohab 4", "Cohab 5", "Coimbras",
    "Condomínio da Nações", "Condomínio Monte Belo", "Eldorado", "Exposição",
    "Flamboyant", "Jacarandá", "Jardim América", "Jardim Cidade",
    "Jardim Colégio de Passos", "Jardim Europa", "Jardim Florença",
    "Jardim dos Lagos", "Mirante do Vale", "Muarama", "Nossa Senhora das Graças",
    "Nova California", "Nova Passos", "Novo Horizonte", "Nsa de Fátima",
    "Panorama", "Parque das Oliveiras", "Penha", "Penha 2", "Planalto",
    "Polivalente", "Primavera", "Recanto do Bosque", "Santa Luzia", "São Benedito",
    "São Francisco", "Tropical", "Vale Verde 1 e 2", "Vilagio D´Italia", "Vila Rica"
])

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

def carregar_visitas():
    try:
        res = supabase.table("visitas").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

def gerar_codigo_imovel_auto():
    imoveis = carregar_imoveis()
    proximo_num = len(imoveis) + 1
    return f"MS-{proximo_num:03d}"

# --- ESTILIZAÇÃO CSS PERSONALIZADA MENDES & SOARES ---
st.markdown(f"""
    <style>
    /* Fundo da aplicação */
    .stApp {{
        background-color: {COR_FUNDO_PAGINA};
        color: {COR_TEXTO};
    }}
    
    /* Estilização da Sidebar Lateral */
    section[data-testid="stSidebar"] {{
        background-color: {COR_AZUL_MARINHO} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        color: #e2e8f0 !important;
    }}

    /* Estilização dos Cards do CRM */
    .stCard {{
        background-color: {COR_CARD};
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(24, 30, 41, 0.06);
        margin-bottom: 24px;
        border-left: 6px solid {COR_DOURADO};
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stCard:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(24, 30, 41, 0.12);
    }}

    /* Badge Elegante de Preço */
    .price-badge {{
        background: linear-gradient(135deg, {COR_DOURADO}, {COR_DOURADO_HOVER});
        color: #ffffff;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1em;
        display: inline-block;
        text-align: center;
        box-shadow: 0 2px 6px rgba(197, 155, 39, 0.3);
    }}

    /* Tags de Diferenciais */
    .feature-tag {{
        background-color: #f1f5f9;
        color: {COR_AZUL_MARINHO};
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid #cbd5e1;
    }}

    /* Botões Primários Estilizados em Dourado */
    div.stButton > button[kind="primary"] {{
        background-color: {COR_DOURADO} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: {COR_DOURADO_HOVER} !important;
        box-shadow: 0 4px 12px rgba(197, 155, 39, 0.4) !important;
    }}

    /* Títulos */
    h1, h2, h3 {{
        color: {COR_AZUL_MARINHO} !important;
        font-weight: 700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
imoveis_data = carregar_imoveis()
leads_data = carregar_leads()
visitas_data = carregar_visitas()

# --- MENU LATERAL COM A LOGO MENDES & SOARES ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown(f"<h2 style='text-align: center; color:{COR_DOURADO};'>MENDES & SOARES</h2>", unsafe_allow_html=True)
        st.caption("<p style='text-align: center; color: #cbd5e1;'>Engenharia e Imóveis</p>", unsafe_allow_html=True)
    
    st.divider()

    menu = st.radio(
        "Navegação do Sistema:",
        [
            "📊 Dashboard", 
            "📋 Imóveis Cadastrados", 
            "📝 Novo Imóvel", 
            "👤 Novo Lead", 
            "👥 Gerenciar Leads", 
            "🎯 Encontrar Matches",
            "📅 Visitas Agendadas"
        ],
        index=0
    )

    st.divider()
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #94a3b8;'>📍 Passos - MG<br>📞 (35) 9 9810-2465</p>", unsafe_allow_html=True)

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Painel Geral — Mendes & Soares")
    st.write("Métricas operacionais e gestão estratégica em tempo real.")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    
    imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
    leads_ativos = [l for l in leads_data if l.get('status', 'Em busca') == 'Em busca']
    visitas_pendentes = [v for v in visitas_data if v.get('status', 'Agendada') == 'Agendada']
    
    with col1:
        st.metric(label="🏠 Imóveis Disponíveis", value=len(imoveis_disponiveis))
    with col2:
        st.metric(label="👥 Leads Ativos", value=len(leads_ativos))
    with col3:
        st.metric(label="📅 Visitas Agendadas", value=len(visitas_pendentes))
    with col4:
        imoveis_vendidos = len(imoveis_data) - len(imoveis_disponiveis)
        st.metric(label="✅ Imóveis Vendidos", value=imoveis_vendidos)

# ==========================================
# 📋 ABA 2: IMÓVEIS CADASTRADOS
# ==========================================
elif menu == "📋 Imóveis Cadastrados":
    st.title("📋 Inventário de Imóveis")
    st.write("Consulte, filtre e gerencie seu catálogo de imóveis em Passos-MG.")
    
    with st.expander("🔍 **Filtros e Busca de Imóveis**", expanded=True):
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1.2, 1.5, 1.2, 1.2, 2])
        
        with f_col1:
            busca_codigo = st.text_input("🔎 Código", placeholder="Ex: MS-001", key="busca_codigo")
        with f_col2:
            filtro_bairro_imovel = st.selectbox("📍 Bairro", ["Todos"] + BAIRROS_PASSOS, key="filtro_bairro_imovel")
        with f_col3:
            filtro_tipo = st.selectbox("🏠 Tipo", ["Todos", "Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"], key="filtro_tipo")
        with f_col4:
            filtro_status = st.selectbox("📌 Status", ["Todos", "Disponível", "Vendido"], index=1, key="filtro_status")
        with f_col5:
            valores = [float(i.get('valor_venda', 0)) for i in imoveis_data] if imoveis_data else [0.0, 1000000.0]
            max_val = max(valores) if valores and max(valores) > 0 else 2000000.0
            filtro_preco_max = st.slider("💰 Valor Máximo (R$)", min_value=0.0, max_value=max_val, value=max_val, step=50000.0, format="R$ %d")

    st.divider()

    imoveis_filtrados = imoveis_data
    if busca_codigo:
        termo_cod = busca_codigo.lower().strip()
        imoveis_filtrados = [i for i in imoveis_filtrados if termo_cod in i.get('codigo_imovel', '').lower()]
    if filtro_bairro_imovel != "Todos":
        imoveis_filtrados = [i for i in imoveis_filtrados if i.get('bairro') == filtro_bairro_imovel]
    if filtro_tipo != "Todos":
        imoveis_filtrados = [i for i in imoveis_filtrados if i.get('tipo') == filtro_tipo]
    if filtro_status != "Todos":
        imoveis_filtrados = [i for i in imoveis_filtrados if i.get('status', 'Disponível') == filtro_status]
    
    imoveis_filtrados = [i for i in imoveis_filtrados if float(i.get('valor_venda', 0)) <= filtro_preco_max]

    st.caption(f"Exibindo **{len(imoveis_filtrados)}** de **{len(imoveis_data)}** imóveis.")

    if not imoveis_filtrados:
        st.info("Nenhum imóvel encontrado com os filtros selecionados.")
    else:
        for imovel in imoveis_filtrados:
            status_atual = imovel.get('status', 'Disponível')
            imovel_id = imovel.get('id')
            
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2.5])
                
                with col1:
                    fotos_urls = imovel.get("fotos_urls") or []
                    if fotos_urls:
                        key_foto = f"foto_idx_{imovel_id}"
                        if key_foto not in st.session_state:
                            st.session_state[key_foto] = 0
                        
                        foto_idx = st.session_state[key_foto]
                        if foto_idx >= len(fotos_urls):
                            foto_idx = 0
                            st.session_state[key_foto] = 0

                        st.image(fotos_urls[foto_idx], use_container_width=True)
                        if len(fotos_urls) > 1:
                            btn_prev, btn_info, btn_next = st.columns([1, 2, 1])
                            with btn_prev:
                                if st.button("◀", key=f"prev_{imovel_id}"):
                                    st.session_state[key_foto] = (foto_idx - 1) % len(fotos_urls)
                                    st.rerun()
                            with btn_info:
                                st.caption(f"🖼️ {foto_idx + 1} / {len(fotos_urls)}")
                            with btn_next:
                                if st.button("▶", key=f"next_{imovel_id}"):
                                    st.session_state[key_foto] = (foto_idx + 1) % len(fotos_urls)
                                    st.rerun()
                    else:
                        st.image("https://via.placeholder.com/400x300?text=Mendes+%26+Soares", use_container_width=True)
                
                with col2:
                    c_title, c_badge = st.columns([3, 1.2])
                    with c_title:
                        st.subheader(f"{imovel.get('tipo')} — Cód: **{imovel.get('codigo_imovel')}**")
                    with c_badge:
                        st.markdown(f'<span class="price-badge">R$ {imovel.get("valor_venda", 0):,.2f}</span>', unsafe_allow_html=True)
                    
                    bairro_txt = imovel.get('bairro', '')
                    endereco_txt = imovel.get('endereco', '')
                    info_local = f"📍 **Bairro:** {bairro_txt}"
                    if endereco_txt:
                        info_local += f" | **Endereço:** {endereco_txt}"
                    st.write(info_local)

                    nome_prop = imovel.get('nome_proprietario', 'Não informado')
                    tel_prop = imovel.get('telefone_proprietario', '')
                    corr_cap = imovel.get('corretor_captacao', 'Não informado')
                    info_prop = f"👤 **Proprietário:** {nome_prop}"
                    if tel_prop:
                        info_prop += f" ({tel_prop})"
                    info_prop += f" | 🔑 **Captação:** {corr_cap}"
                    st.write(info_prop)

                    detalhes = f"🛏️ {imovel.get('quartos', 0)} Quarto(s) | 🚿 {imovel.get('suites', 0)} Suíte(s) | 🚽 {imovel.get('banheiros', 0)} Banheiro(s) | 🚗 {imovel.get('vagas_garagem', 0)} Vaga(s)"
                    if imovel.get('area_terreno'):
                        detalhes += f" | 📐 Lote: {imovel.get('area_terreno')} m²"
                    if imovel.get('area_construida'):
                        detalhes += f" | 🏗️ Área Const.: {imovel.get('area_construida')} m²"
                    
                    st.write(detalhes)
                    
                    tags_html = ""
                    if imovel.get('garagem_coberta'): tags_html += '<span class="feature-tag">🚗 Garagem Coberta</span>'
                    if imovel.get('area_gourmet'): tags_html += '<span class="feature-tag">🍖 Área Gourmet</span>'
                    if imovel.get('sala'): tags_html += '<span class="feature-tag">🛋️ Sala</span>'
                    if imovel.get('copa'): tags_html += '<span class="feature-tag">🍽️ Copa</span>'
                    if imovel.get('cozinha'): tags_html += '<span class="feature-tag">🍳 Cozinha</span>'
                    
                    if tags_html:
                        st.markdown(tags_html, unsafe_allow_html=True)
                    
                    st.write(f"📝 {imovel.get('descricao', 'Sem descrição.')}")
                    
                    c_status, c_actions = st.columns([2, 1])
                    with c_status:
                        novo_status = st.radio(
                            "Status do Imóvel:",
                            ["Disponível", "Vendido"],
                            index=0 if status_atual == "Disponível" else 1,
                            key=f"status_imovel_{imovel_id}",
                            horizontal=True
                        )
                        if novo_status != status_atual:
                            supabase.table("imoveis").update({"status": novo_status}).eq("id", imovel_id).execute()
                            st.success(f"Status atualizado para: **{novo_status}**!")
                            st.rerun()

                # --- EXCLUIR IMÓVEL ---
                with st.expander(f"🗑️ Excluir Imóvel {imovel.get('codigo_imovel')}"):
                    st.warning("⚠️ Esta ação é permanente e removerá o imóvel da base de dados.")
                    confirma_excluir = st.checkbox("Confirmar exclusão deste imóvel", key=f"chk_del_{imovel_id}")
                    if st.button("🚨 Excluir Definitivamente", key=f"btn_del_{imovel_id}", type="primary"):
                        if confirma_excluir:
                            supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                            st.success(f"Imóvel **{imovel.get('codigo_imovel')}** removido com sucesso!")
                            st.rerun()

                # --- EDITAR IMÓVEL ---
                with st.expander(f"✏️ Editar imóvel {imovel.get('codigo_imovel')}"):
                    with st.form(key=f"form_edit_imovel_{imovel_id}"):
                        e_c1, e_c2, e_c3 = st.columns(3)
                        tipos_list = ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"]
                        idx_tipo = tipos_list.index(imovel.get('tipo')) if imovel.get('tipo') in tipos_list else 0
                        idx_bairro = BAIRROS_PASSOS.index(imovel.get('bairro')) if imovel.get('bairro') in BAIRROS_PASSOS else 0
                        idx_corretor = CORRETORES.index(imovel.get('corretor_captacao')) if imovel.get('corretor_captacao') in CORRETORES else 0

                        with e_c1:
                            e_tipo = st.selectbox("Tipo de Imóvel", tipos_list, index=idx_tipo, key=f"e_tipo_{imovel_id}")
                            e_nome_prop = st.text_input("Nome do Proprietário", value=imovel.get('nome_proprietario', ''), key=f"e_np_{imovel_id}")
                        with e_c2:
                            e_bairro = st.selectbox("Bairro (Passos-MG)", BAIRROS_PASSOS, index=idx_bairro, key=f"e_bairro_{imovel_id}")
                            e_tel_prop = st.text_input("Telefone do Proprietário", value=imovel.get('telefone_proprietario', ''), key=f"e_tp_{imovel_id}")
                            e_valor = st.number_input("Valor de Venda (R$)", min_value=0.0, value=float(imovel.get('valor_venda', 0.0)), step=10000.0, key=f"e_valor_{imovel_id}")
                        with e_c3:
                            e_corretor = st.selectbox("Corretor Captação", CORRETORES, index=idx_corretor, key=f"e_corr_{imovel_id}")
                            e_endereco = st.text_input("Endereço do Imóvel", value=imovel.get('endereco', ''), key=f"e_end_{imovel_id}")
                            e_area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, value=float(imovel.get('area_terreno', 0.0) or 0.0), step=10.0, key=f"e_at_{imovel_id}")
                            e_area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=float(imovel.get('area_construida', 0.0) or 0.0), step=10.0, key=f"e_ac_{imovel_id}")

                        st.divider()
                        e_cq1, e_cq2, e_cq3, e_cq4 = st.columns(4)
                        with e_cq1: e_quartos = st.number_input("Dormitórios", min_value=0, value=int(imovel.get('quartos', 0) or 0), step=1, key=f"e_q_{imovel_id}")
                        with e_cq2: e_suites = st.number_input("Suítes", min_value=0, value=int(imovel.get('suites', 0) or 0), step=1, key=f"e_s_{imovel_id}")
                        with e_cq3: e_banheiros = st.number_input("Banheiros", min_value=0, value=int(imovel.get('banheiros', 0) or 0), step=1, key=f"e_b_{imovel_id}")
                        with e_cq4: e_vagas = st.number_input("Vagas Garagem", min_value=0, value=int(imovel.get('vagas_garagem', 0) or 0), step=1, key=f"e_v_{imovel_id}")

                        st.divider()
                        e_c5, e_c6 = st.columns(2)
                        with e_c5:
                            e_sala = st.checkbox("Sala", value=bool(imovel.get('sala', True)), key=f"e_sala_{imovel_id}")
                            e_copa = st.checkbox("Copa", value=bool(imovel.get('copa', False)), key=f"e_copa_{imovel_id}")
                            e_cozinha = st.checkbox("Cozinha", value=bool(imovel.get('cozinha', True)), key=f"e_cozinha_{imovel_id}")
                        with e_c6:
                            e_garagem_coberta = st.checkbox("🚘 Garagem Coberta", value=bool(imovel.get('garagem_coberta', False)), key=f"e_gc_{imovel_id}")
                            e_area_gourmet = st.checkbox("🍖 Área Gourmet", value=bool(imovel.get('area_gourmet', False)), key=f"e_ag_{imovel_id}")

                        e_descricao = st.text_area("Descrição", value=imovel.get('descricao', ''), key=f"e_desc_{imovel_id}")
                        
                        btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
                        if btn_salvar_edicao:
                            payload = {
                                "tipo": str(e_tipo),
                                "bairro": str(e_bairro),
                                "valor_venda": float(e_valor),
                                "nome_proprietario": str(e_nome_prop),
                                "telefone_proprietario": str(e_tel_prop),
                                "endereco": str(e_endereco),
                                "corretor_captacao": str(e_corretor),
                                "quartos": int(e_quartos),
                                "suites": int(e_suites),
                                "banheiros": int(e_banheiros),
                                "vagas_garagem": int(e_vagas),
                                "garagem_coberta": bool(e_garagem_coberta),
                                "area_gourmet": bool(e_area_gourmet),
                                "sala": bool(e_sala),
                                "copa": bool(e_copa),
                                "cozinha": bool(e_cozinha),
                                "area_terreno": float(e_area_terreno) if e_area_terreno else 0.0,
                                "area_construida": float(e_area_construida) if e_area_construida else 0.0,
                                "descricao": str(e_descricao)
                            }
                            
                            colunas_existentes = list(imovel.keys())
                            dados_atualizados = {k: v for k, v in payload.items() if k in colunas_existentes}
                            
                            try:
                                supabase.table("imoveis").update(dados_atualizados).eq("id", imovel_id).execute()
                                st.success("✅ Imóvel atualizado com sucesso!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erro ao atualizar no Supabase: {err}")

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📝 ABA 3: NOVO IMÓVEL
# ==========================================
elif menu == "📝 Novo Imóvel":
    st.title("📝 Cadastrar Novo Imóvel")
    st.write("Adicione um novo imóvel ao inventário da Mendes & Soares.")
    st.divider()

    codigo_gerado = gerar_codigo_imovel_auto()

    with st.form("form_imovel", clear_on_submit=True):
        st.subheader("📌 Informações Básicas")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("Código do Imóvel", value=codigo_gerado, disabled=True)
            tipo = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"])
            corretor_captacao = st.selectbox("Corretor que Captou *", CORRETORES)
        with c2:
            bairro = st.selectbox("Bairro (Passos-MG) *", BAIRROS_PASSOS)
            valor = st.number_input("Valor de Venda (R$) *", min_value=0.0, value=350000.0, step=10000.0)
            endereco = st.text_input("Endereço / Rua e Número")
        with c3:
            area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, value=250.0, step=10.0)
            area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=120.0, step=10.0)

        st.divider()
        st.subheader("👤 Dados do Proprietário")
        cp1, cp2 = st.columns(2)
        with cp1:
            nome_proprietario = st.text_input("Nome do Proprietário *")
        with cp2:
            telefone_proprietario = st.text_input("Telefone do Proprietário", placeholder="(35) 99999-9999")

        st.divider()
        st.subheader("🛏️ Cômodos e Vagas")
        c4, c5, c6, c7 = st.columns(4)
        with c4: quartos = st.number_input("Dormitórios / Quartos", min_value=0, value=3, step=1)
        with c5: suites = st.number_input("Suítes", min_value=0, value=1, step=1)
        with c6: banheiros = st.number_input("Banheiros (Total)", min_value=0, value=2, step=1)
        with c7: vagas = st.number_input("Vagas de Garagem", min_value=0, value=2, step=1)

        st.divider()
        st.subheader("✨ Ambientes e Diferenciais")
        cd1, cd2 = st.columns(2)
        with cd1:
            sala = st.checkbox("Sala de Estar/Jantar", value=True)
            copa = st.checkbox("Copa", value=False)
            cozinha = st.checkbox("Cozinha", value=True)
        with cd2:
            garagem_coberta = st.checkbox("🚘 Garagem Coberta")
            area_gourmet = st.checkbox("🍖 Área Gourmet / Churrasqueira")

        st.divider()
        descricao = st.text_area("📝 Descrição Geral / Observações")
        fotos = st.file_uploader("📷 Fotos do Imóvel", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        submitted = st.form_submit_button("💾 Salvar Imóvel", use_container_width=True, type="primary")
        
        if submitted:
            urls_fotos = []
            if fotos:
                for foto in fotos:
                    caminho_storage = f"imoveis/{codigo_gerado}_{foto.name}"
                    res = supabase.storage.from_("fotos-imoveis").upload(caminho_storage, foto.getvalue(), {"content-type": foto.type})
                    url_publica = supabase.storage.from_("fotos-imoveis").get_public_url(caminho_storage)
                    urls_fotos.append(url_publica)
            
            payload = {
                "codigo_imovel": codigo_gerado, "tipo": tipo, "bairro": bairro,
                "valor_venda": valor, "endereco": endereco,
                "nome_proprietario": nome_proprietario, "telefone_proprietario": telefone_proprietario,
                "corretor_captacao": corretor_captacao,
                "quartos": quartos, "suites": suites,
                "banheiros": banheiros, "vagas_garagem": vagas,
                "garagem_coberta": garagem_coberta, "area_gourmet": area_gourmet,
                "sala": sala, "copa": copa, "cozinha": cozinha,
                "area_terreno": area_terreno, "area_construida": area_construida,
                "descricao": descricao, "fotos_urls": urls_fotos, "status": "Disponível"
            }
            
            imoveis_existentes = carregar_imoveis()
            if imoveis_existentes:
                colunas_existentes = list(imoveis_existentes[0].keys())
                dados_imovel = {k: v for k, v in payload.items() if k in colunas_existentes}
            else:
                dados_imovel = payload

            try:
                supabase.table("imoveis").insert(dados_imovel).execute()
                st.success(f"✅ Imóvel **{codigo_gerado}** cadastrado com sucesso!")
                st.rerun()
            except Exception as err:
                st.error(f"Erro ao salvar imóvel: {err}")

# ==========================================
# 👤 ABA 4: NOVO LEAD
# ==========================================
elif menu == "👤 Novo Lead":
    st.title("👤 Cadastrar Novo Lead")
    st.write("Cadastre novos clientes interessados em comprar imóveis.")
    st.divider()

    with st.form("form_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Cliente *")
            whatsapp = st.text_input("WhatsApp com DDD *", "+5535998102465")
            corretor_lead = st.selectbox("Corretor Responsável *", CORRETORES)
        with col2:
            bairros_interesse = st.multiselect("Bairros de Interesse (Passos-MG) *", BAIRROS_PASSOS, default=["Centro"])
            orcamento = st.number_input("Orçamento Máximo (R$) *", min_value=0.0, value=500000.0, step=10000.0)
        
        st.divider()
        observacoes = st.text_area("📝 Preferências / O que o cliente procura?", placeholder="Ex: Procura casa térrea, com quintal grande, suite com closet e piscina. Aceita financiamento.")

        submitted_lead = st.form_submit_button("💾 Salvar Lead", use_container_width=True, type="primary")
        if submitted_lead:
            if not nome or not bairros_interesse:
                st.error("Por favor, preencha o Nome e escolha ao menos um Bairro de interesse.")
            else:
                payload_lead = {
                    "nome": nome, 
                    "whatsapp": whatsapp, 
                    "bairros_interesse": bairros_interesse,
                    "orcamento_maximo": orcamento, 
                    "corretor_responsavel": corretor_lead, 
                    "observacoes": observacoes,
                    "status": "Em busca"
                }
                
                if leads_data:
                    colunas_lead_existentes = list(leads_data[0].keys())
                    dados_lead = {k: v for k, v in payload_lead.items() if k in colunas_lead_existentes}
                else:
                    dados_lead = payload_lead

                try:
                    supabase.table("leads").insert(dados_lead).execute()
                    st.success(f"✅ Lead **{nome}** cadastrado com sucesso!")
                except Exception as err:
                    st.error(f"Erro ao salvar lead: {err}")

# ==========================================
# 👥 ABA 5: GERENCIAR LEADS
# ==========================================
elif menu == "👥 Gerenciar Leads":
    st.title("👥 Gerenciamento de Leads")
    st.write("Gerencie e atualize o perfil de busca dos clientes.")
    
    with st.expander("🔍 **Filtros e Busca de Leads**", expanded=True):
        fl_col1, fl_col2, fl_col3 = st.columns([2, 1.5, 2.5])
        with fl_col1: busca_lead = st.text_input("🔎 Pesquisar Nome ou WhatsApp", key="busca_lead")
        with fl_col2: filtro_status_lead = st.selectbox("Status", ["Todos", "Em busca", "Já comprou"], index=1, key="filtro_status_lead")
        with fl_col3: filtro_bairro_lead = st.selectbox("Filtrar por Bairro", ["Todos"] + BAIRROS_PASSOS, key="filtro_bairro_lead")

    st.divider()

    leads_filtrados = leads_data
    if busca_lead:
        termo_l = busca_lead.lower().strip()
        leads_filtrados = [l for l in leads_filtrados if termo_l in l.get('nome', '').lower() or termo_l in l.get('whatsapp', '').lower()]
    if filtro_status_lead != "Todos":
        leads_filtrados = [l for l in leads_filtrados if l.get('status', 'Em busca') == filtro_status_lead]
    if filtro_bairro_lead != "Todos":
        leads_filtrados = [l for l in leads_filtrados if filtro_bairro_lead in l.get('bairros_interesse', [])]

    st.caption(f"Exibindo **{len(leads_filtrados)}** de **{len(leads_data)}** clientes.")

    if not leads_filtrados:
        st.info("Nenhum lead encontrado.")
    else:
        for lead in leads_filtrados:
            lead_id = lead.get('id')
            status_lead = lead.get('status', 'Em busca')
            
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"👤 {lead.get('nome')} — {lead.get('whatsapp')}")
                    bairros_str = ", ".join(lead.get('bairros_interesse', [])) if lead.get('bairros_interesse') else "Nenhum"
                    st.write(f"📍 **Bairros de Interesse:** {bairros_str}")
                    st.write(f"💰 **Orçamento Máximo:** R$ {lead.get('orcamento_maximo', 0):,.2f} | 🔑 **Corretor:** {lead.get('corretor_responsavel', 'Não informado')}")
                    if lead.get('observacoes'):
                        st.write(f"📝 **Desejos / Obs:** {lead.get('observacoes')}")
                
                with col2:
                    novo_status_lead = st.radio("Status do Lead:", ["Em busca", "Já comprou"], index=0 if status_lead == "Em busca" else 1, key=f"status_direct_{lead_id}")
                    if novo_status_lead != status_lead:
                        supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead_id).execute()
                        st.success("Status atualizado!")
                        st.rerun()

                # --- EXCLUIR LEAD ---
                with st.expander(f"🗑️ Excluir Lead: {lead.get('nome')}"):
                    st.warning("⚠️ Esta ação é permanente e removerá o lead da base de dados.")
                    confirma_excluir_lead = st.checkbox("Confirmar exclusão deste lead", key=f"chk_del_lead_{lead_id}")
                    if st.button("🚨 Excluir Definitivamente", key=f"btn_del_lead_{lead_id}", type="primary"):
                        if confirma_excluir_lead:
                            supabase.table("leads").delete().eq("id", lead_id).execute()
                            st.success(f"Lead **{lead.get('nome')}** removido com sucesso!")
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🎯 ABA 6: ENCONTRAR MATCHES
# ==========================================
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Matches Imóvel x Lead")
    st.write("Cruzamento inteligente de preferências entre leads cadastrados e imóveis disponíveis.")
    st.divider()

    if not leads_data or not imoveis_data:
        st.warning("É necessário ter leads e imóveis cadastrados para gerar cruzamentos.")
    else:
        for lead in leads_data:
            nome_lead = lead.get('nome', 'Cliente')
            zap_lead = lead.get('whatsapp', '')
            tipo_pref = lead.get('tipo_imovel_interesse') or lead.get('tipo_imovel')
            bairro_pref = lead.get('bairro_interesse') or lead.get('bairro')
            orcad_max = lead.get('orcamento_max') or lead.get('orcamento')

            # Filtra imóveis compatíveis
            matches = []
            for imovel in imoveis_data:
                if imovel.get('status', 'Disponível') == 'Disponível':
                    match_score = True
                    if tipo_pref and tipo_pref.lower() not in imovel.get('tipo', '').lower():
                        match_score = False
                    if match_score:
                        matches.append(imovel)

            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.subheader(f"👤 Lead: {nome_lead}")
                st.write(f"📱 **WhatsApp:** {zap_lead} | 🎯 **Interesse:** {tipo_pref or 'Geral'} em {bairro_pref or 'Qualquer bairro'}")
                
                if not matches:
                    st.info("Nenhum imóvel compatível encontrado no momento.")
                else:
                    st.markdown(f"**{len(matches)} imóvel(is) encontrado(s) para este lead:**")
                    for m in matches:
                        cod_imovel = m.get('codigo_imovel', 'S/C')
                        tipo_imovel = m.get('tipo', 'Imóvel')
                        bairro_imovel = m.get('bairro', 'Excelente localização')
                        quartos = m.get('quartos') or m.get('dormitorios') or 'N/I'
                        vagas = m.get('vagas') or 'N/I'
                        valor = m.get('valor_venda') or m.get('valor') or 'Sob consulta'
                        
                        # Formatação amigável de valor caso seja numérico
                        if isinstance(valor, (int, float)):
                            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        else:
                            valor_fmt = str(valor)

                        # Montagem do texto personalizado para o WhatsApp
                        msg_whatsapp = (
                            f"Olá, {nome_lead}! Tudo bem?\n\n"
                            f"Encontrei uma excelente opção de {tipo_imovel} que se encaixa no seu perfil "
                            f"no bairro {bairro_imovel} (Ref: {cod_imovel}).\n\n"
                            f"📌 *Destaques do imóvel:*\n"
                            f"• {quartos} quarto(s)\n"
                            f"• {vagas} vaga(s) de garagem\n"
                            f"• Valor: {valor_fmt}\n\n"
                            f"Posso te enviar as fotos detalhadas dele por aqui? "
                            f"Se gostar, conseguimos agendar uma visita esta semana!"
                        )

                        # Limpa caracteres não numéricos do WhatsApp
                        zap_limpo = ''.join(filter(str.isdigit, str(zap_lead)))
                        if not zap_limpo.startswith("55") and len(zap_limpo) >= 10:
                            zap_limpo = f"55{zap_limpo}"

                        # Encode da mensagem para URL
                        from urllib.parse import quote
                        link_wa = f"https://wa.me/{zap_limpo}?text={quote(msg_whatsapp)}"

                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            st.write(f"🏠 **{cod_imovel}** — {tipo_imovel} no {bairro_imovel} | 🛏️ {quartos} qts | 🚗 {vagas} vagas | 💰 {valor_fmt}")
                        with col_m2:
                            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:8px 12px;border-radius:5px;cursor:pointer;width:100%;">💬 Enviar Match</button></a>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
  # ==========================================
# 📅 ABA 7: VISITAS AGENDADAS
# ==========================================
elif menu == "📅 Visitas Agendadas":
    st.title("📅 Gestão de Visitas")
    st.write("Agende e acompanhe as visitas técnicas e comerciais aos imóveis.")
    st.divider()

    # Dicionários auxiliares para busca rápida por ID e por Selectbox
    mapa_leads_by_id = {str(l.get('id')): l for l in leads_data} if leads_data else {}
    mapa_imoveis_by_id = {str(i.get('id')): i for i in imoveis_data} if imoveis_data else {}

    dict_select_leads = {f"{l.get('nome')} | {l.get('whatsapp')}": str(l.get('id')) for l in leads_data} if leads_data else {}
    dict_select_imoveis = {f"{i.get('codigo_imovel')} - {i.get('tipo')} ({i.get('bairro')})": str(i.get('id')) for i in imoveis_data} if imoveis_data else {}

    with st.expander("➕ **Agendar Nova Visita**", expanded=False):
        with st.form("form_visita", clear_on_submit=True):
            col_v1, col_v2 = st.columns(2)

            with col_v1:
                lead_sel_label = st.selectbox("Selecione o Lead *", list(dict_select_leads.keys()) if dict_select_leads else ["Nenhum lead cadastrado"])
                imovel_sel_label = st.selectbox("Selecione o Imóvel *", list(dict_select_imoveis.keys()) if dict_select_imoveis else ["Nenhum imóvel disponível"])
                corretor_visita = st.selectbox("Corretor Acompanhante *", CORRETORES)
            with col_v2:
                data_visita = st.date_input("Data da Visita *", date.today())
                hora_visita = st.time_input("Horário *")
                obs_visita = st.text_area("Observações da Visita")

            btn_visita = st.form_submit_button("📅 Confirmar Agendamento", use_container_width=True, type="primary")

            if btn_visita:
                if "Nenhum" in lead_sel_label or "Nenhum" in imovel_sel_label:
                    st.error("Selecione um lead e um imóvel válidos.")
                else:
                    lead_id_val = dict_select_leads.get(lead_sel_label)
                    imovel_id_val = dict_select_imoveis.get(imovel_sel_label)

                    payload_v = {
                        "lead_id": lead_id_val,
                        "imovel_id": imovel_id_val,
                        "corretor": str(corretor_visita),
                        "data_visita": str(data_visita),
                        "hora_visita": str(hora_visita),
                        "observacoes": str(obs_visita),
                        "status": "Agendada"
                    }

                    try:
                        supabase.table("visitas").insert(payload_v).execute()
                        st.success("✅ Visita agendada com sucesso!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro ao agendar visita: {err}")

    st.subheader("📋 Visitas Cadastradas")
    if not visitas_data:
        st.info("Nenhuma visita agendada até o momento.")
    else:
        for v in visitas_data:
            v_id = v.get('id')
            
            # Resgate das chaves estrangeiras (UUIDs)
            l_id = str(v.get('lead_id')) if v.get('lead_id') else None
            i_id = str(v.get('imovel_id')) if v.get('imovel_id') else None
            
            # Busca o objeto real correspondente ao ID
            obj_lead = mapa_leads_by_id.get(l_id, {})
            obj_imovel = mapa_imoveis_by_id.get(i_id, {})
            
            # Monta o texto legível para exibição
            if obj_lead:
                lead_exibicao = f"{obj_lead.get('nome')} ({obj_lead.get('whatsapp', 'S/N')})"
            else:
                lead_exibicao = v.get('lead') or "Lead não encontrado"

            if obj_imovel:
                imovel_exibicao = f"{obj_imovel.get('codigo_imovel')} — {obj_imovel.get('tipo')} ({obj_imovel.get('bairro')})"
            else:
                imovel_exibicao = v.get('imovel') or "Imóvel não encontrado"

            corretor_exibicao = v.get('corretor') or "Não informado"
            data_exibicao = v.get('data_visita') or v.get('data') or "Data não informada"
            hora_exibicao = v.get('hora_visita') or v.get('hora') or "Horário não informado"
            obs_exibicao = v.get('observacoes') or ""
            status_v = v.get('status', 'Agendada')
            
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                
                col_card1, col_card2 = st.columns([3, 1])
                
                with col_card1:
                    st.write(f"📅 **Data/Hora:** {data_exibicao} às {hora_exibicao} | 🔑 **Corretor:** {corretor_exibicao}")
                    st.write(f"👤 **Lead:** {lead_exibicao}")
                    st.write(f"🏠 **Imóvel:** {imovel_exibicao}")
                    if obs_exibicao:
                        st.write(f"📝 **Obs:** {obs_exibicao}")

                with col_card2:
                    opcoes_status = ["Agendada", "Realizada", "Cancelada"]
                    idx_status = opcoes_status.index(status_v) if status_v in opcoes_status else 0
                    
                    novo_status_v = st.selectbox(
                        "Status:", 
                        opcoes_status, 
                        index=idx_status, 
                        key=f"v_status_{v_id}"
                    )
                    
                    if novo_status_v != status_v:
                        supabase.table("visitas").update({"status": novo_status_v}).eq("id", v_id).execute()
                        st.success("Status atualizado!")
                        st.rerun()

                # Botões de Ação (Editar e Excluir)
                col_edit, col_del = st.columns([1, 1])
                
                with col_del:
                    if st.button("🗑️ Excluir", key=f"btn_del_v_{v_id}", use_container_width=True):
                        try:
                            supabase.table("visitas").delete().eq("id", v_id).execute()
                            st.success("Visita excluída com sucesso!")
                            st.rerun()
                        except Exception as err:
                            st.error(f"Erro ao excluir visita: {err}")

                with col_edit:
                    exp_edit = st.expander("✏️ Editar Visita")
                    with exp_edit:
                        with st.form(key=f"form_edit_visita_{v_id}"):
                            # Preparar índices padrão para os selectboxes
                            keys_leads = list(dict_select_leads.keys())
                            keys_imoveis = list(dict_select_imoveis.keys())
                            
                            idx_lead = 0
                            for idx, key in enumerate(keys_leads):
                                if dict_select_leads[key] == l_id:
                                    idx_lead = idx
                                    break
                            
                            idx_imovel = 0
                            for idx, key in enumerate(keys_imoveis):
                                if dict_select_imoveis[key] == i_id:
                                    idx_imovel = idx
                                    break

                            idx_corretor = CORRETORES.index(corretor_exibicao) if corretor_exibicao in CORRETORES else 0

                            # Tratar data e hora para os inputs
                            try:
                                d_val = datetime.strptime(data_exibicao, "%Y-%m-%d").date()
                            except Exception:
                                d_val = date.today()

                            try:
                                h_val = datetime.strptime(hora_exibicao, "%H:%M:%S").time()
                            except Exception:
                                try:
                                    h_val = datetime.strptime(hora_exibicao, "%H:%M").time()
                                except Exception:
                                    h_val = datetime.now().time()

                            edit_lead_label = st.selectbox("Lead *", keys_leads if keys_leads else ["Nenhum lead"], index=idx_lead)
                            edit_imovel_label = st.selectbox("Imóvel *", keys_imoveis if keys_imoveis else ["Nenhum imóvel"], index=idx_imovel)
                            edit_corretor = st.selectbox("Corretor *", CORRETORES, index=idx_corretor)
                            edit_data = st.date_input("Data *", d_val)
                            edit_hora = st.time_input("Horário *", h_val)
                            edit_obs = st.text_area("Observações", value=obs_exibicao)

                            btn_salvar_edit = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")

                            if btn_salvar_edit:
                                lead_id_updated = dict_select_leads.get(edit_lead_label)
                                imovel_id_updated = dict_select_imoveis.get(edit_imovel_label)

                                payload_update = {
                                    "lead_id": lead_id_updated,
                                    "imovel_id": imovel_id_updated,
                                    "corretor": str(edit_corretor),
                                    "data_visita": str(edit_data),
                                    "hora_visita": str(edit_hora),
                                    "observacoes": str(edit_obs)
                                }

                                try:
                                    supabase.table("visitas").update(payload_update).eq("id", v_id).execute()
                                    st.success("Visita atualizada!")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Erro ao atualizar visita: {err}")

                st.markdown('</div>', unsafe_allow_html=True)