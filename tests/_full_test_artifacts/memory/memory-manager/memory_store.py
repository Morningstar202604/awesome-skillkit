
import json, os, hashlib
DB = os.path.join(os.path.dirname(__file__), "memory.json")

def _load():
    return json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else []

def add(topic, text):
    m = _load()
    key = hashlib.sha1(f"{topic}|{text}".encode()).hexdigest()
    if not any(x.get("key") == key for x in m):  # 去重
        m.append({"key": key, "topic": topic, "text": text})
    json.dump(m, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(m)

def search(topic):
    return [x for x in _load() if x["topic"] == topic]

if __name__ == "__main__":
    print("after add: ", add("dev", "use venv under runtime dir"), "dups:", add("dev", "use venv under runtime dir"))
    print("search dev:", len(search("dev")), "hits")
    assert len(search("dev")) == 1, "dedup failed"
    print("OK")
