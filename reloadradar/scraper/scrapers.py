# Standard Libraries
from dataclasses import dataclass
from re import sub

# Third Party Libraries
from requests_html import HTMLSession

# Django Libraries
from django.apps import apps

# First Party Libraries
from core.models import Link, Pricing


@dataclass
class Scraper:
    link: Link
    ready: bool = False

    def __post_init__(self):
        self.url = self.link.link_url
        self.product_type = apps.get_model("core", self.link.link_type)
        self.supplier = self.link.content_object

    def get_response(self):
        with HTMLSession() as session:
            self.response = session.get(self.url)
            self.ready = True

    def scrape(self):
        if not self.ready:
            self.get_response()

        getattr(self, self.product_type.__name__.lower())()


class SafariOutdoorScraper(Scraper):
    def propellant(self):
        all_propellants = [prop.name for prop in self.product_type.objects.all()]
        for item in self.response.html.find(".product.details.product-item-details"):
            _price = float(sub(r"[^\d.]", "", item.find(".price", first=True).text))
            _url = item.find("a.product-item-link", first=True).attrs.get("href")
            _name = item.find("a.product-item-link", first=True).text

            print(f"Parsing {_name=}")

            for prop in all_propellants:
                if prop in _name:
                    _propellant = self.product_type.objects.get(name=prop)

                    _last_price = _propellant.prices.last()

                    if not _last_price or (
                        _last_price and not _last_price.price == _price
                    ):
                        Pricing.objects.create(
                            content_object=_propellant,
                            price=_price,
                            supplier=self.supplier,
                            price_url=_url,
                        )


class ZimbiScraper(Scraper):
    def propellant(self):
        all_propellants = [prop.name for prop in self.product_type.objects.all()]
        for item in self.response.html.find(
            "a.woocommerce-LoopProduct-link.woocommerce-loop-product__link"
        ):
            _price = float(sub(r"[^\d.]", "", item.find(".price", first=True).text))
            _url = item.find("a.woocommerce-LoopProduct-link", first=True).attrs.get(
                "href"
            )
            _name = item.find("h2.woocommerce-loop-product__title", first=True).text

            print(f"Parsing {_name=}")

            found = False
            for prop in all_propellants:
                if prop in _name:
                    _propellant = self.product_type.objects.get(name=prop)

                    _last_price = _propellant.prices.filter(
                        supplier=self.supplier
                    ).last()

                    if not _last_price or (
                        _last_price and not _last_price.price == _price
                    ):
                        Pricing.objects.create(
                            content_object=_propellant,
                            price=_price,
                            supplier=self.supplier,
                            price_url=_url,
                        )

                    found = True

            if not found:
                print(f"{_name} not on Propellant List")
