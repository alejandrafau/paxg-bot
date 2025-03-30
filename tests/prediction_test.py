import unittest
from gold.predictions import fetch_predictions
from datetime import datetime,timedelta
import pandas as pd
from gold.main import send_email_report
import os


class TestCsv(unittest.TestCase):

    def test_fetch_predictions(self):
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        prices = pd.read_csv("test_prices.csv")
        df = prices[-5:]
        predictions = fetch_predictions(now, df)
        self.assertIsInstance(predictions, dict)
        self.assertIn('compra', predictions)
        self.assertIn('venta', predictions)
        self.assertIsInstance(predictions['compra'], float)
        self.assertIsInstance(predictions['venta'], float)

    def test_matrix_creation(self):
        ERROR = 12.72
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        predictions={"compra": 3540.5, "venta": 3480.3}
        prices = pd.read_csv("test_prices.csv")
        df = prices[-5:]
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

        df.to_csv("test_daily.matrix.csv", float_format="%.2f", index=False)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(24,len(df))




    def test_send_mail(self):
        send_email_report(
            sender_email='maria.alejandra.fauquie@gmail.com',
            sender_password=os.getenv('GMAIL_PASSWORD'),
            recipient_email='maria.alejandra.fauquie@gmail.com',
            subject='Corridas bot',
            body='Please find the attached report.',
            attachment_paths=['test_balance_sheet.csv']
        )

