"""URL-first supplier product intake with safe fallback parsing."""

from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from procm.config import FETCH_TIMEOUT, USER_AGENT

SUPPLIER_DOMAINS = {
    "teurlings.nl": "Teurlings de Mulder",
    "plein.nl": "Plein",
    "bol.com": "Bol",
    "scharrelpluimvee.nl": "Scharrelpluimvee",
    "olba.nl": "Olba",
}

PRICE_RE = re.compile(
    r"(?:€|EUR)\s*(\d{1,4}(?:[.,]\d{2})?)|(\d{1,4}(?:[.,]\d{2})?)\s*(?:€|EUR)",
    re.IGNORECASE,
)
WEIGHT_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(kg|g|gram|liter|l|stuks?|zak)\b",
    re.IGNORECASE,
)


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.images: list[str] = []
        self.body_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (ad.get("name") or ad.get("property") or "").lower()
            content = html.unescape((ad.get("content") or "").strip())
            if name and content:
                self.meta[name] = content
                if name in ("og:image", "twitter:image") and content not in self.images:
                    self.images.append(content)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title += text
        if len(text) < 200:
            self.body_text.append(text)


def decode_entities(text: str) -> str:
    prev = ""
    result = text or ""
    for _ in range(4):
        result = html.unescape(result)
        if result == prev:
            break
        prev = result
    return result


def fetch_page(url: str) -> tuple[str | None, str | None]:
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace"), None
    except Exception as exc:  # noqa: BLE001 — MVP fallback
        return None, str(exc)


def slug_to_name(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return ""
    slug = path.split("/")[-1]
    slug = re.sub(r"\.(html?|php|aspx)$", "", slug, flags=re.IGNORECASE)
    slug = slug.replace("-", " ").replace("_", " ")
    return " ".join(w.capitalize() for w in slug.split() if w)


def detect_supplier_name(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().replace("www.", "")
    for domain, name in SUPPLIER_DOMAINS.items():
        if domain in host:
            return name
    return host.split(".")[0].capitalize() if host else "Generic Supplier"


def extract_price(text: str) -> float | None:
    for match in PRICE_RE.finditer(text):
        raw = match.group(1) or match.group(2)
        if not raw:
            continue
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            continue
    return None


def extract_package(text: str) -> tuple[float | None, str | None]:
    match = WEIGHT_RE.search(text)
    if not match:
        return None, None
    try:
        size = float(match.group(1).replace(",", "."))
    except ValueError:
        return None, None
    unit = match.group(2).lower()
    if unit in ("g", "gram"):
        unit = "g"
    elif unit in ("l", "liter"):
        unit = "liter"
    elif unit.startswith("stuk") or unit == "zak":
        unit = "stuk"
    return size, unit


def parse_product_page(url: str, html_content: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source_url": url,
        "supplier_name": detect_supplier_name(url),
        "product_name": slug_to_name(url),
        "title": "",
        "description": "",
        "price": None,
        "image_url": "",
        "package_size": None,
        "package_unit": None,
        "parser": "fallback",
    }
    if not html_content:
        return result

    parser = _PageParser()
    try:
        parser.feed(html_content)
    except Exception:  # noqa: BLE001
        pass

    og_title = decode_entities(parser.meta.get("og:title", ""))
    title = decode_entities(parser.title.strip()) or og_title
    description = decode_entities(
        parser.meta.get("og:description", "")
        or parser.meta.get("description", "")
    )
    image = parser.meta.get("og:image", "") or (parser.images[0] if parser.images else "")

    combined = " ".join([title, description, " ".join(parser.body_text[:50])])
    price = extract_price(combined) or extract_price(html_content[:50000])
    package_size, package_unit = extract_package(combined)

    result.update(
        {
            "title": title,
            "product_name": title or result["product_name"],
            "description": description,
            "price": price,
            "image_url": image,
            "package_size": package_size,
            "package_unit": package_unit,
            "parser": "html-heuristic",
        }
    )
    return result


def run_url_intake(conn, url: str) -> dict[str, Any]:
    """Create import job, fetch page, snapshot, and draft supplier product."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = parse_product_page(url, None)
    supplier_name = parsed["supplier_name"]

    row = conn.execute("SELECT id FROM suppliers WHERE name = ?", (supplier_name,)).fetchone()
    if row:
        supplier_id = row["id"]
    else:
        domain = (urlparse(url).hostname or "").replace("www.", "")
        cur = conn.execute(
            "INSERT INTO suppliers (name, domain) VALUES (?, ?)",
            (supplier_name, domain),
        )
        supplier_id = cur.lastrowid

    status = "PENDING"
    error_message = None
    html_content, fetch_error = fetch_page(url)
    if fetch_error:
        status = "MANUAL_REQUIRED"
        error_message = fetch_error
        parsed = parse_product_page(url, None)
    else:
        parsed = parse_product_page(url, html_content)
        status = "COMPLETED" if parsed.get("product_name") else "MANUAL_REQUIRED"

    html_hash = (
        hashlib.sha256(html_content.encode("utf-8", errors="replace")).hexdigest()
        if html_content
        else None
    )

    job_cur = conn.execute(
        "INSERT INTO import_jobs (source_url, supplier_id, status, error_message) VALUES (?, ?, ?, ?)",
        (url, supplier_id, status, error_message),
    )
    job_id = job_cur.lastrowid

    conn.execute(
        "INSERT INTO imported_pages (import_job_id, raw_title, raw_html_hash) VALUES (?, ?, ?)",
        (job_id, parsed.get("title") or parsed.get("product_name"), html_hash),
    )

    snapshot = json.dumps(parsed, ensure_ascii=False)
    conn.execute(
        "INSERT INTO supplier_product_snapshots (import_job_id, captured_json) VALUES (?, ?)",
        (job_id, snapshot),
    )

    product_cur = conn.execute(
        """
        INSERT INTO supplier_products (
            supplier_id, supplier_product_name, canonical_name, source_url,
            package_size, package_unit, current_price, image_url, description, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            supplier_id,
            parsed.get("product_name") or "Draft product",
            parsed.get("product_name"),
            url,
            parsed.get("package_size"),
            parsed.get("package_unit"),
            parsed.get("price"),
            parsed.get("image_url") or None,
            parsed.get("description"),
            "Created via URL intake — review and save",
        ),
    )
    product_id = product_cur.lastrowid

    if parsed.get("image_url"):
        conn.execute(
            "INSERT INTO supplier_product_images (supplier_product_id, image_url) VALUES (?, ?)",
            (product_id, parsed["image_url"]),
        )

    conn.execute(
        "INSERT INTO supplier_product_imports (import_job_id, supplier_product_id, outcome) VALUES (?, ?, ?)",
        (job_id, product_id, status),
    )
    conn.execute(
        "UPDATE supplier_product_snapshots SET supplier_product_id = ? WHERE import_job_id = ?",
        (product_id, job_id),
    )

    if parsed.get("price"):
        from procm.services.pricing import record_price

        record_price(conn, product_id, float(parsed["price"]), source="url_intake")

    return {
        "import_job_id": job_id,
        "supplier_product_id": product_id,
        "status": status,
        "parsed": parsed,
        "error_message": error_message,
    }
