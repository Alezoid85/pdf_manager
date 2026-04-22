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
    
    /* Pannello Master (Impostazioni Rapide) */
    div[data-testid="stExpander"] {
        border: 2px solid #002D62 !important;
        background-color: #f0f2f6 !important;
        border-radius: 10px;
    }
    
    /* Popover Anteprima più grande */
    div[data-testid="stPopoverContent"] {
        width: 600px !important;
        background-color: white !important;
        border: 2px solid #002D62 !important;
    }
    
    /* Compattazione righe */
    .stColumn { padding: 0.2rem 0rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
    
    /* Sidebar */
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

# --- BLOCCO MASTER (La modifica che mancava) ---
st.markdown("### 🛠️ Impostazioni Rapide")
with st.expander("CLICCA QUI PER IMPOSTARE IL TIPO A TUTTI I FILE", expanded=True):
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        # Questo comando controlla tutti i selectbox sotto
        master_tipo = st.selectbox(
            "Scegli tipo (es. CMR) per applicarlo a tutto l'elenco:", 
            ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"],
            index=0
        )
    with col_m2:
        st.info("💡 Seleziona il tipo una volta sola qui sopra per risparmiare decine di clic.")

uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_to_zip = []
    
    st.markdown("---")
    # Intestazioni Tabella compatta
    h1, h2, h3, h4 = st.columns([2, 0.6, 2.2, 1.2])
    h1.markdown("**File Originale**")
    h2.markdown("**Vedi**")
    h3.markdown("**Dati Rinomina**")
    h4.markdown("**Azione**")
    st.markdown("---")

    # Lista dei tipi per gestire l'index del selectbox
    lista_tipi = ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"]

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 0.6, 2.2, 1.2])
        current_file_bytes = file.getvalue()
        
        with col_nome:
            # Tronca nomi troppo lunghi
            nome_corto = file.name[:30] + "..." if len(file.name) > 30 else file.name
            st.text(nome_corto)
        
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
                # SE IL MASTER È SELEZIONATO, USA QUELLO, ALTRIMENTI USA "-"
                index_da_usare = lista_tipi.index(master_tipo) if master_tipo != "-" else 0
                
                tipo = st.selectbox(
                    "T", 
                    lista_tipi, 
                    index=index_da_usare, 
                    key=f"t_{i}", 
                    label_visibility="collapsed"
                )
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Codice...")
            
        with col_dl:
            if valore and tipo != "-":
                # NOME ATTACCATO ISP_TIPOVALORE.pdf
                nome_finale = f"ISP_{tipo}{valore}.pdf"
                files_to_zip.append({"name": nome_finale, "bytes": current_file_bytes})
                st.download_button("💾", current_file_bytes, file_name=nome_finale, key=f"d_{i}", use_container_width=True)
        
    # --- SIDEBAR DOWNLOAD MASSIVO ---
    if files_to_zip:
        st.sidebar.header("📦 Scarico Massivo")
        st.sidebar.success(f"File pronti: {len(files_to_zip)} / {len(uploaded_files)}")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f in files_to_zip:
                zip_file.writestr(f["name"], f["bytes"])
        
        st.sidebar.download_button(
            label="🚀 SCARICA TUTTO (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Archivio_Documenti.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.info("Trascina i file PDF per iniziare.")

# Tasto per resettare tutto
if st.sidebar.button("🗑️ Pulisci tutto"):
    st.rerun()