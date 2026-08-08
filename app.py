import streamlit as st
from supabase import create_client
import urllib.parse

SUPABASE_URL = "https://dsnamhmffvjxcfqtlzet.supabase.co"
SUPABASE_KEY = "sb_publishable_XVO9PLxpxWBnr32_UYt_UA_HSdspi16"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Painel do Corretor", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Integrado - CRM & Match Imobiliário")

aba1, aba2, aba3, aba4 = st.tabs(["📝 Novo Imóvel", "📋 Ver Imóveis", "👤 Novo Lead", "🎯 Encontrar Matches"])

# --- ABA 1: CADASTRAR IMÓVEL ---
with aba1:
    st.subheader("Cadastrar Imóvel")
    codigo = st.text_input("Código do Imóvel", "CA-002")
    tipo = st.selectbox("Tipo", ["Casa", "Apartamento", "Terreno"])
    bairro = st.text_input("Bairro", "Centro")
    valor = st.number_input("Valor de Venda (R$)", min_value=0.0, value=350000.0, step=10000.0)
    quartos = st.slider("Quantidade de Quartos", 1, 6, 3)
    descricao = st.text_area("Descrição do Imóvel")
    
    fotos = st.file_uploader("Selecione as Fotos do Imóvel", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    if st.button("Salvar Imóvel"):
        urls_fotos = []
        if fotos:
            for foto in fotos:
                caminho_storage = f"imoveis/{codigo}_{foto.name}"
                res = supabase.storage.from_("fotos-imoveis").upload(caminho_storage, foto.getvalue(), {"content-type": foto.type})
                url_publica = supabase.storage.from_("fotos-imoveis").get_public_url(caminho_storage)
                urls_fotos.append(url_publica)
        
        dados_imovel = {
            "codigo_imovel": codigo,
            "tipo": tipo,
            "bairro": bairro,
            "valor_venda": valor,
            "quartos": quartos,
            "descricao": descricao,
            "fotos_urls": urls_fotos
        }
        supabase.table("imoveis").insert(dados_imovel).execute()
        st.success(f"✅ Imóvel {codigo} cadastrado com sucesso!")

# --- ABA 2: VISUALIZAR IMÓVEIS ---
with aba2:
    st.subheader("Imóveis Cadastrados")
    if st.button("🔄 Atualizar Lista de Imóveis"):
        imoveis = supabase.table("imoveis").select("*").execute().data
        if imoveis:
            for imovel in imoveis:
                col1, col2 = st.columns([1, 2])
                with col1:
                    fotos_urls = imovel.get("fotos_urls")
                    if fotos_urls and len(fotos_urls) > 0:
                        st.image(fotos_urls[0], use_container_width=True)
                    else:
                        st.info("Sem foto cadastrada")
                with col2:
                    st.markdown(f"### {imovel.get('tipo')} - Código: **{imovel.get('codigo_imovel')}**")
                    st.write(f"📍 **Bairro:** {imovel.get('bairro')}")
                    st.write(f"💰 **Valor:** R$ {imovel.get('valor_venda', 0):,.2f}")
                    st.write(f"🛏️ **Quartos:** {imovel.get('quartos')}")
                    st.write(f"📝 **Descrição:** {imovel.get('descricao', 'Sem descrição')}")
                st.divider()
        else:
            st.info("Nenhum imóvel cadastrado ainda.")

# --- ABA 3: CADASTRAR LEAD ---
with aba3:
    st.subheader("Cadastrar Lead / Cliente")
    nome = st.text_input("Nome do Cliente")
    whatsapp = st.text_input("WhatsApp (com DDD)", "+5511999999999")
    bairro_interesse = st.text_input("Bairro de Interesse", "Centro")
    orcamento = st.number_input("Orçamento Máximo (R$)", min_value=0.0, value=500000.0, step=10000.0)
    quartos_min = st.slider("Quartos Mínimos Desejados", 1, 6, 2)
    
    if st.button("Salvar Lead"):
        dados_lead = {
            "nome": nome,
            "whatsapp": whatsapp,
            "bairros_interesse": [bairro_interesse],
            "orcamento_maximo": orcamento,
            "quartos_minimos": quartos_min
        }
        supabase.table("leads").insert(dados_lead).execute()
        st.success(f"✅ Lead {nome} cadastrado com sucesso!")

# --- ABA 4: MATCH INTELIGENTE ---
with aba4:
    st.subheader("Cruzar Leads e Imóveis (Match Inteligente)")
    if st.button("🔄 Rodar Match"):
        leads = supabase.table("leads").select("*").execute().data
        imoveis = supabase.table("imoveis").select("*").execute().data
        
        for lead in leads:
            st.markdown(f"### 👤 Lead: **{lead.get('nome', 'Sem nome')}**")
            whatsapp_num = lead.get('whatsapp', '').replace("+", "").replace(" ", "").replace("-", "")
            orcamento = lead.get('orcamento_maximo', 0)
            bairros = lead.get('bairros_interesse', [])
            quartos_min = lead.get('quartos_minimos', 1)
            
            st.caption(f"Orçamento: R$ {orcamento:,.2f} | Quartos Mín.: {quartos_min} | Bairro: {', '.join(bairros)}")
            
            matches = []
            for imovel in imoveis:
                preco_ok = imovel.get('valor_venda', 0) <= orcamento
                bairro_ok = (not bairros) or (imovel.get('bairro') in bairros)
                quartos_ok = imovel.get('quartos', 0) >= quartos_min
                
                if preco_ok and bairro_ok and quartos_ok:
                    matches.append(imovel)
            
            if matches:
                for m in matches:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"🏠 **{m.get('tipo')} [{m.get('codigo_imovel')}]** - R$ {m.get('valor_venda'):,.2f} ({m.get('quartos')} quartos no {m.get('bairro')})")
                    with col2:
                        foto_link = m.get('fotos_urls')[0] if m.get('fotos_urls') else 'Sem foto'
                        texto_msg = f"Olá {lead.get('nome')}! Encontrei um imóvel ideal para você: {m.get('tipo')} no {m.get('bairro')} por R$ {m.get('valor_venda'):,.2f}. Confira a foto: {foto_link}"
                        link_wa = f"https://wa.me/{whatsapp_num}?text={urllib.parse.quote(texto_msg)}"
                        st.markdown(f"[📲 Enviar via WhatsApp]({link_wa})")
            else:
                st.info("Nenhum imóvel compatível para este cliente no momento.")
            st.divider()
