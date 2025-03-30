from datetime import datetime
import pandas as pd
import ccxt
import os
from gold.df_generation import create_daily_matrix
import smtplib
from email.message import EmailMessage
from gold.trade import Trade
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

wallet2 = ccxt.kraken({
    'apiKey': os.getenv("KRAKEN_API_KEY_PUB"),
    'secret': os.getenv("KRAKEN_API_KEY_PRIV"),
})

wallet = ccxt.binance({
    'apiKey': os.getenv("BINANCE_API_KEY_PUB"),
    'secret': os.getenv("BINANCE_API_KEY_PRIV"),
})


def send_email_report(sender_email, sender_password, recipient_email, subject, body, attachment_paths=None):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)

    if attachment_paths is None:
        attachment_paths = []

    for path in attachment_paths:

        if os.path.exists(path):
            with open(path, 'rb') as file:
                file_data = file.read()
                file_name = os.path.basename(path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
                print("Email sent successfully!")


def midnight_processing(tim):
    logger.info("procesamiento de medianoche comenzado")
    if os.path.exists("balance_sheet.csv"):
        logger.info("hoja de balances encontrada")
        try:
            send_email_report(
                sender_email='maria.alejandra.fauquie@gmail.com',
                sender_password=os.getenv('GMAIL_PASSWORD'),
                recipient_email='maria.alejandra.fauquie@gmail.com',
                subject='Corridas de bot',
                body='Please find the attached report.',
                attachment_paths=['./balance_sheet.csv', './app.log']
            )
            logger.info("Mail enviado con hoja de balances y hoja de errores")
        except Exception as e:
            logger.error("No se pudo enviar la hoja de balances ni de errores", e, exc_info=True)

    compra, venta = trade.compra, trade.venta
    row = [tim.date(), compra, venta]
    if os.path.exists("prices.csv"):
        prices = pd.read_csv("prices.csv")
    else:
        logger.info("creando registro de precios")
        prices = pd.DataFrame(columns=["fecha", "compra", "venta"])
    prices.loc[len(prices)] = row
    prices.to_csv("prices.csv", index=False)
    logger.info("registro de precios actualizado y guardado")
    if len(prices) >= 5:
        create_daily_matrix(tim, prices[-5:])
        logger.info("registro de precios con longitud adecuada para modelado, creando matriz de proyecciones")


def regular_processing(tim):
    if os.path.exists("daily_matrix.csv"):
        matrix = pd.read_csv("daily_matrix.csv")
        try:
            trade.roadmap = matrix
            if matrix["pred_compra"].iloc[-1] < trade.compra:
                return  # Corrected: Stop execution instead of using 'break'
            trade.run(tim)
        except Exception as e:
            logger.error(f"No se pudo correr trade: {e}", exc_info=True)  # Corrected error logging
    else:
        logger.info("No hay matriz de predicciones")


if __name__ == "__main__":
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    trade = Trade(wallet, now)

    if now.hour == 0:
        midnight_processing(now)
    else:
        regular_processing(now)
