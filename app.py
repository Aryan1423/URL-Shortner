import sqlite3
import string
import random
import validators
from flask import Flask, request, redirect, render_template, jsonify, url_for
from datetime import datetime
from contextlib import closing

app = Flask(__name__)
app.config['DATABASE'] = 'urls.db'

# Database initialization
def init_db():
    """Initialize the database with required schema"""
    with closing(sqlite3.connect(app.config['DATABASE'])) as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def generate_short_code(length=6):
    """Generate a random short code of specified length"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_unique_short_code():
    """Generate a unique short code that doesn't exist in database"""
    max_attempts = 10
    for _ in range(max_attempts):
        short_code = generate_short_code()
        with closing(get_db()) as db:
            existing = db.execute(
                'SELECT short_code FROM urls WHERE short_code = ?',
                (short_code,)
            ).fetchone()
            if not existing:
                return short_code
    
    # If collision after max attempts, increase length
    return generate_short_code(length=8)

@app.route('/')
def index():
    """Render the main page with URL submission form"""
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    POST endpoint to shorten a URL
    Expects JSON: {"url": "https://example.com/long/url"}
    Returns: {"short_url": "http://localhost:5000/abc123", "short_code": "abc123"}
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url'].strip()
    
    # Validate URL
    if not validators.url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Check if URL already exists
    with closing(get_db()) as db:
        existing = db.execute(
            'SELECT short_code FROM urls WHERE original_url = ?',
            (original_url,)
        ).fetchone()
        
        if existing:
            short_code = existing['short_code']
        else:
            # Generate unique short code
            short_code = get_unique_short_code()
            
            # Insert into database
            try:
                db.execute(
                    'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                    (original_url, short_code)
                )
                db.commit()
            except sqlite3.IntegrityError:
                return jsonify({'error': 'Failed to create short URL. Please try again.'}), 500
    
    # Generate full short URL
    short_url = url_for('redirect_to_url', short_code=short_code, _external=True)
    
    return jsonify({
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url
    }), 201

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """
    GET route that redirects short code to original URL
    Returns 301 permanent redirect if found, 404 if not found
    """
    with closing(get_db()) as db:
        url_entry = db.execute(
            'SELECT original_url FROM urls WHERE short_code = ?',
            (short_code,)
        ).fetchone()
    
    if url_entry:
        return redirect(url_entry['original_url'], code=301)
    else:
        return render_template('404.html', short_code=short_code), 404

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """Optional: Get statistics about a short URL"""
    with closing(get_db()) as db:
        url_entry = db.execute(
            'SELECT * FROM urls WHERE short_code = ?',
            (short_code,)
        ).fetchone()
    
    if url_entry:
        return jsonify({
            'short_code': url_entry['short_code'],
            'original_url': url_entry['original_url'],
            'created_at': url_entry['created_at']
        })
    else:
        return jsonify({'error': 'Short code not found'}), 404

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
