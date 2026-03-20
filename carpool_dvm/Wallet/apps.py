from django.apps import AppConfig


class WalletConfig(AppConfig):
    name = "Wallet"

    def ready(self):
        import Wallet.signals