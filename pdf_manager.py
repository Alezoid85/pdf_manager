import streamlit as st
import io
import zipfile

# --- CONFIGURAZIONE PAGINA E STILE ---
st.set_page_config(page_title="Ale PDF Manager", layout="wide")

# CSS Personalizzato per sfondo bianco e testo blu scuro
st.markdown("""
    <style>
    /* Sfondo principale */
    .stApp {
        background-color: white;
    }
    /* Titoli e scritte in blu scuro */
    h1, h2, h3, p, label, .stMarkdown {
        color: #002D62 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Colore dei nomi dei file caricati */
    .stText {
        color: #002D62 !important;
    }
    /* Linea di separazione blu */
    hr {
        border: 1px solid #002D62;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 PDF Renamer Professionale")
st.write("Interfaccia semplificata per rinomina massiva.")

tipologie = ["ISP_AWB", "ISP_CMR", "ISP_MRN", "ISP_ESITO", "ISP_BDC", "ISP_POD"]

# Area di caricamento
uploaded_files = st.file_uploader("Trascina i PDF qui", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.divider()
    
    # Intestazioni tabella
    cols_h = st.columns([3, 2, 3, 2, 1])
    cols_h[0].markdown("**Nome Originale**")
    cols_h[1].markdown("**Tipologia**")
    cols_h[2].markdown("**Valore (Excel)**")
    cols_h[3].markdown("**Nuovo Nome**")
    cols_h[4].markdown("**Azione**")

    files_da_scaricare = []

    for i, file in enumerate(uploaded_files):
        c1, c2, c3, c4, c5 = st.columns([3, 2, 3, 2, 1])
        
        # 1. Nome originale
        c1.text(file.name)
        
        # 2. Menu a tendina
        tipo = c2.selectbox(f"Tipo {i}", tipologie, label_visibility="collapsed", key=f"tipo_{i}")
        
        # 3. Valore (incollato da Excel)
        valore = c3.text_input(f"Valore {i}", label_visibility="collapsed", key=f"val_{i}")
        
        # 4. Anteprima nome finale
        nome_finale = f"{tipo}{valore}.pdf" if valore else ""
        if nome_finale:
            c4.code(nome_finale)
            files_da_scaricare.append({"content": file.getvalue(), "name": nome_finale})
            
            # 5. Pulsante download singolo
            c5.download_button(
                label="💾",
                data=file.getvalue(),
                file_name=nome_finale,
                mime="application/pdf",
                key=f"btn_{i}"
            )
        else:
            c4.write("---")

    st.divider()

    # --- DOWNLOAD MASSIVO ---
    if len(files_da_scaricare) > 1:
        st.subheader("📦 Download Massivo")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for f in files_da_scaricare:
                zip_file.writestr(f["name"], f["content"])
        
        st.download_button(
            label="SCARICA TUTTI I FILE (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="pdf_rinominati_ale.zip",
            mime="application/zip",
            use_container_width=True
        )