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

# --- LISTA ATUALIZADA DE BAIRROS DE PASSOS - MG (ORDEM ALFABÉTICA) ---
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
            q_min = lead.get('quartos_minimos', 1)
            for im in imoveis_disponiveis:
                bairro_ok = (not bairros) or (im.get('bairro') in bairros)
                if im.get('valor_venda', 0) <= orc and bairro_ok and im.get('quartos', 0) >= q_min:
                    total_matches += 1
        st.metric(label="🔥 Matches Ativos", value=total_matches)

# ==========================================
# 📋 ABA 2: IMÓVEIS CADASTRADOS & EDIÇÃO
# ==========================================
elif menu == "📋 Imóveis Cadastrados":
    st.title("📋 Inventário de Imóveis")
    st.write("Consulte, gerencie e edite os imóveis cadastrados em Passos-MG.")
    
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
                    
                    st.write(f"📍 **Bairro:** {imovel.get('bairro')}")
                    
                    detalhes = f"🛏️ {imovel.get('quartos', 0)} Quartos | 🚿 {imovel.get('suites', 0)} Suítes | 🚗 {imovel.get('vagas_garagem', 0)} Vagas"
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
                    
                    c_status, c_edit = st.columns([2, 1])
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

                # --- SANFONA PARA EDITAR O IMÓVEL ---
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
                        e_c4, e_c5, e_c6 = st.columns(3)
                        with e_c4:
                            e_quartos = st.number_input("Quartos", min_value=0, value=int(imovel.get('quartos', 0)), step=1, key=f"e_q_{imovel_id}")
                            e_suites = st.number_input("Suítes", min_value=0, value=int(imovel.get('suites', 0)), step=1, key=f"e_s_{imovel_id}")
                        with e_c5:
                            e_vagas = st.number_input("Vagas de Garagem", min_value=0, value=int(imovel.get('vagas_garagem', 0)), step=1, key=f"e_v_{imovel_id}")
                        with e_c6:
                            st.write("**Ambientes:**")
                            e_sala = st.checkbox("Sala", value=bool(imovel.get('sala', True)), key=f"e_sala_{imovel_id}")
                            e_copa = st.checkbox("Copa", value=bool(imovel.get('copa', False)), key=f"e_copa_{imovel_id}")
                            e_cozinha = st.checkbox("Cozinha", value=bool(imovel.get('cozinha', True)), key=f"e_cozinha_{imovel_id}")

                        e_cd1, e_cd2 = st.columns(2)
                        with e_cd1:
                            e_garagem_coberta = st.checkbox("🚘 Garagem Coberta", value=bool(imovel.get('garagem_coberta', False)), key=f"e_gc_{imovel_id}")
                        with e_cd2:
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
        c4, c5, c6 = st.columns(3)
        with c4:
            quartos = st.number_input("Quantidade de Quartos", min_value=0, value=3, step=1)
            suites = st.number_input("Quantidade de Suítes", min_value=0, value=1, step=1)
        with c5:
            vagas = st.number_input("Vagas de Garagem", min_value=0, value=2, step=1)
        with c6:
            st.write("**Ambientes Presentes:**")
            sala = st.checkbox("Sala de Estar/Jantar", value=True)
            copa = st.checkbox("Copa", value=False)
            cozinha = st.checkbox("Cozinha", value=True)

        st.divider()
        st.subheader("✨ Diferenciais do Imóvel")
        cd1, cd2 = st.columns(2)
        with cd1:
            garagem_coberta = st.checkbox("🚘 Garagem Coberta")
        with cd2:
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
# 👤 ABA 4: NOVO LEAD
# ==========================================
elif menu == "👤 Novo Lead":
    st.title("👤 Cadastrar Novo Lead")
    st.write("Você pode selecionar múltiplos bairros de interesse para este cliente.")
    st.divider()

    with st.form("form_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Cliente *")
            whatsapp = st.text_input("WhatsApp com DDD *", "+5535999999999")
            quartos_min = st.slider("Mínimo de Quartos Desejados", 1, 6, 2)
        with col2:
            bairros_interesse = st.multiselect("Bairros de Interesse (Passos-MG) *", BAIRROS_PASSOS, default=["Centro"])
            orcamento = st.number_input("Orçamento Máximo (R$) *", min_value=0.0, value=500000.0, step=10000.0)
        
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
                    "quartos_minimos": quartos_min,
                    "status": "Em busca"
                }
                supabase.table("leads").insert(dados_lead).execute()
                st.success(f"✅ Lead **{nome}** cadastrado com sucesso para {len(bairros_interesse)} bairro(s)!")

