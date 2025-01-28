import csv
import json
from pathlib import Path

def csv_to_js(file: str):

    # Read CSV data
    with open(f"{file}.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Convert numeric strings to numbers
    for row in data:
        for key, value in row.items():
            if value.replace('.', '').isdigit():
                row[key] = float(value) if '.' in value else int(value)
            elif value.lower() in ['true', 'false']:
                row[key] = value.lower() == 'true'
            elif len(value) == 0:
                row[key] = None
    
    # Generate JavaScript code with different formats
    js_array = f"const {file} = [\n"
    
    # Generate array format with individual objects
    for row in data:
        js_array += f"  {json.dumps(row)},\n"
    js_array += "];"
    
    # Write all formats to file
    with open(f"{file}.js", 'w', encoding='utf-8') as f:
        f.write(js_array)

if __name__ == "__main__":
    files = ['mains', 'sides','drinks']
    
    for file in files:
        print(f"processing: {file}")
        csv_to_js(file)
