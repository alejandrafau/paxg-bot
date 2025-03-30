import anthropic
from dotenv import load_dotenv
import os
import time
from datetime import timedelta
import re
import logging

logger = logging.getLogger(__name__)

load_dotenv()


llm = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )


def fetch_predictions(now, df):
    today = now.date()
    tomorrow = today + timedelta(days=1)
    prompt = (f"from {df['fecha'].iloc[0]} to {df['fecha'].iloc[4]} "
              f"the closing prices of pax gold in the ask side were {df['compra'].iloc[0]},"
              f"{df['compra'].iloc[1]},{df['compra'].iloc[2]},{df['compra'].iloc[3]},{df['compra'].iloc[4]}. "
              f"What might the closing price of pax gold on the asking side on {tomorrow}. "
              "Respond only with a numeric value, no explanation or additional text.")

    message = llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    pred_compra = float(message.content[0].text)
    print(f"pred compra es: {pred_compra}")
    print(message.content)
    time.sleep(4.5)

    prompt = (f"from {df['fecha'].iloc[0]} to {df['fecha'].iloc[4]} "
              f"the closing prices of pax gold in the bid side were {df['venta'].iloc[0]},"
              f"{df['venta'].iloc[1]},{df['venta'].iloc[2]},{df['venta'].iloc[3]},{df['venta'].iloc[4]}. "
              f"What might the closing price of pax gold on the bid side on {tomorrow}. "
              "Respond only with a numeric value, no explanation or additional text.")

    message = llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    pred_venta = float(message.content[0].text)
    print(f"pred venta es: {pred_venta}")
    print(message.content)

    predictions = {"compra":pred_compra,"venta": pred_venta}
    return predictions





