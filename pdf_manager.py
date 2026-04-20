import streamlit as st
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Manager", layout="wide")

# CSS per il "quadratino" di anteprima che appare al passaggio
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: #002D62 !important; }
    
    /* Stile per il tooltip/anteprima */
    .preview-container {
        position: relative;
        display: inline-block;
        cursor: pointer;
        color: #002D62;
        font-weight: bold;
        text-decoration: underline;
    }

    .preview-content {
        display: none;
        position: absolute;
        z-index: 100;
        border: 2px solid #002D62;
        background-color: white;
        padding: 5px;
        border-radius: 8px;
        width: 400px;
        height: 500px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
    }

    .preview-container:hover .preview-content {
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

def get_pdf_display(file_bytes):
    """Genera il codice HTML per l'anteprima piccola"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    return f'''
        <div class="preview-container">
            👁️ Passa qui per l'anteprima
            <div class="preview-content">
                <embed
                    src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0"
                    width="100%"
                    height="100%"
                    type="application/pdf"
                >
            </div>
        </div>
    '''

st.title("📄 PDF Manager - Ale Edition")
st.write("Versione ultra-rapida: passa il mouse sull'icona per vedere il documento.")

uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Intestazione Tabella
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    c1.write("**Nome File**")
    c2.write("**Anteprima Rapida**")
    c3.write("**Nuovo Nome**")
    c4.write("**Azione**")
    st.divider()

    for i, file in enumerate(uploaded_files):
        col_nome, col_preview, col_input, col_dl = st.columns([2, 2, 2, 2])
        
        with col_nome:
            st.text(file.name)
            
        with col_preview:
            # Qui appare il quadratino magico
            st.components.v1.html(get_pdf_display(file.getvalue()), height=40)
            
        with col_input:
            tipo = st.selectbox("Tipo", ["AWB", "CMR", "BDC", "POD"], key=f"t_{i}", label_visibility="collapsed")
            valore = st.text_input("Codice", key=f"v_{i}", label_visibility="collapsed", placeholder="Incolla codice...")
            
        with col_dl:
            if valore:
                nome_finale = f"ISP_{tipo}_{valore}.pdf"
                st.download_button("💾 Scarica", file.getvalue(), file_name=nome_finale, key=f"d_{i}")
            else:
                st.write("---")