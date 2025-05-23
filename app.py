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
                "params": [session_key, survey_id, "csv", "de-informal", "long"],
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
                decoded_bytes = base64.b64decode(export_data)
                decoded_str = decoded_bytes.decode("utf-8-sig")
                csv_reader = csv.DictReader(io.StringIO(decoded_str), delimiter=';')
                data = list(csv_reader)

                # Fragen abfragen
                questions_payload = {
                    "method": "list_questions",
                    "params": [session_key, survey_id],
                    "id": 2
                }
                questions_response = requests.post(LS_URL, json=questions_payload)
                questions = questions_response.json().get("result", [])
                code_to_text = {q["title"]: q["question"] for q in questions}
                qid_to_code = {q["qid"]: q["title"] for q in questions}

                # Antwortoptionen abfragen
                answer_map = {}
                for q in questions:
                    answers_payload = {
                        "method": "list_answers",
                        "params": [session_key, survey_id, q["qid"]],
                        "id": 3
                    }
                    answers_response = requests.post(LS_URL, json=answers_payload)
                    st.write(f"Antwort von list_answers für {q['title']} (qid={q['qid']}):", answers_response.text)
                    if answers_response.status_code == 200 and answers_response.text.strip():
                        try:
                            answers = answers_response.json().get("result", [])
                        except Exception as e:
                            st.warning(f"Antworten für Frage {q['title']} konnten nicht geladen werden: {e}")
                            answers = []
                    else:
                        st.warning(f"Keine Antwortdaten für Frage {q['title']} erhalten.")
                        answers = []
                    code_ans_map = {a["code"]: a["answer"] for a in answers}
                    if code_ans_map:
                        answer_map[q["title"]] = code_ans_map

                # Spaltennamen ersetzen: "G01Q01" -> "G01Q01. /Fragetext/"
                new_fieldnames = []
                for col in data[0].keys():
                    code = col.split()[0]  # nimmt den Code vor evtl. ". "
                    if code in code_to_text:
                        new_fieldnames.append(f"{code}. /{code_to_text[code]}/")
                    else:
                        new_fieldnames.append(col)

                # Antworten ersetzen
                new_data = []
                for row in data:
                    new_row = {}
                    for col, value in row.items():
                        code = col.split()[0]
                        new_col = f"{code}. /{code_to_text[code]}/" if code in code_to_text else col
                        if code in answer_map and value in answer_map[code]:
                            new_row[new_col] = answer_map[code][value]
                        else:
                            new_row[new_col] = value
                    new_data.append(new_row)
                payload = {"responses": data}

                # Übergib das Dictionary direkt an die Auswertung
                pdf_bytes = generiere_auswertung_pdf(payload)
                st.success("✅ PDF erfolgreich erstellt")
                st.download_button("⬇️ PDF herunterladen", data=pdf_bytes, file_name="auswertung.pdf")
