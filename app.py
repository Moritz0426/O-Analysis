import streamlit as st
import json
from auswertung import generiere_auswertung_pdf  # Import der Auswertungsfunktion

st.set_page_config(page_title="LimeSurvey JSON-Auswertung", layout="centered")
st.title("📊 LimeSurvey JSON-Auswertung")

st.markdown("Du kannst entweder eine JSON-Datei hochladen **oder** den JSON-Rohtext direkt einfügen.")

# Auswahl zwischen Datei-Upload oder JSON-Text
modus = st.radio("📥 Eingabemodus wählen", ["Datei hochladen", "JSON-Rohtext einfügen"])

data = None

if modus == "Datei hochladen":
    uploaded_file = st.file_uploader("Lade den LimeSurvey-JSON-Export hoch", type="json")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            st.success("✅ Datei erfolgreich geladen.")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei: {e}")
else:
    raw_text = st.text_area("📋 JSON-Rohtext hier einfügen", height=300)
    if raw_text.strip():
        try:
            data = json.loads(raw_text)
            st.success("✅ JSON-Rohtext erfolgreich geladen.")
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen des JSON-Rohtexts: {e}")

# PDF-Generierung und Download außerhalb des Formulars
pdf_bytes = None
filename = "auswertung.pdf"

if data and "responses" in data:
    with st.form("pdf_form"):
        filename = st.text_input("📄 Dateiname der PDF", value="auswertung.pdf")
        generate = st.form_submit_button("📄 PDF erstellen")
    if generate:
        try:
            pdf_bytes = generiere_auswertung_pdf(data)
            st.success("✅ PDF erfolgreich erstellt.")
        except Exception as e:
            st.error(f"❌ Fehler bei der PDF-Erstellung: {e}")
    if pdf_bytes:
        st.download_button("⬇️ PDF herunterladen", data=pdf_bytes, file_name=filename, mime="application/pdf")
elif data:
    st.warning("⚠️ Kein 'responses'-Key im JSON gefunden.")
else:
    st.info("⬆️ Bitte lade eine Datei hoch oder füge JSON ein.")
