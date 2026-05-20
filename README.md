# Flask URL Shortener

A simple URL shortening API built with **Python**, **Flask**, and **SQLite**.

## Features

- Shorten long URLs into short, shareable links
- Custom short codes support
- Click tracking and analytics
- Automatic redirect on short URL visit
- List and delete shortened URLs
- Input validation

## Tech Stack

- **Language:** Python 3
- **Framework:** Flask
- **Database:** SQLite

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Ola-mide1/flask-url-shortener.git
cd flask-url-shortener

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server runs at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Shorten a URL |
| GET | `/<short_code>` | Redirect to original URL |
| GET | `/api/stats/<short_code>` | Get click statistics |
| GET | `/api/urls` | List all shortened URLs |
| DELETE | `/api/urls/<short_code>` | Delete a short URL |

### Example Usage

```bash
# Shorten a URL
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url/path"}'

# Shorten with custom code
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/Ola-mide1", "custom_code": "mygit"}'

# Check stats
curl http://localhost:5000/api/stats/mygit
```

## License

MIT
