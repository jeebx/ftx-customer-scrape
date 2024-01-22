import fitz  # PyMuPDF
import re
from decimal import Decimal
import json


def parse_tokens(text_block):
    # Find all token-value pairs
    pattern = re.compile(r"([A-Z0-9-]+)\[([\d.]+)\]")
    matches = pattern.findall(text_block)

    tokens = {}
    for token, value_str in matches:
        # Convert value to the correct numeric type: int or float
        if "." in value_str:
            value = float(value_str)
        else:
            value = int(value_str)
        tokens[token] = value

    return tokens


def extract_tokens_from_pdf(customer_id):
    # Depending on the customerID, check EU first, if no customer is found, check US list based on the customerID, ranges are as follows:
    # US
    # F1: 00000000-00286600
    # F2: 00286601-00453838
    # F3: 00453848-00601233
    # F4: 00601235-00819051
    # F5: 00819052-01051992
    # F6: 01051994-01271650
    # F7: 01271651-01541266
    # F8: 01541277-01767134
    # F9: 01767141-01977626
    # F10: 01977627-02206059
    # F11: 02206060-02498445
    # F12: 02498449-02760808
    # F13: 02760809-03026617
    # F14: 03026626-03304077
    # F15: 03304080-03598804
    # F16: 03598805-04215163
    # F17: 04215165-04644861
    # F18: 04644862-04988544
    # F19: 04988556-06299341
    # F20: 06299344-07086317
    # F21: 07086319-07187419

    # EU:
    # 00000009-00286600

    # path: "schedules/amendedScheduleF7.pdf"

    # Check if the customerID is in the EU range
    ranges = [
        (range(9, 286601), "schedules/amendedScheduleEU.pdf"),
        # Define all the US ranges with their respective PDF paths
        (range(0, 286601), "schedules/amendedScheduleF1.pdf"),
        (range(286601, 453839), "schedules/amendedScheduleF2.pdf"),
        (range(453848, 601234), "schedules/amendedScheduleF3.pdf"),
        (range(601235, 819052), "schedules/amendedScheduleF4.pdf"),
        (range(819052, 1051993), "schedules/amendedScheduleF5.pdf"),
        (range(1051994, 1271651), "schedules/amendedScheduleF6.pdf"),
        (range(1271651, 1541267), "schedules/amendedScheduleF7.pdf"),
        (range(1541277, 1767135), "schedules/amendedScheduleF8.pdf"),
        (range(1767141, 1977627), "schedules/amendedScheduleF9.pdf"),
        (range(1977627, 2206060), "schedules/amendedScheduleF10.pdf"),
        (range(2206060, 2498446), "schedules/amendedScheduleF11.pdf"),
        (range(2498449, 2760809), "schedules/amendedScheduleF12.pdf"),
        (range(2760809, 3026618), "schedules/amendedScheduleF13.pdf"),
        (range(3026626, 3304078), "schedules/amendedScheduleF14.pdf"),
        (range(3304080, 3598805), "schedules/amendedScheduleF15.pdf"),
        (range(3598805, 4215164), "schedules/amendedScheduleF16.pdf"),
        (range(4215165, 4644862), "schedules/amendedScheduleF17.pdf"),
        (range(4644862, 4988545), "schedules/amendedScheduleF18.pdf"),
        (range(4988556, 6299342), "schedules/amendedScheduleF19.pdf"),
        (range(6299344, 7086318), "schedules/amendedScheduleF20.pdf"),
        (range(7076319, 7187420), "schedules/amendedScheduleF21.pdf"),
    ]

    customer_id_num = int(customer_id)
    pdf_path = None
    for id_range, path in ranges:
        if customer_id_num in id_range:
            pdf_path = path
            break

    if not pdf_path:
        return {}

    # Open the PDF
    document = fitz.open(pdf_path)
    tokens = {}

    # Search each page for the customer ID
    for page_num in range(len(document)):
        page = document[page_num]
        text = page.get_text("text")

        # Split the text by lines and iterate through them
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if customer_id in line:
                print(
                    f"Customer ID {customer_id} found on page: {page_num + 1} of document: {pdf_path}"
                )
                # Collect all subsequent lines until the next customer ID is found
                for token_line in lines[i + 1 :]:
                    if re.match(r"^\d{8}$", token_line):
                        # Next customer ID found, stop processing
                        break
                    tokens.update(parse_tokens(token_line))

    document.close()
    return tokens


# Example usage:
tokens = extract_tokens_from_pdf("03273185")
print(json.dumps(tokens, indent=4))
