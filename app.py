import streamlit as st
from supabase import create_client, Client
import datetime

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Mendes & Soares | CRM Imobiliário",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Personalizada (CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d3b13b {
        background-color: #111827;
    }
    .stCard {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM SUPABASE
# ==========================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")
    st.stop()

# ==========================================
# 3. CONSTANTES E CONFIGURAÇÕES DO SISTEMA
# ==========================================
BAIRROS_PASSOS = [
    "Centro", "Nossa Senhora das Graças", "São José", "Jardim América", 
    "Avenue", "Penha", "Calixtopolis", "Nova Passos", "Muambas", 
    "Jardim Europa", "Jardim Panorama", "Jardim Cirano", "Coimbras", 
    "Belo Horizonte", "Eucaliptos", "Rancho Alegre", "Outro"
]

CORRETORES = ["Erick Mendes", "Soares", "Outro"]

# ==========================================
# 4. FUNÇÕES DE CARREGAMENTO DE DADOS
# ==========================================
def carregar_imoveis():
    try:
        res = supabase.table("imoveis").select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao buscar imóveis: {e}")
        return []

def carregar_leads():
    try:
        res = supabase.table("leads").select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao buscar leads: {e}")
        return []

imoveis_data = carregar_imoveis()
leads_data = carregar_leads()

# ==========================================
# 5. BARRA LATERAL (SIDEBAR & NAVEGAÇÃO)
# ==========================================
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/main/docs/static/logo.png", width=150) # Substitua se tiver URL do seu logo
    st.title("Mendes & Soares")
    st.subheader("Engenharia e Imóveis")
    st.divider()

    menu = st.radio(
        "Navegação do Sistema:",
        [
            "📊 Dashboard",
            "📋 Imóveis Cadastrados",
            "📝 Novo Imóvel",
            "👤 Novo Lead",
            "👥 Gerenciar Leads",
            "🎯 Encontrar Matches"
        ]
    )

    st.divider()
    st.caption("Passos - MG")
    st.caption("📞 (35) 9 9810-2465")

# ==========================================
# 6. LÓGICA DAS ABAS
# ==========================================

# ------------------------------------------
# 📊 ABA 1: DASHBOARD
# ------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 Painel Geral de Desempenho")
    st.write("Visão geral dos imóveis e clientes cadastrados no sistema.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Imóveis", len(imoveis_data))
    with col2:
        st.metric("Total de Leads", len(leads_data))
    with col3:
        leads_ativos = len([l for l in leads_data if l.get('status', 'Em busca') == 'Em busca'])
        st.metric("Leads Em Busca", leads_ativos)
    with col4:
        valor_total = sum([float(i.get('valor_venda', 0) or 0) for i in imoveis_data])
        st.metric("V. Total da Carteira", f"R$ {valor_total:,.2f}")

    st.divider()
    st.subheader("Últimos Imóveis Cadastrados")
    if imoveis_data:
        st.dataframe(
            [{"Código": i.get("codigo_imovel"), "Tipo": i.get("tipo"), "Bairro": i.get("bairro"), "Valor": f"R$ {float(i.get('valor_venda', 0)):,.2f}"} for i in imoveis_data[:5]],
            use_container_width=True
        )
    else:
        st.info("Nenhum imóvel cadastrado no momento.")

# ------------------------------------------
# 📋 ABA 2: IMÓVEIS CADASTRADOS
# ------------------------------------------
elif menu == "📋 Imóveis Cadastrados":
    st.title("📋 Imóveis Cadastrados")
    st.write("Gerencie os imóveis disponíveis na sua carteira.")

    with st.expander("🔍 **Filtros e Busca**", expanded=True):
        fc1, fc2, fc3 = st.columns([2, 1.5, 1.5])
        with fc1: busca = st.text_input("🔎 Pesquisar por Código, Proprietário ou Descrição")
        with fc2: filtro_tipo = st.selectbox("Tipo de Imóvel", ["Todos", "Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"])
        with fc3: filtro_bairro = st.selectbox("Bairro", ["Todos"] + BAIRROS_PASSOS)

    st.divider()

    imoveis_filtrados = imoveis_data
    if busca:
        termo = busca.lower().strip()
        imoveis_filtrados = [
            i for i in imoveis_filtrados 
            if termo in str(i.get('codigo_imovel', '')).lower() 
            or termo in str(i.get('nome_proprietario', '')).lower() 
            or termo in str(i.get('descricao', '')).lower()
        ]
    if filtro_tipo != "Todos":
        imoveis_filtrados = [i for i in imoveis_filtrados if i.get('tipo') == filtro_tipo]
    if filtro_bairro != "Todos":
        imoveis_filtrados = [i for i in imoveis_filtrados if i.get('bairro') == filtro_bairro]

    st.caption(f"Exibindo **{len(imoveis_filtrados)}** de **{len(imoveis_data)}** imóveis.")

    if not imoveis_filtrados:
        st.info("Nenhum imóvel encontrado com os filtros selecionados.")
    else:
        for imovel in imoveis_filtrados:
            imovel_id = imovel.get('id')
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(f"🏠 {imovel.get('tipo', 'Imóvel')} - {imovel.get('bairro', 'Bairro não informado')} (Cód: {imovel.get('codigo_imovel', 'S/N')})")
                    st.write(f"💰 **Valor:** R$ {float(imovel.get('valor_venda', 0)):,.2f}")
                    st.write(f"📍 **Endereço:** {imovel.get('endereco', 'Não informado')}")
                    st.write(f"👤 **Proprietário:** {imovel.get('nome_proprietario', 'Não informado')} | 📞 {imovel.get('telefone_proprietario', 'Não informado')}")
                    st.write(f"🛏️ {imovel.get('quartos', 0)} quartos ({imovel.get('suites', 0)} suítes) | 🚿 {imovel.get('banheiros', 0)} banheiros | 🚘 {imovel.get('vagas_garagem', 0)} vagas")
                    if imovel.get('descricao'):
                        st.text_area("Descrição", value=imovel.get('descricao'), disabled=True, key=f"view_desc_{imovel_id}")
                
                with c2:
                    with st.expander("🗑️ Excluir"):
                        if st.button("Confirmar Exclusão", key=f"del_imovel_{imovel_id}", type="primary"):
                            try:
                                supabase.table("imoveis").delete().eq("id", imovel_id).execute()
                                st.success("Imóvel excluído!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")

                # --- EDITAR IMÓVEL ---
                with st.expander(f"✏️ Editar imóvel {imovel.get('codigo_imovel')}"):
                    with st.form(key=f"form_edit_imovel_{imovel_id}"):
                        e_c1, e_c2, e_c3 = st.columns(3)
                        tipos_list = ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"]
                        idx_tipo = tipos_list.index(imovel.get('tipo')) if imovel.get('tipo') in tipos_list else 0
                        idx_bairro = BAIRROS_PASSOS.index(imovel.get('bairro')) if imovel.get('bairro') in BAIRROS_PASSOS else 0

                        with e_c1:
                            e_tipo = st.selectbox("Tipo de Imóvel", tipos_list, index=idx_tipo, key=f"e_tipo_{imovel_id}")
                            e_nome_prop = st.text_input("Nome do Proprietário", value=imovel.get('nome_proprietario', ''), key=f"e_np_{imovel_id}")
                        with e_c2:
                            e_bairro = st.selectbox("Bairro (Passos-MG)", BAIRROS_PASSOS, index=idx_bairro, key=f"e_bairro_{imovel_id}")
                            e_tel_prop = st.text_input("Telefone do Proprietário", value=imovel.get('telefone_proprietario', ''), key=f"e_tp_{imovel_id}")
                            e_valor = st.number_input("Valor de Venda (R$)", min_value=0.0, value=float(imovel.get('valor_venda', 0.0)), step=10000.0, key=f"e_valor_{imovel_id}")
                        with e_c3:
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
                            dados_atualizados = {
                                "tipo": e_tipo,
                                "bairro": e_bairro,
                                "valor_venda": float(e_valor),
                                "nome_proprietario": e_nome_prop,
                                "telefone_proprietario": e_tel_prop,
                                "endereco": e_endereco,
                                "quartos": int(e_quartos),
                                "suites": int(e_suites),
                                "banheiros": int(e_banheiros),
                                "vagas_garagem": int(e_vagas),
                                "garagem_coberta": e_garagem_coberta,
                                "area_gourmet": e_area_gourmet,
                                "sala": e_sala,
                                "copa": e_copa,
                                "cozinha": e_cozinha,
                                "area_terreno": float(e_area_terreno),
                                "area_construida": float(e_area_construida),
                                "descricao": e_descricao
                            }
                            
                            # Filtra enviando apenas colunas que realmente existem no seu BD
                            colunas_existentes = list(imovel.keys())
                            dados_filtrados = {k: v for k, v in dados_atualizados.items() if k in colunas_existentes}

                            try:
                                supabase.table("imoveis").update(dados_filtrados).eq("id", imovel_id).execute()
                                st.success("✅ Imóvel atualizado com sucesso!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erro ao salvar: {err}")

                st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# 📝 ABA 3: NOVO IMÓVEL
# ------------------------------------------
elif menu == "📝 Novo Imóvel":
    st.title("📝 Cadastrar Novo Imóvel")
    st.write("Preencha as informações para adicionar um imóvel ao sistema.")

    with st.form("form_novo_imovel", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            codigo = st.text_input("Código do Imóvel", value=f"IMO-{len(imoveis_data)+1:03d}")
            tipo = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Sobrado", "Cobertura", "Sítio/Chácara"])
            nome_proprietario = st.text_input("Nome do Proprietário")
        with c2:
            bairro = st.selectbox("Bairro (Passos-MG)", BAIRROS_PASSOS)
            telefone_proprietario = st.text_input("Telefone do Proprietário")
            valor_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=10000.0)
        with c3:
            endereco = st.text_input("Endereço / Rua")
            area_terreno = st.number_input("Tamanho do Lote (m²)", min_value=0.0, step=10.0)
            area_construida = st.number_input("Área Construída (m²)", min_value=0.0, step=10.0)

        st.divider()
        cq1, cq2, cq3, cq4 = st.columns(4)
        with cq1: quartos = st.number_input("Dormitórios", min_value=0, step=1)
        with cq2: suites = st.number_input("Suítes", min_value=0, step=1)
        with cq3: banheiros = st.number_input("Banheiros", min_value=0, step=1)
        with cq4: vagas = st.number_input("Vagas Garagem", min_value=0, step=1)

        st.divider()
        descricao = st.text_area("Descrição Completa do Imóvel")

        btn_cadastrar_imovel = st.form_submit_button("➕ Cadastrar Imóvel", use_container_width=True, type="primary")

        if btn_cadastrar_imovel:
            novo_imovel_data = {
                "codigo_imovel": codigo,
                "tipo": tipo,
                "bairro": bairro,
                "valor_venda": float(valor_venda),
                "nome_proprietario": nome_proprietario,
                "telefone_proprietario": telefone_proprietario,
                "endereco": endereco,
                "quartos": int(quartos),
                "suites": int(suites),
                "banheiros": int(banheiros),
                "vagas_garagem": int(vagas),
                "area_terreno": float(area_terreno),
                "area_construida": float(area_construida),
                "descricao": descricao
            }
            try:
                supabase.table("imoveis").insert(novo_imovel_data).execute()
                st.success("✅ Imóvel cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar imóvel no Supabase: {e}")

# ------------------------------------------
# 👤 ABA 4: NOVO LEAD
# ------------------------------------------
elif menu == "👤 Novo Lead":
    st.title("👤 Cadastrar Novo Lead / Cliente")
    st.write("Registre o perfil de busca do cliente para encontrar imóveis no sistema.")

    with st.form("form_novo_lead", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_lead = st.text_input("Nome do Cliente *")
            whatsapp_lead = st.text_input("WhatsApp com DDD *")
            corretor = st.selectbox("Corretor Responsável", CORRETORES)
        with col2:
            bairros_pref = st.multiselect("Bairros de Interesse em Passos", BAIRROS_PASSOS)
            orcamento = st.number_input("Orçamento Máximo (R$)", min_value=0.0, step=10000.0)

        btn_salvar_lead = st.form_submit_button("➕ Cadastrar Lead", use_container_width=True, type="primary")

        if btn_salvar_lead:
            if not nome_lead or not whatsapp_lead:
                st.error("Por favor, preencha os campos obrigatórios (Nome e WhatsApp).")
            else:
                payload_lead = {
                    "nome": nome_lead,
                    "whatsapp": whatsapp_lead,
                    "corretor_responsavel": corretor,
                    "bairros_interesse": bairros_pref,
                    "orcamento_maximo": float(orcamento),
                    "status": "Em busca"
                }
                try:
                    supabase.table("leads").insert(payload_lead).execute()
                    st.success("✅ Lead cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    # Tenta fallback sem a coluna 'corretor_responsavel' caso ela não exista no BD
                    payload_reduzido = {
                        "nome": nome_lead,
                        "whatsapp": whatsapp_lead,
                        "bairros_interesse": bairros_pref,
                        "orcamento_maximo": float(orcamento),
                        "status": "Em busca"
                    }
                    try:
                        supabase.table("leads").insert(payload_reduzido).execute()
                        st.success("✅ Lead cadastrado com sucesso!")
                        st.rerun()
                    except Exception as err_final:
                        st.error(f"Erro ao salvar lead no Supabase: {err_final}")

# ------------------------------------------
# 👥 ABA 5: GERENCIAR LEADS
# ------------------------------------------
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
        leads_filtrados = [l for l in leads_filtrados if filtro_bairro_lead in (l.get('bairros_interesse') or [])]

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
                    bairros_raw = lead.get('bairros_interesse')
                    if isinstance(bairros_raw, list):
                        bairros_str = ", ".join(bairros_raw)
                    else:
                        bairros_str = str(bairros_raw) if bairros_raw else "Nenhum"
                        
                    st.write(f"📍 **Bairros de Interesse:** {bairros_str}")
                    st.write(f"💰 **Orçamento Máximo:** R$ {float(lead.get('orcamento_maximo', 0)):,.2f} | 🔑 **Corretor:** {lead.get('corretor_responsavel', 'Não informado')}")
                
                with col2:
                    novo_status_lead = st.radio("Status do Lead:", ["Em busca", "Já comprou"], index=0 if status_lead == "Em busca" else 1, key=f"status_direct_{lead_id}")
                    if novo_status_lead != status_lead:
                        try:
                            supabase.table("leads").update({"status": novo_status_lead}).eq("id", lead_id).execute()
                            st.success("Status atualizado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar status: {e}")

                # --- EXCLUIR LEAD ---
                with st.expander(f"🗑️ Excluir Lead {lead.get('nome')}"):
                    st.warning("⚠️ Esta ação é permanente e removerá o lead do sistema.")
                    confirma_excluir_lead = st.checkbox("Confirmar exclusão deste lead", key=f"chk_del_lead_{lead_id}")
                    if st.button("🚨 Excluir Lead Definitivamente", key=f"btn_del_lead_{lead_id}", type="primary"):
                        if confirma_excluir_lead:
                            try:
                                supabase.table("leads").delete().eq("id", lead_id).execute()
                                st.success(f"Lead **{lead.get('nome')}** removido com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")

                # --- EDITAR LEAD ---
                with st.expander(f"✏️ Editar dados de {lead.get('nome')}"):
                    with st.form(key=f"form_edit_lead_{lead_id}"):
                        el_c1, el_c2 = st.columns(2)
                        idx_corr_lead = CORRETORES.index(lead.get('corretor_responsavel')) if lead.get('corretor_responsavel') in CORRETORES else 0
                        
                        with el_c1:
                            e_nome = st.text_input("Nome", value=lead.get('nome', ''), key=f"e_nome_{lead_id}")
                            e_whatsapp = st.text_input("WhatsApp", value=lead.get('whatsapp', ''), key=f"e_wa_{lead_id}")
                            e_corretor_l = st.selectbox("Corretor Responsável", CORRETORES, index=idx_corr_lead, key=f"e_corr_l_{lead_id}")
                        
                        with el_c2:
                            bairros_atuais = lead.get('bairros_interesse', [])
                            if isinstance(bairros_atuais, str):
                                bairros_atuais = [b.strip() for b in bairros_atuais.split(",")]
                            elif not isinstance(bairros_atuais, list):
                                bairros_atuais = []
                                
                            bairros_validos = [b for b in bairros_atuais if b in BAIRROS_PASSOS]
                            e_bairros = st.multiselect("Bairros", BAIRROS_PASSOS, default=bairros_validos, key=f"e_bairros_{lead_id}")
                            e_orcamento = st.number_input("Orçamento (R$)", min_value=0.0, value=float(lead.get('orcamento_maximo', 0.0)), step=10000.0, key=f"e_orc_{lead_id}")
                        
                        btn_salvar_lead = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
                        if btn_salvar_lead:
                            dados_lead_atualizados = {
                                "nome": e_nome,
                                "whatsapp": e_whatsapp,
                                "corretor_responsavel": e_corretor_l,
                                "bairros_interesse": e_bairros,
                                "orcamento_maximo": float(e_orcamento)
                            }
                            
                            # Filtra enviando apenas colunas que realmente existem no seu BD
                            colunas_existentes_lead = list(lead.keys())
                            dados_lead_filtrados = {k: v for k, v in dados_lead_atualizados.items() if k in colunas_existentes_lead}

                            try:
                                supabase.table("leads").update(dados_lead_filtrados).eq("id", lead_id).execute()
                                st.success("✅ Lead atualizado com sucesso!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erro ao salvar lead no Supabase: {err}")

                st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# 🎯 ABA 6: ENCONTRAR MATCHES
# ------------------------------------------
elif menu == "🎯 Encontrar Matches":
    st.title("🎯 Cruzamento de Dados (Imóveis x Leads)")
    st.write("Encontre os melhores imóveis para cada lead com base no perfil de busca.")

    if not leads_data or not imoveis_data:
        st.info("É necessário ter imóveis e leads cadastrados para realizar cruzamentos.")
    else:
        lead_selecionado_nome = st.selectbox("Selecione um Lead:", [f"{l.get('nome')} ({l.get('whatsapp')})" for l in leads_data if l.get('status', 'Em busca') == 'Em busca'])
        
        if lead_selecionado_nome:
            nome_limpo = lead_selecionado_nome.split(" (")[0]
            lead_obj = next((l for l in leads_data if l.get('nome') == nome_limpo), None)
            
            if lead_obj:
                st.subheader(f"Perfil de Busca: {lead_obj.get('nome')}")
                st.write(f"💰 **Orçamento Máximo:** R$ {float(lead_obj.get('orcamento_maximo', 0)):,.2f}")
                bairros = lead_obj.get('bairros_interesse', [])
                st.write(f"📍 **Bairros Desejados:** {', '.join(bairros) if isinstance(bairros, list) else bairros}")
                
                st.divider()
                st.write("### 🏠 Imóveis Compatíveis:")
                
                matches = []
                for im in imoveis_data:
                    valor_imovel = float(im.get('valor_venda', 0) or 0)
                    bairro_imovel = im.get('bairro')
                    orc_max = float(lead_obj.get('orcamento_maximo', 0) or 0)
                    
                    bairros_desejados = lead_obj.get('bairros_interesse', [])
                    if isinstance(bairros_desejados, str):
                        bairros_desejados = [b.strip() for b in bairros_desejados.split(",")]

                    # Regra de compatibilidade
                    match_bairro = (bairro_imovel in bairros_desejados) if bairros_desejados else True
                    match_valor = (valor_imovel <= orc_max) if orc_max > 0 else True
                    
                    if match_bairro and match_valor:
                        matches.append(im)

                if not matches:
                    st.warning("Nenhum imóvel compatível encontrado para esse perfil no momento.")
                else:
                    st.success(f"Encontrados **{len(matches)}** imóveis compatíveis!")
                    for m in matches:
                        with st.container():
                            st.markdown('<div class="stCard">', unsafe_allow_html=True)
                            mc1, mc2 = st.columns([3, 1])
                            with mc1:
                                st.subheader(f"🏠 {m.get('tipo')} - {m.get('bairro')} (Cód: {m.get('codigo_imovel')})")
                                st.write(f"💰 **Valor:** R$ {float(m.get('valor_venda', 0)):,.2f}")
                                st.write(f"📍 **Endereço:** {m.get('endereco')}")
                                st.write(f"🛏️ {m.get('quartos')} quartos | 🚿 {m.get('banheiros')} banheiros")
                            with mc2:
                                txt_msg = f"Olá {lead_obj.get('nome')}, encontrei um imóvel perfeito para seu perfil! Código: {m.get('codigo_imovel')}, Valor: R$ {float(m.get('valor_venda', 0)):,.2f}."
                                url_wa = f"https://wa.me/55{lead_obj.get('whatsapp')}?text={txt_msg.replace(' ', '%20')}"
                                st.link_button("📲 Enviar no WhatsApp", url_wa)
                            st.markdown('</div>', unsafe_allow_html=True)
