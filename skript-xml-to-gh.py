import requests
import xml.etree.ElementTree as ET
import os

# URL feedu
url = "https://www.goldpc.cz/export/productsComplete.xml?patternId=-5&partnerId=3&hash=b6980705f27e462dc4b2da6beeb8f8b5b7746b5d927f5eaf5692ddc19d8cf3d0&exactCode=10749&stockState=1&defaultCategoryId=792"

# stáhnout feed
print("Stahuji feed...")
response = requests.get(url)
response.encoding = "utf-8"

if response.status_code != 200:
    raise Exception("Nepodařilo se stáhnout XML feed")

root = ET.fromstring(response.text)

# vytvořit nový XML root
new_root = ET.Element("SHOP")

# seznam povolených tagů
allowed_tags = {
    "NAME", "SHORT_DESCRIPTION", "DESCRIPTION", "MANUFACTURER", "WARRANTY",
    "CATEGORIES", "IMAGES", "INFORMATION_PARAMETERS", "SURCHARGE_PARAMETERS",
    "CODE", "PRICE_VAT", "PURCHASE_PRICE", "STOCK"
}

for item in root.findall("SHOPITEM"):
    new_item = ET.Element("SHOPITEM")
    for child in item:
        if child.tag in allowed_tags:
            new_item.append(child)
    new_root.append(new_item)

# cesta k výstupu (uloží se do repa)
output_file = "clean_products.xml"
tree = ET.ElementTree(new_root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)

print(f"Hotovo! Vyčištěný feed uložen do: {output_file}")
