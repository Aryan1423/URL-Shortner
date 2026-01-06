import unittest
import json
import os
from app import app, init_db

class URLShortenerTestCase(unittest.TestCase):
    """Test cases for URL Shortener application"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = 'test_urls.db'
        self.client = self.app.test_client()
        
        # Initialize test database
        with self.app.app_context():
            init_db()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists('test_urls.db'):
            os.remove('test_urls.db')
    
    def test_index_page(self):
        """Test that index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_shorten_valid_url(self):
        """Test shortening a valid URL"""
        response = self.client.post('/shorten',
            data=json.dumps({'url': 'https://www.example.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('short_url', data)
        self.assertIn('short_code', data)
        self.assertEqual(data['original_url'], 'https://www.example.com')
        self.assertEqual(len(data['short_code']), 6)
    
    def test_shorten_invalid_url(self):
        """Test shortening an invalid URL"""
        response = self.client.post('/shorten',
            data=json.dumps({'url': 'not-a-valid-url'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_shorten_missing_url(self):
        """Test request without URL parameter"""
        response = self.client.post('/shorten',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_shorten_empty_url(self):
        """Test shortening an empty URL"""
        response = self.client.post('/shorten',
            data=json.dumps({'url': '   '}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_redirect_valid_code(self):
        """Test redirecting with a valid short code"""
        # First create a short URL
        response = self.client.post('/shorten',
            data=json.dumps({'url': 'https://www.google.com'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        short_code = data['short_code']
        
        # Test redirect
        response = self.client.get(f'/{short_code}')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, 'https://www.google.com')
    
    def test_redirect_invalid_code(self):
        """Test redirecting with an invalid short code"""
        response = self.client.get('/invalid123')
        self.assertEqual(response.status_code, 404)
    
    def test_duplicate_url(self):
        """Test that same URL returns same short code"""
        url = 'https://www.duplicate-test.com'
        
        # First request
        response1 = self.client.post('/shorten',
            data=json.dumps({'url': url}),
            content_type='application/json'
        )
        data1 = json.loads(response1.data)
        
        # Second request with same URL
        response2 = self.client.post('/shorten',
            data=json.dumps({'url': url}),
            content_type='application/json'
        )
        data2 = json.loads(response2.data)
        
        # Should return same short code
        self.assertEqual(data1['short_code'], data2['short_code'])
    
    def test_stats_endpoint(self):
        """Test the stats API endpoint"""
        # Create a short URL
        response = self.client.post('/shorten',
            data=json.dumps({'url': 'https://www.stats-test.com'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        short_code = data['short_code']
        
        # Get stats
        response = self.client.get(f'/api/stats/{short_code}')
        self.assertEqual(response.status_code, 200)
        stats = json.loads(response.data)
        self.assertEqual(stats['short_code'], short_code)
        self.assertEqual(stats['original_url'], 'https://www.stats-test.com')
        self.assertIn('created_at', stats)
    
    def test_stats_invalid_code(self):
        """Test stats endpoint with invalid code"""
        response = self.client.get('/api/stats/invalid999')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
