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
    .stColumn { padding: 0.1rem 0rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONI TECNICHE ---
def get_pdf_preview_image(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1)) 
            img_data = pix.tobytes("jpg")
            doc.close()
            return img_data
    except: return None
    return None

# Funzione per forzare l'aggiornamento di tutte le righe
def update_all():
    for key in st.session_state.keys():
        if key.startswith("t_"): # Cerca tutte le chiavi dei selectbox delle righe
            st.session_state[key] = st.session_state.master_selector

# --- 3. INTERFACCIA ---
st.title("📄 PDF Manager Turbo - Ale")

opzioni = ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"]

# Pannello Master
st.markdown("### 🛠️ Configurazione Rapida")
with st.expander("IMPOSTA TIPO DOCUMENTO PER TUTTI", expanded=True):
    # Il segreto è l'on_change: appena tocchi questo, parte la funzione update_all
    st.selectbox(
        "Seleziona il tipo e verrà applicato istantaneamente a tutte le righe:",
        opzioni,
        key="master_selector",
        on_change=update_all
    )

uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_to_zip = []
    st.markdown("---")
    
    # Intestazione
    h1, h2, h3, h4 = st.columns([2, 0.6, 2.2, 1.2])
    h1.write("**Nome Originale**")
    h2.write("**Vedi**")
    h3.write("**Dati Rinomina**")
    h4.write("**Salva**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 0.6, 2.2, 1.2])
        current_file_bytes = file.getvalue()
        
        # Chiave per il selectbox di questa riga
        row_key = f"t_{i}"
        
        # Se la riga non ha ancora un valore, gli diamo quello del master
        if row_key not in st.session_state:
            st.session_state[row_key] = st.session_state.master_selector

        with col_nome:
            st.text(file.name[:30] + "..." if len(file.name) > 30 else file.name)
        
        with col_preview:
            with st.popover("👁️"):
                img = get_pdf_preview_image(current_file_bytes)
                if img: st.image(img)
                else: st.error("No preview")
        
        with col_input:
            c_tipo, c_val = st.columns([0.4, 0.6])
            with c_tipo:
                # Il selectbox ora è collegato direttamente alla session_state
                tipo = st.selectbox(
                    "T", opzioni, 
                    key=row_key, 
                    label_visibility="collapsed"
                )
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Codice...")
            
        with col_dl:
            if valore and tipo != "-":
                nome_finale = f"ISP_{tipo}{valore}.pdf"
                files_to_zip.append({"name": nome_finale, "bytes": current_file_bytes})
                st.download_button("💾", current_file_bytes, file_name=nome_finale, key=f"d_{i}", use_container_width=True)
        
    # Sidebar ZIP
    if files_to_zip:
        st.sidebar.header("📦 Scarico Massivo")
        st.sidebar.success(f"File pronti: {len(files_to_zip)}")
        
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files_to_zip:
                z.writestr(f["name"], f["bytes"])
        
        st.sidebar.download_button(
            "🚀 SCARICA TUTTI (.ZIP)",
            buf.getvalue(),
            "Documenti_Ale.zip",
            "application/zip",
            use_container_width=True
        )

if st.sidebar.button("🗑️ Reset Totale"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()