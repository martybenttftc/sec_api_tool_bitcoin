from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sec_api import QueryApi, ExtractorApi, XbrlApi, FullTextSearchApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Initialize API clients
API_KEY = os.getenv('SEC_API_KEY')

if not API_KEY:
    raise ValueError("SEC_API_KEY is not set in the .env file or environment variables")

query_api = QueryApi(api_key=API_KEY)
extractor_api = ExtractorApi(API_KEY)
xbrl_api = XbrlApi(API_KEY)
full_text_search_api = FullTextSearchApi(api_key=API_KEY)

@app.route('/')
def index():
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

@app.route('/filing/<filing_id>')
def get_filing(filing_id):
    query = {
        'query': {
            'query_string': {
                'query': f'accessionNumber:{filing_id}'
            }
        },
        'from': '0',
        'size': '1'
    }
    
    response = query_api.get_filings(query)
    
    if response['filings']:
        return jsonify(response['filings'][0])
    else:
        return jsonify({"error": "Filing not found"}), 404

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
