# LimeSurvey PDF-Dashboard

Dieses Projekt bietet eine Weboberfläche zur Eingabe einer Survey-ID und erzeugt automatisch eine PDF-Auswertung anhand der LimeSurvey-Antworten.

## Setup

1. Erstelle ein privates Repository auf GitHub.
2. Lade den Inhalt dieses Ordners hoch.
3. Verknüpfe das Repository mit [streamlit.io/cloud](https://streamlit.io/cloud).
4. Trage in `Secrets` folgende Variablen ein:

```toml
LS_URL = "https://osurvey.uber.space/index.php/admin/remotecontrol"
LS_USER = "admin"
LS_PASSWORD = "dein_admin_passwort"
```

5. Starte die App und gib eine Survey-ID ein.
6. Lade dein fertiges PDF herunter ✅
