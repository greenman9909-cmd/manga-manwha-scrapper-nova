import requests as req
import re
import os
from dotenv import load_dotenv
from Manga.Bato import Bato
from Manga.Asurascans import Asura
from Manga.Manhuaus import Manhuaus
from Manga.Yakshascans import Yaksha
from Manga.Weebcentral import Weeb
from Manga.MangaDex import MangaDex
from Manga.Kunmanga import Kunmanga
from Manga.Toonily import Toonily
from Manga.Toongod import Toongod
from Manga.Mangapill import Mangapill
from Manga.Mangahere import Mangahere

load_dotenv()

MANGAPI_URL = os.environ.get("MANGAPI_URL")

BATO_IMAGES_QUERY = """
    query Images($getChapterNodeId: ID!) {
      get_chapterNode(id: $getChapterNodeId) {
        data {
          imageFile {
            urlList
          }
        }
      }
    }
"""

def search(title, source):
    try:
        source = int(source)
    except:
        raise ValueError(f"Invalid source: {source}. Please choose a valid source.")
    
    match source:
        case 0: #MangaDex
            return MangaDex.search(title)

        case 1: #Manhuaus
            return Manhuaus.search(title)

        case 2: #Yakshascans
            return Yaksha.search(title)
        
        case 3: #Asurascan
            return Asura.search(title)
        
        case 4: #Kunmanga
            return Kunmanga.search(title)
        case 5: #Toonily
            return Toonily.search(title)
        case 6: #Toongod
            return Toongod.search(title)
        case 7: #Mangahere
            return Mangahere.search(title)

        case 8: #Mangapill
            return Mangapill.search(title)

        case 9: #Bato
            return Bato.search(title)
                
        case 10: # Weebcentral
            return Weeb.search(title)
        
        case _:
            raise ValueError(f"Invalid source: {source}. Please choose a valid source.")
    return

def get_chapters(id: str, source: int):
    try:
        source = int(source)
    except:
        raise ValueError(f"Invalid source: {source}. Please choose a valid source.")
        
    match source:
        case 0: #MangaDex
            return MangaDex.get_chapters(id)

        case 1: #Manhuaus
            return Manhuaus.get_chapters(id)

        case 2:  # Yakshascans
            return Yaksha.get_chapters(id)
            
        case 3:  # Asurascan
            return Asura.get_chapters(id)

        case 4:  # Kunmanga
            return Kunmanga.get_chapters(id)
        case 5:  # Toonily
            return Toonily.get_chapters(id)
        case 6:  # Toongod
            return Toongod.get_chapters(id)
        case 7:  # Mangahere
            return Mangahere.get_chapters(id)

        case 8:  # Mangapill
            return Mangapill.get_chapters(id)

        case 9:  # Bato
            return Bato.get_chapters(id)
            
        case 10:  # Weebcentral
            return Weeb.get_chapters(id)

        case _:
            raise ValueError(f"Invalid source: {source}. Please choose a valid source.")


def get_chapter_pages(chapter_id: str, source: int):
    try:
        source = int(source)
    except:
        raise ValueError(f"Invalid source: {source}. Please choose a valid source.")

    if not chapter_id:
        raise ValueError("chapter_id cannot be empty")

    # MangaDex
    if source == 0:
        response = req.get(f"https://api.mangadex.org/at-home/server/{chapter_id}", timeout=15)
        response.raise_for_status()
        data = response.json()
        base_url = data.get("baseUrl")
        chapter_data = data.get("chapter", {})
        hash_url = chapter_data.get("hash")
        images = chapter_data.get("data", [])
        if not base_url or not hash_url or not images:
            raise Exception("No pages found for this chapter")
        return {"pages": [{"url": f"{base_url}/data/{hash_url}/{img}", "referer": ""} for img in images]}

    # Mangahere
    if source == 7:
        response = req.get(f"{MANGAPI_URL}/manga/mangahere/read", params={"chapterId": chapter_id}, timeout=15)
        response.raise_for_status()
        data = response.json()
        pages = []
        for page in data:
            image_url = page.get("img")
            referer = page.get("headerForImage", {}).get("Referer", "")
            if image_url:
                pages.append({"url": image_url, "referer": referer})
        if not pages:
            raise Exception("No pages found for this chapter")
        return {"pages": pages}

    # Mangapill
    if source == 8:
        response = req.get(f"{MANGAPI_URL}/manga/mangapill/read", params={"chapterId": chapter_id}, timeout=15)
        response.raise_for_status()
        data = response.json()
        pages = [{"url": page.get("img"), "referer": "https://mangapill.com"} for page in data if page.get("img")]
        if not pages:
            raise Exception("No pages found for this chapter")
        return {"pages": pages}

    # Bato
    if source == 9:
        response = req.post(
            "https://bato.si/ap2/",
            json={
                "query": BATO_IMAGES_QUERY,
                "variables": {"getChapterNodeId": chapter_id, "operationName": "Images"},
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        images = data.get("data", {}).get("get_chapterNode", {}).get("data", {}).get("imageFile", {}).get("urlList", [])
        if not images:
            raise Exception("No pages found for this chapter")
        return {"pages": [{"url": img, "referer": ""} for img in images]}

    raise ValueError("Reader mode is currently supported for sources: 0, 7, 8, 9")
        