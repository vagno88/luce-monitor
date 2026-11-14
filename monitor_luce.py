import os
import json
import smtplib
import pandas as pd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_URL = "https://docs.google.com/spreadsheets/d/18bzSR5JAIGhiISITbEMehDAWRVXMJqUNbqXeTmYLttM/export?format=csv&gid=325699321"

STATE_FILE = "best_offer.json"

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

EMAIL_TO = [
    x.strip()
    for x in os.environ["EMAIL_TO"].split(",")
]


def send_email(subject, html_body):

    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)

    msg.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8"
        )
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            EMAIL_USER,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_USER,
            EMAIL_TO,
            msg.as_string()
        )


def load_previous():

    if not os.path.exists(STATE_FILE):
        return {}

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_current(data):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


print("Download offerte...")

df = pd.read_csv(CSV_URL)

df["TOTALE_NUM"] = (
    df["TOTALE"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

df["TOTALE_NUM"] = pd.to_numeric(
    df["TOTALE_NUM"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "GESTORE",
        "DENOMINAZIONE OFFERTA",
        "PREZZO Smc",
        "TOTALE_NUM"
    ]
)

df = df[
    ~df["DENOMINAZIONE OFFERTA"]
    .astype(str)
    .str.contains(
        "questa parte del foglio",
        case=False,
        na=False
    )
]

top3 = (
    df.sort_values("TOTALE_NUM")
      .head(3)
)

best = top3.iloc[0]


current = {
    "gestore": str(best["GESTORE"]),
    "offerta": str(best["DENOMINAZIONE OFFERTA"]),
    "totale": float(best["TOTALE_NUM"]),
    "smc": str(best["PREZZO Smc"])
}

previous = load_previous()

changed = (
    previous.get("gestore") != current["gestore"]
    or previous.get("offerta") != current["offerta"]
    or previous.get("totale") != current["totale"]
)

if changed:

    medals = ["🥇", "🥈", "🥉"]

    cards = ""

    for idx, (_, row) in enumerate(top3.iterrows()):

        difference_block = ""

        if idx == 0:

            difference_block = f"""
            
            """

        cards += f"""
        <div style="
            background:#ffffff;
            border-radius:18px;
            padding:20px;
            margin-bottom:20px;
            border:1px solid #d9d9d9;
            box-shadow:0 3px 12px rgba(0,0,0,0.08);
        ">

            <h2 style="
                margin:0;
                color:#003366;
            ">
                {medals[idx]} {row['GESTORE']}
            </h2>

            <div style="
                margin-top:8px;
                font-size:17px;
                font-weight:bold;
            ">
                {row['DENOMINAZIONE OFFERTA']}
            </div>

            <div style="
                background:#dff6dd;
                color:#0a6417;
                padding:18px;
                border-radius:12px;
                text-align:center;
                margin-top:15px;
                margin-bottom:15px;
            ">

                <div style="
                    font-size:13px;
                    font-weight:bold;
                    letter-spacing:1px;
                ">
                    PREZZO SMC
                </div>

                <div style="
                    font-size:38px;
                    font-weight:bold;
                    margin-top:5px;
                ">
                    {row['PREZZO Smc']}
                </div>

            </div>
           

            {difference_block}

            <table style="
                width:100%;
                border-collapse:collapse;
                font-size:14px;
            ">

                <tr>
                    <td style="padding:6px;"><b>📋 QVD-CCV</b></td>
                    <td style="padding:6px;">{row['QVD - CCV']}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>📅 Aggiornato</b></td>
                    <td style="padding:6px;">{row['AGGIORNATO']}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>⏳ Validità</b></td>
                    <td style="padding:6px;">{row["VALIDITA'"]}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>📝 Durata contratto</b></td>
                    <td style="padding:6px;">{row['DURATA CONTRATTO']}</td>
                </tr>

            </table>

            <div style="
                background:#fff8e1;
                border-left:5px solid #ffb300;
                padding:12px;
                margin-top:15px;
                border-radius:8px;
            ">

                <div style="
                    font-weight:bold;
                    margin-bottom:8px;
                ">
                    📌 NOTE IMPORTANTI
                </div>

                {row['NOTE']}

            </div>

            <div style="
                text-align:center;
                margin-top:15px;
            ">

                <a href="{row['LINK OFFERTA']}"
                   style="
                        background:#0078d4;
                        color:white;
                        text-decoration:none;
                        padding:14px 24px;
                        border-radius:10px;
                        display:inline-block;
                        font-weight:bold;
                        font-size:16px;
                   ">

                   🔗 APRI OFFERTA

                </a>

            </div>

        </div>
        """

    html_body = f"""
    <html>

    <body style="
        background:#f0f2f5;
        font-family:Arial,sans-serif;
        margin:0;
        padding:20px;
    ">

        <div style="
            max-width:700px;
            margin:auto;
        ">

            <h1 style="
                color:#003366;
                text-align:center;
            ">
                🏆 Nuova Migliore Offerta Gas
            </h1>

            <p style="
                text-align:center;
                color:#555;
                font-size:16px;
            ">
                È stata rilevata una variazione nella classifica delle offerte gas a prezzo fisso.
            </p>

            {cards}

            <div style="
                background:#fff3cd;
                border-radius:12px;
                padding:16px;
                margin-top:20px;
                border:1px solid #ffe69c;
            ">

                <h3 style="margin-top:0;">
                    📌 Migliore Offerta Precedente
                </h3>

                <b>Gestore:</b>
                {previous.get('gestore', 'N/D')}

                <br><br>

                <b>Offerta:</b>
                {previous.get('offerta', 'N/D')}

                <br><br>

                <b>Totale:</b>
                {previous.get('totale', 'N/D')}

            </div>

        </div>

    </body>

    </html>
    """

    send_email(
        f"🏆 {best['GESTORE']} | {best['PREZZO Smc']}",
        html_body
    )

    save_current(current)

    print("EMAIL INVIATA")

else:

    print("NESSUNA VARIAZIONE")
