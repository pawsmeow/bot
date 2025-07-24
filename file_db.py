import json
from pathlib import Path

DB_FILE = Path("users.json")


def _load(path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_registered(user_id):
    data = _load(DB_FILE)
    return str(user_id) in data


def register_user(user_id, user_data):
    data = _load(DB_FILE)
    data[str(user_id)] = user_data
    _save(DB_FILE, data)


def get_user_data(user_id):
    data = _load(DB_FILE)
    return data.get(str(user_id))


def get_all_users():
    return _load(DB_FILE)


def delete_user(user_id):
    db = _load(DB_FILE)
    uid = str(user_id)
    if uid in db:
        del db[uid]
        _save(DB_FILE, db)
        return True
    return False