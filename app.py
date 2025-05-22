import base64
import streamlit as st
import requests
import json
import os
import tempfile
from auswertung import generiere_auswertung_pdf

st.set_page_config(page_title="LimeSurvey PDF-Auswerter", layout="centered")
st.title("📊 LimeSurvey PDF-Auswerter")
st.markdown("Gib eine gültige **Survey-ID** deiner Umfrage ein, um eine PDF-Auswertung zu generieren.")

survey_id = st.text_input("📋 Survey-ID", placeholder="z. B. 123456")

if st.button("📄 PDF generieren") and survey_id:
    LS_URL = os.environ.get("LS_URL")
    LS_USER = os.environ.get("LS_USER")
    LS_PASSWORD = os.environ.get("LS_PASSWORD")

    if not all([LS_URL, LS_USER, LS_PASSWORD]):
        st.error("API-Zugangsdaten fehlen. Bitte setze die Streamlit Secrets korrekt.")
    else:
        # Session starten
        session_payload = {
            "method": "get_session_key",
            "params": [LS_USER, LS_PASSWORD],
            "id": 1
        }
        r = requests.post(LS_URL, json=session_payload)
        st.code(f"HTTP-Status: {r.status_code}\nAntwort:\n{r.text[:1000]}")
        st.code(f"Status: {r.status_code}\nAntwort:\n{r.text[:500]}")
        session_key = r.json().get("result")


        if not session_key:
            st.error("❌ Zugriff auf LimeSurvey fehlgeschlagen. Bitte Zugangsdaten prüfen.")
        else:
            export_payload = {
                "method": "export_responses",
                "params": [session_key, int(survey_id), "json"],
                "id": 2
            }
            r = requests.post(LS_URL, json=export_payload)
            st.code(f"Export-Antwort (Status: {r.status_code}):\n{r.text[:1000]}")
            st.json(r.json())  # zeigt strukturierte JSON-Antwort
            export_data = r.json().get("result")

            if not export_data:
                st.error("❌ Keine Daten gefunden oder Export fehlgeschlagen.")
            else:
                # Base64-Dekodierung
                decoded_bytes = base64.b64decode(export_data)
                decoded_str = decoded_bytes.decode("utf-8")

                # Jetzt als JSON parsen
                data = json.loads(decoded_str)
                # Übergib das Dictionary direkt an die Auswertung
                pdf_bytes = generiere_auswertung_pdf({"responses": data})
                st.success("✅ PDF erfolgreich erstellt")
                st.download_button("⬇️ PDF herunterladen", data=pdf_bytes, file_name="auswertung.pdf")
