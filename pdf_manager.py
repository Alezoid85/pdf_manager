import streamlit as st
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Visual Renamer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, p, label { color: #002D62 !important; }
    .css-1r6slb0 { border: 1px solid #002D62; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

def display_pdf(file_bytes):
    # Funzione per mostrare il PDF nell'interfaccia
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("📄 PDF Renamer con Anteprima")
st.write("Carica i file, guarda l'anteprima a sinistra e scrivi il nome a destra.")

uploaded_files = st.file_uploader("Trascina qui i PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        with st.container():
            col_anteprima, col_dati = st.columns([1, 1])
            
            with col_anteprima:
                st.subheader(f"🔍 Anteprima: {file.name}")
                display_pdf(file.getvalue())
            
            with col_dati:
                st.subheader("✍️ Rinomina")
                tipo = st.selectbox(f"Tipologia", ["AWB", "CMR", "BDC", "POD", "MRN"], key=f"tipo_{i}")
                valore = st.text_input(f"Inserisci Numero/Riferimento", key=f"val_{i}")
                
                if valore:
                    nuovo_nome = f"ISP_{tipo}_{valore}.pdf"
                    st.info(f"Nuovo nome: **{nuovo_nome}**")
                    
                    st.download_button(
                        label="💾 SCARICA PDF RINOMINATO",
                        data=file.getvalue(),
                        file_name=nuovo_nome,
                        mime="application/pdf",
                        key=f"dl_{i}"
                    )
            st.divider()