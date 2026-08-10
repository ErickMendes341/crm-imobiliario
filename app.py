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

# --- LISTA DE BAIRROS DE PASSOS - MG (ORDEM ALFABÉTICA) ---
BAIRROS_PASSOS = [
    "Aclimação", "Alto dos Maias", "Alvorada", "Antenas", "Aroeiras",
    "Bela Vista 1 e 2", "Belo Horizonte", "Califórnia", "Canadá 1, 2 e 3",
    "Canjeranus", "Carmelo", "Centro", "Cohab 4", "Cohab 5", "Coimbras",
    "Condomínio da Nações", "Condomínio Monte Belo", "Eldorado", "Exposição",
    "Flamboyant", "Jacarandá", "Jardim América", "Jardim Cidade",
    "Jardim Colégio de Passos", "Jardim Europa", "Jardim Florença",
    "Jardim dos Lagos", "Mirante do Vale", "Muarama", "Nossa Senhora das Graças",
    "Nova California", "Nova Passos 1, 2, 3 e 4", "Novo Horizonte", "Nsa de Fátima",
    "Panorama", "Parque das Oliveiras", "Penha", "Penha 2", "Planalto",
    "Polivalente", "Primavera", "Recanto do Bosque", "Santa Luzia", "São Benedito",
    "São Francisco", "Tropical", "Vale Verde 1 e 2", "Vilagio D´Italia", "Vila Rica"
]

