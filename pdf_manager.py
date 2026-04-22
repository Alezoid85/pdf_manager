import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import zipfile

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Manager Pro", layout="wide")

# Personalizzazione estetica ISP
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, span { color: #002D62 !important; }
    
    /* Popover Anteprima */
    div[data-testid="stPopoverContent"] {
        width: 500px !important;
        background-color: white !important;
        border: 2px solid #002D62 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Sidebar Stile */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        border-right: 2px solid #002D62;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE ANTEPRIMA ---
def get_pdf_preview_image(file_bytes):
    """Genera un'immagine della prima pagina per bypassare i blocchi di Chrome"""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
            img_data = pix.tobytes("jpg")
            doc.close()
            return img_data
    except:
        return None
    return None

# --- 3. INTERFACCIA PRINCIPALE ---
st.title("📄 PDF Manager - Ale Edition")
st.write("Rinomina i file e scaricali singolarmente o tutti insieme in uno ZIP.")

# Caricamento file
uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Lista per raccogliere i file pronti per lo ZIP
    files_to_zip = []
    
    st.markdown("---")
    # Intestazioni Tabella
    h1, h2, h3, h4 = st.columns([2, 0.8, 2, 1.2])
    h1.markdown("**File Originale**")
    h2.markdown("**Vedi**")
    h3.markdown("**Nuovi Dati**")
    h4.markdown("**Azione**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 0.8, 2, 1.2])
        current_file_bytes = file.getvalue()
        
        with col_nome:
            st.text(file.name)
        
        with col_preview:
            with st.popover("👁️"):
                preview_img = get_pdf_preview_image(current_file_bytes)
                if preview_img:
                    st.image(preview_img, use_column_width=True, caption="Anteprima Pagina 1")
                else:
                    st.error("Impossibile caricare anteprima")
        
        with col_input:
            c_tipo, c_val = st.columns([0.4, 0.6])
            with c_tipo:
                tipo = st.selectbox("T", ["AWB", "CMR", "BDC", "POD", "MRN", "ESITO"], key=f"t_{i}", label_visibility="collapsed")
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Codice...")
            
        with col_dl:
            if valore:
                # Nome file senza underscore tra tipo e valore
                nome_finale = f"ISP_{tipo}{valore}.pdf"
                
                # Aggiunta alla lista per lo scarico massivo
                files_to_zip.append({"name": nome_finale, "bytes": current_file_bytes})
                
                st.download_button(
                    label="💾 Salva", 
                    data=current_file_bytes, 
                    file_name=nome_finale, 
                    key=f"d_{i}",
                    use_container_width=True
                )
        st.divider()

    # --- SIDEBAR PER SCARICO MASSIVO ---
    if files_to_zip:
        st.sidebar.header("📦 Download Massivo")
        st.sidebar.info(f"File pronti per lo ZIP: {len(files_to_zip)} / {len(uploaded_files)}")
        
        # Creazione dello ZIP in memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f in files_to_zip:
                zip_file.writestr(f["name"], f["bytes"])
        
        st.sidebar.download_button(
            label="🚀 SCARICA TUTTI (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Documenti_Rinominati_Ale.zip",
            mime="application/zip",
            use_container_width=True
        )
    else:
        st.sidebar.warning("Inserisci i codici per attivare lo scarico massivo.")

else:
    st.info("Trascina i file PDF per iniziare il lavoro.")
    st.sidebar.write("Carica dei file per vedere le opzioni di scarico.")