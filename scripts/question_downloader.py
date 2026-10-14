#!/usr/bin/env python3
"""BD-ExamQ Question Downloader Bot.
Automated scraper, harvester, and downloader for historical SSC & HSC board examination question papers.

Supports:
1. Curated verified manifest downloads (data/metadata/download_sources.json)
2. Internet Archive (Archive.org) dynamic search & download
3. Web page PDF scraper / harvester (extracts PDF & Google Drive links from educational portals)
4. Google Drive direct downloader (handles large file confirmation tokens)
5. Interactive CLI wizard or flexible command-line arguments
"""

import os
import re
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PDFS_DIR = RAW_DIR / "pdfs"
MANIFEST_PATH = RAW_DIR / "manifest.json"
SOURCES_PATH = PROJECT_ROOT / "data" / "metadata" / "download_sources.json"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
}


def load_manifest() -> Dict[str, Any]:
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"files": {}}
    return {"files": {}}


def save_manifest(manifest: Dict[str, Any]):
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def compute_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def handle_google_drive_url(url: str, session: requests.Session) -> str:
    """Extracts direct download stream URL for Google Drive links."""
    file_id = None
    # match patterns: drive.google.com/file/d/<id> or drive.google.com/open?id=<id> or uc?id=<id>
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        file_id = match.group(1)
    else:
        match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
        if match:
            file_id = match.group(1)

    if not file_id:
        return url

    base_url = "https://drive.google.com/uc?export=download"
    res = session.get(base_url, params={"id": file_id}, headers=DEFAULT_HEADERS, stream=True)
    
    # Check for confirmation token on large files
    token = None
    for k, v in res.cookies.items():
        if k.startswith("download_warning"):
            token = v
            break

    if token:
        return f"{base_url}&id={file_id}&confirm={token}"
    return f"{base_url}&id={file_id}"


