import streamlit as st
import base64
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ale PDF Visual Renamer", layout="wide")

# CSS Personalizzato: Sfondo bianco e testi blu scuro
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #002D62 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Stile per il contenitore del PDF */
    .pdf-container {
        border: 2px solid #002D62;
        border-radius: 10px;
        padding: 5px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

def display_pdf(file_bytes):
    """Funzione per generare l'anteprima del PDF nell'interfaccia"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    
    # Usiamo il tag <embed> che è più supportato per i flussi di dati base64
    pdf_display = f'''
        <div class="pdf-container">
            <embed
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="700"
                type="application/pdf"
            >
        </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- INTERFACCIA PRINCIPALE ---
st.title("📄 PDF Renamer con Anteprima")
st.write("Carica i file, controlla il contenuto a sinistra e rinomina a destra.")

# Caricamento file
uploaded_files = st.file_uploader("Trascina qui i tuoi PDF aziendali", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        # Creiamo un contenitore per ogni file caricato
        with st.container():
            col_anteprima, col_dati = st.columns([1.2, 0.8])
            
            with col_anteprima:
                st.subheader(f"🔍 Documento: {file.name}")
                display_pdf(file.getvalue())
            
            with col_dati:
                st.subheader("✍️ Dati Nuova Rinomina")
                
                # Selezione tipologia (le tue categorie ISP)
                tipo = st.selectbox(
                    f"Seleziona Tipo", 
                    ["AWB", "CMR", "BDC", "POD", "MRN", "ESITO"], 
                    key=f"tipo_{i}"
                )
                
                # Inserimento codice (qui incollerai da Excel)
                valore = st.text_input(
                    f"Inserisci Numero Riferimento", 
                    key=f"val_{i}",
                    placeholder="Esempio: 12345678"
                )
                
                if valore:
                    nuovo_nome = f"ISP_{tipo}_{valore}.pdf"
                    st.success(f"✅ Pronto per la rinomina:")
                    st.code(nuovo_nome, language=None)
                    
                    # Pulsante di download per il singolo file rinominato
                    st.download_button(
                        label=f"💾 SCARICA {nuovo_nome}",
                        data=file.getvalue(),
                        file_name=nuovo_nome,
                        mime="application/pdf",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
                else:
                    st.info("Inserisci un riferimento per generare il nuovo nome.")
            
            # Linea di separazione tra un file e l'altro
            st.markdown("---")

else:
    st.info("In attesa di file da elaborare... Trascina i PDF sopra per iniziare.")