import streamlit as st
from supabase import create_client
import urllib.parse
import os
from datetime import date, datetime, timedelta
from PIL import Image, ImageOps
import io

# --- IMPORTAÇÃO PARA IA ---
from google import genai

# ==========================================
# ⚙️ CONFIGURAÇÕES DA EMPRESA (CENTRALIZADAS)
# ==========================================
CONFIG_EMPRESA = {
    "NOME": "Mendes & Soares | Engenharia e Imóveis",
    "WHATSAPP_NUMERO": "5535998102465", # Número principal de atendimento
    "MENSAGEM_PADRAO_CLIENTE": "Olá! Gostaria de agendar uma visita e obter mais informações sobre este imóvel.",
    "CORRETORES": ["Erick Mendes", "Pedro Siqueira"]
}

# ==========================================
# 📊 FUNÇÕES DO SUPABASE PARA LEADS E STATUS
# ==========================================
def excluir_lead(lead_id):
    try:
        supabase.table("leads").delete().eq("id", lead_id).execute()
        limpar_cache()
        st.success("Lead excluído com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao excluir lead: {e}")

def registrar_status_imovel_lead_direto(lead, codigo_imovel, novo_status):
    try:
        lead_id = lead.get('id')
        interacoes = lead.get('interacoes_imoveis') or {}
        if isinstance(interacoes, str):
            import json
            try:
                interacoes = json.loads(interacoes)
            except Exception:
                interacoes = {}
        
        interacoes[codigo_imovel] = novo_status
        
        supabase.table("leads").update({"interacoes_imoveis": interacoes}).eq("id", lead_id).execute()
        limpar_cache()
    except Exception as e:
        st.error(f"Erro ao salvar status: {e}")

@st.cache_data(ttl=30)
def carregar_status_imoveis_leads():
    try:
        res = supabase.table("imoveis_leads_status").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

def registrar_status_imovel_lead(lead_id, codigo_imovel, novo_status):
    try:
        supabase.table("imoveis_leads_status").upsert(
            {
                "lead_id": lead_id,
                "codigo_imovel": codigo_imovel,
                "status_interacao": novo_status
            },
            on_conflict="lead_id,codigo_imovel"
        ).execute()
        limpar_cache()
    except Exception as e:
        st.error(f"Erro ao registrar status: {e}")

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
CORRETORES = CONFIG_EMPRESA["CORRETORES"]

# --- FUNIL DE VENDAS COM EMOJIS DE TEMPERATURA / STATUS ---
STATUS_LEADS = [
    "🔵 Em busca (Frio)",
    "🟡 Visita Agendada",
    "🟠 Proposta Enviada (Quente)",
    "🟣 Em Cartório",
    "🟢 Já comprou (Fechado)",
    "🔴 Perdido/Inativo"
]

MAPEAMENTO_STATUS = {
    "Em busca": "🔵 Em busca (Frio)",
    "Visita Agendada": "🟡 Visita Agendada",
    "Proposta Enviada": "🟠 Proposta Enviada (Quente)",
    "Em Cartório": "🟣 Em Cartório",
    "Já comprou": "🟢 Já comprou (Fechado)",
    "Perdido/Inativo": "🔴 Perdido/Inativo"
}

OPCOES_TIPO_IMOVEL = ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Comercial", "Chácara/Sítio"]

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title=CONFIG_EMPRESA["NOME"],
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
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dsnamhmffvjxcfqtlzet.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRzbmFtaG1mZnZqeGNmcXRsemV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxMzYwOTYsImV4cCI6MjEwMTcxMjA5Nn0.e9Uqxp0qv_ifezQ29q-7qcAKmBmzo7-wD5GwK-Bxqts")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

URL_BASE_APP = "https://crm-imobiliario-jfduwtza7vr6okamx3nfxf.streamlit.app"

# ==========================================
# 🚀 FUNÇÕES COM CACHE PARA DESEMPENHO
# ==========================================
@st.cache_data(ttl=60)
def carregar_imoveis():
    try:
        res = supabase.table("imoveis").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar imóveis: {e}")
        return []

@st.cache_data(ttl=60)
def carregar_leads():
    try:
        res = supabase.table("leads").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return []

@st.cache_data(ttl=60)
def carregar_visitas():
    try:
        res = supabase.table("visitas").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

@st.cache_data(ttl=30)
def buscar_imovel_cliente(codigo_imovel):
    try:
        res = supabase.table("imoveis").select("*").eq("codigo_imovel", codigo_imovel).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

def limpar_cache():
    st.cache_data.clear()

