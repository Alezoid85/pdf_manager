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
    /* Riduce lo spazio tra i widget nelle colonne */
    [data-testid="column"] { gap: 0.5rem; }
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

def update_all():
    for key in st.session_state.keys():
        if key.startswith("t_"):
            st.session_state[key] = st.session_state.master_selector

# Funzione per gestire l'incollo multiplo (Excel)
def handle_paste(index, uploaded_files):
    key = f"tr_{index}"
    raw_data = st.session_state[key]
    
    # Se il dato contiene dei "a capo", allora è un incollo multiplo
    if "\n" in raw_data:
        lines = [line.strip() for line in raw_data.split("\n") if line.strip()]
        for i, line in enumerate(lines):
            target_idx = index + i
            if target_idx < len(uploaded_files):
                # Distribuiamo i dati nelle righe successive
                st.session_state[f"tr_{target_idx}"] = line

# --- 3. INTERFACCIA ---
st.title("📄 PDF Manager Turbo - Ale")

opzioni = ["-", "AWB", "CMR", "BDC", "POD", "MRN", "ESITO"]

# Pannello Master
st.markdown("### 🛠️ Configurazione Rapida")
with st.expander("IMPOSTA TIPO DOCUMENTO PER TUTTI", expanded=True):
    st.selectbox(
        "Seleziona il tipo e verrà applicato a tutte le righe:",
        opzioni,
        key="master_selector",
        on_change=update_all
    )

uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_to_zip = []
    st.markdown("---")
    
    # Intestazione Colonne
    h1, h2, h3, h4, h5, h6, h7 = st.columns([1.5, 0.4, 0.8, 1.2, 1.2, 1.2, 0.8])
    h1.write("**Nome File**")
    h2.write("**Vedi**")
    h3.write("**Tipo**")
    h4.write("**Tracking**")
    h5.write("**Spedizione**")
    h6.write("**Data**")
    h7.write("**Salva**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_tipo, col_track, col_sped, col_data, col_dl = st.columns([1.5, 0.4, 0.8, 1.2, 1.2, 1.2, 0.8])
        
        current_file_bytes = file.getvalue()
        row_key_tipo = f"t_{i}"
        
        if row_key_tipo not in st.session_state:
            st.session_state[row_key_tipo] = st.session_state.master_selector

        with col_nome:
            st.text(file.name[:25] + "..." if len(file.name) > 25 else file.name)
        
        with col_preview:
            with st.popover("👁️"):
                img = get_pdf_preview_image(current_file_bytes)
                if img: st.image(img)
                else: st.error("N/A")
        
        with col_tipo:
            tipo = st.selectbox("T", opzioni, key=row_key_tipo, label_visibility="collapsed")
            
        with col_track:
            # On_change gestisce l'incollo da Excel
            track = st.text_input("Trk", key=f"tr_{i}", label_visibility="collapsed", 
                                  placeholder="Tracking...", on_change=handle_paste, args=(i, uploaded_files))
            
        with col_sped:
            sped = st.text_input("Sped", key=f"sp_{i}", label_visibility="collapsed", placeholder="Spedizione...")
            
        with col_data:
            data_doc = st.text_input("Data", key=f"dt_{i}", label_visibility="collapsed", placeholder="Data Doc...")
            
        with col_dl:
            # Logica di rinomina: ISP_TipoTrack - Spedizione - Data - Documento
            # Se un campo è vuoto, mettiamo un segnaposto o lo saltiamo
            if tipo != "-":
                parts = [f"ISP_{tipo}{track}", sped, data_doc, tipo]
                # Filtriamo solo le parti che hanno testo per evitare troppi trattini vuoti
                nome_finale = " - ".join([p for p in parts if p.strip()]) + ".pdf"
                
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
            "Documenti_Ale_Turbo.zip",
            "application/zip",
            use_container_width=True
        )

if st.sidebar.button("🗑️ Reset Totale"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()