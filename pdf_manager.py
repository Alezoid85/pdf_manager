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
    
    /* Popover Anteprima più grande e centrato */
    div[data-testid="stPopoverContent"] {
        width: 600px !important;
        background-color: white !important;
        border: 2px solid #002D62 !important;
    }
    
    /* Compattazione righe per meno scroll */
    .stColumn { padding: 0.2rem 0rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
    
    /* Sidebar per lo scarico */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        border-right: 2px solid #002D62;
    }
    </style>
    """, unsafe_allow_html=True)

def get_pdf_preview_image(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2)) 
            img_data = pix.tobytes("jpg")
            doc.close()
            return img_data
    except: return None
    return None

# --- 2. INTERFACCIA ---
st.title("📄 PDF Manager Turbo - Ale")

# --- CONTROLLI MASSIVI (Per zittire gli scettici) ---
with st.expander("🛠️ Impostazioni Veloci (Applica a tutti)", expanded=True):
    c1, c2 = st.columns([1, 2])
    with c1:
        master_tipo = st.selectbox("Seleziona tipo per TUTTI i file:", ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"])
    with c2:
        st.write("👉 *Seleziona un tipo qui sopra per non doverlo cliccare su ogni riga.*")

uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_to_zip = []
    
    st.markdown("---")
    h1, h2, h3, h4 = st.columns([2, 0.6, 2.2, 1.2])
    h1.markdown("**File Originale**")
    h2.markdown("**Vedi**")
    h3.markdown("**Dati Rinomina**")
    h4.markdown("**Azione**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 0.6, 2.2, 1.2])
        current_file_bytes = file.getvalue()
        
        with col_nome:
            st.text(file.name[:35] + "..." if len(file.name) > 35 else file.name)
        
        with col_preview:
            with st.popover("👁️"):
                preview_img = get_pdf_preview_image(current_file_bytes)
                if preview_img:
                    st.image(preview_img, use_column_width=True)
                else:
                    st.error("Errore preview")
        
        with col_input:
            c_tipo, c_val = st.columns([0.4, 0.6])
            with c_tipo:
                # Se il master_tipo è selezionato, lo usiamo come default
                index_default = ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"].index(master_tipo) if master_tipo != "-" else 0
                tipo = st.selectbox("T", ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"], index=index_default, key=f"t_{i}", label_visibility="collapsed")
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Incolla codice...")
            
        with col_dl:
            if valore and tipo != "-":
                nome_finale = f"ISP_{tipo}{valore}.pdf"
                files_to_zip.append({"name": nome_finale, "bytes": current_file_bytes})
                st.download_button("💾", current_file_bytes, file_name=nome_finale, key=f"d_{i}", use_container_width=True)
        
    # --- SIDEBAR DOWNLOAD ---
    if files_to_zip:
        st.sidebar.header("📦 Scarico Massivo")
        st.sidebar.success(f"Pronti: {len(files_to_zip)} / {len(uploaded_files)}")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f in files_to_zip:
                zip_file.writestr(f["name"], f["bytes"])
        
        st.sidebar.download_button(
            label="🚀 SCARICA TUTTO (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Archivio_Rinominati.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.info("Trascina i file per iniziare.")

# Tasto per pulire la sessione
if st.sidebar.button("🗑️ Pulisci tutto"):
    st.rerun()