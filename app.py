from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from sec_api import QueryApi, ExtractorApi, XbrlApi, FullTextSearchApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

print(f"Available routes: {[rule.rule for rule in app.url_map.iter_rules()]}")  # Debug print

# Initialize API clients
API_KEY = os.getenv('SEC_API_KEY')

if not API_KEY:
    raise ValueError("SEC_API_KEY is not set in the .env file or environment variables")

query_api = QueryApi(api_key=API_KEY)
extractor_api = ExtractorApi(API_KEY)
xbrl_api = XbrlApi(API_KEY)
full_text_search_api = FullTextSearchApi(api_key=API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        accession_number = request.form.get('accession_number')
        return redirect(url_for('get_filing', accession_number=accession_number))
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_filings():
    query = request.json.get('query')
    search_query = {
        "query": {"query_string": {"query": query}},
        "from": "0",
        "size": "10",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    results = query_api.get_filings(search_query)
    return jsonify(results)

@app.route('/filing/<accession_number>', methods=['GET', 'POST'])
def get_filing(accession_number):
    print(f"Received request for accession number: {accession_number}")  # Debug print

    query = {
        "query": f"accessionNo:\"{accession_number}\"",
        "from": "0",
        "size": "20",
        "sort": [{ "filedAt": { "order": "desc" } }]
    }

    print(f"Query: {query}")  # Debug print

    try:
        response = query_api.get_filings(query)
        print(f"API Response: {response}")  # Debug print

        if response.get('filings'):
            filing_data = response['filings'][0]
            return render_template('index.html', filing=filing_data)
        else:
            return render_template('index.html', error="Filing not found")
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug print
        return render_template('index.html', error=f"An error occurred: {str(e)}")

@app.route('/financials/<ticker>')
def get_financials(ticker):
    search_query = {
        "query": {"query_string": {"query": f"ticker:{ticker} AND formType:\"10-K\""}},
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    results = query_api.get_filings(search_query)
    if results['filings']:
        filing_url = results['filings'][0]['linkToFilingDetails']
        xbrl_json = xbrl_api.xbrl_to_json(htm_url=filing_url)
        income_statement = xbrl_json['StatementsOfIncome']
        return jsonify(income_statement)
    else:
        return jsonify({"error": "No filing found"})

@app.route('/full-text-search', methods=['POST'])
def full_text_search():
    query = request.json.get('query')
    search_query = {
        "query": query,
        "formTypes": ["10-K", "10-Q", "8-K"],
        "startDate": "2020-01-01",
        "endDate": "2023-12-31",
    }

    results = full_text_search_api.get_filings(search_query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)