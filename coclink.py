#!/data/data/com.termux/files/usr/bin/python
"""
Scrape Clash of Clans TH18 base layout links from YouTube channels.

This module uses the YouTube Data API to find recent videos from specific
Clash of Clans channels, extracts TH18 layout links from their descriptions,
and generates an HTML report of the findings.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import regex as re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from pathlib import Path

# Load API Key
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Configuration
CHANNELS: Dict[str, str] = {
    "Blueprint_CoC": "UCQJJGSWnPUCb8uKV_MoJeOA",
    "iTzu": "UCLKKvlo0yK8OgWvjCiZQ3sA",
    "Clash_Champs": "UC_mD8S6pWpSstY3mXJ9nEqw",
}


def get_videos(youtube: Any, channel_id: str) -> List[Dict[str, str]]:
    """
    Fetch recent videos from a specific YouTube channel.

    Args:
        youtube: The YouTube API client.
        channel_id: The ID of the channel to search.

    Returns:
        A list of dictionaries containing video title, description, and URL.
    """
    # Calculate RFC3339 date for 30 days ago
    past_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    videos: List[Dict[str, str]] = []
    try:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            publishedAfter=past_date,
            maxResults=50,
            order="date",
            type="video",
        )

        while request:
            response = request.execute()
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                # Fetch full description (search only gives a snippet)
                video_details = youtube.videos().list(part="snippet", id=video_id).execute()

                if not video_details.get("items"):
                    continue

                snippet = video_details["items"][0]["snippet"]
                videos.append(
                    {
                        "title": snippet["title"],
                        "description": snippet["description"],
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    }
                )

            request = youtube.search().list_next(request, response)
            if len(videos) > 100:
                break  # Safety limit
    except Exception as e:
        print(f"Error fetching videos for channel {channel_id}: {e}")
        
    return videos


def extract_th18_links(description: str) -> List[str]:
    """
    Extract Clash of Clans layout links from a video description if they relate to TH18.

    Args:
        description: The video description text.

    Returns:
        A list of layout links found.
    """
    # Regex to find CoC layout links
    pattern = r"(https?://link\.clashofclans\.com/[^\s]+)"
    links = re.findall(pattern, description)
    # Filter for TH18 context or actual layout IDs containing TH18
    return [l for l in links if "TH18" in l.upper() or "TH18" in description.upper()]


def create_html(channel_name: str, base_data: List[Dict[str, Any]]) -> None:
    """
    Generate an HTML file listing the found base layouts.

    Args:
        channel_name: The name of the YouTube channel.
        base_data: A list of found bases and their sources.
    """
    date_str = datetime.now().strftime("%d-%m-%Y")
    dir_path = Path(f"output/{date_str}_{channel_name}")
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / "bases.html"

    html_content = f"""
    <html>
    <head>
        <title>{channel_name} TH18 Bases</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #f4f4f4; }}
            .card {{ background: white; margin-bottom: 15px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            a {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
            .vid-ref {{ font-size: 0.9em; color: #555; }}
        </style>
    </head>
    <body>
        <h1>TH18 Bases from {channel_name} (Last 30 Days)</h1>
    """

    for item in base_data:
        html_content += f"""
        <div class="card">
            <h3>{item["title"]}</h3>
            <p class="vid-ref">Source: <a href="{item["video_url"]}" target="_blank">Watch Video</a></p>
            <ul>
        """
        for link in item["links"]:
            html_content += f'<li><a href="{link}">Get Base Layout</a></li>'
        html_content += "</ul></div>"

    html_content += "</body></html>"

    try:
        file_path.write_text(html_content, encoding="utf-8")
        print(f"Generated: {file_path}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")


def main() -> None:
    """
    Main entry point for the scraper.
    """
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY not found in .env file.")
        return

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return

    for name, cid in CHANNELS.items():
        print(f"Processing {name}...")
        vids = get_videos(youtube, cid)
        results: List[Dict[str, Any]] = []

        for v in vids:
            links = extract_th18_links(v["description"])
            if links:
                results.append(
                    {
                        "title": v["title"],
                        "video_url": v["url"],
                        "links": list(set(links)),  # Unique links
                    }
                )

        if results:
            create_html(name, results)
        else:
            print(f"No TH18 links found for {name}.")


if __name__ == "__main__":
    main()
