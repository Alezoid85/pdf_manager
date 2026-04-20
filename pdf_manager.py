import streamlit as st
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Manager", layout="wide")

# CSS per forzare il tema bianco/blu e gestire la dimensione del popover
st.markdown("""
    <style>
    /* Sfondo bianco e testi blu scuro */
    .stApp { background-color: white; }
    h1, h2, h3, p, label, span { color: #002D62 !important; }
    
    /* Forza il popover (l'anteprima) a non allargarsi troppo */
    div[data-testid="stPopoverContent"] {
        width: 500px !important;
        background-color: #f0f2f6 !important;
        border: 2px solid #002D62 !important;
    }

    /* Stile per i divisori */
    hr { border: 0.5px solid #002D62 !important; opacity: 0.2; }
    </style>
    """, unsafe_allow_html=True)

def show_pdf_preview(file_bytes):
    """Genera l'anteprima PDF dentro il popover"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'''
        <iframe
            src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0"
            width="100%"
            height="550px"
            style="border:none;"
        ></iframe>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- TITOLO ---
st.title("📄 PDF Manager Professionale - Ale")
st.write("Carica i file e usa il tasto '👁️' per controllare il contenuto senza ingombrare la pagina.")

# --- CARICAMENTO FILE ---
uploaded_files = st.file_uploader("Trascina qui i PDF aziendali", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.markdown("---")
    # Intestazioni tabella
    h1, h2, h3, h4 = st.columns([2, 1, 2, 1.5])
    h1.markdown("**File Originale**")
    h2.markdown("**Vedi**")
    h3.markdown("**Nuovo Nome (Tipo + Codice)**")
    h4.markdown("**Azione**")
    st.markdown("---")

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 1, 2, 1.5])
        
        # 1. Nome del file originale
        col_nome.text(file.name)
        
        # 2. Popover per l'anteprima (il "quadratino" che si apre)
        with col_preview:
            with st.popover("👁️"):
                st.write(f"Anteprima di: {file.name}")
                show_pdf_preview(file.getvalue())
        
        # 3. Campi per rinominare
        with col_input:
            c_tipo, c_val = st.columns([0.4, 0.6])
            with c_tipo:
                tipo = st.selectbox("T", ["AWB", "CMR", "BDC", "POD", "MRN"], key=f"t_{i}", label_visibility="collapsed")
            with c_val:
                valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Incolla codice...")
            
        # 4. Tasto Download
        with col_dl:
            if valore:
                nome_finale = f"ISP_{tipo}_{valore}.pdf"
                st.download_button(
                    label="💾 Salva", 
                    data=file.getvalue(), 
                    file_name=nome_finale, 
                    key=f"d_{i}",
                    use_container_width=True
                )
            else:
                st.write("")
        
        st.divider()

else:
    st.info("Trascina i PDF sopra per iniziare il lavoro.")