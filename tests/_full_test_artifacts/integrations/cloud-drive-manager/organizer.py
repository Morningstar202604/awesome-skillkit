
import os, sys
EXT_MAP = {".md": "docs", ".txt": "docs", ".csv": "data", ".xlsx": "data",
           ".jpg": "images", ".png": "images"}
def organize(src, dst):
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if not os.path.isfile(p):
            continue
        ext = os.path.splitext(f)[1].lower()
        cat = EXT_MAP.get(ext, "misc")
        target = os.path.join(dst, cat)
        os.makedirs(target, exist_ok=True)
        os.replace(p, os.path.join(target, f))
if __name__ == "__main__":
    organize(sys.argv[1], sys.argv[2])
    print("organized")
