from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
from enum import Enum


def extract_lozenge(soup, type):
    element = soup.select_one(f'li.lozenge.{type}')

    # Check the specific class level
    print(element['class'])
    level = None
    if 'high' in element['class']:
        level = NutritionLevel.HIGH
    elif 'medium' in element['class']:
        level = NutritionLevel.MEDIUM
    elif 'low' in element['class']:
        level = NutritionLevel.LOW
    
    amount = element.find('div',{'class':'lozengeHeaderSection'}).find_all('p')[-1].get_text()
    return {'level': level, 'amount': amount}

def parse_value(value_str):
    # Remove any non-numeric characters except decimal point
    numeric_str = re.sub(r'[^\d.]', '', value_str)
    return float(numeric_str) if numeric_str else 0.0

def extract_nutritional_values(soup):
    nutrition_table = soup.find('table', class_='nutritionTable')
    
    nutrition_dict = {}
    rows = nutrition_table.find_all('tr', class_=['tableRow0', 'tableRow1'])
    values={}
    for row in rows:
        nutrient = row.find('th', class_='rowHeader')
        if nutrient is None:
            nutrient = 'Energy'
        else:
            nutrient = nutrient.text.strip()
         # Replace hyphen with underscore for valid Python attribute name
        nutrient_key = nutrient.replace('-', '_')
        per_pack_value = row.find_all('td')[1].text.strip()
        values[nutrient_key] = parse_value(per_pack_value)


    return NutritionalValues(**values)

class NutritionLevel(Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

@dataclass
class NutritionalValues:
    Energy: float
    Fat: float
    Saturates: float
    Mono_unsaturates: float
    Polyunsaturates: float
    Carbohydrate: float
    Sugars: float
    Starch: float
    Fibre: float
    Protein: float
    Salt: float

@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    img_url: str
    description: str
    allegens: set[str]
    weight: int
    fat_level: NutritionLevel
    sat_level: NutritionLevel
    sugar_level: NutritionLevel
    salt_level: NutritionLevel
    rating: float
    nutritional_values: NutritionalValues
    
# {'Energy': '484kcal', 'Fat': '26.9g', 'Saturates': '10.6g', 'Mono-unsaturates': '11.5g', 'Polyunsaturates': '4.8g', 'Carbohydrate': '40.2g', 'Sugars': '3.2g', 'Starch': '37.0g', 'Fibre': '3.7g', 'Protein': '18.4g', 'Salt': '1.65g'}

def download_html(url):
    with sync_playwright() as p:
        # Launch a browser (headless or visible)
        browser = p.chromium.launch(headless=False)  # Set headless=True for faster, invisible scraping
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Navigate to the page
            page.goto(url, timeout=60000)  # Increase timeout if needed

            # Wait for the page to fully load
            page.wait_for_selector("h1", timeout=10000)

            # Get the HTML content
            html_content = page.content()

            soup = BeautifulSoup(html_content, 'html.parser')

            image_url = soup.find('img', {'class': 'pd__image pd__image__nocursor'})['src']
            # print(image_url)
            sku = soup.find('span', {'id': 'productSKU'}).get_text()
            # print(sku)
            header = soup.find('h1').get_text(strip=True)
            description =soup.find('div', {'class':'pd__description'}).get_text(strip=True)
            # print(header)
            # print(description)
            cals = extract_lozenge(soup, 'energy')
            fat = extract_lozenge(soup, 'fat')
            sats = extract_lozenge(soup, 'saturates')
            sugars = extract_lozenge(soup, 'sugars')
            salt = extract_lozenge(soup, 'salt')
            # print(cals)
            # print(fat)
            # print(sats)
            # print(sugars)
            # print(salt)

            allegens_elements = soup.select('div.productText strong')
            allegens = set()
            for a in allegens_elements:
                text = a.get_text()
                if text.strip() == 'INGREDIENTS:' or text.strip() =='Table of Nutritional Information':
                    continue
                allegens.add(text)

            # print(allegens)

            match = re.search(r'Typical Values per 100g : Energy 1217 kJ/(\d+)\s?kcal',html_content)
            kcal_value = int(match.group(1))
            # print(f'Extracted kcal value: {kcal_value}')
            weight = ( int(cals['amount'].removesuffix('kcal')) / kcal_value) * 100
            # print(f"{weight}g") 

            rating = soup.select_one('div.pd-reviews__summary__text').get_text().strip().split(' ')[0]
            # print(rating)

            nutritional_values = extract_nutritional_values(soup)
            # print(nutritional_values)
            # TODO: most ingredients

            # # Save the HTML to a file
            # with open(f"sainsburys_product_page.html", "w", encoding="utf-8") as file:
            #     file.write(html_content)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
    return Product(
        sku,
        header,
        image_url,
        description,
        allegens,
        weight,
        fat['level'],
        sats['level'],
        sugars['level'],
        salt['level'],
        float(rating),
        nutritional_values
    )


# URL of the product page
url = "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-cheese---onion-sandwich"
product = download_html(url)
print(product)