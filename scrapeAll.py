import re
import fitz  # PyMuPDF
from decimal import Decimal
import json
from botoTest import get_dynamodb


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

    for page_num in range(len(document)):
        page = document[page_num]
        text = page.get_text("text")
        lines = text.split("\n")
        current_customer_id = None

        for line in lines:
            # Check for customer ID
            customer_id_match = customer_id_pattern.match(line)
            if customer_id_match:
                current_customer_id = customer_id_match.group(1)
                customer_tokens[current_customer_id] = []

            # Check for tokens
            token_matches = token_pattern.findall(line)
            for match in token_matches:
                token, value = match
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
    pdfs = [
        "schedules/amendedScheduleF1.pdf",
        # "schedules/amendedScheduleF2.pdf",
        # "schedules/amendedScheduleF3.pdf",
        # "schedules/amendedScheduleF4.pdf",
        # "schedules/amendedScheduleF5.pdf",
        # "schedules/amendedScheduleF6.pdf",
        # "schedules/amendedScheduleF7.pdf",
        # "schedules/amendedScheduleF8.pdf",
        # "schedules/amendedScheduleF9.pdf",
        # "schedules/amendedScheduleF10.pdf",
        # "schedules/amendedScheduleF11.pdf",
        # "schedules/amendedScheduleF12.pdf",
        # "schedules/amendedScheduleF13.pdf",
        # "schedules/amendedScheduleF14.pdf",
        # "schedules/amendedScheduleF15.pdf",
        # "schedules/amendedScheduleF16.pdf",
        # "schedules/amendedScheduleF17.pdf",
        # "schedules/amendedScheduleF18.pdf",
        # "schedules/amendedScheduleF19.pdf",
        # "schedules/amendedScheduleF20.pdf",
        # "schedules/amendedScheduleF21.pdf",
        # "schedules/amendedScheduleWF1.pdf",
        # "schedules/amendedScheduleWF2.pdf",
        # "schedules/amendedScheduleWF3.pdf",
        # "schedules/amendedScheduleWF4.pdf",
        # "schedules/amendedScheduleWF5.pdf",
        # "schedules/amendedScheduleWF6.pdf",
        # "schedules/amendedScheduleWF7.pdf",
        # "schedules/amendedScheduleWF8.pdf",
    ]

    table = get_dynamodb()

    for pdf_path in pdfs:
        customer_tokens = process_pdf(pdf_path)
        customer_tokens = enrich_tokens_with_prices(customer_tokens)

        for customer_id, tokens in customer_tokens.items():
            # Sort tokens by value, high to low
            tokens = sorted(tokens, key=lambda k: k["value"], reverse=True)
            # Put the item in the table
            print(f"Putting item: {customer_id} with tokens: {tokens}")
            # table.put_item(Item={"customerId": customer_id, "tokens": tokens})


# Example usage:
if __name__ == "__main__":
    main()
