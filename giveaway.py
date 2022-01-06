import dotenv
import requests
import tinydb

config = dotenv.dotenv_values(".env")


def fetch_active_giveaways():
    url = config["GAMERPOWER_API_URL"] + "?" + config["PARAM_TYPE"] + "&" + config["PARAM_SORT"]

    print(f"GET {url}")

    resp = requests.get(url)

    if resp.status_code != 200:
        print(f"HTTP ERROR: Failed to make request: CODE: {resp.status_code} Content: {resp.content[:300]}...")
        raise requests.RequestException()

    print("HTTP 200 OK")

    return resp.json()


def init_db():
    try:
        tinydb.TinyDB(config["DATABASE_FILE"]).table(config["TABLE_GAMES"]).clear_cache()
    except Exception as ex:
        print(f"ERROR: Failed to init db: {ex!r}")
        raise


def giveaway_exists_db(ga_id) -> bool:
    db = tinydb.TinyDB(config["DATABASE_FILE"]).table(config["TABLE_GAMES"])
    if db.search(tinydb.where('id') == ga_id):
        return True
    return False


def insert_giveaways(data):
    try:
        db = tinydb.TinyDB(config["DATABASE_FILE"]).table(config["TABLE_GAMES"])
        for entry in data:
            if giveaway_exists_db(entry['id']):
                continue
            db.insert(entry)
    except Exception as ex:
        print(f"ERROR: Failed to insert new giveaways: {ex!r}")
        raise


def filter_giveaways(source, new_only: bool, min_value: float = None, max_value: float = None) -> list:
    filtered = []

    for entry in source:
        try:
            ga_id = int(entry['id'])
            status = str(entry['status'])
            price = None

            if entry['worth'] == "N/A":
                continue
            else:
                price = float(entry['worth'][1:])

            if status != "Active":
                continue

            if min_value is not None and price < min_value:
                continue

            if max_value is not None and price > max_value:
                continue

            if new_only and giveaway_exists_db(ga_id):
                continue

            filtered.append(entry)
            # print(entry)

        except Exception as ex:
            print(f"Failed entry: {entry}")
            print(f"Caught exception during filter: {ex!r}")

    print(f"Filtered count: {len(filtered)}")
    return filtered
