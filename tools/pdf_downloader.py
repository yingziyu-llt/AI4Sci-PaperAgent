"""
PDF downloader and text extractor for academic papers.
Supports arXiv, bioRxiv, and Nature (with fallback).
"""
import os
import re
import tempfile
import requests
from typing import Optional


# Max characters to extract from PDF to avoid LLM context overflow
MAX_PDF_CHARS = 150000
PDF_CACHE_DIR = "/tmp/paper_pdfs"


def _ensure_cache_dir():
    os.makedirs(PDF_CACHE_DIR, exist_ok=True)


def _get_pdf_url(paper_link: str, journal: str) -> Optional[str]:
    """Convert a paper's web link to its PDF download URL."""
    if "arxiv.org" in paper_link:
        # https://arxiv.org/abs/2603.02952 -> https://arxiv.org/pdf/2603.02952
        return paper_link.replace("/abs/", "/pdf/")
    elif "biorxiv.org" in paper_link or "medrxiv.org" in paper_link:
        # https://www.biorxiv.org/content/10.1101/2023.01.01.123456v1
        # -> https://www.biorxiv.org/content/10.1101/2023.01.01.123456v1.full.pdf
        link = paper_link.strip().rstrip("/")
        if link.endswith(".pdf"):
            return link
        # If the link is a landing page content link, append .full.pdf
        if "/content/" in link:
            return link + ".full.pdf"
        return link + ".full.pdf" # Fallback
    elif "nature.com" in paper_link:
        # Nature papers often have: /articles/s41587-026-03040-4
        # PDF: /articles/s41587-026-03040-4.pdf
        link = paper_link.strip().rstrip("/")
        if not link.endswith(".pdf"):
            return link + ".pdf"
        return link
    return None


def _download_pdf(pdf_url: str, timeout: int = 30, retries: int = 2) -> Optional[str]:
    """Download PDF to a temp file, return the file path or None on failure."""
    _ensure_cache_dir()
    
    # Create a safe filename from the URL
    safe_name = re.sub(r'[^\w\-.]', '_', pdf_url.split("/")[-1])
    if not safe_name.endswith(".pdf"):
        safe_name += ".pdf"
    filepath = os.path.join(PDF_CACHE_DIR, safe_name)
    
    # Use cached file if it exists
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return filepath
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) DailyPaperAgent/1.0"
    }
    
    for attempt in range(retries + 1):
        try:
            # Try with SSL verification first, then without on retry
            verify_ssl = (attempt == 0)
            resp = requests.get(
                pdf_url, headers=headers, timeout=timeout, 
                stream=True, verify=verify_ssl
            )
            if resp.status_code != 200:
                print(f"  PDF download failed (HTTP {resp.status_code}): {pdf_url}")
                return None
            
            # Check content type
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower() and "octet-stream" not in content_type.lower():
                print(f"  Not a PDF (Content-Type: {content_type}): {pdf_url}")
                return None
            
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.getsize(filepath) < 1000:
                os.remove(filepath)
                return None
                
            return filepath
        except requests.exceptions.SSLError:
            if attempt < retries:
                print(f"  SSL error, retrying without verification (attempt {attempt + 2})...")
                continue
            print(f"  PDF download SSL error after {retries + 1} attempts: {pdf_url}")
            return None
        except Exception as e:
            print(f"  PDF download error: {e}")
            return None


def _extract_text_from_pdf(filepath: str, max_chars: int = MAX_PDF_CHARS) -> Optional[str]:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("  PyMuPDF not installed, falling back to abstract-only summarization")
        return None
    
    try:
        doc = fitz.open(filepath)
        text_parts = []
        total_chars = 0
        
        for page in doc:
            page_text = page.get_text()
            text_parts.append(page_text)
            total_chars += len(page_text)
            if total_chars >= max_chars:
                break
        
        doc.close()
        full_text = "\n".join(text_parts)
        
        # Clean up common PDF artifacts
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        full_text = re.sub(r'[ \t]{2,}', ' ', full_text)
        
        # Truncate to max_chars
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n...[truncated]"
        
        return full_text if len(full_text) > 100 else None
    except Exception as e:
        print(f"  PDF text extraction error: {e}")
        return None


def download_and_extract_pdf(paper_link: str, journal: str = "") -> Optional[str]:
    """
    Download a paper's PDF and extract its text content.
    
    Returns the extracted text, or None if download/extraction fails.
    Caller should fall back to using the abstract when None is returned.
    """
    pdf_url = _get_pdf_url(paper_link, journal)
    if not pdf_url:
        return None
    
    print(f"  Downloading PDF: {pdf_url}")
    filepath = _download_pdf(pdf_url)
    if not filepath:
        return None
    
    print(f"  Extracting text from PDF...")
    text = _extract_text_from_pdf(filepath)
    if text:
        print(f"  Extracted {len(text)} chars from PDF")
    return text