OPCOES_PAGAMENTO = ["À vista", "Financiamento", "Consórcio", "Permuta / Troca", "Indefinido"]
OPCOES_URGENCIA = ["Imediata (até 30 dias)", "Médio Prazo (1 a 3 meses)", "Longo Prazo / Pesquisando"]
OPCOES_ORIGEM = ["Instagram / Facebook", "Portal Imobiliário", "Indicação", "Placa no Imóvel", "Passante / Loja", "Outro"]

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
    return f"IMO-{proximo_num:03d}"

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
    .feature-tag {
        background-color: #f1f5f9;
        color: #334155;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.85em;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
imoveis_data = carregar_imoveis()
leads_data = carregar_leads()

# --- MENU LATERAL ---
st.sidebar.image("https://img.icons8.com/color/96/real-estate.png", width=70)
st.sidebar.title("CRM Imobiliário")
st.sidebar.caption("Passos - MG | Gestão Inteligente")

menu = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📋 Imóveis Cadastrados", "📝 Novo Imóvel", "👤 Novo Lead", "👥 Gerenciar Leads", "🎯 Encontrar Matches"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("📍 **Foco na região de Passos - MG**")

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Painel Geral de Vendas")
    st.write("Métricas em tempo real sobre seu inventário e clientes em Passos-MG.")
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
        total_matches = 0
        for lead in leads_ativos:
            orc = lead.get('orcamento_maximo', 0)
            bairros = lead.get('bairros_interesse', [])
            min_q = lead.get('min_quartos', 0) or 0
            min_s = lead.get('min_suites', 0) or 0
            min_b = lead.get('min_banheiros', 0) or 0
            min_v = lead.get('min_vagas', 0) or 0
            
            for im in imoveis_disponiveis:
                bairro_ok = (not bairros) or (im.get('bairro') in bairros)
                preco_ok = im.get('valor_venda', 0) <= orc
                q_ok = (im.get('quartos', 0) or 0) >= min_q
                s_ok = (im.get('suites', 0) or 0) >= min_s
                b_ok = (im.get('banheiros', 0) or 0) >= min_b
                v_ok = (im.get('vagas_garagem', 0) or 0) >= min_v

                if preco_ok and bairro_ok and q_ok and s_ok and b_ok and v_ok:
                    total_matches += 1
        st.metric(label="🔥 Matches Ativos", value=total_matches)

# ==========================================
# 📋 ABA 2: IMÓVEIS CADASTRADOS
# ==========================================
elif menu == "📋 Imóveis Cadastrados":
    st.title("📋 Inventário de Imóveis")
    st.write("Consulte, gerencie, edite e remova imóveis cadastrados em Passos-MG.")
    
    if st.button("🔄 Atualizar Lista"):
        st.rerun()

    st.divider()

    if not imoveis_data:
        st.info("Nenhum imóvel cadastrado no momento.")
    else:
        for imovel in imoveis_data:
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
                        st.image("https://via.placeholder.com/400x300?text=Sem+Foto", use_container_width=True)
                
                with col2:
                    c_title, c_badge = st.columns([3, 1])
                    with c_title:
                        st.subheader(f"{imovel.get('tipo')} — Cod: **{imovel.get('codigo_imovel')}**")
                    with c_badge:
                        st.markdown(f'<span class="price-badge">R$ {imovel.get("valor_venda", 0):,.2f}</span>', unsafe_allow_html=True)
                    
                    st.write(f"📍 **Bairro:** {imovel.get('bairro')}")
                    
                    detalhes = f"🛏️ {imovel.get('quartos', 0)} Quarto(s) | 🚿 {imovel.get('suites', 0)} Suíte(s) | 🚽 {imovel.get('banheiros', 0)} Banheiro(s) | 🚗 {imovel.get('vagas_garagem', 0)} Vaga(s)"
                    if imovel.get('area_terreno'):
                        detalhes += f" | 📐 Terreno: {imovel.get('area_terreno')} m²"
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
                    
                    c_status, c_del = st.columns([2, 1])
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
                    st.warning("⚠️ Esta ação é permanente e removerá o imóvel da sua carteira.")
                    confirma_excluir = st.checkbox("Confirmar que desejo excluir este imóvel", key=f"chk_del_{imovel_id}")
                    if st.button("🚨 Confirmar Exclusão Definitiva", key=f"btn_del_{imovel_id}", type="primary"):
                        if confirma_excluir:
                            supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                            st.success(f"Imóvel **{imovel.get('codigo_imovel')}** removido com sucesso!")
                            st.rerun()

                # --- EDITAR IMÓVEL ---
                with st.expander(f"✏️ Editar dados do imóvel {imovel.get('codigo_imovel')}"):
                    with st.form(key=f"form_edit_imovel_{imovel_id}"):
                        e_c1, e_c2, e_c3 = st.columns(3)
                        
                        tipos_list = ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"]
                        idx_tipo = tipos_list.index(imovel.get('tipo')) if imovel.get('tipo') in tipos_list else 0
                        idx_bairro = BAIRROS_PASSOS.index(imovel.get('bairro')) if imovel.get('bairro') in BAIRROS_PASSOS else 0
                        
                        with e_c1:
                            e_tipo = st.selectbox("Tipo de Imóvel", tipos_list, index=idx_tipo, key=f"e_tipo_{imovel_id}")
                        with e_c2:
                            e_bairro = st.selectbox("Bairro (Passos-MG)", BAIRROS_PASSOS, index=idx_bairro, key=f"e_bairro_{imovel_id}")
                            e_valor = st.number_input("Valor de Venda (R$)", min_value=0.0, value=float(imovel.get('valor_venda', 0.0)), step=10000.0, key=f"e_valor_{imovel_id}")
                        with e_c3:
                            e_area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, value=float(imovel.get('area_terreno', 0.0) or 0.0), step=10.0, key=f"e_at_{imovel_id}")
                            e_area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=float(imovel.get('area_construida', 0.0) or 0.0), step=10.0, key=f"e_ac_{imovel_id}")

                        st.divider()
                        e_cq1, e_cq2, e_cq3, e_cq4 = st.columns(4)
                        with e_cq1:
                            e_quartos = st.number_input("Dormitórios / Quartos", min_value=0, value=int(imovel.get('quartos', 0) or 0), step=1, key=f"e_q_{imovel_id}")
                        with e_cq2:
                            e_suites = st.number_input("Suítes", min_value=0, value=int(imovel.get('suites', 0) or 0), step=1, key=f"e_s_{imovel_id}")
                        with e_cq3:
                            e_banheiros = st.number_input("Banheiros", min_value=0, value=int(imovel.get('banheiros', 0) or 0), step=1, key=f"e_b_{imovel_id}")
                        with e_cq4:
                            e_vagas = st.number_input("Vagas de Garagem", min_value=0, value=int(imovel.get('vagas_garagem', 0) or 0), step=1, key=f"e_v_{imovel_id}")

                        st.divider()
                        st.write("**Ambientes e Diferenciais:**")
                        e_c5, e_c6 = st.columns(2)
                        with e_c5:
                            e_sala = st.checkbox("Sala", value=bool(imovel.get('sala', True)), key=f"e_sala_{imovel_id}")
                            e_copa = st.checkbox("Copa", value=bool(imovel.get('copa', False)), key=f"e_copa_{imovel_id}")
                            e_cozinha = st.checkbox("Cozinha", value=bool(imovel.get('cozinha', True)), key=f"e_cozinha_{imovel_id}")
                        with e_c6:
                            e_garagem_coberta = st.checkbox("🚘 Garagem Coberta", value=bool(imovel.get('garagem_coberta', False)), key=f"e_gc_{imovel_id}")
                            e_area_gourmet = st.checkbox("🍖 Área Gourmet", value=bool(imovel.get('area_gourmet', False)), key=f"e_ag_{imovel_id}")

                        e_descricao = st.text_area("Descrição", value=imovel.get('descricao', ''), key=f"e_desc_{imovel_id}")
                        
                        btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações no Imóvel", use_container_width=True)
                        if btn_salvar_edicao:
                            dados_atualizados = {
                                "tipo": e_tipo,
                                "bairro": e_bairro,
                                "valor_venda": e_valor,
                                "quartos": e_quartos,
                                "suites": e_suites,
                                "banheiros": e_banheiros,
                                "vagas_garagem": e_vagas,
                                "garagem_coberta": e_garagem_coberta,
                                "area_gourmet": e_area_gourmet,
                                "sala": e_sala,
                                "copa": e_copa,
                                "cozinha": e_cozinha,
                                "area_terreno": e_area_terreno,
                                "area_construida": e_area_construida,
                                "descricao": e_descricao
                            }
                            supabase.table("imoveis").update(dados_atualizados).eq("id", imovel_id).execute()
                            st.success("✅ Imóvel atualizado com sucesso!")
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📝 ABA 3: NOVO IMÓVEL
# ==========================================
elif menu == "📝 Novo Imóvel":
    st.title("📝 Cadastrar Novo Imóvel")
    st.write("Selecione o bairro de Passos-MG e preencha a ficha do imóvel.")
    st.divider()

    codigo_gerado = gerar_codigo_imovel_auto()

    with st.form("form_imovel", clear_on_submit=True):
        st.subheader("📌 Informações Básicas")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("Código do Imóvel", value=codigo_gerado, disabled=True)
            tipo = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"])
        with c2:
            bairro = st.selectbox("Bairro (Passos-MG) *", BAIRROS_PASSOS)
            valor = st.number_input("Valor de Venda (R$) *", min_value=0.0, value=350000.0, step=10000.0)
        with c3:
            area_terreno = st.number_input("Tamanho do Lote / Terreno (m²)", min_value=0.0, value=250.0, step=10.0)
            area_construida = st.number_input("Área Construída (m²)", min_value=0.0, value=120.0, step=10.0)

        st.divider()
        st.subheader("🛏️ Cômodos e Vagas")
        c4, c5, c6, c7 = st.columns(4)
        with c4:
            quartos = st.number_input("Dormitórios / Quartos", min_value=0, value=3, step=1)
        with c5:
            suites = st.number_input("Suítes", min_value=0, value=1, step=1)
        with c6:
            banheiros = st.number_input("Banheiros (Total)", min_value=0, value=2, step=1)
        with c7:
            vagas = st.number_input("Vagas de Garagem", min_value=0, value=2, step=1)

        st.divider()
        st.subheader("✨ Ambientes e Diferenciais")
        cd1, cd2 = st.columns(2)
        with cd1:
            st.write("**Ambientes Presentes:**")
            sala = st.checkbox("Sala de Estar/Jantar", value=True)
            copa = st.checkbox("Copa", value=False)
            cozinha = st.checkbox("Cozinha", value=True)
        with cd2:
            st.write("**Diferenciais:**")
            garagem_coberta = st.checkbox("🚘 Garagem Coberta")
            area_gourmet = st.checkbox("🍖 Área Gourmet / Churrasqueira")

        st.divider()
        descricao = st.text_area("📝 Descrição Geral / Observações")
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
                "suites": suites,
                "banheiros": banheiros,
                "vagas_garagem": vagas,
                "garagem_coberta": garagem_coberta,
                "area_gourmet": area_gourmet,
                "sala": sala,
                "copa": copa,
                "cozinha": cozinha,
                "area_terreno": area_terreno,
                "area_construida": area_construida,
                "descricao": descricao,
                "fotos_urls": urls_fotos,
                "status": "Disponível"
            }
            supabase.table("imoveis").insert(dados_imovel).execute()
            st.success(f"✅ Imóvel **{codigo_gerado}** cadastrado com sucesso no bairro **{bairro}**!")

