from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import re
from enum import Enum


def extract_lozenge(soup, type):
    element = soup.select_one(f'li.lozenge.{type}')

    if element is None:
        return {'level': None, 'amount': None}
    
    # Check the specific class level
    # print(element['class'])
    level = None
    if 'high' in element['class']:
        level = NutritionLevel.HIGH
    elif 'medium' in element['class']:
        level = NutritionLevel.MEDIUM
    elif 'low' in element['class']:
        level = NutritionLevel.LOW
    
    amount_elems = element.find('div',{'class':'lozengeHeaderSection'}).find_all('p')
    if type == 'energy':
        for x in amount_elems:
            if x.get_text().endswith('kcal'):
                amount = x.get_text()
    else: 
        amount = amount_elems[-1].get_text()

    return {'level': level, 'amount': amount}

def parse_value(value_str):
    # Remove any non-numeric characters except decimal point
    numeric_str = re.sub(r'[^\d.]', '', value_str)
    return float(numeric_str) if numeric_str else 0.0

def extract_nutritional_values(soup):
    nutrition_table = soup.find('table', class_='nutritionTable')
    if nutrition_table is None:
        return NutritionalValues()
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

@dataclass(frozen=True, kw_only=True)
class NutritionalValues:
    Energy: float | None = None
    Fat: float | None= None
    Saturates: float | None= None
    Mono_unsaturates: float| None= None
    Polyunsaturates: float| None= None
    Carbohydrate: float| None= None
    Sugars: float| None= None
    Starch: float| None= None
    Fibre: float| None= None
    Protein: float| None = None
    Salt: float| None = None

@dataclass(frozen=True, kw_only=True)
class Product:
    sku: str
    name: str
    url: str
    price: str
    img_url: str
    description: str
    allegens: set[str]
    weight: int
    cals: float
    fat_level: NutritionLevel
    sat_level: NutritionLevel
    sugar_level: NutritionLevel
    salt_level: NutritionLevel
    rating: float | None
    Energy: float | None = None
    Fat: float | None= None
    Saturates: float | None= None
    Mono_unsaturates: float| None= None
    Polyunsaturates: float| None= None
    Carbohydrate: float| None= None
    Sugars: float| None= None
    Starch: float| None= None
    Fibre: float| None= None
    Protein: float| None = None
    Salt: float| None = None

  
    
# {'Energy': '484kcal', 'Fat': '26.9g', 'Saturates': '10.6g', 'Mono-unsaturates': '11.5g', 'Polyunsaturates': '4.8g', 'Carbohydrate': '40.2g', 'Sugars': '3.2g', 'Starch': '37.0g', 'Fibre': '3.7g', 'Protein': '18.4g', 'Salt': '1.65g'}

def download_html(url):
    print(f"processing: {url}")
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

            image_url = soup.find('img', {'class': 'pd__image'})['src']

            # print(image_url)
            sku = soup.find('span', {'id': 'productSKU'}).get_text()

            price = soup.find('span', {'data-testid' :'pd-retail-price'}).get_text()
            # print(sku)
            name = soup.find('h1').get_text(strip=True)
            description =soup.find('div', {'class':'pd__description'}).get_text(strip=True)
            # print(header)
            # print(description)
            cals = extract_lozenge(soup, 'energy')
            fat = extract_lozenge(soup, 'fat')
            sats = extract_lozenge(soup, 'saturates')
            sugars = extract_lozenge(soup, 'sugars')
            salt = extract_lozenge(soup, 'salt')
            print(cals)
            print(fat)
            print(sats)
            print(sugars)
            print(salt)

            allegens_elements = soup.select('div.productText strong')
            allegens = set()
            for a in allegens_elements:
                text = a.get_text()
                if text.strip() == 'INGREDIENTS:' or 'Information' in text.strip():
                    continue
                allegens.add(text)

            # print(allegens)

            match_1 =  re.search(r'100g\s?(?:\s*\(as sold\))?:\s?(?:Energy)?\s?\d+\.?\d*\s?kJ/\s?(\d+\.?\d*)\s?kcal',html_content)
            match_2 =  re.search(r'100ml\s?(?:\s*\(as sold\))?:\s?(?:Energy)?\s?\d+\.?\d*\s?kJ/\s?(\d+\.?\d*)\s?kcal',html_content)
            # match_4 = re.search(r'Energy per 100g (as sold): 1577kJ/374kcal')
            kcal_value = None
            if match_1:
                kcal_value = float(match_1.group(1))
                # print(f'Extracted kcal value: {kcal_value}')
                # weight = ( int(cals['amount'].removesuffix('kcal')) / kcal_value) * 100
                # print(f"{weight}g") 
            elif match_2:
                kcal_value = float(match_2.group(1))
  
            if kcal_value is not None and cals['amount'] is not None:
                print(f'Extracted kcal value: {kcal_value}')
                print(float(cals['amount'].removesuffix('kcal')))
                weight = ( float(cals['amount'].removesuffix('kcal')) / kcal_value) * 100
                print(f"weight {weight}")
            else:
                weight = None
            rating_elem = soup.select_one('div.pd-reviews__summary__text')
            if rating_elem is not None:
                rating = float(rating_elem.get_text().strip().split(' ')[0])
            else:
                rating = None
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
        sku=sku,
        name=name,
        url=url,
        price=price,
        img_url=image_url,
        description=description,
        allegens=allegens,
        weight=weight,
        cals=cals['amount'],
        fat_level=fat['level'],
        sat_level=sats['level'],
        sugar_level=sugars['level'],
        salt_level=salt['level'],
        rating=rating,
        **asdict(nutritional_values)   
    )


# URL of the product page
# url = "https://www.sainsburys.co.uk/gol-ui/product/sainsburys-cheese---onion-sandwich"
# url = "https://www.sainsburys.co.uk/shop/gb/groceries/product/details/coca-cola--diet-500ml"
# url = "https://www.sainsburys.co.uk/shop/gb/groceries/product/details/trek-power-biscoff-protein-bar-55g"
# product = download_html(url)
# print(product)