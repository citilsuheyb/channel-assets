import os
import re
import shutil
from pathlib import Path
import bibtexparser

# =====================
# CONFIG
# =====================
BIB_FILE = "MT.bib"
PDF_DIR = "files"
OUTPUT_DIR = "renamed_pdfs"
# DRY_RUN = True

DRY_RUN = False




# =====================
# CLEAN KEY
# =====================
def clean_key(key: str) -> str:
    return re.sub(r'[^\w\-]+', '_', key)


# =====================
# PARSE BIB
# =====================
def parse_bib(path):
    with open(path, encoding="utf-8") as f:
        bib_database = bibtexparser.load(f)

    entries = bib_database.entries

    mapping = {}

    for e in entries:
        citekey = e.get("ID")  # Better BibTeX key

        file_field = e.get("file", "")

        if not citekey or not file_field:
            continue

        # Zotero format:
        # file = {storage:XXXX.pdf:application/pdf}
        files = file_field.split(";")

        pdfs = []

        for f in files:
            if ".pdf" in f:
                # extract filename
                name = f.split(":")[-2] if ":" in f else f
                name = os.path.basename(name)
                pdfs.append(name)

        if pdfs:
            mapping[citekey] = pdfs

    return mapping


# =====================
# FIND FILE
# =====================
def find_pdf(filename):
    target = filename.lower()

    for p in Path(PDF_DIR).rglob("*"):
        if p.is_file() and p.name.lower() == target:
            return p

    return None


# =====================
# RUN
# =====================
def run():
    print("\n📄 Parsing BibTeX...")

    mapping = parse_bib(BIB_FILE)

    print(f"FOUND {len(mapping)} ITEMS\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ok = 0
    miss = 0

    for citekey, pdfs in mapping.items():

        key = clean_key(citekey)

        for i, pdf in enumerate(pdfs):

            src = find_pdf(pdf)

            if not src:
                print(f"❌ MISSING: {pdf}")
                miss += 1
                continue

            suffix = f"_{i+1}" if len(pdfs) > 1 else ""
            new_name = f"{key}{suffix}.pdf"

            dest = os.path.join(OUTPUT_DIR, new_name)

            print(f"✔ {src.name} → {new_name}")

            if not DRY_RUN:
                shutil.copy2(src, dest)
                ok += 1

    print("\n====================")
    print(f"OK: {ok}")
    print(f"MISSING: {miss}")
    print("====================")


if __name__ == "__main__":
    run()