# ==========================================
# 👤 ABA 4: NOVO LEAD (COM NOVAS MÉTRICAS E REQUISITOS)
# ==========================================
elif menu == "👤 Novo Lead":
    st.title("👤 Cadastrar Novo Lead")
    st.write("Preencha os dados do cliente e defina suas preferências para qualificação e match automático.")
    st.divider()

    with st.form("form_lead", clear_on_submit=True):
        st.subheader("📌 Dados Pessoais & Contato")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Cliente *")
            whatsapp = st.text_input("WhatsApp com DDD *", "+5535999999999")
        with col2:
            origem = st.selectbox("Origem do Lead", OPCOES_ORIGEM)
            urgencia = st.selectbox("Urgência / Tempo de Compra", OPCOES_URGENCIA)

        st.divider()
        st.subheader("💰 Orçamento & Condições Financeiras")
        c_fin1, c_fin2 = st.columns(2)
        with c_fin1:
            orcamento = st.number_input("Orçamento Máximo (R$) *", min_value=0.0, value=500000.0, step=10000.0)
        with c_fin2:
            forma_pagamento = st.selectbox("Forma de Pagamento", OPCOES_PAGAMENTO)

        st.divider()
        st.subheader("🏠 Preferências & Requisitos Mínimos para Match")
        bairros_interesse = st.multiselect("Bairros de Interesse (Passos-MG) *", BAIRROS_PASSOS, default=["Centro"])
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            min_quartos = st.number_input("Mínimo de Quartos", min_value=0, value=0, step=1)
        with m2:
            min_suites = st.number_input("Mínimo de Suítes", min_value=0, value=0, step=1)
        with m3:
            min_banheiros = st.number_input("Mínimo de Banheiros", min_value=0, value=0, step=1)
        with m4:
            min_vagas = st.number_input("Mínimo de Vagas", min_value=0, value=0, step=1)

        submitted_lead = st.form_submit_button("💾 Salvar Lead", use_container_width=True)
        if submitted_lead:
            if not nome or not bairros_interesse:
                st.error("Por favor, preencha o Nome e selecione pelo menos um Bairro de interesse.")
            else:
                dados_lead = {
                    "nome": nome,
                    "whatsapp": whatsapp,
                    "bairros_interesse": bairros_interesse,
                    "orcamento_maximo": orcamento,
                    "forma_pagamento": forma_pagamento,
                    "urgencia": urgencia,
                    "origem": origem,
                    "min_quartos": min_quartos,
                    "min_suites": min_suites,
                    "min_banheiros": min_banheiros,
                    "min_vagas": min_vagas,
                    "status": "Em busca"
                }
                supabase.table("leads").insert(dados_lead).execute()
                st.success(f"✅ Lead **{nome}** cadastrado com sucesso para {len(bairros_interesse)} bairro(s)!")