def renderizar_carrossel_swiper(fotos_urls, altura_px=320, id_prefixo="swiper"):
    if not fotos_urls:
        return '<div style="background:#e2e8f0; height:200px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#64748b;">Sem fotos cadastradas</div>'
    
    slides_html = "".join([f'<div class="swiper-slide"><img src="{url}" style="width:100%; border-radius:12px; height:{altura_px}px; object-fit:cover;"></div>' for url in fotos_urls])
    
    swiper_code = f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <style>
        body {{ margin: 0; background-color: transparent; }}
        .swiper {{ width: 100%; height: {altura_px}px; border-radius: 12px; }}
        .swiper-button-next, .swiper-button-prev {{ color: #c59b27; }}
        .swiper-pagination-bullet-active {{ background: #c59b27; }}
    </style>
    <div class="swiper {id_prefixo}">
        <div class="swiper-wrapper">
            {slides_html}
        </div>
        <div class="swiper-pagination"></div>
        <div class="swiper-button-prev"></div>
        <div class="swiper-button-next"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        new Swiper('.{id_prefixo}', {{
            loop: true,
            pagination: {{ el: '.swiper-pagination', clickable: true }},
            navigation: {{ nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }},
        }});
    </script>
    """
    return swiper_code

# ==========================================
# 🌐 VISUALIZAÇÃO LIMPA DO CLIENTE (MOBILE FIRST)
# ==========================================
query_params = st.query_params

if "imovel" in query_params:
    codigo_imovel_param = query_params["imovel"]
    imovel_cli = buscar_imovel_cliente(codigo_imovel_param)
    
    if imovel_cli:
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {display: none !important;}
                .stApp { max-width: 600px; margin: 0 auto; }
                .price-tag {
                    background-color: #c59b27;
                    color: white;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 1.1rem;
                    display: inline-block;
                    margin-bottom: 15px;
                }
                .bairro-codigo {
                    font-size: 0.85rem;
                    color: #555555;
                    margin-top: -10px;
                    margin-bottom: 10px;
                    line-height: 1.2;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        if os.path.exists("logo.png"):
            st.image("logo.png", width=140)
        else:
            st.markdown(f"<h3 style='color:{COR_DOURADO}; margin-bottom:0;'>MENDES & SOARES</h3>", unsafe_allow_html=True)
            st.caption("Engenharia e Imóveis")

        st.markdown(f"<h2 style='margin-bottom: 2px;'>{imovel_cli.get('tipo', 'Imóvel')}</h2>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="bairro-codigo">📍 {imovel_cli.get("bairro", "Passos-MG")} | Código: <b>{imovel_cli.get("codigo_imovel")}</b></div>', 
            unsafe_allow_html=True
        )
        
        st.markdown(f'<div class="price-tag">R$ {float(imovel_cli.get("valor_venda", 0)):,.2f}</div>', unsafe_allow_html=True)
        
        fotos_cli = imovel_cli.get("fotos_urls") or []
        if fotos_cli:
            html_swiper = renderizar_carrossel_swiper(fotos_cli, altura_px=320, id_prefixo="swiper-cli")
            st.components.v1.html(html_swiper, height=330)
        else:
            st.info("Nenhuma foto cadastrada para este imóvel.")

        st.subheader("📌 Características")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🛏️ **Quartos:** {imovel_cli.get('quartos', 0)}")
            st.write(f"🚿 **Suítes:** {imovel_cli.get('suites', 0)}")
            st.write(f"🚽 **Banheiros:** {imovel_cli.get('banheiros', 0)}")
        with col2:
            st.write(f"🚗 **Vagas:** {imovel_cli.get('vagas_garagem', 0)}")
            if imovel_cli.get("area_terreno"):
                st.write(f"📐 **Lote:** {imovel_cli.get('area_terreno')} m²")
            if imovel_cli.get("area_construida"):
                st.write(f"🏗️ **Área Const.:** {imovel_cli.get('area_construida')} m²")

        st.subheader("📋 Descrição do Imóvel")
        st.write(imovel_cli.get("descricao", "Sem descrição disponível."))

        st.divider()

        msg_wsp = f"Olá! Vi o imóvel {imovel_cli.get('codigo_imovel')} ({imovel_cli.get('tipo')} no {imovel_cli.get('bairro')}) e gostaria de agendar uma visita!"
        url_wsp = f"https://wa.me/{CONFIG_EMPRESA['WHATSAPP_NUMERO']}?text={urllib.parse.quote(msg_wsp)}"
        
        st.link_button("📱 Agendar Visita via WhatsApp", url_wsp, use_container_width=True, type="primary")

        st.stop()
    else:
        st.error("Imóvel não encontrado.")
        st.stop()

# --- GERAR DESCRIÇÃO COM IA (GEMINI) ---
import time

def gerar_descricao_ia(tipo, bairro, quartos, suites, vagas, valor):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "Erro: A chave 'GEMINI_API_KEY' não foi encontrada."

    prompt = f"""
    Você é um copywriter especialista no mercado imobiliário da Mendes & Soares Engenharia e Imóveis.
    Escreva uma descrição comercial altamente atraente e fácil leitura usando ícones para separar bem as características do imóvel, não incluir telefone e site para o seguinte imóvel:
    - Tipo: {tipo}
    - Bairro: {bairro} (Passos-MG)
    - Quartos: {quartos} (sendo {suites} suítes)
    - Vagas: {vagas}
    - Valor: R$ {valor:,.2f}
    """

    client = genai.Client(api_key=api_key)
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if ("503" in str(e) or "UNAVAILABLE" in str(e)) and tentativa < tentativas - 1:
                time.sleep(2)
                continue
            return f"Erro ao comunicar com a API do Gemini: {str(e)}"

def calcular_total_matches(imoveis, leads):
    total = 0
    leads_ativos = [l for l in leads if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']]
    imoveis_disp = [i for i in imoveis if i.get('status', 'Disponível') == 'Disponível']
    
    for l in leads_ativos:
        orc = float(l.get('orcamento_maximo') or l.get('orcamento_max') or 0.0)
        margem_superior = orc * 1.15
        
        bairros_raw = l.get('bairros_interesse', [])
        if isinstance(bairros_raw, str):
            limpo_b = bairros_raw.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            bairros = [b.strip().lower() for b in limpo_b.split(",") if b.strip()]
        elif isinstance(bairros_raw, list):
            bairros = [str(b).strip().lower() for b in bairros_raw if str(b).strip()]
        else:
            bairros = []
            
        for im in imoveis_disp:
            preco = float(im.get('valor_venda', 0.0))
            bairro_im = str(im.get('bairro', '')).strip().lower()
            if preco <= margem_superior and ((not bairros) or (bairro_im in bairros)):
                total += 1
    return total

def gerar_codigo_imovel_auto():
    imoveis = carregar_imoveis()
    if not imoveis:
        return "MS-001"
    
    numeros = []
    for item in imoveis:
        cod = item.get("codigo_imovel", "")
        if cod and ("-" in cod):
            try:
                numeros.append(int(cod.split("-")[1]))
            except ValueError:
                pass
                
    proximo = max(numeros) + 1 if numeros else 1
    return f"MS-{proximo:03d}"

# --- ESTILIZAÇÃO CSS DA APLICAÇÃO ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COR_FUNDO_PAGINA};
        color: {COR_TEXTO};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {COR_AZUL_MARINHO} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    .stCard {{
        background-color: {COR_CARD};
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 15px rgba(24, 30, 41, 0.06);
        margin-bottom: 12px;
        border-left: 6px solid {COR_DOURADO};
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }}
    .price-badge {{
        background: linear-gradient(135deg, {COR_DOURADO}, {COR_DOURADO_HOVER});
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }}
    .feature-tag {{
        background-color: #f1f5f9;
        color: {COR_AZUL_MARINHO};
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8em;
        font-weight: 600;
        margin-right: 4px;
        display: inline-block;
        border: 1px solid #cbd5e1;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: {COR_DOURADO} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- MENU LATERAL ---
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
            "👥 Funil de Leads", 
            "🎯 Encontrar Matches",
            "📅 Visitas Agendadas"
        ],
        index=0
    )

    st.divider()
    num_wsp_formatted = f"({CONFIG_EMPRESA['WHATSAPP_NUMERO'][2:4]}) {CONFIG_EMPRESA['WHATSAPP_NUMERO'][4:5]} {CONFIG_EMPRESA['WHATSAPP_NUMERO'][5:9]}-{CONFIG_EMPRESA['WHATSAPP_NUMERO'][9:]}"
    st.markdown(f"<p style='text-align: center; font-size: 0.9em; color: #94a3b8;'>📍 Passos - MG<br>📞 {num_wsp_formatted}</p>", unsafe_allow_html=True)

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    imoveis_data = carregar_imoveis()
    leads_data = carregar_leads()
    visitas_data = carregar_visitas()

    st.title("📊 Painel Geral — Mendes & Soares")
    st.write("Métricas operacionais e gestão estratégica do funil de vendas.")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)
    
    imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
    leads_em_negociacao = [l for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']]
    visitas_pendentes = [v for v in visitas_data if v.get('status', 'Agendada') == 'Agendada']
    total_matches = calcular_total_matches(imoveis_data, leads_data)
    leads_fechados = [l for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) == '🟢 Já comprou (Fechado)']
    
    with col1: st.metric(label="🏠 Imóveis Disponíveis", value=len(imoveis_disponiveis))
    with col2: st.metric(label="👥 Leads em Negociação", value=len(leads_em_negociacao))
    with col3: st.metric(label="🎯 Matches Ativos", value=total_matches)
    with col4: st.metric(label="📅 Visitas Agendadas", value=len(visitas_pendentes))
    with col5: st.metric(label="🎉 Vendas Concluídas", value=len(leads_fechados))

# ==========================================
# 📋 ABA 2: IMÓVEIS CADASTRADOS
# ==========================================
elif menu == "📋 Imóveis Cadastrados":
    imoveis_data = carregar_imoveis()
    
    st.title("📋 Inventário de Imóveis")
    st.write("Consulte, filtre e gerencie seu catálogo de imóveis em Passos-MG.")
    
    with st.expander("🔍 **Filtros e Busca de Imóveis**", expanded=True):
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1.2, 1.5, 1.2, 1.2, 2])
        
        with f_col1: busca_codigo = st.text_input("🔎 Código", placeholder="Ex: MS-001", key="busca_codigo")
        with f_col2: filtro_bairro_imovel = st.selectbox("📍 Bairro", ["Todos"] + BAIRROS_PASSOS, key="filtro_bairro_imovel")
        with f_col3: filtro_tipo = st.selectbox("🏠 Tipo", ["Todos"] + OPCOES_TIPO_IMOVEL, key="filtro_tipo")
        with f_col4: filtro_status = st.selectbox("📌 Status", ["Todos", "Disponível", "Vendido"], index=1, key="filtro_status")
        with f_col5:
            valores = [float(i.get('valor_venda', 0)) for i in imoveis_data] if imoveis_data else [0.0, 1000000.0]
            max_val = max(valores) if valores and max(valores) > 0 else 2000000.0
            filtro_preco_max = st.slider("💰 Valor Máximo (R$)", min_value=0.0, max_value=max_val, value=max_val, step=50000.0, format="R$ %d")

    st.divider()

    imoveis_filtrados = imoveis_data
    if busca_codigo:
        imoveis_filtrados = [i for i in imoveis_filtrados if busca_codigo.lower().strip() in i.get('codigo_imovel', '').lower()]
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
            cod_imovel = imovel.get('codigo_imovel')
            link_cliente = f"{URL_BASE_APP}/?imovel={cod_imovel}"
            
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([1.2, 2.3])
                
                with col1:
                    fotos_urls = imovel.get("fotos_urls") or []
                    if fotos_urls:
                        html_swiper_card = renderizar_carrossel_swiper(fotos_urls, altura_px=240, id_prefixo=f"swiper-{imovel_id}")
                        st.components.v1.html(html_swiper_card, height=250)
                    else:
                        st.image("https://via.placeholder.com/400x300?text=Mendes+%26+Soares", use_container_width=True)
                
                with col2:
                    c_title, c_badge = st.columns([3, 1.2])
                    with c_title: st.subheader(f"{imovel.get('tipo')} — Cód: **{cod_imovel}**")
                    with c_badge: st.markdown(f'<span class="price-badge">R$ {imovel.get("valor_venda", 0):,.2f}</span>', unsafe_allow_html=True)
                    
                    st.write(f"📍 **Bairro:** {imovel.get('bairro', '')} | **Endereço:** {imovel.get('endereco', 'Não informado')}")
                    st.write(f"👤 **Proprietário:** {imovel.get('nome_proprietario', 'Não informado')} ({imovel.get('telefone_proprietario', '')}) | 🔑 **Captação:** {imovel.get('corretor_captacao', '')}")

                    detalhes = f"🛏️ {imovel.get('quartos', 0)} Qtos | 🚿 {imovel.get('suites', 0)} Suítes | 🚽 {imovel.get('banheiros', 0)} Banheiros | 🚗 {imovel.get('vagas_garagem', 0)} Vagas"
                    st.write(detalhes)
                    
                    tags_html = ""
                    if imovel.get('garagem_coberta'): tags_html += '<span class="feature-tag">🚗 Garagem Coberta</span>'
                    if imovel.get('area_gourmet'): tags_html += '<span class="feature-tag">🍖 Área Gourmet</span>'
                    if tags_html: st.markdown(tags_html, unsafe_allow_html=True)
                    
                    st.caption("🔗 Link para envio direto ao cliente:")
                    st.code(link_cliente, language="text")

                    novo_status = st.radio(
                        "Status do Imóvel:", ["Disponível", "Vendido"],
                        index=0 if status_atual == "Disponível" else 1,
                        key=f"status_imovel_{imovel_id}", horizontal=True
                    )
                    if novo_status != status_atual:
                        supabase.table("imoveis").update({"status": novo_status}).eq("id", imovel_id).execute()
                        limpar_cache()
                        st.success(f"Status atualizado para: **{novo_status}**!")
                        st.rerun()

                with st.expander(f"✏️ Editar / 🗑️ Excluir Imóvel {cod_imovel}"):
                    with st.form(key=f"form_edit_imovel_{imovel_id}"):
                        st.markdown("##### 📝 Atualizar Dados do Imóvel")
                        
                        ed_i1, ed_i2, ed_i3 = st.columns(3)
                        with ed_i1:
                            idx_tipo = OPCOES_TIPO_IMOVEL.index(imovel.get('tipo')) if imovel.get('tipo') in OPCOES_TIPO_IMOVEL else 0
                            novo_tipo = st.selectbox("Tipo de Imóvel", OPCOES_TIPO_IMOVEL, index=idx_tipo, key=f"edit_tipo_{imovel_id}")
                            
                            bairro_atual = imovel.get('bairro')
                            idx_bairro = BAIRROS_PASSOS.index(bairro_atual) if bairro_atual in BAIRROS_PASSOS else 0
                            novo_bairro = st.selectbox("Bairro", BAIRROS_PASSOS, index=idx_bairro, key=f"edit_bairro_{imovel_id}")
                            
                            novo_corretor = st.selectbox("Corretor Captação", CORRETORES, index=CORRETORES.index(imovel.get('corretor_captacao')) if imovel.get('corretor_captacao') in CORRETORES else 0, key=f"edit_corretor_{imovel_id}")

                        with ed_i2:
                            novo_valor_venda = st.number_input("Valor de Venda (R$)", value=float(imovel.get('valor_venda', 0.0)), step=10000.0, key=f"edit_valor_{imovel_id}")
                            novo_endereco = st.text_input("Endereço", value=imovel.get('endereco', ''), key=f"edit_end_{imovel_id}")
                            novo_nome_prop = st.text_input("Nome Proprietário", value=imovel.get('nome_proprietario', ''), key=f"edit_prop_{imovel_id}")

                        with ed_i3:
                            novo_tel_prop = st.text_input("Telefone Proprietário", value=imovel.get('telefone_proprietario', ''), key=f"edit_tel_{imovel_id}")
                            novo_lote = st.number_input("Lote (m²)", value=float(imovel.get('area_terreno', 0.0)), step=10.0, key=f"edit_lote_{imovel_id}")
                            novo_const = st.number_input("Área Construída (m²)", value=float(imovel.get('area_construida', 0.0)), step=10.0, key=f"edit_const_{imovel_id}")

                        ed_i4, ed_i5, ed_i6, ed_i7 = st.columns(4)
                        with ed_i4: novo_quartos = st.number_input("Quartos", value=int(imovel.get('quartos', 0)), min_value=0, key=f"edit_qtos_{imovel_id}")
                        with ed_i5: novo_suites = st.number_input("Suítes", value=int(imovel.get('suites', 0)), min_value=0, key=f"edit_suites_{imovel_id}")
                        with ed_i6: novo_banheiros = st.number_input("Banheiros", value=int(imovel.get('banheiros', 0)), min_value=0, key=f"edit_bans_{imovel_id}")
                        with ed_i7: novo_vagas = st.number_input("Vagas", value=int(imovel.get('vagas_garagem', 0)), min_value=0, key=f"edit_vagas_{imovel_id}")

                        chk1, chk2 = st.columns(2)
                        with chk1:
                            nova_garagem_cob = st.checkbox("Garagem Coberta", value=bool(imovel.get('garagem_coberta', False)), key=f"edit_gco_{imovel_id}")
                            nova_area_gourmet = st.checkbox("Área Gourmet", value=bool(imovel.get('area_gourmet', False)), key=f"edit_agourm_{imovel_id}")
                        with chk2:
                            nova_sala = st.checkbox("Sala", value=bool(imovel.get('sala', True)), key=f"edit_sala_{imovel_id}")
                            nova_cozinha = st.checkbox("Cozinha", value=bool(imovel.get('cozinha', True)), key=f"edit_coz_{imovel_id}")

                        nova_descricao = st.text_area("Descrição", value=imovel.get('descricao', ''), key=f"edit_desc_{imovel_id}")

                        btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações do Imóvel", type="primary", use_container_width=True)

                        if btn_salvar_edicao:
                            dados_atualizados_imovel = {
                                "tipo": novo_tipo,
                                "bairro": novo_bairro,
                                "corretor_captacao": novo_corretor,
                                "valor_venda": novo_valor_venda,
                                "endereco": novo_endereco,
                                "nome_proprietario": novo_nome_prop,
                                "telefone_proprietario": novo_tel_prop,
                                "area_terreno": novo_lote,
                                "area_construida": novo_const,
                                "quartos": novo_quartos,
                                "suites": novo_suites,
                                "banheiros": novo_banheiros,
                                "vagas_garagem": novo_vagas,
                                "garagem_coberta": nova_garagem_cob,
                                "area_gourmet": nova_area_gourmet,
                                "sala": nova_sala,
                                "cozinha": nova_cozinha,
                                "descricao": nova_descricao
                            }
                            try:
                                supabase.table("imoveis").update(dados_atualizados_imovel).eq("id", imovel_id).execute()
                                limpar_cache()
                                st.success("Imóvel atualizado com sucesso!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erro ao atualizar imóvel: {err}")

                    st.divider()
                    st.markdown("##### 🚨 Zona de Exclusão")
                    if st.button("🗑️ Excluir Definitivamente", key=f"btn_del_{imovel_id}", type="secondary", use_container_width=True):
                        supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                        limpar_cache()
                        st.success("Imóvel removido!")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📝 ABA 3: NOVO IMÓVEL
# ==========================================
elif menu == "📝 Novo Imóvel":
    st.title("📝 Cadastrar Novo Imóvel")
    st.write("Adicione um novo imóvel ao inventário da Mendes & Soares.")
    st.divider()

    codigo_gerado = gerar_codigo_imovel_auto()

    st.subheader("📌 Informações Básicas")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("Código do Imóvel", value=codigo_gerado, disabled=True)
        tipo = st.selectbox("Tipo de Imóvel", OPCOES_TIPO_IMOVEL)
        corretor_captacao = st.selectbox("Corretor que Captou *", CORRETORES)
    with c2:
        bairro = st.selectbox("Bairro (Passos-MG) *", BAIRROS_PASSOS)
        valor = st.number_input("Valor de Venda (R$) *", min_value=0.0, value=350000.0, step=10000.0)
        endereco = st.text_input("Endereço / Rua e Número")
    with c3:
        area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, value=250.0, step=10.0)
        area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=120.0, step=10.0)

    st.divider()
    cp1, cp2 = st.columns(2)
    with cp1: nome_proprietario = st.text_input("Nome do Proprietário *")
    with cp2: telefone_proprietario = st.text_input("Telefone do Proprietário", placeholder="(35) 99999-9999")

    st.divider()
    c4, c5, c6, c7 = st.columns(4)
    with c4: quartos = st.number_input("Dormitórios", min_value=0, value=3, step=1)
    with c5: suites = st.number_input("Suítes", min_value=0, value=1, step=1)
    with c6: banheiros = st.number_input("Banheiros", min_value=0, value=2, step=1)
    with c7: vagas = st.number_input("Vagas", min_value=0, value=2, step=1)

    cd1, cd2 = st.columns(2)
    with cd1:
        sala = st.checkbox("Sala de Estar/Jantar", value=True)
        copa = st.checkbox("Copa", value=False)
        cozinha = st.checkbox("Cozinha", value=True)
    with cd2:
        garagem_coberta = st.checkbox("🚘 Garagem Coberta")
        area_gourmet = st.checkbox("🍖 Área Gourmet / Churrasqueira")

    st.divider()
    if st.button("✨ Gerar Descrição com IA"):
        with st.spinner("Gerando descrição com IA..."):
            st.session_state['descricao_temp'] = gerar_descricao_ia(tipo, bairro, quartos, suites, vagas, valor)
            st.rerun()

    descricao = st.text_area("Descrição Geral", value=st.session_state.get('descricao_temp', ''), height=150)
    
    st.markdown("### 📷 Fotos do Imóvel")
    st.info("💡 **Dica mobile:** Clique no botão abaixo para selecionar fotos da galeria ou abrir diretamente a **câmera completa do seu celular** (com controle de zoom, foco e lentes).")

    fotos_upload = st.file_uploader(
        "Selecione ou tire as fotos do imóvel:", 
        type=["jpg", "png", "jpeg"], 
        accept_multiple_files=True
    )

    fotos_processadas = []
    if fotos_upload:
        for f in fotos_upload:
            fotos_processadas.append({"nome": f.name, "dados": f.getvalue()})
if st.button("💾 Salvar Imóvel", use_container_width=True, type="primary"):
        urls_fotos = []
        if fotos_processadas:
            logo_img = None
            if os.path.exists("logo.png"):
                try:
                    logo_img = Image.open("logo.png").convert("RGBA")
                except Exception:
                    logo_img = None

            import time
            for i, foto_dict in enumerate(fotos_processadas):
                try:
                    img = Image.open(io.BytesIO(foto_dict["dados"])).convert("RGBA")
                    img_w, img_h = img.size

                    if logo_img:
                        # Redimensiona a logo proporcionalmente (~18% da largura da foto original)
                        target_logo_width = int(img_w * 0.18)
                        aspect_ratio = logo_img.height / logo_img.width
                        target_logo_height = int(target_logo_width * aspect_ratio)
                        
                        logo_resized = logo_img.resize((target_logo_width, target_logo_height), Image.Resampling.LANCZOS)
                        
                        # Margens proporcionais no canto inferior direito
                        margin_x = int(img_w * 0.03)
                        margin_y = int(img_h * 0.03)
                        pos_x = img_w - target_logo_width - margin_x
                        pos_y = img_h - target_logo_height - margin_y
                        
                        # Aplica a marca d'água utilizando o canal alfa
                        img.paste(logo_resized, (pos_x, pos_y), logo_resized)
                    
                    # Salva em JPEG mantendo a qualidade alta
                    img_final = img.convert("RGB")
                    buffer_img = io.BytesIO()
                    img_final.save(buffer_img, format="JPEG", quality=95)
                    bytes_finais = buffer_img.getvalue()

                    # Cria um nome único usando timestamp para evitar duplicidade ("image.jpg")
                    timestamp_unico = int(time.time() * 1000)
                    nome_limpo = f"foto_{i}_{timestamp_unico}.jpg"
                    caminho_storage = f"imoveis/{codigo_gerado}_{nome_limpo}"
                    
                    supabase.storage.from_("fotos-imoveis").upload(caminho_storage, bytes_finais, {"content-type": "image/jpeg"})
                    url_publica = supabase.storage.from_("fotos-imoveis").get_public_url(caminho_storage)
                    urls_fotos.append(url_publica)
                except Exception as ex:
                    st.error(f"Erro ao processar foto {foto_dict['nome']}: {ex}")

        dados_imovel = {
            "codigo_imovel": codigo_gerado, "tipo": tipo, "bairro": bairro,
            "valor_venda": valor, "endereco": endereco,
            "nome_proprietario": nome_proprietario, "telefone_proprietario": telefone_proprietario,
            "corretor_captacao": corretor_captacao, "quartos": quartos, "suites": suites,
            "banheiros": banheiros, "vagas_garagem": vagas, "garagem_coberta": garagem_coberta,
            "area_gourmet": area_gourmet, "sala": sala, "copa": copa, "cozinha": cozinha,
            "area_terreno": area_terreno, "area_construida": area_construida,
            "descricao": descricao, "fotos_urls": urls_fotos, "status": "Disponível"
        }

        try:
            supabase.table("imoveis").insert(dados_imovel).execute()
            limpar_cache()
            st.success(f"✅ Imóvel **{codigo_gerado}** cadastrado com sucesso!")
            if 'descricao_temp' in st.session_state: del st.session_state['descricao_temp']
            st.rerun()
        except Exception as err:
            st.error(f"Erro ao salvar imóvel: {err}")

# ==========================================
# 👤 ABA 4: NOVO LEAD (COM MULTISELECT)
# ==========================================
elif menu == "👤 Novo Lead":
    st.title("➕ Cadastrar Novo Lead")
    st.write("Registre um novo cliente no sistema com suas preferências de busca.")
    st.divider()

    with st.form("form_novo_lead", clear_on_submit=True):
        nome = st.text_input("Nome do Lead*")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            whatsapp = st.text_input("WhatsApp (ex: 35999999999)*")
        with col_c2:
            email = st.text_input("E-mail")
            
        orcamento = st.number_input("Orçamento Máximo (R$)", min_value=0.0, value=500000.0, step=10000.0, format="%.2f")
        
        tipos_imovel = st.multiselect(
            "Tipos de Imóvel de Interesse*",
            OPCOES_TIPO_IMOVEL,
            default=["Casa", "Apartamento"]
        )
        
        bairros_selecionados = st.multiselect(
            "Bairros de Interesse (Passos-MG)",
            BAIRROS_PASSOS
        )

        observacoes = st.text_area("Observações Adicionais")
        
        submitted = st.form_submit_button("💾 Salvar Lead", type="primary", use_container_width=True)
        
        if submitted:
            if not nome or not whatsapp or not tipos_imovel:
                st.error("Por favor, preencha os campos obrigatórios (*).")
            else:
                dados_lead = {
                    "nome": nome,
                    "whatsapp": whatsapp,
                    "email": email,
                    "orcamento_maximo": orcamento,
                    "tipo_imovel": tipos_imovel,
                    "bairros_interesse": bairros_selecionados,
                    "observacoes": observacoes,
                    "status": "🔵 Em busca (Frio)"
                }
                
                try:
                    supabase.table("leads").insert(dados_lead).execute()
                    limpar_cache()
                    st.success(f"Lead **{nome}** cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar lead no banco de dados: {e}")

# ==========================================
# 👥 ABA 5: FUNIL DE LEADS
# ==========================================
elif menu == "👥 Funil de Leads":
    leads_data = carregar_leads()
    st.title("👥 Funil de Negociação de Leads")
    st.write("Gerencie seus clientes e atualize os status de negociação.")
    st.divider()

    contagem_por_status = {status: 0 for status in STATUS_LEADS}
    leads_agrupados = {status: [] for status in STATUS_LEADS}

    for l in leads_data:
        st_normal = MAPEAMENTO_STATUS.get(l.get('status'), l.get('status'))
        if st_normal in leads_agrupados:
            leads_agrupados[st_normal].append(l)
            contagem_por_status[st_normal] += 1

    titulos_abas = [f"{contagem_por_status[st]:02d} {st}" for st in STATUS_LEADS]
    tabs = st.tabs(titulos_abas)

    for i, status_original in enumerate(STATUS_LEADS):
        with tabs[i]:
            leads_da_aba = leads_agrupados[status_original]
            if not leads_da_aba:
                st.info("Nenhum cliente nesta etapa.")
            else:
                for lead in leads_da_aba:
                    lead_id = lead.get('id')
                    nome_lead = lead.get('nome', 'Sem Nome')
                    whatsapp_lead = lead.get('whatsapp', '')
                    email_lead = lead.get('email', '')
                    orc_lead = float(lead.get('orcamento_maximo') or lead.get('orcamento_max') or 0.0)
                    obs_lead = lead.get('observacoes', '')
                    
                    bairros_raw = lead.get('bairros_interesse', [])
                    if isinstance(bairros_raw, str):
                        bairros_lead = [b.strip() for b in bairros_raw.split(",") if b.strip()]
                    elif isinstance(bairros_raw, list):
                        bairros_lead = [b.strip() for b in bairros_raw if b.strip()]
                    else:
                        bairros_lead = []

                    tipos_raw = lead.get('tipo_imovel', [])
                    if isinstance(tipos_raw, str):
                        tipos_lead = [t.strip() for t in tipos_raw.split(",") if t.strip()]
                    elif isinstance(tipos_raw, list):
                        tipos_lead = [t.strip() for t in tipos_raw if t.strip()]
                    else:
                        tipos_lead = []

                    bairros_str_titulo = ", ".join(bairros_lead) if bairros_lead else "Todos os bairros"

                    with st.expander(f"👤 **{nome_lead}** | 💰 R$ {orc_lead:,.2f} | 📍 {bairros_str_titulo}"):
                        with st.container():
                            st.markdown('<div class="stCard">', unsafe_allow_html=True)
                            c1, c2 = st.columns([2.5, 1.5])
                            
                            with c1:
                                st.markdown(f"### **{nome_lead}**")
                                st.write(f"📱 **WhatsApp:** {whatsapp_lead} | 📧 **Email:** {email_lead if email_lead else 'Não informado'}")
                                st.write(f"💰 **Orçamento:** R$ {orc_lead:,.2f}")
                                if tipos_lead:
                                    st.write(f"🏠 **Interesse:** {', '.join(tipos_lead)}")
                                if bairros_lead:
                                    st.caption(f"📍 **Bairros:** {', '.join(bairros_lead)}")
                                if obs_lead:
                                    st.caption(f"📝 **Obs:** {obs_lead}")

                            with c2:
                                idx_atual = STATUS_LEADS.index(status_original) if status_original in STATUS_LEADS else 0
                                novo_st = st.selectbox("Mover Etapa:", STATUS_LEADS, index=idx_atual, key=f"f_move_{lead_id}")
                                if novo_st != status_original:
                                    supabase.table("leads").update({"status": novo_st}).eq("id", lead_id).execute()
                                    limpar_cache()
                                    st.success("Status atualizado!")
                                    st.rerun()

                            phone_clean = ''.join(filter(str.isdigit, str(whatsapp_lead)))
                            if phone_clean and not phone_clean.startswith("55"):
                                phone_clean = f"55{phone_clean}"
                            
                            msg_wsp_funil = f"Olá {nome_lead}, aqui é da Mendes & Soares Engenharia e Imóveis. Gostaríamos de dar continuidade ao seu atendimento!"
                            url_wsp_funil = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(msg_wsp_funil)}"
                            
                            st.link_button("💬 Enviar Mensagem no WhatsApp", url_wsp_funil, use_container_width=True)
                                          
                            with st.expander(f"✏️ Editar / 🗑️ Excluir Dados de {nome_lead}"):
                                with st.form(key=f"form_edit_lead_{lead_id}"):
                                    ed_col1, ed_col2 = st.columns(2)
                                    with ed_col1:
                                        novo_nome = st.text_input("Nome", value=nome_lead)
                                        novo_wsp = st.text_input("WhatsApp", value=whatsapp_lead)
                                        novo_email = st.text_input("E-mail", value=email_lead)
                                    with ed_col2:
                                        novo_orc = st.number_input("Orçamento Máx (R$)", value=orc_lead, step=10000.0)
                                        novos_tipos = st.multiselect(
                                            "Tipos de Imóvel",
                                            OPCOES_TIPO_IMOVEL,
                                            default=[t for t in tipos_lead if t in OPCOES_TIPO_IMOVEL]
                                        )
                                        novos_bairros = st.multiselect(
                                            "Bairros de Interesse",
                                            BAIRROS_PASSOS,
                                            default=[b for b in bairros_lead if b in BAIRROS_PASSOS]
                                        )
                                    
                                    novas_obs = st.text_area("Observações", value=obs_lead)

                                    btn_salvar_lead = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                                    
                                    if btn_salvar_lead:
                                        dados_atualizados = {
                                            "nome": novo_nome,
                                            "whatsapp": novo_wsp,
                                            "email": novo_email,
                                            "orcamento_maximo": float(novo_orc),
                                            "tipo_imovel": novos_tipos,
                                            "bairros_interesse": novos_bairros,
                                            "observacoes": novas_obs
                                        }
                                        supabase.table("leads").update(dados_atualizados).eq("id", lead_id).execute()
                                        limpar_cache()
                                        st.success("Lead atualizado com sucesso!")
                                        st.rerun()

                                st.divider()
                                st.markdown("##### ⚠️ Zona de Exclusão")
                                col_del1, col_del2 = st.columns([3, 1])
                                with col_del1:
                                    st.caption("Esta ação exclui permanentemente o lead do banco de dados e não pode ser desfeita.")
                                with col_del2:
                                    if st.button("🗑️ Excluir Lead", key=f"btn_del_lead_{lead_id}", type="secondary", use_container_width=True):
                                        excluir_lead(lead_id)

                            st.markdown('</div>', unsafe_allow_html=True)
                
# ==========================================
# 🎯 ABA 6: ENCONTRAR MATCHES
# ==========================================
elif menu == "🎯 Encontrar Matches":
    leads_data = carregar_leads()
    imoveis_data = carregar_imoveis()
    
    st.title("🎯 Cruzamento de Dados (Matches)")
    st.write("Gerencie as sugestões de imóveis e acompanhe a resposta do cliente.")
    st.divider()

    leads_ativos = [
        l for l in leads_data 
        if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']
    ]

    if not leads_ativos:
        st.info("Nenhum lead ativo encontrado para cruzamento.")
    else:
        for lead in leads_ativos:
            lead_id = lead.get('id')
            nome_lead = lead.get('nome', 'Sem Nome')
            wsp_lead = lead.get('whatsapp', '')
            
            interacoes_lead = lead.get('interacoes_imoveis') or {}
            if isinstance(interacoes_lead, str):
                import json
                try:
                    interacoes_lead = json.loads(interacoes_lead)
                except Exception:
                    interacoes_lead = {}
            
            phone_clean = ''.join(filter(str.isdigit, str(wsp_lead)))
            if phone_clean and not phone_clean.startswith("55"):
                phone_clean = f"55{phone_clean}"

            try:
                orc_lead = float(lead.get('orcamento_maximo') or lead.get('orcamento_max') or 0.0)
            except (ValueError, TypeError):
                orc_lead = 0.0

            orc_min_margem = orc_lead * 0.85
            orc_max_margem = orc_lead * 1.15 if orc_lead > 0 else float('inf')
            
            tipos_raw = lead.get('tipo_imovel', [])
            if isinstance(tipos_raw, str):
                limpo = tipos_raw.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                tipos_interesse = [t.strip().lower() for t in limpo.split(",") if t.strip()]
            elif isinstance(tipos_raw, list):
                tipos_interesse = [str(t).strip().lower() for t in tipos_raw if str(t).strip()]
            else:
                tipos_interesse = []

            bairros_raw = lead.get('bairros_interesse', [])
            if isinstance(bairros_raw, str):
                limpo_b = bairros_raw.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                bairros_interesse = [b.strip().lower() for b in limpo_b.split(",") if b.strip()]
            elif isinstance(bairros_raw, list):
                bairros_interesse = [str(b).strip().lower() for b in bairros_raw if str(b).strip()]
            else:
                bairros_interesse = []

            matches_com_score = []
            for im in imoveis_data:
                if str(im.get('status', 'Disponível')).strip().lower() != 'disponível':
                    continue
                
                try:
                    preco_imovel = float(im.get('valor_venda', 0.0))
                except (ValueError, TypeError):
                    preco_imovel = 0.0

                bairro_imovel = str(im.get('bairro', '')).strip().lower()
                tipo_imovel = str(im.get('tipo', '')).strip().lower()
                
                valido_preco = (orc_lead == 0.0) or (orc_min_margem <= preco_imovel <= orc_max_margem)
                valido_bairro = (not bairros_interesse) or (bairro_imovel in bairros_interesse)
                
                if valido_preco and valido_bairro:
                    score = 70.0
                    if preco_imovel <= orc_lead:
                        score += 15.0
                    else:
                        score += 5.0
                        
                    if tipos_interesse and tipo_imovel in tipos_interesse:
                        score += 10.0
                    elif not tipos_interesse:
                        score += 5.0
                        
                    if bairros_interesse and bairro_imovel in bairros_interesse:
                        score += 5.0

                    probabilidade = min(int(score), 99)
                    matches_com_score.append((probabilidade, im))

            matches_com_score.sort(key=lambda x: x[0], reverse=True)
            qnt_matches = len(matches_com_score)
            badge_matches = f"🔥 {qnt_matches} imóvel(is) compatível(is)" if qnt_matches > 0 else "⚪ Nenhum imóvel no perfil"
            
            with st.expander(f"👤 **{nome_lead}** — 📱 {wsp_lead} | ({badge_matches})"):
                bairros_exibicao = lead.get('bairros_interesse', [])
                if isinstance(bairros_exibicao, list):
                    bairros_str = ", ".join(bairros_exibicao)
                else:
                    bairros_str = str(bairros_exibicao).replace("[", "").replace("]", "").replace("'", "")

                tipos_exibicao = lead.get('tipo_imovel', [])
                if isinstance(tipos_exibicao, list):
                    tipos_str = ", ".join(tipos_exibicao)
                else:
                    tipos_str = str(tipos_exibicao).replace("[", "").replace("]", "").replace("'", "")

                st.markdown(f"""
                **Parâmetros do Cliente:**
                - 💰 **Orçamento:** R$ {orc_lead:,.2f} *(Faixa ±15%: R$ {orc_min_margem:,.2f} até R$ {orc_max_margem:,.2f})*
                - 📍 **Bairros:** {bairros_str if bairros_str else "Todos os bairros"}
                - 🏠 **Tipos:** {tipos_str if tipos_str else "Todos os tipos"}
                """)
                st.divider()

                if not matches_com_score:
                    st.warning("Nenhum imóvel atende aos critérios de valor (±15%) e bairro para este cliente.")
                else:
                    st.subheader(f"🏠 Imóveis Recomendados ({qnt_matches})")
                    for prob, match in matches_com_score:
                        cod_im = match.get('codigo_imovel')
                        valor_imovel = float(match.get('valor_venda', 0))
                        status_atual = interacoes_lead.get(cod_im, "⚪ Não Enviado")
                        
                        msg_whatsapp = (
                            f"Olá {nome_lead}, nosso algoritmo identificou que este imóvel tem {prob}% de probabilidade "
                            f"de se encaixar perfeitamente no seu perfil e recomenda esta opção para você! "
                            f"Posso te enviar o link com as fotos e agendarmos uma visita?"
                        )
                        
                        url_whatsapp = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(msg_whatsapp)}"

                        with st.container():
                            st.markdown('<div class="stCard">', unsafe_allow_html=True)
                            st.markdown(f"🎯 **{prob}% de probabilidade para este cliente**")
                            
                            c_title, c_badge = st.columns([3, 1.2])
                            with c_title:
                                st.markdown(f"### {match.get('tipo')} — Cód: **{cod_im}**")
                                st.write(f"📍 **Bairro:** {match.get('bairro')} | 🛏️ {match.get('quartos', 0)} qtos | 🚗 {match.get('vagas_garagem', 0)} vagas")
                            with c_badge:
                                st.markdown(f'<span class="price-badge">R$ {valor_imovel:,.2f}</span>', unsafe_allow_html=True)
                            
                            st.link_button("📲 Enviar no WhatsApp du Lead", url_whatsapp, type="primary", use_container_width=True)

                            opcoes_status = ["⚪ Não Enviado", "👁️ Visto", "❌ Sem Interesse", "📅 Visita Agendada"]
                            
                            novo_status = st.segmented_control(
                                label="**Status da Interação:**",
                                options=opcoes_status,
                                default=status_atual if status_atual in opcoes_status else "⚪ Não Enviado",
                                key=f"seg_{lead_id}_{cod_im}"
                            )

                            if novo_status != status_atual:
                                registrar_status_imovel_lead_direto(lead, cod_im, novo_status)
                                st.toast(f"Status atualizado para: **{novo_status}**")
                                st.rerun()

                            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📅 ABA 7: VISITAS AGENDADAS
# ==========================================
elif menu == "📅 Visitas Agendadas":
    visitas_data = carregar_visitas()
    imoveis_data = carregar_imoveis()
    leads_data = carregar_leads()

    st.title("📅 Agendamento de Visitas")
    st.divider()

    with st.form("form_visita", clear_on_submit=True):
        imoveis_opts = [f"{i.get('codigo_imovel')} - {i.get('tipo')}" for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
        leads_opts = [f"{l.get('nome')} ({l.get('whatsapp')})" for l in leads_data]

        v_c1, v_c2 = st.columns(2)
        with v_c1:
            imovel_visita = st.selectbox("Imóvel *", imoveis_opts if imoveis_opts else ["Nenhum"])
            lead_visita = st.selectbox("Lead *", leads_opts if leads_opts else ["Nenhum"])
            corretor_visita = st.selectbox("Corretor *", CORRETORES)
        with v_c2:
            data_visita = st.date_input("Data *", date.today())
            hora_visita = st.time_input("Horário *", datetime.now().time())
            obs_visita = st.text_area("Obs")

        if st.form_submit_button("📅 Confirmar Agendamento", type="primary", use_container_width=True):
            payload_visita = {
                "imovel_info": imovel_visita, "lead_info": lead_visita,
                "corretor": corretor_visita, "data": str(data_visita),
                "hora": str(hora_visita), "observacoes": obs_visita, "status": "Agendada"
            }
            supabase.table("visitas").insert(payload_visita).execute()
            limpar_cache()
            st.success("Visita agendada!")
            st.rerun()

    st.divider()
    for v in visitas_data:
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.write(f"📅 **{v.get('data')} às {v.get('hora')}** | {v.get('imovel_info')} | {v.get('lead_info')}")
            if st.button("🗑️ Cancelar", key=f"del_vis_{v.get('id')}"):
                supabase.table("visitas").delete().eq("id", v.get('id')).execute()
                limpar_cache()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
