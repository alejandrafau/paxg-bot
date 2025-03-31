import pandas as pd
from datetime import timedelta
from predictions import fetch_predictions
import logging
ERROR = 12.72
logger = logging.getLogger(__name__)


def create_daily_matrix(now, df):
    try:
        predictions = fetch_predictions(now, df)
        logger.info(f"Predictions received: {predictions}")
        compra = df.compra.iloc[-1]
        pred_compra = predictions["compra"]
        compra_down = pred_compra - ERROR
        compra_up = pred_compra + ERROR
        venta = df.venta.iloc[- 1]
        pred_venta = predictions["venta"]
        venta_down = pred_venta - ERROR
        venta_up = pred_venta + ERROR
        hours = [(now + timedelta(hours=i)).hour for i in range(24)]
        inc_compra = (pred_compra - compra) / 23
        inc_compra_up = (compra_up - compra) / 23
        inc_compra_down = (compra_down - compra) / 23
        pred_compra = [compra + i * inc_compra for i in range(24)]
        compra_up = [compra + i * inc_compra_up for i in range(24)]
        compra_down = [compra + i * inc_compra_down for i in range(24)]

        inc_venta = (pred_venta - venta) / 23
        inc_venta_up = (venta_up - venta) / 23
        inc_venta_down = (venta_down - venta) / 23

        pred_venta = [venta + i * inc_venta for i in range(24)]
        venta_up = [venta + i * inc_venta_up for i in range(24)]
        venta_down = [venta + i * inc_venta_down for i in range(24)]

        df = pd.DataFrame({
            "hour": hours,
            "pred_compra": pred_compra,
            "compra_up": compra_up,
            "compra_down": compra_down,
            "pred_venta": pred_venta,
            "venta_up": venta_up,
            "venta_down": venta_down,
        })

        df.to_csv("daily_matrix.csv", float_format="%.2f", index=False)
        logger.info("matriz construida")

    except Exception as e:
        logger.error("no se pudo obtener predicciones", e, exc_info=True)
