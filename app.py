# app.py
from flask import Flask, request, jsonify
from scraper import amazon_price_scrapper

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    asin_list = data.get("asins", [])
    min_prices = data.get("min_prices", [])
    max_prices = data.get("max_prices", [])
    cookies = data.get("cookies", [])

    if not asin_list or not min_prices or not max_prices or not cookies:
        return jsonify({"error": "Missing ASINs, prices, or cookies"}), 400

    try:
        results = amazon_price_scrapper(asin_list, min_prices, max_prices, cookies)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


