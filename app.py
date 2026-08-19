import streamlit as st
import urllib.parse
from supabase import create_client, Client

# ==========================================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Mendes & Soares — CRM Imobiliário",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔌 CONEXÃO SUPABASE
# ==========================================
# Substitua com suas credenciais ou carregue de st.secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://seu-projeto.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sua-chave-anon-key")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")

# ==========================================
# 📊 CARREGAMENTO DE DADOS
# ==========================================
def carregar_imoveis():
    try:
        res = supabase.table("imoveis").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Erro ao carregar imóveis: {e}")
        return []

def carregar_leads():
    try:
        res = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return []

imoveis_data = carregar_imoveis()
leads_data = carregar_leads()

# Mapeamento padrão de status do lead
MAPEAMENTO_STATUS = {
    "Novo Lead": "🔵 Novo Lead (Sem Contato)",
    "Em Atendimento": "🟡 Em Atendimento",
    "Visita Agendada": "🟡 Visita Agendada",
    "Proposta Enviada": "🟠 Proposta Enviada (Quente)",
    "Já comprou": "🟢 Já comprou (Fechado)",
    "Perdido/Inativo": "🔴 Perdido/Inativo"
}

# Base da URL do aplicativo para geração dos links
BASE_APP_URL = "https://crm-imobiliario-jfduwtza7vr6okamx3nfxf.streamlit.app"

# ==========================================
# 🌐 1. PÁGINA PÚBLICA DE VISUALIZAÇÃO DO IMÓVEL (VIA LINK)
# ==========================================
query_params = st.query_params
codigo_imovel_param = query_params.get("imovel")

if codigo_imovel_param:
    res_imovel = supabase.table("imoveis").select("*").eq("codigo_imovel", codigo_imovel_param).execute()
    
    if res_imovel.data:
        imovel_pub = res_imovel.data[0]
        
        st.markdown(f"# 🏠 {imovel_pub.get('tipo', 'Imóvel')} — Cód: {imovel_pub.get('codigo_imovel')}")
        st.caption(f"📍 Bairro: {imovel_pub.get('bairro', 'Não informado')} | Passos - MG")
        st.divider()

        # Galeria de fotos
        fotos = imovel_pub.get("fotos_urls", []) or imovel_pub.get("fotos", [])
        if isinstance(fotos, str):
            fotos = [f.strip() for f in fotos.split(",") if f.strip()]

        if fotos:
            st.subheader("🖼️ Galeria de Fotos")
            st.image(fotos[0], use_container_width=True)
            
            if len(fotos) > 1:
                cols_fotos = st.columns(min(len(fotos) - 1, 4))
                for idx, url_foto in enumerate(fotos[1:]):
                    with cols_fotos[idx % 4]:
                        st.image(url_foto, use_container_width=True)
        else:
            st.info("Nenhuma foto cadastrada para este imóvel.")

        st.divider()

        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("📌 Características do Imóvel")
            st.markdown(f"""
            * **Valor de Venda:** R$ {float(imovel_pub.get('valor_venda', 0)):,.2f}
            * **Dormitórios:** {imovel_pub.get('quartos', 0)} quarto(s)
            * **Suítes:** {imovel_pub.get('suites', 0)} suíte(s)
            * **Vagas de Garagem:** {imovel_pub.get('vagas_garagem', 0)} vaga(s)
            * **Bairro:** {imovel_pub.get('bairro')}
            """)

            if imovel_pub.get("descricao"):
                st.subheader("📝 Descrição")
                st.write(imovel_pub.get("descricao"))

        with c2:
            st.markdown("### 💬 Gostou deste imóvel?")
            st.write("Entre em contato com nossa equipe para agendar uma visita ou tirar dúvidas.")
            
            msg_interesse = f"Olá! Vi o imóvel {imovel_pub.get('tipo')} (Cód: {imovel_pub.get('codigo_imovel')}) no site e gostaria de mais informações."
            link_wa = f"https://wa.me/5535998102465?text={urllib.parse.quote(msg_interesse)}"
            
            st.markdown(
                f'<a href="{link_wa}" target="_blank" style="text-decoration:none;">'
                f'<button style="width:100%; padding:14px; background-color:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer;">'
                f'📱 Falar no WhatsApp</button></a>',
                unsafe_allow_html=True
            )

        st.stop()  # Interrompe o carregamento do painel administrativo
    else:
        st.error("Imóvel não encontrado ou indisponível.")
        st.stop()

# ==========================================
# 📌 MENU LATERAL - PAINEL INTERNO
# ==========================================
st.sidebar.title("Mendes & Soares")
st.sidebar.caption("Engenharia e Imóveis | CRM")

menu = st.sidebar.radio(
    "Navegação do Sistema:",
    [
        "📊 Dashboard",
        "🏠 Imóveis Cadastrados",
        "➕ Novo Imóvel",
        "👤 Novo Lead",
        "🗂️ Funil de Leads",
        "🎯 Encontrar Matches",
        "📅 Visitas Agendadas"
    ]
)

