import requests
import time
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client, Client

# Ganti dengan info Supabase kamu
SUPABASE_URL = "https://cqakrownxujefhtmsefa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxYWtyb3dueHVqZWZodG1zZWZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIyNjMyMzMsImV4cCI6MjA0NzgzOTIzM30.E9jJxNBxFsVZsndwhsMZ_2hXaeHdDTLS7jZ50l-S72U"
SUPABASE_TABLE_NAME = "scp"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API Serper
API_KEY = "95164e01ffd98f4ddd47e12e6166a783b020c575"
URL_API = "https://google.serper.dev/search"

# Rentang baris yang akan diproses
mulai = 97500
endnya = 100000

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def search_url(idx, target_url):
    query = f"site:{target_url}"
    payload = {"q": query}

    try:
        response = requests.post(URL_API, headers=headers, json=payload)
        data = response.json()

        if "organic" in data and len(data["organic"]) > 0:
            top_result = data["organic"][0]
            title = top_result.get("title", "")
            link = top_result.get("link", "")
            print(f"[{idx}] ✔ {title} -> {link}")
            return {"title": title, "url": link}
        else:
            print(f"[{idx}] ❌ Tidak ditemukan: {target_url}")
            return None

    except Exception as e:
        print(f"[{idx}] ⚠ Error: {e}")
        return None

    finally:
        time.sleep(1.2)

def insert_to_supabase(data):
    if data is None:
        return
    try:
        res = supabase.table(SUPABASE_TABLE_NAME).insert(data).execute()
        if hasattr(res, 'error') and res.error is not None:
            print(f"⚠ Gagal insert ke Supabase: {res.error}")
        elif isinstance(res, dict) and "error" in res and res["error"] is not None:
            print(f"⚠ Gagal insert ke Supabase: {res['error']}")
        else:
            print(f"✔ Data berhasil disimpan ke Supabase: {getattr(res, 'data', res)}")
    except Exception as e:
        print(f"⚠ Error insert ke Supabase: {e}")

def worker(idx, url):
    result = search_url(idx, url)
    if result:
        insert_to_supabase(result)

def main(start_line=1, end_line=None):
    with open("list_url.csv", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    urls = urls[start_line - 1 : end_line]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, idx + start_line, url) for idx, url in enumerate(urls)]
        for f in futures:
            f.result()

if __name__ == "__main__":
    main(start_line=mulai, end_line=endnya)
