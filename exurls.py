#!/usr/bin/env python3
"""
A utility to extract all URLs from a given webpage, separating them into internal and external links.
Uses BeautifulSoup for parsing and requests for fetching content.
"""

import argparse
import os
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def extract_links(url: str) -> list[str]:
    """
    Fetches the content of a URL and extracts all valid absolute HTTP/HTTPS links.
    
    Args:
        url (str): The URL of the webpage to scrape.
        
    Returns:
        list[str]: A sorted list of unique absolute URLs.
    """
    with requests.Session() as session:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag.get("href").strip()
        if href:
            abs_url = urljoin(url, href)
            parsed = urlparse(abs_url)
            if parsed.scheme in ("http", "https"):
                links.add(abs_url)

    return sorted(links)


def split_internal_external(base_url: str, links: list[str]) -> tuple[list[str], list[str]]:
    """
    Categorizes a list of links into internal (same domain) and external (different domain).
    
    Args:
        base_url (str): The URL of the source page to determine the base domain.
        links (list[str]): The list of URLs to categorize.
        
    Returns:
        tuple[list[str], list[str]]: A tuple containing (internal_links, external_links).
    """
    base_domain = urlparse(base_url).netloc

    internal = []
    external = []

    for link in links:
        if urlparse(link).netloc == base_domain:
            internal.append(link)
        else:
            external.append(link)

    return internal, external


def save_links(out_dir: str, filename: str, links: list[str]) -> None:
    """
    Saves a list of links to a text file.
    
    Args:
        out_dir (str): The directory where the file will be saved.
        filename (str): The name of the output file.
        links (list[str]): The list of links to write.
    """
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")


def main():
    """
    Main entry point: handles CLI arguments, fetches links, and saves them to files.
    """
    parser = argparse.ArgumentParser(description="Extract and save all URLs from a webpage")
    parser.add_argument("url", nargs="?", help="Target URL (e.g., https://example.com)")
    parser.add_argument("-o", "--out", default="output", help="Output directory (default: 'output')")

    args = parser.parse_args()

    # Handle interactive input if URL is not provided as an argument
    target_url = args.url or input("Enter URL: ").strip()
    if not target_url.startswith(("http://", "https://")):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)

    print(f"Fetching links from: {target_url}...")
    try:
        links = extract_links(target_url)
    except Exception as e:
        print(f"Failed to fetch or parse URL: {e}", file=sys.stderr)
        sys.exit(1)

    if not links:
        print("No links found on the page.")
        return

    internal, external = split_internal_external(target_url, links)

    save_links(args.out, "all_links.txt", links)
    save_links(args.out, "internal_links.txt", internal)
    save_links(args.out, "external_links.txt", external)

    print(f"\nSummary:")
    print(f"  Total links     : {len(links)}")
    print(f"  Internal links  : {len(internal)}")
    print(f"  External links  : {len(external)}")
    print(f"  Results saved to: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