# ==========================================
# 👥 ABA 5: GERENCIAR & EDITAR LEADS
# ==========================================
elif menu == "👥 Gerenciar Leads":
    st.title("👥 Gerenciamento de Leads")
    st.write("Consulte e altere preferências, nome, telefone ou orçamento dos clientes.")
    
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
                    st.write(f"📍 **Bairros de Interesse:** {bairros_str}")
                    st.write(f"💰 **Orçamento Máximo:** R$ {lead.get('orcamento_maximo', 0):,.2f} | 🛏️ **Min. Quartos:** {lead.get('quartos_minimos', 1)}")
                
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

                # --- SANFONA PARA EDITAR LEAD ---
                with st.expander(f"✏️ Editar dados do lead {lead.get('nome')}"):
                    with st.form(key=f"form_edit_lead_{lead_id}"):
                        el_c1, el_c2 = st.columns(2)
                        with el_c1:
                            e_nome = st.text_input("Nome Completo", value=lead.get('nome', ''), key=f"e_nome_{lead_id}")
                            e_whatsapp = st.text_input("WhatsApp", value=lead.get('whatsapp', ''), key=f"e_wa_{lead_id}")
                            e_quartos_min = st.slider("Mínimo de Quartos", 1, 6, value=int(lead.get('quartos_minimos', 2)), key=f"e_qmin_{lead_id}")
                        with el_c2:
                            bairros_atuais = lead.get('bairros_interesse', [])
                            bairros_validos = [b for b in bairros_atuais if b in BAIRROS_PASSOS]
                            e_bairros = st.multiselect("Bairros de Interesse", BAIRROS_PASSOS, default=bairros_validos, key=f"e_bairros_{lead_id}")
                            e_orcamento = st.number_input("Orçamento Máximo (R$)", min_value=0.0, value=float(lead.get('orcamento_maximo', 0.0)), step=10000.0, key=f"e_orc_{lead_id}")
                        
                        btn_salvar_lead = st.form_submit_button("💾 Salvar Alterações no Lead", use_container_width=True)
                        if btn_salvar_lead:
                            dados_lead_atualizados = {
                                "nome": e_nome,
                                "whatsapp": e_whatsapp,
                                "bairros_interesse": e_bairros,
                                "orcamento_maximo": e_orcamento,
                                "quartos_minimos": e_quartos_min
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
    st.write("Cruza os bairros de interesse do cliente com os imóveis disponíveis.")
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
            quartos_min = lead.get('quartos_minimos', 1)
            
            bairros_texto = ", ".join(bairros) if bairros else "Qualquer Bairro"
            st.caption(f"💰 Orçamento Máx: **R$ {orcamento:,.2f}** | 📍 Bairros: **{bairros_texto}** | 🛏️ Mín. Quartos: **{quartos_min}**")
            
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
                        st.write(f"🏠 **{m.get('tipo')} [{m.get('codigo_imovel')}]** — R$ {m.get('valor_venda'):,.2f} ({m.get('quartos')} qtos no **{m.get('bairro')}**)")
                    with c2:
                        foto_link = m.get('fotos_urls')[0] if m.get('fotos_urls') else 'Sem foto'
                        texto_msg = f"Olá {lead.get('nome')}! Encontrei o imóvel ideal para você no bairro {m.get('bairro')}: {m.get('tipo')} por R$ {m.get('valor_venda'):,.2f}. Confira fotos aqui: {foto_link}"
                        link_wa = f"https://wa.me/{whatsapp_num}?text={urllib.parse.quote(texto_msg)}"
                        st.markdown(f"[📲 **Enviar WhatsApp**]({link_wa})")
            else:
                st.warning("Nenhum imóvel disponível compatível nos bairros selecionados.")
            st.divider()
