import streamlit as st
from supabase import create_client
import urllib.parse
import os
from datetime import date, datetime
import requests

# --- IMPORTAÇÃO PARA IA ---
from google import genai

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

# --- FUNIL DE VENDAS COM EMOJIS DE TEMPERATURA / STATUS ---
STATUS_LEADS = [
    "🔵 Em busca (Frio)",
    "🟡 Visita Agendada",
    "🟠 Proposta Enviada (Quente)",
    "🟣 Em Cartório",
    "🟢 Já comprou (Fechado)",
    "🔴 Perdido/Inativo"
]

# DICIONÁRIO PARA NORMALIZAR STATUS ANTIGOS SE NECESSÁRIO
MAPEAMENTO_STATUS = {
    "Em busca": "🔵 Em busca (Frio)",
    "Visita Agendada": "🟡 Visita Agendada",
    "Proposta Enviada": "🟠 Proposta Enviada (Quente)",
    "Em Cartório": "🟣 Em Cartório",
    "Já comprou": "🟢 Já comprou (Fechado)",
    "Perdido/Inativo": "🔴 Perdido/Inativo"
}

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
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dsnamhmffvjxcfqtlzet.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_XVO9PLxpxWBnr32_UYt_UA_HSdspi16")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# URL base para links compartilháveis do imóvel para clientes
URL_BASE_APP = "https://crm-imobiliario-jfduwtza7vr6okamx3nfxf.streamlit.app"
import urllib.parse

# ==========================================
# 🌐 VISUALIZAÇÃO LIMPA DO CLIENTE (MOBILE FIRST)
# ==========================================
query_params = st.query_params

