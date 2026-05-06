import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Manager Turbo", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, span { color: #002D62 !important; }
    div[data-testid="stExpander"] { border: 2px solid #002D62 !important; background-color: #f8f9fa !important; }
    .stColumn { padding: 0.1rem 0.1rem !important; }
    [data-testid="column"] { gap: 0.3rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONI TECNICHE ---
def get_pdf_preview_image(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8)) 
            img_data = pix.tobytes("jpg")
            doc.close()
            return img_data
    except: return None
    return None

def update_all_types():
    for key in st.session_state.keys():
        if key.startswith("t_"):
            st.session_state[key] = st.session_state.master_selector

# --- 3. INTERFACCIA ---
st.title("📄 PDF Manager Turbo - Ale")

opzioni = ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"]

# Pannello Master con Incollo Multiplo per tutte le colonne
st.markdown("### 🛠️ Configurazione Rapida e Incollo Excel")
with st.expander("INCOLLA QUI LE COLONNE DA EXCEL", expanded=True):
    # Riga per il menu a tendina universale
    st.selectbox("Imposta Tipo Documento (Menu) per tutti:", opzioni, key="master_selector", on_change=update_all_types)
    
    st.markdown("---")
    st.write("Copia una colonna da Excel e incollala nel box corrispondente:")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.text_area("Incolla Tracking", key="p_track", height=80, placeholder="Colonna Tracking...")
    with m2: st.text_area("Incolla Spedizione", key="p_sped", height=80, placeholder="Colonna Spedizione...")
    with m3: st.text_area("Incolla Data", key="p_data", height=80, placeholder="Colonna Data...")
    with m4: st.text_area("Incolla Documento", key="p_doc", height=80, placeholder="Colonna Documento...")

uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # --- LOGICA DI DISTRIBUZIONE DATI ---
    # Gestiamo l'incollo per ogni colonna
    pastes = {
        "tr_": st.session_state.p_track,
        "sp_": st.session_state.p_sped,
        "dt_": st.session_state.p_data,
        "dc_": st.session_state.p_doc
    }
    
    for prefix, raw_text in pastes.items():
        if raw_text:
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            for idx, line in enumerate(lines):
                if idx < len(uploaded_files):
                    st.session_state[f"{prefix}{idx}"] = line

    files_to_zip = []
    st.markdown("---")
    
    # Intestazione Colonne
    h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.2, 0.4, 0.8, 1.2, 1.2, 1.2, 1.2, 0.6])
    h1.write("**Originale**")
    h2.write("**Vedi**")
    h3.write("**Menu**")
    h4.write("**Tracking**")
    h5.write("**Spedizione**")
    h6.write("**Data**")
    h7.write("**Documento**")
    h8.write("**Salva**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        c_nome, c_prev, c_menu, c_track, c_sped, c_data, c_doc, c_dl = st.columns([1.2, 0.4, 0.8, 1.2, 1.2, 1.2, 1.2, 0.6])
        
        current_file_bytes = file.getvalue()
        
        # Inizializzazione stato Menu
        row_key_menu = f"t_{i}"
        if row_key_menu not in st.session_state:
            st.session_state[row_key_menu] = st.session_state.master_selector

        with c_nome:
            st.text(file.name[:18] + ".." if len(file.name) > 18 else file.name)
        
        with c_prev:
            with st.popover("👁️"):
                img = get_pdf_preview_image(current_file_bytes)
                if img: st.image(img)
                else: st.error("N/A")
        
        with c_menu:
            tipo_menu = st.selectbox("M", opzioni, key=row_key_menu, label_visibility="collapsed")
            
        with c_track:
            track = st.text_input("Trk", key=f"tr_{i}", label_visibility="collapsed")
            
        with c_sped:
            sped = st.text_input("Sped", key=f"sp_{i}", label_visibility="collapsed")
            
        with c_data:
            data_val = st.text_input("Data", key=f"dt_{i}", label_visibility="collapsed")
            
        with c_doc:
            doc_val = st.text_input("Doc", key=f"dc_{i}", label_visibility="collapsed")
            
        with c_dl:
            # Formato richiesto: ISP_AWBTracking - Spedizione - Data - Documento
            prefix_file = f"ISP_{tipo_menu}" if tipo_menu != "-" else "ISP"
            nome_finale = f"{prefix_file}{track} - {sped} - {data_val} - {doc_val}.pdf"
            
            files_to_zip.append({"name": nome_finale, "bytes": current_file_bytes})
            st.download_button("💾", current_file_bytes, file_name=nome_finale, key=f"d_{i}", use_container_width=True)
        
    # Sidebar ZIP
    if files_to_zip:
        st.sidebar.header("📦 Scarico Massivo")
        st.sidebar.info(f"File pronti: {len(files_to_zip)}")
        
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files_to_zip:
                z.writestr(f["name"], f["bytes"])
        
        st.sidebar.download_button(
            "🚀 SCARICA TUTTI (.ZIP)",
            buf.getvalue(),
            "Documenti_Rinominati.zip",
            "application/zip",
            use_container_width=True
        )

if st.sidebar.button("🗑️ Reset Totale"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
