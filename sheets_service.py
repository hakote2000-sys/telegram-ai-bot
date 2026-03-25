import gspread
import google.auth

SPREADSHEET_ID = "1rpXhj4pwSbuWSoiRMP8K-mQ_EvtY5XezvfS_1E74TQI"
WORKSHEET_NAME = "products"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

def get_worksheet():
    credentials, _ = google.auth.default(scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

def get_all_products():
    worksheet = get_worksheet()
    rows = worksheet.get_all_records()

    products = []
    for row in rows:
        status = str(row.get("status", "")).strip().lower()
        if status != "active":
            continue

        products.append({
            "id": row.get("id"),
            "name": row.get("name"),
            "category": row.get("category"),
            "price": row.get("price"),
            "cpu": row.get("cpu"),
            "gpu": row.get("gpu"),
            "ram": row.get("ram"),
            "ssd": row.get("ssd"),
        })

    return products

def get_products_by_budget(min_price=None, max_price=None):
    products = get_all_products()
    result = []

    for p in products:
        try:
            price = int(str(p["price"]).replace(" ", "").replace("₽", ""))
        except Exception:
            continue

        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        result.append(p)

    return result

def get_products_by_category(category: str):
    category = category.strip().lower()
    return [
        p for p in get_all_products()
        if str(p.get("category", "")).strip().lower() == category
    ]