st.sidebar.divider()
st.sidebar.caption("📍 Passos - MG | 📱 (35) 9 9810-2465")

# ==========================================
# 📊 ABA 1: DASHBOARD
# ==========================================
if "Dashboard" in menu:
    st.title("📊 Painel de Controle (Dashboard)")
    st.write("Visão geral de imóveis e leads da imobiliária.")
    st.divider()

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("Total de Imóveis", len(imoveis_data))
    col_d2.metric("Imóveis Disponíveis", sum(1 for i in imoveis_data if i.get("status", "Disponível") == "Disponível"))
    col_d3.metric("Total de Leads", len(leads_data))
    col_d4.metric("Leads Ativos", sum(1 for l in leads_data if l.get("status") not in ["🟢 Já comprou (Fechado)", "🔴 Perdido/Inativo"]))

# ==========================================
# 🏠 ABA 2: IMÓVEIS CADASTRADOS
# ==========================================
elif "Imóveis Cadastrados" in menu:
    st.title("🏠 Imóveis Cadastrados")
    st.write("Consulte e gerencie o catálogo de imóveis.")
    st.divider()

    if not imoveis_data:
        st.info("Nenhum imóvel cadastrado no momento.")
    else:
        for imovel in imoveis_data:
            im_id = imovel.get("id")
            cod_imovel = imovel.get("codigo_imovel", "S/C")
            link_imovel = f"{BASE_APP_URL}/?imovel={cod_imovel}"

            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {imovel.get('tipo')} — Cód: {cod_imovel}")
                    st.write(f"📍 Bairro: **{imovel.get('bairro')}** | 💰 **R$ {float(imovel.get('valor_venda', 0)):,.2f}**")
                    st.write(f"🛏️ {imovel.get('quartos', 0)} qtos | 🚿 {imovel.get('suites', 0)} suítes | 🚗 {imovel.get('vagas_garagem', 0)} vagas")
                with c2:
                    st.text_input("🔗 Link de Visualização:", value=link_imovel, key=f"link_im_{im_id}")
                    st.markdown(f'<a href="{link_imovel}" target="_blank"><button style="width:100%; padding:8px; background-color:#1E88E5; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">👁️ Abrir Vitrine</button></a>', unsafe_allow_html=True)
                st.divider()

# ==========================================
# ➕ ABA 3: NOVO IMÓVEL
# ==========================================
elif "Novo Imóvel" in menu:
    st.title("➕ Cadastrar Novo Imóvel")
    st.write("Preencha as especificações para disponibilizar o imóvel.")
    st.divider()

    with st.form("form_novo_imovel", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            codigo_imovel = st.text_input("Código do Imóvel *", placeholder="Ex: MS-004")
            tipo = st.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Terreno", "Chácara"])
            bairro = st.text_input("Bairro *", placeholder="Ex: Vilagio D' Itália")
            valor_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=10000.0, format="%.2f")
        with col2:
            quartos = st.number_input("Quartos", min_value=0, step=1, value=2)
            suites = st.number_input("Suítes", min_value=0, step=1, value=1)
            vagas = st.number_input("Vagas de Garagem", min_value=0, step=1, value=1)
            fotos_input = st.text_area("URLs das Fotos (separadas por vírgula)", placeholder="https://link1.com/foto.jpg, https://link2.com/foto.jpg")

        descricao = st.text_area("Descrição Detalhada do Imóvel")
        submitted = st.form_submit_button("💾 Salvar Imóvel", use_container_width=True)

        if submitted:
            if not codigo_imovel or not bairro:
                st.error("Preencha os campos obrigatórios (Código e Bairro).")
            else:
                try:
                    urls_lista = [u.strip() for u in fotos_input.split(",") if u.strip()] if fotos_input else []
                    novo_imovel = {
                        "codigo_imovel": codigo_imovel,
                        "tipo": tipo,
                        "bairro": bairro,
                        "valor_venda": valor_venda,
                        "quartos": int(quartos),
                        "suites": int(suites),
                        "vagas_garagem": int(vagas),
                        "fotos_urls": urls_lista,
                        "descricao": descricao,
                        "status": "Disponível"
                    }
                    supabase.table("imoveis").insert(novo_imovel).execute()
                    st.success(f"Imóvel **{codigo_imovel}** cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar imóvel: {e}")

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
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar lead no Supabase: {e}")

# ==========================================
# 🗂️ ABA 5: FUNIL DE LEADS
# ==========================================
elif "Funil de Leads" in menu:
    st.title("🗂️ Funil de Vendas de Leads")
    st.write("Acompanhe o andamento das negociações.")
    st.divider()

    colunas_funil = [
        "🔵 Novo Lead (Sem Contato)",
        "🟡 Em Atendimento",
        "🟡 Visita Agendada",
        "🟠 Proposta Enviada (Quente)",
        "🟢 Já comprou (Fechado)",
        "🔴 Perdido/Inativo"
    ]

    cols = st.columns(len(colunas_funil))

    for idx, col_nome in enumerate(colunas_funil):
        with cols[idx]:
            st.markdown(f"#### {col_nome.split()[0]} {col_nome.split()[1]}")
            leads_col = [l for l in leads_data if l.get("status") == col_nome]
            
            for l in leads_col:
                with st.expander(f"👤 {l.get('nome')}"):
                    st.write(f"📱 {l.get('whatsapp')}")
                    if l.get("email"):
                        st.write(f"✉️ {l.get('email')}")
                    st.write(f"💰 Max: R$ {float(l.get('orcamento_maximo', 0)):,.2f}")
                    if l.get("financiamento") == "Sim":
                        st.caption(f"🏦 Financiamento: {l.get('financiamento_aprovado')}")

