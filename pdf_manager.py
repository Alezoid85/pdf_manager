import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Manager Pro", layout="wide")

# Stile ISP: Bianco e Blu con popover controllato
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, span { color: #002D62 !important; }
    
    /* Forza il quadratino dell'anteprima (Popover) */
    div[data-testid="stPopoverContent"] {
        width: 500px !important;
        background-color: white !important;
        border: 2px solid #002D62 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Layout tabella compatto */
    .stColumn { padding: 0.5rem 0rem !important; }
    
    /* Input field stile pulito */
    .stTextInput input {
        border-color: #002D62 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE ANTEPRIMA (ANTI-BLOCCO CHROME) ---
def get_pdf_preview_image(file_bytes):
    """Trasforma la prima pagina del PDF in immagine per bypassare i blocchi di sicurezza di Chrome"""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc.load_page(0)
            # Zoom 1.5 per rendere i testi leggibili nell'anteprima
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
            img_data = pix.tobytes("jpg")
            doc.close()
            return img_data
    except Exception as e:
        return None
    return None

# --- 3. INTERFACCIA UTENTE ---
st.title("📄 PDF Manager - Ale Edition")
st.write("Rinomina i tuoi file in modo rapido. Anteprima immagine attiva per evitare blocchi browser.")

# Caricamento file
uploaded_files = st.file_uploader("Trascina qui i tuoi PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.markdown("---")
    # Intestazioni Tabella
    h1, h2, h3, h4 = st.columns([2, 0.8, 2, 1.2])
    h1.markdown("**File Originale**")
    h2.markdown("**Vedi**")
    h3.markdown("**Dati per Rinomina**")
    h4.markdown("**Azione**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 0.8, 2, 1.2])
        
        # Bytes del file per preview e download
        current_file_bytes = file.getvalue()
        
        with col_nome:
            st.text(file.name)
        
        with col_preview:
            # Popover per l'anteprima rapida
            with st.popover("👁️"):
                preview_img = get_pdf_preview_image(current_file_bytes)
                if preview_img:
                    st.image(preview_img, caption="Prima pagina del documento", use_column_width=True)
                else:
                    st.error("Anteprima non disponibile")
        
        with col_input:
            c_tipo, c_val = st.columns([0.4, 0.6])
            with c_tipo:
                tipo = st.selectbox("Tipo", ["AWB", "CMR", "BDC", "POD", "MRN", "ESITO"], key=f"t_{i}", label_visibility="collapsed")
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Codice...")
            
        with col_dl:
            if valore:
                # CORREZIONE: Underscore rimosso tra {tipo} e {valore}
                nome_finale = f"ISP_{tipo}{valore}.pdf"
                st.download_button(
                    label="💾 Salva", 
                    data=current_file_bytes, 
                    file_name=nome_finale, 
                    key=f"d_{i}",
                    use_container_width=True
                )
            else:
                st.write("")
        
        st.divider()
else:
    st.info("In attesa di file PDF da elaborare...")