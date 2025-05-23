import streamlit as st
import json

st.set_page_config(page_title="LimeSurvey JSON-Import", layout="centered")
st.title("LimeSurvey JSON-Export Auswertung")

uploaded_file = st.file_uploader("Lade den LimeSurvey-JSON-Export hoch", type="json")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        st.success("Datei erfolgreich geladen!")
        # Zeige die ersten Zeilen/Keys zur Kontrolle
        st.write("Schlüssel im JSON:", list(data.keys()))
        # Hier kannst du wie bisher mit data["responses"] usw. weiterarbeiten
        # Beispiel:
        if "responses" in data:
            st.write("Erste 5 Antworten:", data["responses"][:5])
        else:
            st.warning("Im JSON wurde kein 'responses'-Key gefunden.")
        # Optional: Rufe deine Auswertungsfunktion auf
        # pdf_bytes = generiere_auswertung_pdf(data)
        # st.download_button("PDF herunterladen", pdf_bytes, file_name="auswertung.pdf")
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {e}")
else:
    st.info("Bitte eine JSON-Datei hochladen.")