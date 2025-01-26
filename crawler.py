import os
from bs4 import BeautifulSoup

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
        url = p['href']
        price = product.find('p', class_='pricePerUnit').get_text(strip=True)

    
        products.append( {
            'name': name,
            'price': price,
            'url': url
        })
    return products

def process_html_files(directory):
    """
    Process all HTML files in a given directory and extract product details.
    
    Args:
        directory (str): Path to directory containing HTML files
    
    Returns:
        list: List of dictionaries with product details
    """
    
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            try:
                products = extract_product_details(file_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
            import csv
            with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'price', 'url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow(product)
            
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