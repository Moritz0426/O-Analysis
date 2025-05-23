import streamlit as st
import json
from auswertung import generiere_auswertung_pdf  # Import der Auswertungsfunktion

st.set_page_config(page_title="LimeSurvey JSON-Import", layout="centered")
st.title("📊 LimeSurvey JSON-Auswertung")

uploaded_file = st.file_uploader("📁 Lade den LimeSurvey-JSON-Export hoch", type="json")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        st.success("✅ Datei erfolgreich geladen!")

        if "responses" not in data:
            st.warning("⚠️ Im JSON wurde kein 'responses'-Key gefunden.")
        else:
            # Eingabe für PDF-Namen
            default_name = "auswertung.pdf"
            filename_input = st.text_input("📄 Gewünschter PDF-Dateiname:", value=default_name)

            # Button zum Auslösen der Auswertung
            if st.button("📄 PDF generieren"):
                with st.spinner("⏳ PDF wird erstellt..."):
                    pdf_bytes = generiere_auswertung_pdf(data)

                st.success("✅ PDF erfolgreich erstellt!")
                st.download_button(
                    "⬇️ PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename_input if filename_input else default_name,
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"❌ Fehler beim Verarbeiten der Datei: {e}")

else:
    st.info("ℹ️ Bitte eine JSON-Datei hochladen.")
