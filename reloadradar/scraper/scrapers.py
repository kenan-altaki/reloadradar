# Standard Libraries
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from re import sub

# Third Party Libraries
from requests_html import HTMLSession

# Django Libraries
from django.apps import apps
from django.utils import timezone

# First Party Libraries
from core.models import Link, Manufacturer, Pricing


@dataclass
class Scraper:
    link: Link
    ready: bool = False

    def __post_init__(self):
        self.url = self.link.link_url
        self.product_model = apps.get_model("core", self.link.link_type)
        self.product_name = self.product_model.__name__.lower()
        self.supplier = self.link.content_object
        print(f"{self} completed PostInit.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__} for {self.product_name} at ({self.url})"

    def get_response(self):
        with HTMLSession() as session:
            self.response = session.get(self.url)

        # Parse the scraped list into an attribute
        getattr(self, f"parse_{self.product_name}_list")(),
        self.ready = True
        print(f"{self} got {self.response}, {self.ready=}")

    def scrape(self):
        if not self.ready:
            self.get_response()

        getattr(self, "process_" + self.product_name + "_list")()

    def find_product(self, name: str):
        for _man in Manufacturer.objects.all():
            if _man.name.lower() in name.lower():
                manufacturer = _man
                break

        if manufacturer:
            for _prod in getattr(manufacturer, self.product_name + "s").all():
                if _prod.name.lower() in name.lower():
                    return _prod
        else:
            for _prod in self.product_model.objects.all():
                if _prod.name.lower() in name.lower():
                    return _prod

        return None

    def get_last_pricing(self, product):
        return product.prices.filter(supplier=self.supplier).last()

    def export_list_to_csv(self):
        if not self.ready:
            self.get_response()

        base_location = Path("./reloadradar/scraper/output")
        file_location = base_location / self.product_name / str(self.supplier.id)
        file_path = file_location / f"{timezone.now().strftime('%Y-%m-%d-%H')}.csv"

        os.makedirs(file_location, exist_ok=True)

        with open(file_path, "a", newline="") as csv_file:
            fieldnames = ["name", "price", "url"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if os.path.getsize(file_path) == 0:
                writer.writeheader()

            for data in getattr(self, self.product_name + "_list"):
                writer.writerow(data)

    def import_last_csv(self):
        base_location = Path("./reloadradar/scraper/output")
        file_location = base_location / self.product_name / str(self.supplier.id)

        files = os.listdir(file_location)
        file_paths = [
            os.path.join(file_location, file)
            for file in files
            if os.path.isfile(os.path.join(file_location, file))
        ]
        file_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        if file_paths:
            last_updated_file = file_paths[0]
            print("Last updated file:", last_updated_file)
            data_list = []

            # Open and read the CSV file
            with open(last_updated_file) as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data_list.append(row)

            setattr(self, self.product_name + "_list", data_list)
            print(f"Populated {len(getattr(self, self.product_name + '_list'))} rows")
            self.ready = True
        else:
            print("No files found in the directory")


class SafariOutdoorScraper(Scraper):
    def parse_propellant_list(self):
        self.propellant_list = []
        for item in self.response.html.find(".product.details.product-item-details"):
            price: float = float(
                sub(r"[^\d.]", "", item.find(".price", first=True).text)
            )
            url: str = item.find("a.product-item-link", first=True).attrs.get("href")
            name: str = item.find("a.product-item-link", first=True).text

            self.propellant_list.append({"name": name, "price": price, "url": url})

    def process_propellant_list(self):
        for name, price, url in self.propellant_list:
            print(f"Processing {name=}")

            propellant = self.find_product(name)

            if not propellant:
                print(f"Unable to match {name=} to anything")
                propellant_name = input("What is the name of this item")
                propellant_weight = input("What is the weight of this item")
                propellant_manufacturer = input("Who is the manufacturer")

                for _prop in self.product_model.objects.all():
                    if _prop.name.lower() in propellant_name.lower():
                        propellant = _prop
                        break
                    else:
                        propellant = self.product_model.create(
                            name=propellant_name,
                            weight=propellant_weight,
                            manufacturer=Manufacturer.objects.get(
                                name__icontains=propellant_manufacturer
                            ),
                        )

            if not propellant:
                raise ValueError(f"{name} cannot be matched")

            last_price = self.get_last_pricing(propellant)

            if not last_price or (last_price and not last_price.price == price):
                Pricing.objects.create(
                    content_object=propellant,
                    price=price,
                    supplier=self.supplier,
                    price_url=url,
                )


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

    def process_propellant_list(self):
        for name, price, url in self.propellant_list:
            print(f"Processing {name=}")

            propellant = self.find_product(name)

            if not propellant:
                print(f"Unable to match {name=} to anything")
                propellant_name = input(
                    "What is the name of this item? (leave blank to skip): "
                )
                if not propellant_name:
                    continue

                propellant_weight = input("What is the weight of this item? ")
                propellant_manufacturer = input("Who is the manufacturer? ")

                for _prop in self.product_model.objects.all():
                    if _prop.name.lower() in propellant_name.lower():
                        propellant = _prop
                        break
                    else:
                        propellant = self.product_model.objects.create(
                            name=propellant_name,
                            weight=propellant_weight,
                            manufacturer=Manufacturer.objects.get(
                                name__icontains=propellant_manufacturer
                            ),
                        )

            if not propellant:
                raise ValueError(f"{name} cannot be matched")

            last_price = self.get_last_pricing(propellant)

            if not last_price or (last_price and not last_price.price == price):
                Pricing.objects.create(
                    content_object=propellant,
                    price=price,
                    supplier=self.supplier,
                    price_url=url,
                )