# ==========================================
# 👥 ABA 5: GERENCIAR & EDITAR LEADS
# ==========================================
elif menu == "👥 Gerenciar Leads":
    st.title("👥 Gerenciamento de Leads")
    st.write("Consulte e altere preferências, qualificações ou orçamento dos clientes.")
    
    if st.button("🔄 Atualizar Lista de Leads"):
        st.rerun()

    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado até o momento.")
    else:
        for lead in leads_data:
            lead_id = lead.get('id')
            status_lead = lead.get('status', 'Em busca')
            
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"👤 {lead.get('nome')} — {lead.get('whatsapp')}")
                    bairros_str = ", ".join(lead.get('bairros_interesse', [])) if lead.get('bairros_interesse') else "Nenhum"
                    st.write(f"📍 **Bairros:** {bairros_str}")
                    st.write(f"💰 **Orçamento:** R$ {lead.get('orcamento_maximo', 0):,.2f} | **Pagamento:** {lead.get('forma_pagamento', 'N/I')}")
                    st.write(f"⏱️ **Urgência:** {lead.get('urgencia', 'N/I')} | 📢 **Origem:** {lead.get('origem', 'N/I')}")
                    
                    reqs = []
                    if lead.get('min_quartos'): reqs.append(f"🛏️ Mín. {lead.get('min_quartos')} quarto(s)")
                    if lead.get('min_suites'): reqs.append(f"🚿 Mín. {lead.get('min_suites')} suíte(s)")
                    if lead.get('min_banheiros'): reqs.append(f"🚽 Mín. {lead.get('min_banheiros')} banheiro(s)")
                    if lead.get('min_vagas'): reqs.append(f"🚗 Mín. {lead.get('min_vagas')} vaga(s)")
                    if reqs:
                        st.caption(f"Exigências: {' | '.join(reqs)}")
                
                with col2:
                    novo_status_lead = st.radio(
                        "Status do Lead:",
                        ["Em busca", "Já comprou"],
                        index=0 if status_lead == "Em busca" else 1,
                        key=f"status_direct_{lead_id}",
                        horizontal=False
                    )
                    if novo_status_lead != status_lead:
                        supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead_id).execute()
                        st.success("Status atualizado!")
                        st.rerun()

                # --- EDITAR LEAD ---
                with st.expander(f"✏️ Editar dados do lead {lead.get('nome')}"):
                    with st.form(key=f"form_edit_lead_{lead_id}"):
                        el_c1, el_c2 = st.columns(2)
                        with el_c1:
                            e_nome = st.text_input("Nome Completo", value=lead.get('nome', ''), key=f"e_nome_{lead_id}")
                            e_whatsapp = st.text_input("WhatsApp", value=lead.get('whatsapp', ''), key=f"e_wa_{lead_id}")
                            
                            pag_idx = OPCOES_PAGAMENTO.index(lead.get('forma_pagamento')) if lead.get('forma_pagamento') in OPCOES_PAGAMENTO else 0
                            e_forma_pagamento = st.selectbox("Forma de Pagamento", OPCOES_PAGAMENTO, index=pag_idx, key=f"e_fp_{lead_id}")
                            
                            urg_idx = OPCOES_URGENCIA.index(lead.get('urgencia')) if lead.get('urgencia') in OPCOES_URGENCIA else 0
                            e_urgencia = st.selectbox("Urgência / Tempo de Compra", OPCOES_URGENCIA, index=urg_idx, key=f"e_urg_{lead_id}")

                        with el_c2:
                            bairros_atuais = lead.get('bairros_interesse', [])
                            bairros_validos = [b for b in bairros_atuais if b in BAIRROS_PASSOS]
                            e_bairros = st.multiselect("Bairros de Interesse", BAIRROS_PASSOS, default=bairros_validos, key=f"e_bairros_{lead_id}")
                            e_orcamento = st.number_input("Orçamento Máximo (R$)", min_value=0.0, value=float(lead.get('orcamento_maximo', 0.0)), step=10000.0, key=f"e_orc_{lead_id}")
                            
                            ori_idx = OPCOES_ORIGEM.index(lead.get('origem')) if lead.get('origem') in OPCOES_ORIGEM else 0
                            e_origem = st.selectbox("Origem do Lead", OPCOES_ORIGEM, index=ori_idx, key=f"e_ori_{lead_id}")

                        st.divider()
                        st.write("**Requisitos Mínimos para Match:**")
                        em1, em2, em3, em4 = st.columns(4)
                        with em1:
                            e_min_q = st.number_input("Mín. Quartos", min_value=0, value=int(lead.get('min_quartos', 0) or 0), step=1, key=f"e_mq_{lead_id}")
                        with em2:
                            e_min_s = st.number_input("Mín. Suítes", min_value=0, value=int(lead.get('min_suites', 0) or 0), step=1, key=f"e_ms_{lead_id}")
                        with em3:
                            e_min_b = st.number_input("Mín. Banheiros", min_value=0, value=int(lead.get('min_banheiros', 0) or 0), step=1, key=f"e_mb_{lead_id}")
                        with em4:
                            e_min_v = st.number_input("Mín. Vagas", min_value=0, value=int(lead.get('min_vagas', 0) or 0), step=1, key=f"e_mv_{lead_id}")

                        btn_salvar_lead = st.form_submit_button("💾 Salvar Alterações no Lead", use_container_width=True)
                        if btn_salvar_lead:
                            dados_lead_atualizados = {
                                "nome": e_nome,
                                "whatsapp": e_whatsapp,
                                "bairros_interesse": e_bairros,
                                "orcamento_maximo": e_orcamento,
                                "forma_pagamento": e_forma_pagamento,
                                "urgencia": e_urgencia,
                                "origem": e_origem,
                                "min_quartos": e_min_q,
                                "min_suites": e_min_s,
                                "min_banheiros": e_min_b,
                                "min_vagas": e_min_v
                            }
                            supabase.table("leads").update(dados_lead_atualizados).eq("id", lead_id).execute()
                            st.success("✅ Dados do Lead atualizados com sucesso!")
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🎯 ABA 6: MATCH INTELIGENTE
# ==========================================
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Automação de Match Imobiliário")
    st.write("Cruza os bairros, orçamento e exigências mínimas do cliente com os imóveis disponíveis.")
    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado para realizar o cruzamento.")
    else:
        for lead in leads_data:
            status_lead = lead.get('status', 'Em busca')
            
            st.subheader(f"👤 Cliente: {lead.get('nome', 'Sem nome')}")
            
            novo_status_lead = st.radio(
                "Status do Cliente:",
                ["Em busca", "Já comprou"],
                index=0 if status_lead == "Em busca" else 1,
                key=f"status_lead_match_{lead.get('id')}",
                horizontal=True
            )
            
            if novo_status_lead != status_lead:
                supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead.get("id")).execute()
                st.success(f"Status do Lead atualizado para: **{novo_status_lead}**!")
                st.rerun()

            if novo_status_lead == "Já comprou":
                st.success("🎉 Cliente com compra concluída!")
                st.divider()
                continue

            whatsapp_num = lead.get('whatsapp', '').replace("+", "").replace(" ", "").replace("-", "")
            orcamento = lead.get('orcamento_maximo', 0)
            bairros = lead.get('bairros_interesse', [])
            min_q = lead.get('min_quartos', 0) or 0
            min_s = lead.get('min_suites', 0) or 0
            min_b = lead.get('min_banheiros', 0) or 0
            min_v = lead.get('min_vagas', 0) or 0
            
            bairros_texto = ", ".join(bairros) if bairros else "Qualquer Bairro"
            st.caption(
                f"💰 Orçamento Máx: **R$ {orcamento:,.2f}** | 📍 Bairros: **{bairros_texto}** | "
                f"🎯 Filtros Mínimos: {min_q}Q / {min_s}S / {min_b}B / {min_v}V"
            )
            
            imoveis_disponiveis = [i for i in imoveis_data if i.get('status', 'Disponível') == 'Disponível']
            
            matches = []
            for imovel in imoveis_disponiveis:
                preco_ok = imovel.get('valor_venda', 0) <= orcamento
                bairro_ok = (not bairros) or (imovel.get('bairro') in bairros)
                
                # Validação dos requisitos mínimos
                q_ok = (imovel.get('quartos', 0) or 0) >= min_q
                s_ok = (imovel.get('suites', 0) or 0) >= min_s
                b_ok = (imovel.get('banheiros', 0) or 0) >= min_b
                v_ok = (imovel.get('vagas_garagem', 0) or 0) >= min_v
                
                if preco_ok and bairro_ok and q_ok and s_ok and b_ok and v_ok:
                    matches.append(imovel)
            
            if matches:
                for m in matches:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"🏠 **{m.get('tipo')} [{m.get('codigo_imovel')}]** — R$ {m.get('valor_venda'):,.2f} no bairro **{m.get('bairro')}**")
                    with c2:
                        caracteristicas = []
                        if m.get('quartos'):
                            caracteristicas.append(f"🛏️ {m.get('quartos')} quarto(s)")
                        if m.get('suites'):
                            caracteristicas.append(f"🚿 {m.get('suites')} suíte(s)")
                        if m.get('banheiros'):
                            caracteristicas.append(f"🚽 {m.get('banheiros')} banheiro(s)")
                        if m.get('vagas_garagem'):
                            caracteristicas.append(f"🚗 {m.get('vagas_garagem')} vaga(s) de garagem")
                        if m.get('garagem_coberta'):
                            caracteristicas.append("🚘 Garagem coberta")
                        if m.get('area_gourmet'):
                            caracteristicas.append("🍖 Área gourmet / churrasqueira")
                        if m.get('sala'):
                            caracteristicas.append("🛋️ Sala")
                        if m.get('copa'):
                            caracteristicas.append("🍽️ Copa")
                        if m.get('cozinha'):
                            caracteristicas.append("🍳 Cozinha")
                        if m.get('area_construida'):
                            caracteristicas.append(f"🏗️ Área construída: {m.get('area_construida')}m²")
                        if m.get('area_terreno'):
                            caracteristicas.append(f"📐 Terreno: {m.get('area_terreno')}m²")

                        texto_caracteristicas = ""
                        if caracteristicas:
                            texto_caracteristicas = "\n\n*Destaques do Imóvel:*\n• " + "\n• ".join(caracteristicas)

                        texto_msg = (
                            f"Olá {lead.get('nome')}! Tudo bem?\n\n"
                            f"Encontrei uma opção de *{m.get('tipo')}* no bairro *{m.get('bairro')}* "
                            f"por *R$ {m.get('valor_venda'):,.2f}* que atende o seu perfil e exigências."
                            f"{texto_caracteristicas}\n\n"
                            f"Posso te enviar as fotos para você dar uma olhada?"
                        )
                        link_wa = f"https://wa.me/{whatsapp_num}?text={urllib.parse.quote(texto_msg)}"
                        st.markdown(f"[📲 **Enviar WhatsApp**]({link_wa})")
            else:
                st.warning("Nenhum imóvel disponível atende a todos os critérios/requisitos deste lead.")
            st.divider()
