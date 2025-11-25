# backend/app/services/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_garuda_sample():
    """
    Fallback: Manual CSV jika scraping gagal
    """
    # Coba scraping sederhana
    try:
        # URL GARUDA BRIN (sesuaikan dengan struktur aktual)
        url = "https://garuda.kemdikbud.go.id/..."
        response = requests.get(url, timeout=10)
        # Parse HTML...
    except Exception as e:
        print(f"Scraping failed: {e}")
        print("Using manual CSV backup...")
        return load_manual_csv()

def load_manual_csv():
    """Backup: Load dari CSV manual"""
    df = pd.read_csv("data/raw/brin_publications.csv")
    return df