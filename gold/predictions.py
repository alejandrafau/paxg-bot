import anthropic
from dotenv import load_dotenv
import os
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

    values_compra = ",".join(str(v) for v in df["compra"].iloc[:5])
    values_venta  = ",".join(str(v) for v in df["venta"].iloc[:5])

    prompt = (
        f"From {df['fecha'].iloc[0]} to {df['fecha'].iloc[4]}, "
        f"the closing ask-side prices of pax gold were {values_compra}, "
        f"and the closing bid-side prices were {values_venta}. "
        f"What might be the closing prices of pax gold on {tomorrow}? "
        f"Respond only with two numeric values in the format: (compra, venta). "
        "Do not include any explanation or extra text."
    )

    message = llm.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    print("Raw model output:", text)

    # Parse (compra, venta)
    match = re.findall(r"[-+]?\d*\.?\d+", text)
    if len(match) >= 2:
        pred_compra, pred_venta = map(float, match[:2])
    else:
        raise ValueError(f"Could not parse tuple from: {text}")

    predictions = {"compra": pred_compra, "venta": pred_venta}
    print("Parsed predictions:", predictions)

    return predictions