# ==========================================
# 🎯 ABA 6: ENCONTRAR MATCHES COM AÇÕES
# ==========================================
elif "Encontrar Matches" in menu:
    st.title("🎯 Cruzamento de Dados (Matches)")
    st.write("Encontre os imóveis ideais para cada cliente e gerencie as etapas do match.")
    st.divider()

    if not leads_data:
        st.info("Nenhum lead cadastrado para realizar o cruzamento.")
    else:
        opcoes_leads = {
            f"{l.get('nome', 'Sem nome')} ({l.get('whatsapp', 'S/N')})": l 
            for l in leads_data 
            if MAPEAMENTO_STATUS.get(l.get('status'), l.get('status')) not in ['🟢 Já comprou (Fechado)', '🔴 Perdido/Inativo']
        }
        
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
                bairros_lead = bairros_lead_raw or []

            orc_lead = float(lead_sel.get('orcamento_maximo') or lead_sel.get('orcamento_max') or 0.0)

            st.markdown(f"**Perfil do Lead:** Orçamento de até **R$ {orc_lead:,.2f}** nos bairros: *{', '.join(bairros_lead) if bairros_lead else 'Todos'}*")
            
            # --- CARREGAR HISTÓRICO DE MATCHES ---
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
                    cod_imovel = match.get('codigo_imovel')
                    link_imovel = f"{BASE_APP_URL}/?imovel={cod_imovel}"
                    
                    with st.container():
                        st.markdown('<div class="stCard">', unsafe_allow_html=True)
                        m_c1, m_c2 = st.columns([2.5, 1.5])
                        
                        with m_c1:
                            st.markdown(f"### {match.get('tipo')} — Cód: {cod_imovel}")
                            st.write(f"📍 Bairro: **{match.get('bairro')}** | 💰 R$ {float(match.get('valor_venda', 0)):,.2f}")
                            st.write(f"🛏️ {match.get('quartos', 0)} qtos | 🚿 {match.get('suites', 0)} suítes | 🚗 {match.get('vagas_garagem', 0)} vagas")
                            
                            if st_match != "Pendente":
                                st.caption(f"📌 **Status atual do Match:** `{st_match}`")

                        with m_c2:
                            msg_wa = f"Olá {lead_sel.get('nome')}! Encontrei este imóvel perfeito para você: {match.get('tipo')} no bairro {match.get('bairro')}. Veja fotos e detalhes no link: {link_imovel}"
                            url_wa = f"https://wa.me/{str(lead_sel.get('whatsapp')).replace('+', '').replace(' ', '').replace('-', '')}?text={urllib.parse.quote(msg_wa)}"
                            
                            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:8px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom: 6px;">📱 Enviar WhatsApp</button></a>', unsafe_allow_html=True)
                            
                            st.text_input("🔗 Link de Visualização:", value=link_imovel, key=f"link_{imovel_id}_{lead_id}")
                            
                            st.divider()
                            st.caption("Ações do Match:")
                            
                            col_a1, col_a2, col_a3 = st.columns(3)
                            
                            # 1. BOTÃO DESCARTAR
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

                            # 2. BOTÃO VISITA
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

                            # 3. BOTÃO PROPOSTA
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
elif "Visitas Agendadas" in menu:
    st.title("📅 Visitas Agendadas")
    st.write("Consulte as visitas marcadas a partir do cruzamento de matches.")
    st.divider()

    try:
        res_visitas = supabase.table("matches_status").select("*, leads(*), imoveis(*)").eq("status", "Visita Agendada").execute()
        visitas = res_visitas.data or []

        if not visitas:
            st.info("Nenhuma visita agendada no momento.")
        else:
            for vis in visitas:
                lead = vis.get("leads", {}) or {}
                imovel = vis.get("imoveis", {}) or {}

                with st.container():
                    st.markdown(f"### 👤 Lead: {lead.get('nome', 'Sem nome')} — 📱 {lead.get('whatsapp', 'S/N')}")
                    st.write(f"🏠 **Imóvel:** {imovel.get('tipo')} (Cód: {imovel.get('codigo_imovel')}) no bairro {imovel.get('bairro')}")
                    st.write(f"💰 Valor: R$ {float(imovel.get('valor_venda', 0)):,.2f}")
                    st.divider()
    except Exception as e:
        st.error(f"Erro ao buscar visitas agendadas: {e}")
