
import requests
import xml.etree.ElementTree as ET
import time

# --- Konfigurace ---
url = "https://www.goldpc.cz/export/productsComplete.xml?patternId=-5&partnerId=3&hash=b6980705f27e462dc4b2da6beeb8f8b5b7746b5d927f5eaf5692ddc19d8cf3d0&stockState=1&defaultCategoryId=864"
output_file = "gpcz_lcd.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; GitHub Actions)"
}

# --- Stáhnout feed s retry ---
for attempt in range(3):
    try:
        print("Stahuji feed...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        xml_content = response.content
        print("Hotovo!")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} selhal: {e}")
        time.sleep(5)
else:
    raise Exception("Nepodařilo se stáhnout XML feed po 3 pokusech.")

# --- Parsování XML ---
tree = ET.ElementTree(ET.fromstring(xml_content))
root = tree.getroot()

# --- Funkce pro vyčištění jednoho SHOPITEM ---
def clean_shopitem(item):
    keep_tags = [
        "NAME", "SHORT_DESCRIPTION", "DESCRIPTION", "MANUFACTURER", "WARRANTY",
        "CATEGORIES", "IMAGES", "INFORMATION_PARAMETERS", "SURCHARGE_PARAMETERS",
        "CODE", "PRICE_VAT", "STOCK", "PRICE_VAT_B2B", "VAT"
    ]
    for child in list(item):
        if child.tag not in keep_tags:
            item.remove(child)

    # --- Úprava CATEGORIES: odstranit všechny <CATEGORY>, ponechat jen <DEFAULT_CATEGORY> ---
    categories = item.find("CATEGORIES")
    if categories is not None:
        for cat in list(categories):
            if cat.tag != "DEFAULT_CATEGORY":
                categories.remove(cat)

    # --- Odstranit konkrétně INCLUDING_VAT a REQUIRED_VALUE ---
    for elem in item.iter():
        for unwanted_tag in ["INCLUDING_VAT", "REQUIRED_VALUE", "LOCATION", "MINIMAL_AMOUNT", "MAXIMAL_AMOUNT"]:
            for child in list(elem):
                if child.tag == unwanted_tag:
                    elem.remove(child)
    
    return item

import xml.etree.ElementTree as ET

# projdeme všechny SHOPITEM elementy
for item in root.findall("SHOPITEM"):
    # přečteme původní ceny
    price_vat = float(item.find("PRICE_VAT").text)
    price_purchase_elem = item.find("PURCHASE_PRICE")
    price_purchase = float(price_purchase_elem.text) if price_purchase_elem is not None else 0

    # vytvoříme PRICE_VAT_B2B
    price_vat_b2b = ((price_vat + price_vat + price_purchase) / 3) * 1.01
    b2b_elem = ET.Element("PRICE_VAT_B2B")
    b2b_elem.text = str(round(price_vat_b2b))

    # místo item.append(b2b_elem) použij:
    price_vat_elem = item.find("PRICE_VAT")
    idx = list(item).index(price_vat_elem)
    item.insert(idx + 1, b2b_elem)   # vloží hned za PRICE_VAT

    # odstraníme PRICE_PURCHASE z XML
    if price_purchase_elem is not None:
        item.remove(price_purchase_elem)

# --- Zpracování všech SHOPITEM ---
for shopitem in root.findall("SHOPITEM"):
    clean_shopitem(shopitem)

# --- Uložení vyčištěného feedu ---
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Vyčištěný feed uložen do: {output_file}")