if "imovel" in query_params:
    codigo_imovel_param = query_params["imovel"]
    
    try:
        res_cli = supabase.table("imoveis").select("*").eq("codigo_imovel", codigo_imovel_param).execute()
        if res_cli.data:
            imovel_cli = res_cli.data[0]
            
            # CSS Personalizado
            st.markdown(
                """
                <style>
                    [data-testid="stSidebar"] {display: none !important;}
                    .stApp { max-width: 600px; margin: 0 auto; }
                    .price-tag {
                        background-color: #c59b27;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: bold;
                        font-size: 1.2rem;
                        display: inline-block;
                        margin-bottom: 15px;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Cabeçalho
            if os.path.exists("logo.png"):
                st.image("logo.png", width=160)
            else:
                st.markdown(f"<h2 style='color:{COR_DOURADO}; margin-bottom:0;'>MENDES & SOARES</h2>", unsafe_allow_html=True)
                st.caption("Engenharia e Imóveis")

            st.title(f"{imovel_cli.get('tipo', 'Imóvel')} — {imovel_cli.get('bairro', 'Passos-MG')}")
            st.caption(f"Código: **{imovel_cli.get('codigo_imovel')}** | Passos - MG")
            
            st.markdown(f'<div class="price-tag">R$ {float(imovel_cli.get("valor_venda", 0)):,.2f}</div>', unsafe_allow_html=True)
            
            # Carrossel de Fotos
            fotos_cli = imovel_cli.get("fotos_urls") or []
            if fotos_cli:
                idx_foto = st.slider("Fotos do imóvel", 1, len(fotos_cli), 1, label_visibility="collapsed")
                st.image(fotos_cli[idx_foto - 1], use_container_width=True)
                st.caption(f"Foto {idx_foto} de {len(fotos_cli)}")
            else:
                st.info("Nenhuma foto cadastrada para este imóvel.")

            # Especificações
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

            # Descrição
            st.subheader("📋 Descrição do Imóvel")
            st.write(imovel_cli.get("descricao", "Sem descrição disponível."))

            st.divider()

            # Chamada de Ação (WhatsApp)
            msg_wsp = f"Olá! Vi o imóvel {imovel_cli.get('codigo_imovel')} ({imovel_cli.get('tipo')} no {imovel_cli.get('bairro')}) e gostaria de agendar uma visita!"
            url_wsp = f"https://wa.me/5535998102465?text={urllib.parse.quote(msg_wsp)}"
            
            st.link_button("📱 Agendar Visita via WhatsApp", url_wsp, use_container_width=True, type="primary")

            st.stop()
        else:
            st.error("Imóvel não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar dados do imóvel: {e}")
        st.stop()
            # --- ESPECIFICAÇÕES EM GRID ---
            st.markdown(f"""
                <div class="spec-grid">
                    <div class="spec-item">🛏️ {imovel_cli.get('quartos', 0)} Dormitórios</div>
                    <div class="spec-item">🚿 {imovel_cli.get('suites', 0)} Suítes</div>
                    <div class="spec-item">🚽 {imovel_cli.get('banheiros', 0)} Banheiros</div>
                    <div class="spec-item">🚗 {imovel_cli.get('vagas_garagem', 0)} Vagas</div>
                    {"<div class='spec-item'>📐 Lote: " + str(imovel_cli.get('area_terreno')) + " m²</div>" if imovel_cli.get('area_terreno') else ""}
                    {"<div class='spec-item'>🏗️ Á. Const: " + str(imovel_cli.get('area_construida')) + " m²</div>" if imovel_cli.get('area_construida') else ""}
                </div>
            """, unsafe_allow_html=True)

            # --- DESCRIÇÃO ---
            st.subheader("📋 Descrição do Imóvel")
            st.write(imovel_cli.get("descricao", "Sem descrição disponível."))

            # --- BOTÃO FIXO FLUTUANTE DE WHATSAPP ---
            msg_wsp = f"Olá! Vi o imóvel {imovel_cli.get('codigo_imovel')} ({imovel_cli.get('tipo')} no {imovel_cli.get('bairro')}) e gostaria de agendar uma visita!"
            url_wsp = f"https://wa.me/5535998102465?text={urllib.parse.quote(msg_wsp)}"
            
            st.markdown(
                f'<a href="{url_wsp}" target="_blank" class="whatsapp-float">'
                f'📱 Agendar Visita no WhatsApp'
                f'</a>',
                unsafe_allow_html=True
            )

            st.stop()
        else:
            st.error("Imóvel não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar dados do imóvel: {e}")
        st.stop()
            
            # --- GALERIA DE FOTOS COM SWIPE TOUCH (SWIPER.JS) ---
            fotos_cli = imovel_cli.get("fotos_urls") or []
            if fotos_cli:
                slides_html = "".join([f'<div class="swiper-slide"><img src="{url}" style="width:100%; border-radius:12px; height:280px; object-fit:cover;"></div>' for url in fotos_cli])
                
                swiper_code = f"""
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
                <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
                
                <div class="swiper mySwiper" style="width:100%; height:300px; padding-bottom:20px;">
                  <div class="swiper-wrapper">
                    {slides_html}
                  </div>
                  <div class="swiper-pagination"></div>
                </div>

                <script>
                  var swiper = new Swiper(".mySwiper", {{
                    pagination: {{ el: ".swiper-pagination", clickable: true }},
                    loop: true,
                  }});
                </script>
                """
                components.html(swiper_code, height=310)
            else:
                st.info("Nenhuma foto cadastrada para este imóvel.")

            # --- ESPECIFICAÇÕES EM GRID ---
            st.markdown(f"""
                <div class="spec-grid">
                    <div class="spec-item">🛏️ {imovel_cli.get('quartos', 0)} Dormitórios</div>
                    <div class="spec-item">🚿 {imovel_cli.get('suites', 0)} Suítes</div>
                    <div class="spec-item">🚽 {imovel_cli.get('banheiros', 0)} Banheiros</div>
                    <div class="spec-item">🚗 {imovel_cli.get('vagas_garagem', 0)} Vagas</div>
                    {"<div class='spec-item'>📐 Lote: " + str(imovel_cli.get('area_terreno')) + " m²</div>" if imovel_cli.get('area_terreno') else ""}
                    {"<div class='spec-item'>🏗️ Á. Const: " + str(imovel_cli.get('area_construida')) + " m²</div>" if imovel_cli.get('area_construida') else ""}
                </div>
            """, unsafe_allow_html=True)

            # --- DESCRIÇÃO ---
            st.subheader("📋 Descrição do Imóvel")
            st.write(imovel_cli.get("descricao", "Sem descrição disponível."))

            # --- BOTÃO FIXO FLUTUANTE DE WHATSAPP ---
            msg_wsp = f"Olá! Vi o imóvel {imovel_cli.get('codigo_imovel')} ({imovel_cli.get('tipo')} no {imovel_cli.get('bairro')}) e gostaria de agendar uma visita!"
            url_wsp = f"https://wa.me/5535998102465?text={urllib.parse.quote(msg_wsp)}"
            
            st.markdown(
                f'<a href="{url_wsp}" target="_blank" class="whatsapp-float">'
                f'📱 Agendar Visita no WhatsApp'
                f'</a>',
                unsafe_allow_html=True
            )

            st.stop()
        else:
            st.error("Imóvel não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar dados do imóvel: {e}")
        st.stop()
            
            # --- GALERIA INTERATIVA COM NAVEGAÇÃO DIRETA (FÁCIL NO CELULAR) ---
            fotos_cli = imovel_cli.get("fotos_urls") or []
            if fotos_cli:
                st.subheader("🖼️ Galeria de Fotos")
                
                # Controle do estado da foto atual do cliente
                if "cli_foto_idx" not in st.session_state:
                    st.session_state.cli_foto_idx = 0

                idx_foto = st.session_state.cli_foto_idx
                if idx_foto >= len(fotos_cli):
                    idx_foto = 0
                    st.session_state.cli_foto_idx = 0

                # Exibe a foto atual em alta resolução
                st.image(fotos_cli[idx_foto], use_container_width=True)

                if len(fotos_cli) > 1:
                    # Botões grandes de navegação direta (◀ Avançar e Recuar ▶) para uso fácil no celular
                    c_btn_prev, c_info, c_btn_next = st.columns([1, 2, 1])
                    
                    with c_btn_prev:
                        if st.button("◀ Anterior", key="cli_btn_prev", use_container_width=True):
                            st.session_state.cli_foto_idx = (idx_foto - 1) % len(fotos_cli)
                            st.rerun()

                    with c_info:
                        st.markdown(
                            f"<p style='text-align:center; margin-top:8px; font-weight:bold;'>"
                            f"Foto {idx_foto + 1} de {len(fotos_cli)}"
                            f"</p>",
                            unsafe_allow_html=True
                        )

                    with c_btn_next:
                        if st.button("Próxima ▶", key="cli_btn_next", type="primary", use_container_width=True):
                            st.session_state.cli_foto_idx = (idx_foto + 1) % len(fotos_cli)
                            st.rerun()

                    # Slider opcional e rápido para arrastar direto no celular
                    novo_idx = st.slider(
                        "Deslize para trocar de foto:",
                        min_value=1,
                        max_value=len(fotos_cli),
                        value=idx_foto + 1,
                        step=1,
                        key="cli_slider_fotos"
                    )
                    
                    if novo_idx - 1 != st.session_state.cli_foto_idx:
                        st.session_state.cli_foto_idx = novo_idx - 1
                        st.rerun()

            else:
                st.info("Nenhuma foto cadastrada para este imóvel.")
                
            st.divider()
            
            # --- ESPECIFICAÇÕES ---
            st.subheader("📐 Especificações do Imóvel")
            c_c1, c_c2, c_c3, c_c4 = st.columns(4)
            c_c1.metric("Quartos", imovel_cli.get("quartos", 0))
            c_c2.metric("Suítes", imovel_cli.get("suites", 0))
            c_c3.metric("Banheiros", imovel_cli.get("banheiros", 0))
            c_c4.metric("Vagas Garagem", imovel_cli.get("vagas_garagem", 0))
            
            if imovel_cli.get("area_terreno") or imovel_cli.get("area_construida"):
                c_a1, c_a2 = st.columns(2)
                if imovel_cli.get("area_terreno"):
                    c_a1.metric("Área do Lote", f"{imovel_cli.get('area_terreno')} m²")
                if imovel_cli.get("area_construida"):
                    c_a2.metric("Área Construída", f"{imovel_cli.get('area_construida')} m²")

            st.divider()
            
            # --- DESCRIÇÃO ---
            st.subheader("📋 Descrição Detalhada")
            st.write(imovel_cli.get("descricao", "Sem descrição disponível."))
            
            st.divider()
            
            # --- BOTÃO DE WHATSAPP ---
            msg_wsp = f"Olá! Vi o imóvel código {imovel_cli.get('codigo_imovel')} e gostaria de agendar uma visita/saber mais detalhes!"
            url_wsp = f"https://wa.me/5535998102465?text={urllib.parse.quote(msg_wsp)}"
            
            st.link_button("📱 Tenho Interesse! Falar com Corretor no WhatsApp", url_wsp, use_container_width=True, type="primary")
            
            st.stop()
        else:
            st.error("Imóvel não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar dados do imóvel: {e}")
        st.stop()

# --- FUNÇÃO DE GERAÇÃO DE DESCRIÇÃO COM IA (GEMINI) ---
def gerar_descricao_ia(tipo, bairro, quartos, suites, vagas, valor):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "Erro: A chave 'GEMINI_API_KEY' não foi encontrada nas Secrets ou Variáveis de Ambiente."

    prompt = f"""
    Você é um copywriter especialista no mercado imobiliário da Mendes & Soares Engenharia e Imóveis.
    Escreva uma descrição comercial altamente atraente e persuasiva para o seguinte imóvel:
    - Tipo: {tipo}
    - Bairro: {bairro} (Passos-MG)
    - Quartos: {quartos} (sendo {suites} suítes)
    - Vagas de Garagem: {vagas}
    - Valor: R$ {valor:,.2f}

    Diretrizes:
    1. Crie um título forte no início.
    2. Destaque o conforto, a localização e os diferenciais.
    3. Use parágrafos curtos e emojis adequados.
    4. Mantenha um tom profissional, elegante e acolhedor.
    5. Termine convidando o cliente para agendar uma visita com a equipe da Mendes & Soares.
    """

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Erro ao comunicar com a API do Gemini: {str(e)}"

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
def carregar_imoveis():
    try:
        res = supabase.table("imoveis").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar imóveis: {e}")
        return []

def carregar_leads():
    try:
        res = supabase.table("leads").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return []

def carregar_visitas():
    try:
        res = supabase.table("visitas").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

def carregar_interacoes(lead_id):
    try:
        res = supabase.table("interacoes_leads").select("*").eq("lead_id", lead_id).order("data_hora", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

def calcular_total_matches(imoveis, leads):
    total = 0
    leads_ativos = [l for l in leads if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']]
    imoveis_disp = [i for i in imoveis if i.get('status', 'Disponível') == 'Disponível']
    
    for l in leads_ativos:
        orc = float(l.get('orcamento_maximo') or l.get('orcamento_max') or 0.0)
        bairros_raw = l.get('bairros_interesse', [])
        if isinstance(bairros_raw, str):
            bairros = [b.strip() for b in bairros_raw.split(",") if b.strip()]
        else:
            bairros = bairros_raw
            
        for im in imoveis_disp:
            preco = float(im.get('valor_venda', 0.0))
            bairro = im.get('bairro', '')
            match_preco = preco <= orc
            match_bairro = (not bairros) or (bairro in bairros)
            if match_preco and match_bairro:
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

# --- ESTILIZAÇÃO CSS ---
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
    section[data-testid="stSidebar"] .stRadio label {{
        color: #e2e8f0 !important;
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
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stCard:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(24, 30, 41, 0.12);
    }}
    .price-badge {{
        background: linear-gradient(135deg, {COR_DOURADO}, {COR_DOURADO_HOVER});
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.0em;
        display: inline-block;
        text-align: center;
        box-shadow: 0 2px 6px rgba(197, 155, 39, 0.3);
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
        margin-bottom: 4px;
        border: 1px solid #cbd5e1;
    }}
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
    h1, h2, h3 {{
        color: {COR_AZUL_MARINHO} !important;
        font-weight: 700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DADOS ---
imoveis_data = carregar_imoveis()
leads_data = carregar_leads()
visitas_data = carregar_visitas()

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
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #94a3b8;'>📍 Passos - MG<br>📞 (35) 9 9810-2465</p>", unsafe_allow_html=True)

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Painel Geral — Mendes & Soares")
    st.write("Métricas operacionais e gestão estratégica do funil de vendas.")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)
    
    imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
    leads_em_negociacao = [l for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']]
    visitas_pendentes = [v for v in visitas_data if v.get('status', 'Agendada') == 'Agendada']
    total_matches = calcular_total_matches(imoveis_data, leads_data)
    leads_fechados = [l for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) == '🟢 Já comprou (Fechado)']
    
    with col1:
        st.metric(label="🏠 Imóveis Disponíveis", value=len(imoveis_disponiveis))
    with col2:
        st.metric(label="👥 Leads em Negociação", value=len(leads_em_negociacao))
    with col3:
        st.metric(label="🎯 Matches Ativos", value=total_matches)
    with col4:
        st.metric(label="📅 Visitas Agendadas", value=len(visitas_pendentes))
    with col5:
        st.metric(label="🎉 Vendas Concluídas", value=len(leads_fechados))

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
            cod_imovel = imovel.get('codigo_imovel')
            link_cliente = f"{URL_BASE_APP}/?imovel={cod_imovel}"
            
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
                        st.subheader(f"{imovel.get('tipo')} — Cód: **{cod_imovel}**")
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
                    
                    with st.expander("📄 Ver descrição detalhada do imóvel"):
                        st.write(imovel.get('descricao', 'Sem descrição cadastrada.'))
                    
                    st.caption("🔗 Link para envio direto ao cliente (com fotos e carrossel):")
                    st.code(link_cliente, language="text")

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

                with st.expander(f"🗑️ Excluir Imóvel {cod_imovel}"):
                    st.warning("⚠️ Esta ação é permanente e removerá o imóvel da base de dados.")
                    confirma_excluir = st.checkbox("Confirmar exclusão deste imóvel", key=f"chk_del_{imovel_id}")
                    if st.button("🚨 Excluir Definitivamente", key=f"btn_del_{imovel_id}", type="primary"):
                        if confirma_excluir:
                            supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                            st.success(f"Imóvel **{cod_imovel}** removido com sucesso!")
                            st.rerun()

                with st.expander(f"✏️ Editar imóvel {cod_imovel}"):
                    tipos_list = ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"]
                    idx_tipo = tipos_list.index(imovel.get('tipo')) if imovel.get('tipo') in tipos_list else 0
                    idx_bairro = BAIRROS_PASSOS.index(imovel.get('bairro')) if imovel.get('bairro') in BAIRROS_PASSOS else 0
                    idx_corretor = CORRETORES.index(imovel.get('corretor_captacao')) if imovel.get('corretor_captacao') in CORRETORES else 0

                    key_desc = f"e_desc_val_{imovel_id}"
                    if key_desc not in st.session_state:
                        st.session_state[key_desc] = imovel.get('descricao', '')

                    with st.form(key=f"form_editar_imovel_{imovel_id}"):
                        e_c1, e_c2, e_c3 = st.columns(3)
                        with e_c1:
                            e_tipo = st.selectbox("Tipo de Imóvel", tipos_list, index=idx_tipo)
                            e_nome_prop = st.text_input("Nome do Proprietário", value=imovel.get('nome_proprietario', ''))
                        with e_c2:
                            e_bairro = st.selectbox("Bairro (Passos-MG)", BAIRROS_PASSOS, index=idx_bairro)
                            e_tel_prop = st.text_input("Telefone do Proprietário", value=imovel.get('telefone_proprietario', ''))
                            e_valor = st.number_input("Valor de Venda (R$)", min_value=0.0, value=float(imovel.get('valor_venda', 0.0)), step=10000.0)
                        with e_c3:
                            e_corretor = st.selectbox("Corretor Captação", CORRETORES, index=idx_corretor)
                            e_endereco = st.text_input("Endereço do Imóvel", value=imovel.get('endereco', ''))
                            e_area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, value=float(imovel.get('area_terreno', 0.0) or 0.0), step=10.0)
                            e_area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=float(imovel.get('area_construida', 0.0) or 0.0), step=10.0)

                        st.divider()
                        e_cq1, e_cq2, e_cq3, e_cq4 = st.columns(4)
                        with e_cq1: e_quartos = st.number_input("Dormitórios", min_value=0, value=int(imovel.get('quartos', 0) or 0), step=1)
                        with e_cq2: e_suites = st.number_input("Suítes", min_value=0, value=int(imovel.get('suites', 0) or 0), step=1)
                        with e_cq3: e_banheiros = st.number_input("Banheiros", min_value=0, value=int(imovel.get('banheiros', 0) or 0), step=1)
                        with e_cq4: e_vagas = st.number_input("Vagas Garagem", min_value=0, value=int(imovel.get('vagas_garagem', 0) or 0), step=1)

                        st.divider()
                        e_c5, e_c6 = st.columns(2)
                        with e_c5:
                            e_sala = st.checkbox("Sala", value=bool(imovel.get('sala', True)))
                            e_copa = st.checkbox("Copa", value=bool(imovel.get('copa', False)))
                            e_cozinha = st.checkbox("Cozinha", value=bool(imovel.get('cozinha', True)))
                        with e_c6:
                            e_garagem_coberta = st.checkbox("🚘 Garagem Coberta", value=bool(imovel.get('garagem_coberta', False)))
                            e_area_gourmet = st.checkbox("🍖 Área Gourmet", value=bool(imovel.get('area_gourmet', False)))

                        st.divider()
                        
                        e_descricao = st.text_area(
                            "Descrição do Imóvel", 
                            value=st.session_state[key_desc], 
                            height=150
                        )

                        c_btn_ia, c_btn_salvar = st.columns([1, 1])
                        
                        with c_btn_ia:
                            btn_ia = st.form_submit_button("✨ Re-gerar Descrição com IA")
                        with c_btn_salvar:
                            btn_salvar = st.form_submit_button("💾 Salvar Alterações", type="primary")

                        if btn_ia:
                            with st.spinner("Gerando nova descrição com IA..."):
                                nova_desc = gerar_descricao_ia(
                                    tipo=e_tipo,
                                    bairro=e_bairro,
                                    quartos=e_quartos,
                                    suites=e_suites,
                                    vagas=e_vagas,
                                    valor=e_valor
                                )
                                st.session_state[key_desc] = nova_desc
                                st.rerun()

                        if btn_salvar:
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
                                "area_terreno": float(e_area_terreno),
                                "area_construida": float(e_area_construida),
                                "descricao": str(e_descricao)
                            }
                            
                            colunas_existentes = list(imovel.keys())
                            dados_atualizados = {k: v for k, v in payload.items() if k in colunas_existentes}
                            
                            try:
                                supabase.table("imoveis").update(dados_atualizados).eq("id", imovel_id).execute()
                                if key_desc in st.session_state:
                                    del st.session_state[key_desc]
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
    
    st.subheader("📝 Descrição do Imóvel")
    if st.button("✨ Gerar Descrição com IA"):
        with st.spinner("A IA está criando o texto para o imóvel..."):
            desc_ia = gerar_descricao_ia(tipo, bairro, quartos, suites, vagas, valor)
            st.session_state['descricao_temp'] = desc_ia
            st.rerun()

    descricao = st.text_area(
        "Descrição Geral / Observações", 
        value=st.session_state.get('descricao_temp', ''),
        height=150
    )
    
    fotos = st.file_uploader("📷 Fotos do Imóvel", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    if st.button("💾 Salvar Imóvel", use_container_width=True, type="primary"):
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
            if 'descricao_temp' in st.session_state:
                del st.session_state['descricao_temp']
            st.rerun()
        except Exception as err:
            st.error(f"Erro ao salvar imóvel: {err}")

# ==========================================
# 👤 ABA 4: NOVO LEAD
# ==========================================
elif "Novo Lead" in menu:
    st.title("➕ Cadastrar Novo Lead")
    st.write("Preencha as preferências e dados do cliente para salvar no sistema.")
    st.divider()

    with st.form("form_novo_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome do Cliente *", placeholder="Ex: João Silva")
            whatsapp = st.text_input("WhatsApp / Telefone *", placeholder="Ex: 35999998888")
            email = st.text_input("E-mail", placeholder="Ex: joao@email.com")
            
            tipo_imovel = st.multiselect(
                "Tipo de Imóvel Preferido",
                options=["Casa", "Apartamento", "Terreno", "Chácara"],
                default=["Casa"]
            )

        with col2:
            num_quartos = st.number_input("Número Mínimo de Quartos", min_value=0, max_value=10, value=2, step=1)
            
            orcamento = st.number_input(
                "Orçamento Máximo (R$)", 
                min_value=0.0, 
                value=300000.0, 
                step=10000.0, 
                format="%.2f"
            )

            e_financiamento = st.radio(
                "Pretende fazer Financiamento Bancário?", 
                options=["Sim", "Não"], 
                horizontal=True
            )
            
            financiamento_aprovado = "Não se aplica"
            if e_financiamento == "Sim":
                financiamento_aprovado = st.radio(
                    "O Crédito / Financiamento já está Aprovado?", 
                    options=["Sim", "Não", "Em Análise"], 
                    horizontal=True
                )

        bairros_sugeridos = ["Centro", "Jardim América", "Vilagio D' Itália", "Nossa Senhora das Graças"]
        bairros = st.multiselect("Bairros de Interesse", options=bairros_sugeridos)

        status_inicial = st.selectbox(
            "Status Inicial no Funil", 
            options=[
                "🔵 Novo Lead (Sem Contato)",
                "🟡 Em Atendimento",
                "🟡 Visita Agendada",
                "🟠 Proposta Enviada (Quente)",
                "🟢 Já comprou (Fechado)",
                "🔴 Perdido/Inativo"
            ]
        )

        observacoes = st.text_area("Observações / Detalhes do Perfil")

        submitted = st.form_submit_button("💾 Salvar Lead", use_container_width=True)

        if submitted:
            if not nome or not whatsapp:
                st.error("Por favor, preencha os campos obrigatórios (Nome e WhatsApp).")
            else:
                try:
                    novo_lead_data = {
                        "nome": nome,
                        "whatsapp": whatsapp,
                        "email": email,
                        "tipo_imovel": tipo_imovel,
                        "quartos_min": int(num_quartos),
                        "orcamento_maximo": float(orcamento),
                        "financiamento": e_financiamento,
                        "financiamento_aprovado": financiamento_aprovado,
                        "bairros_interesse": bairros,
                        "status": status_inicial,
                        "observacoes": observacoes
                    }

                    supabase.table("leads").insert(novo_lead_data).execute()
                    st.success(f"Lead **{nome}** cadastrado com sucesso!")
                    st.toast("Lead registrado!", icon="✅")
                except Exception as e:
                    st.error(f"Erro ao cadastrar lead no Supabase: {e}")

# ==========================================
# 👥 ABA 5: FUNIL DE LEADS COMPACTO POR ABAS
# ==========================================
elif menu == "👥 Funil de Leads":
    st.title("👥 Funil de Negociação de Leads")
    st.caption("Organização em colunas compactas por status de atendimento.")
    
    with st.expander("🔍 **Filtros e Busca**", expanded=False):
        fl_col1, fl_col2 = st.columns([2, 2])
        with fl_col1: 
            busca_lead = st.text_input("🔎 Pesquisar Nome ou WhatsApp", key="busca_lead")
        with fl_col2: 
            filtro_bairro_lead = st.selectbox("Filtrar por Bairro", ["Todos"] + BAIRROS_PASSOS, key="filtro_bairro_lead")

    st.divider()

    leads_filtrados = leads_data
    if busca_lead:
        termo_l = busca_lead.lower().strip()
        leads_filtrados = [l for l in leads_filtrados if termo_l in str(l.get('nome', '')).lower() or termo_l in str(l.get('whatsapp', '')).lower()]
    if filtro_bairro_lead != "Todos":
        leads_filtrados = [l for l in leads_filtrados if filtro_bairro_lead in str(l.get('bairros_interesse', ''))]

    contagem_por_status = {status: 0 for status in STATUS_LEADS}
    leads_agrupados = {status: [] for status in STATUS_LEADS}

    for l in leads_filtrados:
        st_lead = l.get('status', '🔵 Em busca (Frio)')
        st_normalizado = MAPEAMENTO_STATUS.get(st_lead, st_lead)
        
        if st_normalizado in contagem_por_status:
            contagem_por_status[st_normalizado] += 1
            leads_agrupados[st_normalizado].append(l)
        else:
            contagem_por_status["🔵 Em busca (Frio)"] += 1
            leads_agrupados["🔵 Em busca (Frio)"].append(l)

    titulos_abas = [
        f"{contagem_por_status[status]:02d} {status}" 
        for status in STATUS_LEADS
    ]

    tabs = st.tabs(titulos_abas)

    for i, status_original in enumerate(STATUS_LEADS):
        with tabs[i]:
            leads_da_aba = leads_agrupados[status_original]

            st.caption(f"Total nesta etapa: **{len(leads_da_aba)}** cliente(s)")

            if not leads_da_aba:
                st.info("Nenhum cliente nesta etapa.")
            else:
                for lead in leads_da_aba:
                    lead_id = lead.get('id')
                    nome_lead = lead.get('nome', 'Sem nome')
                    zap_lead = lead.get('whatsapp', 'S/N')
                    bairros_raw = lead.get('bairros_interesse', '')
                    bairros_str = ", ".join(bairros_raw) if isinstance(bairros_raw, list) else str(bairros_raw or "Nenhum")
                    orc_val = lead.get('orcamento_maximo') or lead.get('orcamento_max') or 0.0
                    corr_val = lead.get('corretor_responsavel') or lead.get('corretor') or 'Não informado'
                    obs_val = lead.get('observacoes', '')

                    with st.container():
                        st.markdown('<div class="stCard" style="padding: 10px 14px; margin-bottom: 8px;">', unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([2.5, 1.5])
                        with c1:
                            st.markdown(f"**{status_original.split()[0]} {nome_lead}** | 📱 {zap_lead}")
                            st.caption(f"📍 {bairros_str} | 💰 R$ {float(orc_val):,.2f} | 🔑 {corr_val}")
                        
                        with c2:
                            idx_atual = STATUS_LEADS.index(status_original) if status_original in STATUS_LEADS else 0
                            novo_st = st.selectbox(
                                "Mover para:",
                                STATUS_LEADS,
                                index=idx_atual,
                                key=f"fast_move_{lead_id}",
                                label_visibility="collapsed"
                            )
                            if novo_st != status_original:
                                supabase.table("leads").update({"status": novo_st}).eq("id", lead_id).execute()
                                st.rerun()

                        with st.expander("💬 Histórico / Editar"):
                            if obs_val:
                                st.info(f"**Obs:** {obs_val}")
                            
                            with st.form(key=f"form_int_compact_{lead_id}"):
                                ic1, ic2 = st.columns([1, 2])
                                with ic1:
                                    c_int = st.selectbox("Corretor", CORRETORES, key=f"c_ic_{lead_id}")
                                with ic2:
                                    m_int = st.text_input("Nova Mensagem/Anotação", key=f"m_ic_{lead_id}")
                                
                                if st.form_submit_button("➕ Salvar Anotação"):
                                    if m_int:
                                        payload_int = {
                                            "lead_id": lead_id,
                                            "corretor": c_int,
                                            "mensagem": m_int,
                                            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M")
                                        }
                                        supabase.table("interacoes_leads").insert(payload_int).execute()
                                        st.rerun()

                            historico = carregar_interacoes(lead_id)
                            for h in historico:
                                st.caption(f"🕒 {h.get('data_hora', '')} - **{h.get('corretor')}**: {h.get('mensagem')}")

                            st.divider()
                            if st.button("🗑️ Excluir Lead", key=f"del_comp_{lead_id}", type="secondary"):
                                supabase.table("leads").delete().eq("id", lead_id).execute()
                                st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🎯 ABA 6: ENCONTRAR MATCHES COM AÇÕES
# ==========================================
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Cruzamento de Dados (Matches)")
    st.write("Encontre os imóveis ideais para cada cliente e gerencie as etapas do match.")
    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado para realizar o cruzamento.")
    else:
        opcoes_leads = {f"{l.get('nome', 'Sem nome')} ({l.get('whatsapp', 'S/N')})": l for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']}
        
        if not opcoes_leads:
            st.warning("Não há leads ativos em negociação no momento.")
        else:
            lead_sel_nome = st.selectbox("Selecione o Lead para buscar imóveis compatíveis:", list(opcoes_leads.keys()))
            lead_sel = opcoes_leads[lead_sel_nome]
            lead_id = lead_sel.get('id')

            bairros_lead_raw = lead_sel.get('bairros_interesse', [])
            if isinstance(bairros_lead_raw, str):
                bairros_lead = [b.strip() for b in bairros_lead_raw.split(",") if b.strip()]
            else:
                bairros_lead = bairros_lead_raw

            orc_lead = float(lead_sel.get('orcamento_maximo') or lead_sel.get('orcamento_max') or 0.0)

            st.markdown(f"**Perfil do Lead:** Orçamento de até **R$ {orc_lead:,.2f}** nos bairros: *{', '.join(bairros_lead) if bairros_lead else 'Todos'}*")
            
            historico_matches = {}
            try:
                res_m = supabase.table("matches_status").select("*").eq("lead_id", lead_id).execute()
                if res_m.data:
                    historico_matches = {item['imovel_id']: item['status'] for item in res_m.data}
            except Exception:
                pass

            exibir_arquivados = st.checkbox("👁️ Mostrar imóveis arquivados/descartados por este cliente", value=False)
            st.divider()

            matches = []
            for im in imoveis_data:
                im_id = im.get('id')
                status_match = historico_matches.get(im_id, "Pendente")

                if status_match == "Viu e não gostou" and not exibir_arquivados:
                    continue

                if im.get('status', 'Disponível') == 'Disponível':
                    preco_imovel = float(im.get('valor_venda', 0.0))
                    bairro_imovel = im.get('bairro', '')
                    
                    match_preco = preco_imovel <= orc_lead
                    match_bairro = (not bairros_lead) or (bairro_imovel in bairros_lead)

                    if match_preco and match_bairro:
                        matches.append((im, status_match))

            st.subheader(f"Imóveis Encontrados: {len(matches)}")
            
            if not matches:
                st.info("Nenhum imóvel disponível corresponde aos critérios deste lead no momento.")
            else:
                for match, st_match in matches:
                    imovel_id = match.get('id')
                    cod_im = match.get('codigo_imovel')
                    link_match = f"{URL_BASE_APP}/?imovel={cod_im}"
                    
                    with st.container():
                        st.markdown('<div class="stCard">', unsafe_allow_html=True)
                        m_c1, m_c2 = st.columns([2.5, 1.5])
                        
                        with m_c1:
                            st.markdown(f"### {match.get('tipo')} — Cód: {cod_im}")
                            st.write(f"📍 Bairro: **{match.get('bairro')}** | 💰 R$ {match.get('valor_venda', 0):,.2f}")
                            st.write(f"🛏️ {match.get('quartos', 0)} qtos | 🚿 {match.get('suites', 0)} suítes | 🚗 {match.get('vagas_garagem', 0)} vagas")
                            
                            if st_match != "Pendente":
                                st.caption(f"📌 **Status atual do Match:** `{st_match}`")

                        with m_c2:
                            msg_wa = f"Olá {lead_sel.get('nome')}! Encontrei este imóvel perfeito para você: {match.get('tipo')} no bairro {match.get('bairro')} por R$ {match.get('valor_venda', 0):,.2f}.\n\nConfira as fotos e detalhes completa no link:\n{link_match}"
                            url_wa = f"https://wa.me/{str(lead_sel.get('whatsapp')).replace('+', '').replace(' ', '').replace('-', '')}?text={urllib.parse.quote(msg_wa)}"
                            
                            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:8px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom: 6px;">📱 Enviar Link via WhatsApp</button></a>', unsafe_allow_html=True)
                            
                            st.caption("📋 Copiar Link do Imóvel:")
                            st.code(link_match, language="text")
                            
                            st.divider()
                            st.caption("Ações do Match:")
                            
                            col_a1, col_a2, col_a3 = st.columns(3)
                            
                            with col_a1:
                                if st.button("🚫 Descartar", key=f"desc_{imovel_id}_{lead_id}", help="Cliente viu e não gostou (Arquiva o match)"):
                                    try:
                                        supabase.table("matches_status").upsert({
                                            "lead_id": lead_id,
                                            "imovel_id": imovel_id,
                                            "status": "Viu e não gostou"
                                        }).execute()
                                        st.toast("Match arquivado!", icon="📦")
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Erro: {err}")

                            with col_a2:
                                if st.button("📅 Visita", key=f"vis_{imovel_id}_{lead_id}", help="Agendar visita e atualizar lead"):
                                    try:
                                        supabase.table("matches_status").upsert({
                                            "lead_id": lead_id,
                                            "imovel_id": imovel_id,
                                            "status": "Visita Agendada"
                                        }).execute()
                                        
                                        supabase.table("leads").update({"status": "🟡 Visita Agendada"}).eq("id", lead_id).execute()
                                        st.toast("Visita marcada e Lead movido no Funil!", icon="📅")
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Erro: {err}")

                            with col_a3:
                                if st.button("📝 Proposta", key=f"prop_{imovel_id}_{lead_id}", help="Enviar proposta e mover lead"):
                                    try:
                                        supabase.table("matches_status").upsert({
                                            "lead_id": lead_id,
                                            "imovel_id": imovel_id,
                                            "status": "Proposta Enviada"
                                        }).execute()
                                        
                                        supabase.table("leads").update({"status": "🟠 Proposta Enviada (Quente)"}).eq("id", lead_id).execute()
                                        st.toast("Proposta registrada e Lead movido no Funil!", icon="📝")
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Erro: {err}")

                        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📅 ABA 7: VISITAS AGENDADAS
# ==========================================
elif menu == "📅 Visitas Agendadas":
    st.title("📅 Agendamento de Visitas")
    st.write("Agende e acompanhe as visitas técnicas e comerciais aos imóveis.")
    st.divider()

    with st.form("form_visita", clear_on_submit=True):
        v_c1, v_c2 = st.columns(2)
        
        imoveis_opts = [f"{i.get('codigo_imovel')} - {i.get('tipo')} ({i.get('bairro')})" for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
        leads_opts = [f"{l.get('nome')} ({l.get('whatsapp')})" for l in leads_data if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']]

        with v_c1:
            imovel_visita = st.selectbox("Selecione o Imóvel *", imoveis_opts if imoveis_opts else ["Nenhum imóvel disponível"])
            lead_visita = st.selectbox("Selecione o Lead / Cliente *", leads_opts if leads_opts else ["Nenhum lead disponível"])
            corretor_visita = st.selectbox("Corretor Responsável *", CORRETORES)
        with v_c2:
            data_visita = st.date_input("Data da Visita *", date.today())
            hora_visita = st.time_input("Horário da Visita *", datetime.now().time())
            obs_visita = st.text_area("Observações da Visita")

        if st.form_submit_button("📅 Confirmar Agendamento", use_container_width=True, type="primary"):
            if not imoveis_opts or not leads_opts:
                st.error("Não é possível agendar sem imóveis ou leads disponíveis.")
            else:
                payload_visita = {
                    "imovel_info": imovel_visita,
                    "lead_info": lead_visita,
                    "corretor": corretor_visita,
                    "data": str(data_visita),
                    "hora": str(hora_visita),
                    "observacoes": obs_visita,
                    "status": "Agendada"
                }
                try:
                    supabase.table("visitas").insert(payload_visita).execute()
                    st.success("✅ Visita agendada com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar visita: {err}")

    st.divider()
    st.subheader("📋 Visitas Cadastradas")

    if not visitas_data:
        st.info("Nenhuma visita agendada até o momento.")
    else:
        for v in visitas_data:
            v_id = v.get('id')
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                vc1, vc2 = st.columns([3, 1])
                with vc1:
                    st.markdown(f"### 📅 {v.get('data')} às {v.get('hora')}")
                    st.write(f"🏠 **Imóvel:** {v.get('imovel_info')}")
                    st.write(f"👤 **Cliente:** {v.get('lead_info')} | 🔑 **Corretor:** {v.get('corretor')}")
                    if v.get('observacoes'):
                        st.write(f"📝 **Obs:** {v.get('observacoes')}")
                with vc2:
                    st.caption(f"Status: **{v.get('status', 'Agendada')}**")
                    if st.button("🗑️ Cancelar / Excluir", key=f"del_vis_{v_id}"):
                        try:
                            supabase.table("visitas").delete().eq("id", v_id).execute()
                            st.success("Visita removida!")
                            st.rerun()
                        except Exception as err:
                            st.error(f"Erro ao remover: {err}")
                st.markdown('</div>', unsafe_allow_html=True)
