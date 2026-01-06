# URL Shortener Service

A web service built with Python and Flask that takes long URLs and generates short codes (similar to bit.ly). Users can visit the short URL and get redirected to the original link.

## Features

- 🔗 Shorten long URLs into 6-character short codes
- 🔄 Automatic redirect from short URL to original URL
- 🎨 Beautiful, responsive web interface
- 💾 SQLite database for persistent storage
- ✅ URL validation and error handling
- 📊 Stats API to view URL information
- 🔒 Duplicate URL detection (same URL returns same short code)
- ⚡ Collision handling for short code generation

## Key Concepts Demonstrated

- **Hashing algorithms**: Random short code generation with collision detection
- **URL routing with parameters**: Dynamic routes with Flask (`/<short_code>`)
- **HTTP redirects**: 301 permanent redirects for SEO-friendly forwarding
- **Database lookups**: Efficient SQLite queries for URL storage and retrieval
- **Unique ID generation**: Algorithm to generate unique short codes
- **REST API design**: JSON endpoints for programmatic access
- **Error handling**: Comprehensive validation and error responses

## Project Structure

```
URL-Shortner/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── test_app.py        # Unit tests
├── templates/
│   ├── index.html     # Main web interface
│   └── 404.html       # Error page
└── urls.db            # SQLite database (created on first run)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Web Interface

1. Enter a long URL in the input field
2. Click "Shorten URL"
3. Copy your shortened URL and share it
4. Anyone visiting the short URL will be redirected to the original

### API Endpoints

#### Shorten a URL
```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com/very/long/url"
}

Response:
{
  "short_url": "http://localhost:5000/abc123",
  "short_code": "abc123",
  "original_url": "https://example.com/very/long/url"
}
```

#### Redirect to Original URL
```bash
GET /<short_code>
# Returns 301 redirect to original URL
# Returns 404 if short code not found
```

#### Get URL Statistics
```bash
GET /api/stats/<short_code>

Response:
{
  "short_code": "abc123",
  "original_url": "https://example.com/very/long/url",
  "created_at": "2026-01-06 12:34:56"
}
```

## Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    short_code TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Testing

Run the test suite:
```bash
python test_app.py
```

Tests cover:
- Valid and invalid URL submissions
- URL validation
- Redirect functionality
- Duplicate URL handling
- Error cases (missing URLs, invalid codes)
- Stats API endpoint

## Implementation Details

### Short Code Generation
- Uses random combination of letters (a-z, A-Z) and digits (0-9)
- Default length: 6 characters (62^6 = 56+ billion combinations)
- Collision detection: checks database before inserting
- Automatic length increase if too many collisions

### Error Handling
- Invalid URL format validation
- Missing parameter detection
- Database integrity checks
- 404 pages for non-existent short codes
- 500 error handling for server issues

### Features
- **Duplicate Prevention**: Same URL always returns the same short code
- **Clean URLs**: No file extensions needed
- **Permanent Redirects**: Uses 301 status for SEO benefits
- **AJAX Interface**: No page reloads needed
- **Copy to Clipboard**: One-click copying of short URLs

## Technologies Used

- **Flask**: Web framework
- **SQLite**: Database
- **Validators**: URL validation
- **HTML/CSS/JavaScript**: Frontend
- **Python unittest**: Testing

## Future Enhancements

- Click tracking and analytics
- Custom short codes
- QR code generation
- URL expiration dates
- User accounts and dashboard
- Rate limiting
- API authentication

## License

MIT License - Feel free to use for learning and projects!
