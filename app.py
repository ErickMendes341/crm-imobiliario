import streamlit as st
from supabase import create_client
import urllib.parse
import os
from datetime import date, datetime
from io import BytesIO
import requests

# --- NOVAS IMPORTAÇÕES PARA PDF E IA ---
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

# --- FUNÇÃO DE GERAÇÃO DE PDF DE VENDAS (COM FOTOS) ---
def gerar_pdf_imovel(imovel):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor(COR_DOURADO),
        spaceAfter=10
    )

    story.append(Paragraph(f"<b>{imovel.get('tipo', 'Imóvel')} - {imovel.get('bairro', '')}</b>", title_style))
    story.append(Paragraph(f"Código: {imovel.get('codigo_imovel', 'N/A')} | Valor: R$ {float(imovel.get('valor_venda', 0)):,.2f}", styles['Heading2']))
    story.append(Spacer(1, 10))

    fotos_urls = imovel.get("fotos_urls") or []
    if fotos_urls and len(fotos_urls) > 0:
        try:
            resp = requests.get(fotos_urls[0], timeout=5)
            if resp.status_code == 200:
                img_data = BytesIO(resp.content)
                img = Image(img_data, width=400, height=250)
                story.append(img)
                story.append(Spacer(1, 15))
        except Exception:
            pass

    dados_tabela = [
        ["Quartos", "Suítes", "Banheiros", "Vagas"],
        [str(imovel.get('quartos', 0)), str(imovel.get('suites', 0)), str(imovel.get('banheiros', 0)), str(imovel.get('vagas_garagem', 0))]
    ]
    t = Table(dados_tabela, colWidths=[100, 100, 100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(COR_AZUL_MARINHO)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#F5F5F5")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD"))
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Descrição do Imóvel:</b>", styles['Heading3']))
    story.append(Paragraph(imovel.get('descricao', 'Sem descrição cadastrada.'), styles['Normal']))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Mendes & Soares Engenharia e Imóveis</b>", styles['Normal']))
    tel_contato = imovel.get('telefone_proprietario') or '(35) 9 9810-2465'
    story.append(Paragraph(f"Contato: {tel_contato}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNÇÃO DE GERAÇÃO DE DESCRIÇÃO COM IA (GEMINI 3.6 FLASH) ---
def gerar_descricao_ia(tipo, bairro, quartos, suites, vagas, valor):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "Erro: A chave 'GEMINI_API_KEY' não foi encontrada nas Secrets do Streamlit."

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

# --- FUNÇÕES DE DADOS ---
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
    except Exception as e:
        return []

def carregar_interacoes(lead_id):
    try:
        res = supabase.table("interacoes_leads").select("*").eq("lead_id", lead_id).order("data_hora", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

# --- GERAÇÃO AUTOMÁTICA DE CÓDIGO ---
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

# --- ESTILIZAÇÃO CSS PERSONALIZADA MENDES & SOARES + OTIMIZAÇÃO MOBILE ---
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
        padding: 16px;
        box-shadow: 0 4px 15px rgba(24, 30, 41, 0.06);
        margin-bottom: 16px;
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
    
    /* OTIMIZAÇÃO PARA CELULAR (RESPONSIVIDADE) */
    @media (max-width: 768px) {{
        .stCard {{
            padding: 12px !important;
            margin-bottom: 12px !important;
        }}
        div.stButton > button {{
            width: 100% !important;
        }}
        .price-badge {{
            width: 100% !important;
            margin-top: 6px !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
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
                    
                    pdf_imovel = gerar_pdf_imovel(imovel)
                    st.download_button(
                        label="📄 Baixar PDF de Vendas",
                        data=pdf_imovel,
                        file_name=f"imovel_{imovel.get('codigo_imovel', 'ficha')}.pdf",
                        mime="application/pdf",
                        key=f"btn_pdf_cat_{imovel_id}"
                    )
                    
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

                with st.expander(f"🗑️ Excluir Imóvel {imovel.get('codigo_imovel')}"):
                    st.warning("⚠️ Esta ação é permanente e removerá o imóvel da base de dados.")
                    confirma_excluir = st.checkbox("Confirmar exclusão deste imóvel", key=f"chk_del_{imovel_id}")
                    if st.button("🚨 Excluir Definitivamente", key=f"btn_del_{imovel_id}", type="primary"):
                        if confirma_excluir:
                            supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                            st.success(f"Imóvel **{imovel.get('codigo_imovel')}** removido com sucesso!")
                            st.rerun()

                # --- SANFONA DE EDIÇÃO COM GERADOR DE IA ---
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

                        st.divider()
                        
                        btn_ia_edit = st.form_submit_button("✨ Gerar/Recalcular Descrição com IA", type="secondary")
                        
                        desc_padrao = imovel.get('descricao', '')
                        if btn_ia_edit:
                            with st.spinner("Gerando nova descrição com IA..."):
                                nova_desc = gerar_descricao_ia(
                                    tipo=e_tipo,
                                    bairro=e_bairro,
                                    quartos=e_quartos,
                                    suites=e_suites,
                                    vagas=e_vagas,
                                    valor=e_valor
                                )
                                st.session_state[f"temp_desc_edit_{imovel_id}"] = nova_desc

                        val_desc_final = st.session_state.get(f"temp_desc_edit_{imovel_id}", desc_padrao)

                        e_descricao = st.text_area("Descrição do Imóvel", value=val_desc_final, height=150, key=f"e_desc_{imovel_id}")
                        
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
                                if f"temp_desc_edit_{imovel_id}" in st.session_state:
                                    del st.session_state[f"temp_desc_edit_{imovel_id}"]
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
                bairros_valor = ", ".join(bairros_interesse) if isinstance(bairros_interesse, list) else bairros_interesse

                payload_lead = {
                    "nome": nome, 
                    "whatsapp": whatsapp, 
                    "bairros_interesse": bairros_valor,
                    "orcamento_maximo": orcamento, 
                    "orcamento_max": orcamento,
                    "corretor_responsavel": corretor_lead,
                    "corretor": corretor_lead, 
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
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar lead: {err}")

# ==========================================
# 👥 ABA 5: GERENCIAR LEADS + HISTÓRICO DE INTERAÇÕES
# ==========================================
elif menu == "👥 Gerenciar Leads":
    st.title("👥 Gerenciamento de Leads")
    st.write("Gerencie o perfil de busca e acompanhe todo o histórico de interações.")
    
    with st.expander("🔍 **Filtros e Busca de Leads**", expanded=True):
        fl_col1, fl_col2, fl_col3 = st.columns([2, 1.5, 2.5])
        with fl_col1: busca_lead = st.text_input("🔎 Pesquisar Nome ou WhatsApp", key="busca_lead")
        with fl_col2: filtro_status_lead = st.selectbox("Status", ["Todos", "Em busca", "Já comprou"], index=1, key="filtro_status_lead")
        with fl_col3: filtro_bairro_lead = st.selectbox("Filtrar por Bairro", ["Todos"] + BAIRROS_PASSOS, key="filtro_bairro_lead")

    st.divider()

    leads_filtrados = leads_data
    if busca_lead:
        termo_l = busca_lead.lower().strip()
        leads_filtrados = [l for l in leads_filtrados if termo_l in str(l.get('nome', '')).lower() or termo_l in str(l.get('whatsapp', '')).lower()]
    if filtro_status_lead != "Todos":
        leads_filtrados = [l for l in leads_filtrados if l.get('status', 'Em busca') == filtro_status_lead]
    if filtro_bairro_lead != "Todos":
        leads_filtrados = [l for l in leads_filtrados if filtro_bairro_lead in str(l.get('bairros_interesse', ''))]

    st.caption(f"Exibindo **{len(leads_filtrados)}** de **{len(leads_data)}** clientes.")

    if not leads_filtrados:
        st.info("Nenhum lead encontrado.")
    else:
        for lead in leads_filtrados:
            lead_id = lead.get('id')
            status_lead = lead.get('status', 'Em busca')
            nome_lead = lead.get('nome', 'Sem nome')
            zap_lead = lead.get('whatsapp', 'S/N')
            bairros_raw = lead.get('bairros_interesse', '')
            
            if isinstance(bairros_raw, list):
                bairros_str = ", ".join(bairros_raw)
            else:
                bairros_str = str(bairros_raw or "Nenhum")

            orc_val = lead.get('orcamento_maximo') or lead.get('orcamento_max') or 0.0
            corr_val = lead.get('corretor_responsavel') or lead.get('corretor') or 'Não informado'
            obs_val = lead.get('observacoes', '')

            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"👤 {nome_lead} — {zap_lead}")
                    st.write(f"📍 **Bairros de Interesse:** {bairros_str}")
                    st.write(f"💰 **Orçamento Máximo:** R$ {float(orc_val):,.2f} | 🔑 **Corretor:** {corr_val}")
                    if obs_val:
                        st.write(f"📝 **Desejos / Obs:** {obs_val}")
                
                with col2:
                    novo_status_lead = st.radio("Status do Lead:", ["Em busca", "Já comprou"], index=0 if status_lead == "Em busca" else 1, key=f"status_direct_{lead_id}")
                    if novo_status_lead != status_lead:
                        supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead_id).execute()
                        st.success("Status atualizado!")
                        st.rerun()

                # --- HISTÓRICO DE INTERAÇÕES COM O CLIENTE ---
                with st.expander("💬 Histórico de Atendimentos / Interações"):
                    st.write("**Registrar novo contato:**")
                    with st.form(key=f"form_interacao_{lead_id}"):
                        c_i1, c_i2 = st.columns([1, 2])
                        with c_i1:
                            corretor_int = st.selectbox("Corretor", CORRETORES, key=f"c_int_{lead_id}")
                        with c_i2:
                            nota_int = st.text_input("Resumo da conversa / Feedback", placeholder="Ex: Enviei opções pelo WhatsApp, cliente gostou do imóvel MS-002 e quer agendar visita.", key=f"n_int_{lead_id}")
                        
                        btn_salvar_int = st.form_submit_button("💬 Registrar Interação", type="secondary")
                        if btn_salvar_int:
                            if not nota_int:
                                st.error("Escreva um resumo da interação.")
                            else:
                                payload_int = {
                                    "lead_id": lead_id,
                                    "corretor": corretor_int,
                                    "mensagem": nota_int,
                                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M")
                                }
                                try:
                                    supabase.table("interacoes_leads").insert(payload_int).execute()
                                    st.success("Interação registrada com sucesso!")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Erro ao salvar interação: {err}")

                    # Lista interações registradas
                    historico = carregar_interacoes(lead_id)
                    if historico:
                        st.divider()
                        st.write("**Histórico de Conversas:**")
                        for h in historico:
                            st.caption(f"🕒 **{h.get('data_hora', '')}** — **{h.get('corretor', 'Corretor')}**: {h.get('mensagem', '')}")
                    else:
                        st.caption("Nenhuma interação registrada para este cliente ainda.")

                col_edit, col_del = st.columns(2)
                with col_edit:
                    with st.expander("✏️ Editar Lead"):
                        with st.form(key=f"form_edit_lead_{lead_id}"):
                            e_nome = st.text_input("Nome", value=str(nome_lead))
                            e_zap = st.text_input("WhatsApp", value=str(zap_lead))
                            e_orc = st.number_input("Orçamento Máximo (R$)", value=float(orc_val), step=10000.0)
                            
                            idx_corr = CORRETORES.index(corr_val) if corr_val in CORRETORES else 0
                            e_corr = st.selectbox("Corretor Responsável", CORRETORES, index=idx_corr)
                            e_obs = st.text_area("Observações", value=str(obs_val))

                            if st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                                payload_e = {
                                    "nome": str(e_nome),
                                    "whatsapp": str(e_zap),
                                    "orcamento_maximo": float(e_orc),
                                    "orcamento_max": float(e_orc),
                                    "corretor_responsavel": str(e_corr),
                                    "corretor": str(e_corr),
                                    "observacoes": str(e_obs)
                                }
                                colunas_lead_existentes = list(lead.keys())
                                dados_e = {k: v for k, v in payload_e.items() if k in colunas_lead_existentes}
                                try:
                                    supabase.table("leads").update(dados_e).eq("id", lead_id).execute()
                                    st.success("Lead atualizado!")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Erro ao atualizar: {err}")

                with col_del:
                    with st.expander("🗑️ Excluir Lead"):
                        st.write(f"Tem certeza que deseja excluir **{nome_lead}**?")
                        if st.button("Confirmar Exclusão", key=f"btn_del_lead_{lead_id}", type="primary"):
                            try:
                                supabase.table("leads").delete().eq("id", lead_id).execute()
                                st.success("Lead excluído com sucesso!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erro ao excluir: {err}")

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🎯 ABA 6: ENCONTRAR MATCHES
# ==========================================
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Cruzamento de Dados (Matches)")
    st.write("Encontre os imóveis ideais para cada cliente com base em perfil e orçamento.")
    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado para realizar o cruzamento.")
    else:
        opcoes_leads = {f"{l.get('nome', 'Sem nome')} ({l.get('whatsapp', 'S/N')})": l for l in leads_data if l.get('status', 'Em busca') == 'Em busca'}
        
        if not opcoes_leads:
            st.warning("Não há leads com status 'Em busca' no momento.")
        else:
            lead_sel_nome = st.selectbox("Selecione o Lead para buscar imóveis compatíveis:", list(opcoes_leads.keys()))
            lead_sel = opcoes_leads[lead_sel_nome]

            bairros_lead_raw = lead_sel.get('bairros_interesse', [])
            if isinstance(bairros_lead_raw, str):
                bairros_lead = [b.strip() for b in bairros_lead_raw.split(",") if b.strip()]
            else:
                bairros_lead = bairros_lead_raw

            orc_lead = float(lead_sel.get('orcamento_maximo') or lead_sel.get('orcamento_max') or 0.0)

            st.markdown(f"**Perfil do Lead:** Orçamento de até **R$ {orc_lead:,.2f}** nos bairros: *{', '.join(bairros_lead) if bairros_lead else 'Todos'}*")
            st.divider()

            matches = []
            for im in imoveis_data:
                if im.get('status', 'Disponível') == 'Disponível':
                    preco_imovel = float(im.get('valor_venda', 0.0))
                    bairro_imovel = im.get('bairro', '')
                    
                    match_preco = preco_imovel <= orc_lead
                    match_bairro = (not bairros_lead) or (bairro_imovel in bairros_lead)

                    if match_preco and match_bairro:
                        matches.append(im)

            st.subheader(f"Imóveis Encontrados: {len(matches)}")
            
            if not matches:
                st.info("Nenhum imóvel disponível corresponde exatamente aos critérios deste lead.")
            else:
                for match in matches:
                    with st.container():
                        st.markdown('<div class="stCard">', unsafe_allow_html=True)
                        m_c1, m_c2 = st.columns([3, 1])
                        with m_c1:
                            st.markdown(f"### {match.get('tipo')} — Cód: {match.get('codigo_imovel')}")
                            st.write(f"📍 Bairro: **{match.get('bairro')}** | 💰 R$ {match.get('valor_venda', 0):,.2f}")
                            st.write(f"🛏️ {match.get('quartos', 0)} qtos | 🚿 {match.get('suites', 0)} suítes | 🚗 {match.get('vagas_garagem', 0)} vagas")
                        with m_c2:
                            msg_wa = f"Olá {lead_sel.get('nome')}! Encontrei este imóvel perfeito para você: {match.get('tipo')} no bairro {match.get('bairro')} por R$ {match.get('valor_venda', 0):,.2f}. Código: {match.get('codigo_imovel')}."
                            url_wa = f"https://wa.me/{str(lead_sel.get('whatsapp')).replace('+', '').replace(' ', '').replace('-', '')}?text={urllib.parse.quote(msg_wa)}"
                            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Enviar WhatsApp</button></a>', unsafe_allow_html=True)
                            
                            pdf_match = gerar_pdf_imovel(match)
                            st.download_button(
                                label="📄 Baixar PDF de Vendas",
                                data=pdf_match,
                                file_name=f"imovel_{match.get('codigo_imovel', 'ficha')}.pdf",
                                mime="application/pdf",
                                key=f"btn_pdf_match_{match.get('id')}"
                            )
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
        leads_opts = [f"{l.get('nome')} ({l.get('whatsapp')})" for l in leads_data if l.get('status', 'Em busca') == 'Em busca']

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
