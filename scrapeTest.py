import os
import fitz  # PyMuPDF
import re
from decimal import Decimal
import json

# bring in table from botoTest.py
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


def extract_tokens_from_pdf():
    # Check if the customerID is in the EU range
    # ranges = [
    #     # (range(9, 286601), "schedules/amendedScheduleEU.pdf"),
    #     # Define all the US ranges with their respective PDF paths
    #     (range(0, 286601), "schedules/amendedScheduleF1.pdf"),
    #     (range(286601, 453839), "schedules/amendedScheduleF2.pdf"),
    #     (range(453848, 601234), "schedules/amendedScheduleF3.pdf"),
    #     (range(601235, 819052), "schedules/amendedScheduleF4.pdf"),
    #     (range(819052, 1051993), "schedules/amendedScheduleF5.pdf"),
    #     (range(1051994, 1271651), "schedules/amendedScheduleF6.pdf"),
    #     (range(1271651, 1541267), "schedules/amendedScheduleF7.pdf"),
    #     (range(1541277, 1767135), "schedules/amendedScheduleF8.pdf"),
    #     (range(1767141, 1977627), "schedules/amendedScheduleF9.pdf"),
    #     (range(1977627, 2206060), "schedules/amendedScheduleF10.pdf"),
    #     (range(2206060, 2498446), "schedules/amendedScheduleF11.pdf"),
    #     (range(2498449, 2760809), "schedules/amendedScheduleF12.pdf"),
    #     (range(2760809, 3026618), "schedules/amendedScheduleF13.pdf"),
    #     (range(3026626, 3304078), "schedules/amendedScheduleF14.pdf"),
    #     (range(3304080, 3598805), "schedules/amendedScheduleF15.pdf"),
    #     (range(3598805, 4215164), "schedules/amendedScheduleF16.pdf"),
    #     (range(4215165, 4644862), "schedules/amendedScheduleF17.pdf"),
    #     (range(4644862, 4988545), "schedules/amendedScheduleF18.pdf"),
    #     (range(4988556, 6299342), "schedules/amendedScheduleF19.pdf"),
    #     (range(6299344, 7086318), "schedules/amendedScheduleF20.pdf"),
    #     (range(7076319, 7187420), "schedules/amendedScheduleF21.pdf"),
    #     (range(7299572, 7438307), "schedules/amendedScheduleWF1.pdf"),
    #     (range(7438308, 7767508), "schedules/amendedScheduleWF2.pdf"),
    #     (range(7767517, 8225147), "schedules/amendedScheduleWF3.pdf"),
    #     (range(8225148, 8856984), "schedules/amendedScheduleWF4.pdf"),
    #     (range(8856985, 9120591), "schedules/amendedScheduleWF5.pdf"),
    #     (range(9120597, 9444251), "schedules/amendedScheduleWF6.pdf"),
    #     # (range(9444252, 10023695), "schedules/amendedScheduleWF7.pdf"),
    #     # (range(10023698, 10037881), "schedules/amendedScheduleWF8.pdf"),
    # ]

    pdfs = [
        "schedules/amendedScheduleF1.pdf",
        "schedules/amendedScheduleF2.pdf",
        "schedules/amendedScheduleF3.pdf",
        "schedules/amendedScheduleF4.pdf",
        "schedules/amendedScheduleF5.pdf",
        "schedules/amendedScheduleF6.pdf",
        "schedules/amendedScheduleF7.pdf",
        "schedules/amendedScheduleF8.pdf",
        "schedules/amendedScheduleF9.pdf",
        "schedules/amendedScheduleF10.pdf",
        "schedules/amendedScheduleF11.pdf",
        "schedules/amendedScheduleF12.pdf",
        "schedules/amendedScheduleF13.pdf",
        "schedules/amendedScheduleF14.pdf",
        "schedules/amendedScheduleF15.pdf",
        "schedules/amendedScheduleF16.pdf",
        "schedules/amendedScheduleF17.pdf",
        "schedules/amendedScheduleF18.pdf",
        "schedules/amendedScheduleF19.pdf",
        "schedules/amendedScheduleF20.pdf",
        "schedules/amendedScheduleF21.pdf",
        "schedules/amendedScheduleWF1.pdf",
        "schedules/amendedScheduleWF2.pdf",
        "schedules/amendedScheduleWF3.pdf",
        "schedules/amendedScheduleWF4.pdf",
        "schedules/amendedScheduleWF5.pdf",
        "schedules/amendedScheduleWF6.pdf",
        "schedules/amendedScheduleWF7.pdf",
        "schedules/amendedScheduleWF8.pdf",
    ]

    # customer_id_num = int(customer_id)
    # pdf_path = None
    # for id_range, path in ranges:
    #     if customer_id_num in id_range:
    #         pdf_path = path
    #         break

    # if not pdf_path:
    #     return {}

    # Open the PDF
    for pdf_path in pdfs:
        document = fitz.open(pdf_path)

        # Search each page for the customer ID
        for page_num in range(len(document)):
            page = document[page_num]
            text = page.get_text("text")
            # empty tokens dict and empty customer_id
            tokens = {}
            customer_id = None
            # Split the text by lines and iterate through them
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if re.match(r"^\d{8}$", line):
                    # Customer ID found, store it
                    print(line)
                    customer_id = line
                    break
                print(
                    f"Customer ID {customer_id} found on page: {page_num + 1} of document: {pdf_path}"
                )
                # Collect all subsequent lines until the next customer ID is found
                for token_line in lines[i + 1 :]:
                    if re.match(r"^\d{8}$", token_line):
                        # Next customer ID found, stop processing
                        break
                    tokens.update(parse_tokens(token_line))

            token_list = []
            with open("coinPrices.json") as f:
                coin_prices = json.load(f)
            for token in tokens:
                token_obj = {}
                if token in coin_prices:
                    token_obj = {
                        "name": token,
                        "amount": tokens[token],
                        "price": Decimal(coin_prices[token].replace(",", "")),
                        "value": round(
                            Decimal(tokens[token])
                            * Decimal(coin_prices[token].replace(",", "")),
                            2,
                        ),
                    }
                else:
                    token_obj = {
                        "name": token,
                        "amount": tokens[token],
                        "price": 0,
                        "value": 0,
                    }
                token_list.append(token_obj)
            # sort token list by the obj.value high to low
            token_list = sorted(token_list, key=lambda k: k["value"], reverse=True)
            return {"tokens": token_list, "customer_id": customer_id}


# Example usage:
tokens = extract_tokens_from_pdf()

table = get_dynamodb()

print(tokens)

# table.put_item(Item={"customerId": customer_id, "tokens": tokens})
