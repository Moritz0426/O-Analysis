import streamlit as st
import json
from auswertung import generiere_auswertung_pdf  # Import der Auswertungsfunktion

st.set_page_config(page_title="LimeSurvey JSON-Import", layout="centered")
st.title("LimeSurvey JSON-Export Auswertung")

uploaded_file = st.file_uploader("Lade den LimeSurvey-JSON-Export hoch", type="json")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        st.success("Datei erfolgreich geladen!")
        if "responses" in data:
            st.write("PDF wird generiert...")
            # PDF generieren und Download anbieten
            pdf_bytes = generiere_auswertung_pdf(data)
            st.download_button(
                "Auswertung als PDF herunterladen",
                pdf_bytes,
                file_name="auswertung.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Im JSON wurde kein 'responses'-Key gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {e}")
else:
    st.info("Bitte eine JSON-Datei hochladen.")