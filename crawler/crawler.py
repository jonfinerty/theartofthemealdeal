from dataclasses import fields
import os
import csv
from pathlib import Path
from bs4 import BeautifulSoup

from crawler.details import Product, download_html

def extract_product_details(html_file):
    """
    Extract product name, price, and URL from a Sainsbury's product HTML file.
    
    Args:
        html_file (str): Path to the HTML file
    
    Returns:
        dict: Dictionary containing product details
    """
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse the HTML
    soup = BeautifulSoup(content, 'html.parser')
    # Extract product name
    name_elem = soup.find_all('div', {'class':'product'})
    products =[]
    for product in name_elem:
        p = product.find('h3').find('a')
        name = ' '.join(p.get_text(strip=True).split())
        print(name)
        url = p['href']
        
        file_exists = os.path.exists("product.csv")
        if file_exists:
            with open("product.csv", 'r') as file:
                if url in file.read():
                    print("Already scaped")
                    continue

        product = download_html(url)
        # price = product.find('p', class_='pricePerUnit').get_text(strip=True)

        products.append(product)
    
        dataclass_to_csv(product, "product.csv")
        # products.append( {
        #     'name': name,
        #     'price': price,
        #     'url': url
        # })
    return products


def dataclass_to_csv(product: Product, filename: str):
    """
    Write a list of dataclass objects to a CSV file, appending if exists.
    
    :param products: List of Product dataclass instances
    :param filename: Name of the output CSV file
    """
    field_names = [field.name for field in fields(Product)]
    
    # Check if file exists to determine write mode
    file_exists = os.path.exists(filename)
    # if not file_exists:
    #     print("hsdg")
    #     # open(filename, 'w').close()
    #     Path(filename).touch()

    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=field_names)
        
        # Write header only if file is new
        if not file_exists:
            csv_writer.writeheader()
        
        csv_writer.writerow(vars(product))


def process_html_files(directory):
    """
    Process all HTML files in a given directory and extract product details.
    
    Args:
        directory (str): Path to directory containing HTML files
    
    Returns:
        list: List of dictionaries with product details
    """
    
    for filename in os.listdir(directory):
        if filename.endswith('drinks.html'):
            file_path = os.path.join(directory, filename)
            try:
                products = extract_product_details(file_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return products

# Example usage
def main():
    directory = '.'
    results = process_html_files(directory)
    
    # Optional: Write results to a CSV
    import csv
    with open('product_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'price', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in results:
            writer.writerow(product)

if __name__ == '__main__':
    main()