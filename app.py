import streamlit as st
import json
from auswertung import generiere_auswertung_pdf  # Import der Auswertungsfunktion

st.set_page_config(page_title="LimeSurvey JSON-Auswertung", layout="centered")
st.title("📊 LimeSurvey JSON-Auswertung")

# Auswahl der Eingabeart
eingabe_modus = st.radio("Wie möchtest du die Daten bereitstellen?", ["Datei hochladen", "Raw JSON einfügen"])

data = None

# Option 1: Datei hochladen
if eingabe_modus == "Datei hochladen":
    uploaded_file = st.file_uploader("📁 Lade den LimeSurvey-JSON-Export hoch", type="json")
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            st.success("✅ Datei erfolgreich geladen!")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei: {e}")

# Option 2: Raw JSON-Text einfügen
else:
    raw_input = st.text_area("📋 Füge hier den LimeSurvey-Export (Raw JSON) ein:", height=300)
    if raw_input.strip():
        try:
            data = json.loads(raw_input)
            st.success("✅ JSON erfolgreich geparsed!")
        except Exception as e:
            st.error(f"❌ Ungültiges JSON: {e}")

# Weiter, wenn Daten vorhanden
if data and "responses" not in data:
    st.warning("⚠️ Im JSON wurde kein 'responses'-Key gefunden.")

if data and "responses" in data:
    pdf_name = st.text_input("📄 Gewünschter PDF-Dateiname:", value="auswertung.pdf")

    if st.button("📄 PDF generieren"):
        with st.spinner("⏳ PDF wird erstellt..."):
            pdf_bytes = generiere_auswertung_pdf(data)
        st.success("✅ PDF erfolgreich erstellt!")
        st.download_button(
            "⬇️ PDF herunterladen",
            data=pdf_bytes,
            file_name=pdf_name if pdf_name else "auswertung.pdf",
            mime="application/pdf"
        )
