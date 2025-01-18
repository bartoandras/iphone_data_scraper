# iPhone Scraper

A web scraper that collects iPhone listings from hasznaltalma.hu and stores them in a SQLite database.

## Features
- Scrapes iPhone listings including model, price, condition, battery health, and URL
- Extracts additional details from product URLs
- Stores data in SQLite database
- Dockerized for easy deployment

## Requirements
- Python 3.8+
- ChromeDriver
- Docker (optional)

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the scraper:
```bash
python scrape_iphones.py
```

## Docker
Build and run with Docker:
```bash
docker-compose up --build
```

## Database
Data is stored in `/app/data/iphones.db` with the following schema:
- id (primary key)
- model
- price
- condition
- battery
- url
- pro (boolean)
- max (boolean)
- mini (boolean)
- se (boolean)
- capacity (integer)
- created_at (timestamp)
- updated_at (timestamp)

## License
MIT
