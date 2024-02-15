import re
import fitz  # PyMuPDF
from decimal import Decimal
import json
from botoTest import get_dynamodb
import concurrent.futures
from concurrent.futures import as_completed
import argparse
from tqdm import tqdm


def parse_tokens(text_block):
    # Find all token-value pairs
    pattern = re.compile(r"([A-Z0-9-]+)\[(-?[\d.]+)\]")
    matches = pattern.findall(text_block)

    tokens = {}
    for match in matches:
        token, value = match
        # Convert value to Decimal before adding to dictionary
        tokens[token] = Decimal(value)

    return tokens


def extract_customer_tokens(document):
    customer_tokens = {}
    customer_id_pattern = re.compile(r"(\d{8})")
    token_pattern = re.compile(r"([A-Z0-9-]+)\[(-?[\d.]+)\]")

    # Define the horizontal bounds of the third column (you need to adjust these values based on the actual PDF layout)
    first_column_start = 0  # Example starting x-coordinate for the third column
    third_column_end = 500  # Example ending x-coordinate for the third column

    for page_num in range(len(document)):
        page = document[page_num]
        text_dicts = page.get_text("dict")["blocks"]
        current_customer_id = None

        for block in text_dicts:
            if not block["type"] == 0:  # Skip non-text blocks
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    # Check if the text is within the horizontal bounds of the third column
                    if first_column_start <= span["bbox"][0] <= third_column_end:
                        text = span["text"]
                        # Check for customer ID
                        customer_id_match = customer_id_pattern.match(text)

                        if customer_id_match:
                            current_customer_id = customer_id_match.group(1)

                            # if current_customer_id == specific_customer_id:
                            #     continue
                            customer_tokens[current_customer_id] = []

                        # Check for tokens
                        token_matches = token_pattern.findall(text)
                        for match in token_matches:
                            token, value = match
                            if current_customer_id is not None:
                                customer_tokens[current_customer_id].append(
                                    {"name": token, "amount": Decimal(value)}
                                )
    return customer_tokens


def process_pdf(pdf_path):
    document = fitz.open(pdf_path)
    customer_tokens = extract_customer_tokens(document)
    document.close()
    return customer_tokens


def enrich_tokens_with_prices(customer_tokens):
    with open("coinPrices.json") as f:
        coin_prices = json.load(f)

    for customer_id, tokens in customer_tokens.items():
        for token_obj in tokens:
            token_name = token_obj["name"]
            if token_name in coin_prices:
                price = Decimal(coin_prices[token_name].replace(",", ""))
                token_obj["price"] = price
                token_obj["value"] = round(token_obj["amount"] * price, 2)
            else:
                token_obj["price"] = 0
                token_obj["value"] = 0

    return customer_tokens


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("start", type=int, help="Start index for PDFs to process")
    # parser.add_argument("end", type=int, help="End index for PDFs to process")
    # args = parser.parse_args()

    pdfs = [
        "schedules/1748.pdf",
        "schedules/1753.pdf",
    ]

    # pdfs_to_process = pdfs[args.start : args.end]

    table = get_dynamodb()

    def process_and_put(pdf_path):
        customer_tokens = process_pdf(pdf_path)
        customer_tokens = enrich_tokens_with_prices(customer_tokens)

        for customer_id, tokens in tqdm(customer_tokens.items(), desc="Putting items"):
            # Sort tokens by value, high to low
            tokens = sorted(tokens, key=lambda k: k["value"], reverse=True)
            # Put the item in the table
            table.put_item(Item={"customerId": int(customer_id), "tokens": tokens})

        # return customer_id

    process_and_put(pdfs[1])
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = [
    #         executor.submit(process_and_put, pdf_path) for pdf_path in pdfs_to_process
    #     ]

    #     for future in tqdm(
    #         as_completed(futures), total=len(futures), desc="Processing customers"
    #     ):
    #         customer_id = future.result()


# Example usage:
if __name__ == "__main__":
    main()
