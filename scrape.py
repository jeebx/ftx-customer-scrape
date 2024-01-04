import fitz  # PyMuPDF
import re
from decimal import Decimal
import json

def extract_tokens_from_pdf(pdf_path, customer_id):
    # Open the PDF
    document = fitz.open(pdf_path)
    tokens = {}

    # Search each page for the customer ID
    # page = document[0]
    print(len(document))
    for page_num in range(len(document)):
        page = document[page_num]
    
        text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')

        # Check if the customer ID is in the lines
        for i in range(len(lines)):
            if customer_id in lines[i]:
                # If the customer ID is found, parse the next line to extract the tokens
                tokens = parse_line_to_tokens(lines[i+1])
                break

        # document.close()
    return json.dumps(tokens, indent=4)

def parse_line_to_tokens(line):
    # Split the line into parts by comma
    print(line)
    parts = line.split(',')
    tokens = {}
    for part in parts:
        # Split each part into token and value
        token, value = part.split('[')
        value = value.rstrip(']')
        tokens[token] = value
    return tokens

# Example usage:
json_data = extract_tokens_from_pdf('cSchedule.pdf', '00066981')
print(json_data)