
import pandas as pd
import ccxt
import os
import logging

logger = logging.getLogger(__name__)


class Trade:
    def __init__(self, wallet, now, roadmap=None):
        self.wallet = wallet
        self.symbol = 'PAXG/USDT'
        self.commission = 0.001
        self.stop_loss = 0.15
        self.roadmap = roadmap
        self.last_b_price = self._get_last_b_price()

        # Descomentar para producción
        # self.usdt_balance = self._get_usdt_balance()
        self.usdt_balance = 100
        # self.paxg_balance = self._get_paxg_balance()
        self.paxg_balance = 100

        self.compra = self.get_compra()
        self.venta = self.get_venta()
        self.actual_venta = self.venta - (self.venta * self.commission)

        # Descomentar para producción
        # self.total_assets = self._get_assets()
        # self.past_assets = self._get_past_assets()

        self.currently = now.hour

        # Descomentar para producción
        # self.register = pd.DataFrame(columns=["fecha", "hora", "transaccion", "assets"])
        self.register_sand = pd.DataFrame(columns=["fecha", "hora", "transaccion", "precio_trans","precio","precioref"])

    def run(self, now):
        """ Main method to execute trading logic """
        # Get hourly data once
        try:
            hourly_data = self.roadmap.query('hour==@self.currently')
            p_compra = hourly_data["compra_down"].values[0]
            p_venta = hourly_data["venta_up"].values[0]
            transaccion = "None"

            # Descomentar para producción
            if self._buy_signal(p_compra):
                # if self.stop_loss_signal():
                   # self._sell()
                    # transaccion = "stop_loss"
                # else:
                    # self._buy()
                transaccion = "compra"
                logger.info("Hubo señal para comprar")
            elif self._sell_signal(p_venta):
                # self._sell()
                transaccion = "venta"
                logger.info("Hubo señal para vender")
            # elif self._stop_loss_signal():
                # self._sell()
                # transaccion = "stop_loss"

            # Record transaction
            #self._record_transaction(now, transaccion)
            self._record_transaction(now,transaccion, p_compra, p_venta)
            logger.info("Se corrió trade")
        except Exception as e:
            logger.error("No se pudo correr trade", e, exc_info=True)

    def get_compra(self):
        """Obtiene el precio actual de compra (ask).
        Es decir, lo que debo pagar si quiero comprar."""
        ticker = self.wallet.fetch_ticker(self.symbol)
        return ticker["ask"]

    def get_venta(self):
        """Obtiene el precio actual de venta (bid).
        Es decir, lo que recibiría si vendo."""
        ticker = self.wallet.fetch_ticker(self.symbol)
        return ticker["bid"]

    def _buy(self):
        self._buy_order(self.usdt_balance)


    def _sell(self):
        self._sell_order(self.paxg_balance)

    def _buy_signal(self, p_compra):
        return (self.usdt_balance > 0) and \
               (self.compra < p_compra)

    def _sell_signal(self,p_venta):
        target = self.last_b_price 
        """ Check if selling conditions are met """
        return (self.paxg_balance > 0) and (self.venta > p_venta) and (self.actual_venta > target)

    def _record_transaction(self, now, transaccion, p_compra, p_venta):
        """ Record transaction to CSV """
        if transaccion == "compra":
            price = self.compra + (self.compra * self.commission)
            row = [now.date(), now.hour, transaccion, price, self.compra, p_compra]
        elif transaccion == "venta":
            price = self.venta - (self.venta * self.commission)
            row = [now.date(), now.hour, transaccion, price, self.venta, p_venta]
        else:
            transaccion == "nada"
            row = [now.date(), now.hour, transaccion, 0, 0, 0]

        file_path = "balance_sheet.csv"

        # If file exists, append; else, create with header
        if os.path.exists(file_path):
            pd.DataFrame([row], columns=["fecha", "hora", "transaccion", "precio_trans", "precio", "precioref"]) \
                .to_csv(file_path, mode='a', header=False, index=False, float_format="%.8f")
        else:
            pd.DataFrame([row], columns=["fecha", "hora", "transaccion", "precio_trans", "precio", "precioref"]) \
                .to_csv(file_path, mode='w', header=True, index=False, float_format="%.8f")

    def _get_assets(self):
        """ Calculate total assets in USDT """
        pax_in_usdt = self.paxg_balance * self.venta
        return self.usdt_balance + (pax_in_usdt - pax_in_usdt*self.commission)

    def _get_past_assets(self):
        if os.path.exists("balance_sheet.csv"):
            df = pd.read_csv("balance_sheet.csv")
            return df["assets"].iloc[-1]
        return self._get_assets()

    def _get_usdt_balance(self):
        """ Get USDT balance from wallet """
        balance = self.wallet.fetch_balance()
        return balance['total'].get('USDT', 0)

    def _get_paxg_balance(self):
        """ Get PAXG balance from wallet """
        balance = self.wallet.fetch_balance()
        return balance['total'].get('PAXG', 0)

    def _sell_order(self, amount):
        """ Execute a sell order """
        self.wallet.create_market_sell_order(self.symbol, amount)

    def _buy_order(self, funds):
        """ Execute a buy order """
        amount = funds/self.compra
        self.wallet.create_market_buy_order(self.symbol, amount)

    def _get_last_b_price(self):
        if os.path.exists("balance_sheet.csv"):
            balance = pd.read_csv("balance_sheet.csv", index_col=0)
            buys = balance.query("transaccion=='compra'")
            if buys.empty:
                last_b_price = 0
            else:
                last_b_price = buys["precio_trans"].iloc[-1]
        else:
            last_b_price = 0
        return last_b_price



    """ def _stop_loss_signal(self):

            return (self.paxg_balance > 0) and \
                   (self.total_assets < self.past_assets - self.past_assets * self.stop_loss)
    """
