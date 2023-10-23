# Standard Libraries
from re import sub

# App Modules
from .base import Scraper


class SafariOutdoorScraper(Scraper):
    def parse_propellant_list(self):
        self.propellant_list = []
        for item in self.response.html.find(".product.details.product-item-details"):
            price: float = float(
                sub(r"[^\d.]", "", item.find(".price", first=True).text)
            )
            url: str = item.find("a.product-item-link", first=True).attrs.get("href")
            name: str = item.find("a.product-item-link", first=True).text

            if item.find("div.stock.unavailable"):
                print(name, "unavailable")
                continue

            self.propellant_list.append({"name": name, "price": price, "url": url})


class ZimbiScraper(Scraper):
    def parse_propellant_list(self):
        self.propellant_list = []
        for item in self.response.html.find(
            "a.woocommerce-LoopProduct-link.woocommerce-loop-product__link"
        ):
            price: float = float(
                sub(r"[^\d.]", "", item.find(".price", first=True).text)
            )
            url: str = item.attrs.get("href")
            name: str = item.find("h2", first=True).text

            self.propellant_list.append({"name": name, "price": price, "url": url})


class ShootingStuffScraper(Scraper):
    def parse_propellant_list(self):
        self.propellant_list = []
        for item in self.response.html.find(".product.details.product-item-details"):
            price: float = float(
                sub(r"[^\d.]", "", item.find(".price", first=True).text)
            )
            url: str = item.find("a.product-item-link", first=True).attrs.get("href")
            name: str = item.find("a.product-item-link", first=True).text

            if item.find("div.stock.unavailable"):
                print(name, "unavailable")
                continue

            name_mistakes = {
                "Reloader": "Reloder",
                "4350": "H4350",
                "CFE-223": "CFE223",
                "Ba9.5": "BA 9.5",
            }

            for key, value in name_mistakes.items():
                name = name.replace(key, value)

            self.propellant_list.append({"name": name, "price": price, "url": url})
