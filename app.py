"""URL Shortener API built with Flask and SQLite."""

import os
import string
import random
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), "data", "urls.db")


def get_db():
    """Get database connection with row factory."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database tables."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM urls WHERE short_code = ?", (code,)
        ).fetchone()
        conn.close()
        if not existing:
            return code


def is_valid_url(url):
    """Basic URL validation."""
    return url and (url.startswith("http://") or url.startswith("https://"))


# Initialize database on startup
init_db()


@app.route("/")
def index():
    """API information."""
    return jsonify({
        "message": "URL Shortener API",
        "version": "1.0.0",
        "endpoints": {
            "shorten": "POST /api/shorten",
            "redirect": "GET /<short_code>",
            "stats": "GET /api/stats/<short_code>",
            "all_urls": "GET /api/urls",
        },
    })


@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    """Create a shortened URL."""
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    original_url = data["url"].strip()
    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL. Must start with http:// or https://"}), 400

    # Check if URL already exists
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM urls WHERE original_url = ?", (original_url,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({
            "short_code": existing["short_code"],
            "original_url": existing["original_url"],
            "short_url": f"{request.host_url}{existing['short_code']}",
            "clicks": existing["clicks"],
            "created_at": existing["created_at"],
        })

    # Create new short URL
    short_code = data.get("custom_code") or generate_short_code()

    # Validate custom code
    if data.get("custom_code"):
        if len(short_code) < 3 or len(short_code) > 20:
            conn.close()
            return jsonify({"error": "Custom code must be 3-20 characters"}), 400
        check = conn.execute(
            "SELECT id FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        if check:
            conn.close()
            return jsonify({"error": "Custom code already taken"}), 409

    conn.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "short_code": short_code,
        "original_url": original_url,
        "short_url": f"{request.host_url}{short_code}",
    }), 201


@app.route("/<short_code>")
def redirect_to_url(short_code):
    """Redirect short code to original URL."""
    conn = get_db()
    url_entry = conn.execute(
        "SELECT * FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if not url_entry:
        conn.close()
        return jsonify({"error": "Short URL not found"}), 404

    # Increment click counter
    conn.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
    )
    conn.commit()
    conn.close()

    return redirect(url_entry["original_url"])


@app.route("/api/stats/<short_code>")
def get_stats(short_code):
    """Get click statistics for a short URL."""
    conn = get_db()
    url_entry = conn.execute(
        "SELECT * FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()
    conn.close()

    if not url_entry:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "short_code": url_entry["short_code"],
        "original_url": url_entry["original_url"],
        "clicks": url_entry["clicks"],
        "created_at": url_entry["created_at"],
    })


@app.route("/api/urls")
def list_urls():
    """List all shortened URLs."""
    conn = get_db()
    urls = conn.execute(
        "SELECT * FROM urls ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()

    return jsonify([
        {
            "short_code": u["short_code"],
            "original_url": u["original_url"],
            "clicks": u["clicks"],
            "created_at": u["created_at"],
        }
        for u in urls
    ])


@app.route("/api/urls/<short_code>", methods=["DELETE"])
def delete_url(short_code):
    """Delete a shortened URL."""
    conn = get_db()
    url_entry = conn.execute(
        "SELECT id FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if not url_entry:
        conn.close()
        return jsonify({"error": "Short URL not found"}), 404

    conn.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
    conn.commit()
    conn.close()

    return jsonify({"message": "URL deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