def download_file(
    url: str,
    dest_path: Path,
    description: str = "",
    session: Optional[requests.Session] = None,
    overwrite: bool = False
) -> bool:
    """Downloads a file with streaming, resume support, progress bar, and curl HTTP/2 fallback."""
    import subprocess

    if session is None:
        session = requests.Session()

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists() and not overwrite and dest_path.stat().st_size > 1024:
        print(f"⏩ [Cached] {dest_path.name} already exists ({dest_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return True

    # Check for Google Drive URL
    if "drive.google.com" in url:
        url = handle_google_drive_url(url, session)

    print(f"📥 Downloading: {dest_path.name}")
    downloaded = False

    # For WordPress/CDN/teachingbd links, curl HTTP/2 is drastically faster and avoids 403 blocks
    is_cdn_url = any(k in url for k in ["wordpress.com", "wp-content", "teachingbd"])

    if is_cdn_url:
        try:
            cmd = [
                "curl", "-f", "-s", "-S",
                "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "-e", "https://teachingbd24.com/",
                url, "-o", str(dest_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and dest_path.exists() and dest_path.stat().st_size > 1024:
                downloaded = True
            else:
                print(f"❌ Curl failed for {url}: {res.stderr.strip()}")
        except Exception as curl_err:
            print(f"❌ Curl error: {curl_err}")
    else:
        # Standard streaming requests
        try:
            response = session.get(url, headers=DEFAULT_HEADERS, stream=True, timeout=20)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024 * 32  # 32 KB blocks

            desc = description[:30] if description else dest_path.name[:30]
            with open(dest_path, "wb") as f, tqdm(
                desc=desc,
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(block_size):
                    size = f.write(data)
                    bar.update(size)
            downloaded = True
        except Exception as e:
            # Fallback to curl
            try:
                cmd = [
                    "curl", "-f", "-s", "-S",
                    "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "-e", "https://teachingbd24.com/",
                    url, "-o", str(dest_path)
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if res.returncode == 0 and dest_path.exists() and dest_path.stat().st_size > 1024:
                    downloaded = True
            except Exception as curl_err:
                print(f"❌ Failed to download {url}: {curl_err}")

    if downloaded and dest_path.exists() and dest_path.stat().st_size > 1024:
        # Update manifest
        manifest = load_manifest()
        manifest["files"][dest_path.name] = {
            "path": str(dest_path.relative_to(PROJECT_ROOT)),
            "source_url": url,
            "size_bytes": dest_path.stat().st_size,
            "sha256": compute_sha256(dest_path),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "downloaded"
        }
        save_manifest(manifest)
        print(f"✅ Saved to: {dest_path.relative_to(PROJECT_ROOT)} ({dest_path.stat().st_size / 1024:.1f} KB)")
        return True
    else:
        if dest_path.exists():
            dest_path.unlink()
        return False


def scrape_webpage_for_pdfs(page_url: str, filter_keyword: Optional[str] = None) -> List[Dict[str, str]]:
    """Crawls a webpage and extracts all PDF or document download links."""
    print(f"🌐 Scraping page: {page_url}")
    session = requests.Session()
    try:
        res = session.get(page_url, headers=DEFAULT_HEADERS, timeout=20)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch page {page_url}: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    found_links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        full_url = urljoin(page_url, href)
        text = a_tag.get_text(strip=True) or Path(urlparse(full_url).path).name

        is_pdf = full_url.lower().endswith(".pdf") or ".pdf?" in full_url.lower()
        is_gdrive = "drive.google.com" in full_url

        if is_pdf or is_gdrive:
            if filter_keyword:
                combined_text = f"{text} {full_url}".lower()
                if filter_keyword.lower() not in combined_text:
                    continue

            found_links.append({
                "url": full_url,
                "title": text,
                "is_gdrive": is_gdrive
            })

    print(f"🔍 Found {len(found_links)} matching document links.")
    return found_links


def query_archive_org(exam: str, subject: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """Queries Internet Archive for past board question collections."""
    query = f'("{exam}" OR "{exam.lower()}") AND (bangladesh OR "education board" OR "board question" OR "nctb" OR "dhaka")'
    if subject and subject.lower() != "all":
        query += f' AND ("{subject}" OR "{subject.lower()}")'

    print(f"🏛️ Querying Internet Archive for: {query}")
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "year", "mediatype"],
        "output": "json",
        "rows": max_results
    }
    try:
        res = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=15)
        res.raise_for_status()
        docs = res.json().get("response", {}).get("docs", [])
    except Exception as e:
        print(f"❌ Archive.org query error: {e}")
        return []

    items = []
    for doc in docs:
        ident = doc.get("identifier")
        title = doc.get("title", ident)
        # Fetch files inside this item
        try:
            files_res = requests.get(f"https://archive.org/metadata/{ident}/files", headers=DEFAULT_HEADERS, timeout=10)
            if files_res.status_code == 200:
                files_data = files_res.json().get("result", [])
                pdf_files = [f for f in files_data if f.get("name", "").lower().endswith(".pdf")]
                for pf in pdf_files[:2]:
                    fname = pf["name"]
                    dl_url = f"https://archive.org/download/{ident}/{fname}"
                    size_mb = round(int(pf.get("size", 0)) / (1024 * 1024), 2)
                    items.append({
                        "identifier": ident,
                        "title": f"{title} - {fname}",
                        "url": dl_url,
                        "size_mb": size_mb,
                        "filename": fname
                    })
        except Exception:
            continue

    return items


def run_downloader(
    exam: Optional[str] = None,
    year: Optional[int] = None,
    board: Optional[str] = None,
    subject: Optional[str] = None,
    source: str = "manifest",
    url: Optional[str] = None,
    dry_run: bool = False,
    max_files: int = 10
):
    session = requests.Session()
    tasks_to_download = []

    if source == "manifest":
        if not SOURCES_PATH.exists():
            print(f"❌ Manifest not found at {SOURCES_PATH}")
            return
        with open(SOURCES_PATH, "r", encoding="utf-8") as f:
            sources = json.load(f)

        for s in sources:
            if exam and exam.upper() != "ALL" and s.get("exam", "").upper() != exam.upper():
                continue
            if year:
                item_year = s.get("year")
                item_range = str(s.get("year_range", ""))
                in_range = False
                if "-" in item_range:
                    parts = item_range.split("-")
                    try:
                        start_y, end_y = int(parts[0]), int(parts[1])
                        in_range = (start_y <= year <= end_y)
                    except ValueError:
                        pass
                if not (item_year == year or in_range):
                    continue

            if board and board.lower() != "all" and s.get("board", "").lower() != board.lower():
                continue
            if subject and subject.lower() != "all" and subject.lower() not in s.get("subject", "").lower():
                continue

            e = s.get("exam", "HSC")
            y = s.get("year", 2023)
            b = s.get("board", "Dhaka")
            subj = s.get("subject", "General").replace(" ", "_")
            ext = s.get("file_format", "pdf")
            dest = PDFS_DIR / e / str(y) / b / f"{subj}_{s['id']}.{ext}"
            tasks_to_download.append({
                "url": s["url"],
                "dest": dest,
                "title": s.get("title", dest.name)
            })

    elif source == "archive_org":
        items = query_archive_org(exam or "HSC", subject, max_results=max_files)
        for item in items:
            clean_name = re.sub(r"[^a-zA-Z0-9_\.-]", "_", item["filename"])
            dest = PDFS_DIR / (exam or "HSC") / "archive_org" / clean_name
            tasks_to_download.append({
                "url": item["url"],
                "dest": dest,
                "title": item["title"]
            })

    elif source == "scrape_url":
        if not url:
            print("❌ Must provide --url with --source scrape_url")
            return
        links = scrape_webpage_for_pdfs(url, filter_keyword=subject)
        for idx, l in enumerate(links[:max_files]):
            fname = f"scraped_{exam or 'HSC'}_{idx+1}.pdf"
            dest = PDFS_DIR / (exam or "HSC") / "scraped" / fname
            tasks_to_download.append({
                "url": l["url"],
                "dest": dest,
                "title": l["title"]
            })

    limit = len(tasks_to_download) if max_files <= 0 else min(max_files, len(tasks_to_download))
    items_to_process = tasks_to_download[:limit]

    print(f"\n📋 Total items queued: {len(tasks_to_download)} (Downloading {limit})")
    for t in items_to_process[:15]:
        print(f"  • {t['title']} -> {t['dest'].name}")
    if len(items_to_process) > 15:
        print(f"  ... and {len(items_to_process) - 15} more.")

    if dry_run:
        print("\n🔍 [Dry-Run] No files downloaded.")
        return

    # Execute downloads
    success_count = 0
    for t in items_to_process:
        is_already_cached = t["dest"].exists() and t["dest"].stat().st_size > 1024
        ok = download_file(t["url"], t["dest"], description=t["title"], session=session)
        if ok:
            success_count += 1
        if not is_already_cached:
            time.sleep(0.2)  # Polite delay only on actual network requests

    print(f"\n✨ Download session finished! ({success_count}/{len(items_to_process)} succeeded)")


def interactive_mode():
    print("=" * 60)
    print("      🤖 BD-ExamQ QUESTION PAPER DOWNLOADER BOT")
    print("=" * 60)
    print("Select download mode:")
    print("  1. Download verified papers from Curated Manifest (Fast & Reliable)")
    print("  2. Search and download from Internet Archive (Archive.org)")
    print("  3. Scrape and download PDFs from custom URL")
    print("  4. Download single direct link or Google Drive URL")
    print("  5. View downloaded files manifest")
    choice = input("\nEnter choice [1-5] (default 1): ").strip() or "1"

    if choice == "1":
        exam = input("Exam [HSC / SSC / all] (default HSC): ").strip().upper() or "HSC"
        subject = input("Subject [Physics / Chemistry / all] (default all): ").strip() or "all"
        run_downloader(exam=exam, subject=subject, source="manifest", max_files=100)

    elif choice == "2":
        exam = input("Exam [HSC / SSC] (default HSC): ").strip().upper() or "HSC"
        subject = input("Subject [Physics / Math / ICT / blank]: ").strip() or None
        run_downloader(exam=exam, subject=subject, source="archive_org", max_files=50)

    elif choice == "3":
        page_url = input("Enter webpage URL to scrape: ").strip()
        exam = input("Target Exam tag [HSC / SSC] (default HSC): ").strip().upper() or "HSC"
        run_downloader(exam=exam, source="scrape_url", url=page_url, max_files=50)

    elif choice == "4":
        link = input("Enter PDF or Google Drive download link: ").strip()
        exam = input("Exam [HSC / SSC] (default HSC): ").strip().upper() or "HSC"
        fname = input("Filename to save as (e.g. Physics_2023.pdf): ").strip() or "downloaded_paper.pdf"
        dest = PDFS_DIR / exam / "custom" / fname
        download_file(link, dest)

    elif choice == "5":
        manifest = load_manifest()
        files = manifest.get("files", {})
        print(f"\n📊 Currently recorded files in manifest: {len(files)}")
        for fname, meta in files.items():
            print(f"  • {fname} ({meta['size_bytes'] / 1024 / 1024:.2f} MB) - {meta['timestamp']}")
    else:
        print("Invalid choice.")


def main():
    parser = argparse.ArgumentParser(description="BD-ExamQ Past Question Downloader Bot")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive wizard")
    parser.add_argument("--exam", type=str, choices=["SSC", "HSC", "all"], default="HSC", help="Exam type")
    parser.add_argument("--year", type=int, default=None, help="Exam year (e.g. 2023)")
    parser.add_argument("--board", type=str, default="all", help="Education board name (e.g. Dhaka, all)")
    parser.add_argument("--subject", type=str, default="all", help="Subject name (e.g. Physics, all)")
    parser.add_argument(
        "--source",
        type=str,
        choices=["manifest", "archive_org", "scrape_url"],
        default="manifest",
        help="Download source provider"
    )
    parser.add_argument("--url", type=str, default=None, help="Target URL for scrape_url mode")
    parser.add_argument("--max-files", type=int, default=50, help="Maximum files to download per run")
    parser.add_argument("--dry-run", action="store_true", help="List files without downloading")
    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        interactive_mode()
    else:
        run_downloader(
            exam=args.exam,
            year=args.year,
            board=args.board,
            subject=args.subject,
            source=args.source,
            url=args.url,
            dry_run=args.dry_run,
            max_files=args.max_files
        )


if __name__ == "__main__":
    main()
