# Standard Libraries
import csv
import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from re import sub

# Third Party Libraries
from requests_html import HTMLSession

# Django Libraries
from django.apps import apps
from django.utils import timezone

# First Party Libraries
from core.models import Link, Manufacturer, Pricing, Propellant


@dataclass
class Scraper:
    link: Link
    ready: bool = False

    def __post_init__(self):
        self.url = self.link.link_url
        self.product_model = apps.get_model("core", self.link.link_type)
        self.product_name = self.product_model.__name__.lower()
        self.supplier = self.link.content_object

        self.base_location = Path("./reloadradar/scraper/output")
        self.file_location = (
            self.base_location / self.product_name / str(self.supplier.id)
        )

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
        manufacturer = None
        for _man in Manufacturer.objects.all():
            if _man.name.lower() in name.lower():
                manufacturer = _man
                print(f"{manufacturer=} found for {name}")
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

        file_path = self.file_location / f"{timezone.now().strftime('%Y-%m-%d-%H')}.csv"
        os.makedirs(self.file_location, exist_ok=True)
        with open(file_path, "a", newline="") as csv_file:
            fieldnames = ["name", "price", "url"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if os.path.getsize(file_path) == 0:
                writer.writeheader()

            for data in getattr(self, self.product_name + "_list"):
                writer.writerow(data)

    def import_last_csv(self):
        files = os.listdir(self.file_location)
        file_paths = [
            os.path.join(self.file_location, file)
            for file in files
            if "error" not in file
            and os.path.isfile(os.path.join(self.file_location, file))
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

    def import_new_propellants(self):
        files = os.listdir(self.file_location)
        file_paths = [
            os.path.join(self.file_location, file)
            for file in files
            if "propellants" in file
            and os.path.isfile(os.path.join(self.file_location, file))
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

            for item in data_list:
                Propellant.objects.get_or_create(
                    name=item["name"],
                    weight=item["weight"] or 454,
                    manufacturer=Manufacturer.objects.get(
                        name__icontains=item["manufacturer"]
                    ),
                )
        else:
            print("No files found in the directory")

    def log_to_error_file(self, line: dict):
        file_path = (
            self.file_location / f"{timezone.now().strftime('%Y-%m-%d-%H')}-errors.csv"
        )
        os.makedirs(self.file_location, exist_ok=True)
        with open(file_path, "a", newline="") as csv_file:
            fieldnames = line.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if os.path.getsize(file_path) == 0:
                writer.writeheader()

            writer.writerow(line)

    def process_propellant_list(self):
        for item in self.propellant_list:
            print(f"Processing {item['name']=}")

            propellant = self.find_product(item["name"])

            if not propellant:
                print(f"Cannot find {item=}")
                self.log_to_error_file(item)
                continue

            last_price = self.get_last_pricing(propellant)

            if not last_price or (
                last_price and not last_price.price == Decimal(item["price"])
            ):
                print(f"Capturing new {item['price']=} for {propellant=}")
                Pricing.objects.create(
                    content_object=propellant,
                    price=item["price"],
                    supplier=self.supplier,
                    price_url=item["url"],
                )


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
