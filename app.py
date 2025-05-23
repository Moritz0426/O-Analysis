import base64
import csv
import io
import sys

import streamlit as st
import requests
import json
import os
import tempfile

from urllib import request

import urllib3

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

        # Überprüfen, ob die Session erfolgreich erstellt wurde

        if not session_key:
            st.error("❌ Zugriff auf LimeSurvey fehlgeschlagen. Bitte Zugangsdaten prüfen.")
        else:
            export_payload = {
                "method": "export_responses",
                "params": [session_key, survey_id, "csv", "de-informal", "full"],
                "id": 1
            }
            try:
                export_response = requests.post(LS_URL, json=export_payload)
                export_json = export_response.json()
                export_data = export_json.get("result")
            except Exception as e:
                st.error(f"❌ Fehler beim Abrufen der Daten: {e}")
                st.stop()

            if not export_data:
                st.error("❌ Keine Daten gefunden oder Export fehlgeschlagen.")
            else:
                st.code(export_data)
                decoded_bytes = base64.b64decode(export_data)
                decoded_str = decoded_bytes.decode("utf-8-sig")
                csv_reader = csv.reader(io.StringIO(decoded_str), delimiter=';')  # ggf. anderes Trennzeichen
                data = list(csv_reader)
                payload = {"responses": data}

                # Übergib das Dictionary direkt an die Auswertung
                pdf_bytes = generiere_auswertung_pdf(payload)
                st.success("✅ PDF erfolgreich erstellt")
                st.download_button("⬇️ PDF herunterladen", data=pdf_bytes, file_name="auswertung.pdf")
