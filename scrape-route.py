from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import json

app = Flask(__name__)

def extract_tokens_from_pdf(obj):
    # turn case_id into pdf_path
    pdf_path = obj['doc_id'] + '_cSchedule.pdf'
    # Open the PDF
    document = fitz.open(pdf_path)
    tokens = {}

    # Search each page for the customer ID
    # page = document[0]
    print('Document size: ', len(document))
    for page_num in range(len(document)):
        page = document[page_num]
    
        text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')
        # Check if the customer ID is in the lines
        for i in range(len(lines)):
            if obj['customer_id'] in lines[i]:
                print(lines[i])
                # If the customer ID is found, parse the next line to extract the tokens
                tokens = parse_line_to_tokens(lines[i+1])
                print(tokens)
    return json.dumps(tokens, indent=4)

def parse_line_to_tokens(line):
    # Split the line into parts by comma
    parts = line.split(',')
    tokens = {}
    print(parts)
    for part in parts:
        
        # Split each part into token and value
        token, value = part.split('[')
        value = value.rstrip(']')
        tokens[token] = value
    return tokens


@app.route('/get_customer_tokens', methods=['GET'])
def get_customer_tokens():
    # Get the customer ID from the query string parameter
    customer_id = request.args.get('customer_id')
    doc_id = request.args.get('doc_id')

    # Check if case_id was provided
    if not doc_id:
        return jsonify({"error": "Case ID is required"}), 400

    # Check if the customer ID was provided
    if not customer_id:
        return jsonify({"error": "Customer ID is required"}), 400
    obj = {
        "customer_id": customer_id,
        "doc_id": doc_id
    }

    try:
        # Use the previously defined function to extract tokens
        tokens_json = extract_tokens_from_pdf(obj)
        print('Tokens: ', tokens_json)
        return tokens_json
    except Exception as e:
        # Handle exceptions
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
