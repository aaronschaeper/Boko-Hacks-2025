from flask import Blueprint, render_template, jsonify, request
import requests
import json
import re

news_bp = Blueprint('news', __name__, url_prefix='/apps/news')

# Base URL for the News API
NEWS_API_BASE_URL = "https://saurav.tech/NewsAPI"

# Category mapping to prevent arbitrary inputs
CATEGORY_MAPPING = {
    'business': 'business',
    'technology': 'technology',
    'world': 'general'
}

DEFAULT_COUNTRY = 'us'

# Internal news - No longer accessible via filters
INTERNAL_NEWS = [
    {
        "title": "CONFIDENTIAL: Security Breach Report Q3",
        "description": "Details of recent security incidents affecting customer data.",
        "url": "#internal-only",
        "publishedAt": "2025-01-15T08:30:00Z",
        "urlToImage": ""
    },
    {
        "title": "CONFIDENTIAL: Upcoming Product Launch",
        "description": "Specifications for our next-gen product launch.",
        "url": "#internal-only",
        "publishedAt": "2025-02-01T10:15:00Z",
        "urlToImage": ""
    }
]

@news_bp.route('/')
def news_page():
    """Render the news page"""
    return render_template('news.html')

@news_bp.route('/fetch', methods=['GET'])
def fetch_news():
    """Securely fetch news from the external API"""
    try:
        # Get and validate category
        category = request.args.get('category', 'business')
        if category not in CATEGORY_MAPPING:
            return jsonify({"success": False, "error": "Invalid category"}), 400

        api_category = CATEGORY_MAPPING[category]
        api_url = f"{NEWS_API_BASE_URL}/top-headlines/category/{api_category}/{DEFAULT_COUNTRY}.json"

        # Fetch news from external API (timeout added)
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch news. Status code: {response.status_code}'
            }), response.status_code

        # Limit to 10 articles
        articles = response.json().get('articles', [])[:10]

        # Sanitize search parameter
        search_query = request.args.get('search', '').strip()

        if search_query:
            # Block SQL Injection attempts
            if re.search(r"('|--|;|#|--|\*|=|\bor\b|\bunion\b|\bselect\b|\binsert\b|\bdelete\b|\bupdate\b|\bdrop\b)", search_query, re.IGNORECASE):
                return jsonify({"success": False, "error": "Invalid search query"}), 400

            # Filter articles by search query (Simple case-insensitive match)
            articles = [article for article in articles if search_query.lower() in article.get('title', '').lower()]

        # Secure filter handling
        filter_param = request.args.get('filter', '{}')

        try:
            # Validate JSON structure
            if not re.match(r'^\{.*\}$', filter_param):
                return jsonify({"success": False, "error": "Invalid filter format"}), 400
            
            filter_options = json.loads(filter_param)

            # **BLOCK ACCESS TO INTERNAL NEWS**
            if filter_options.get('showInternal'):
                return jsonify({"success": False, "error": "Access denied"}), 403

        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Malformed JSON input"}), 400

        # Process and format articles securely
        transformed_data = {
            'success': True,
            'category': category,
            'data': []
        }

        for article in articles:
            transformed_data['data'].append({
                'title': article.get('title', 'No Title'),
                'content': article.get('description', 'No content available'),
                'date': article.get('publishedAt', ''),
                'readMoreUrl': article.get('url', '#'),
                'imageUrl': article.get('urlToImage', '')
            })

        return jsonify(transformed_data)

    except Exception as e:
        # **Remove sensitive error messages**
        return jsonify({
            'success': False,
            'error': "An internal error occurred. Please try again later."
        }), 500
