import os
from typing import Any, Dict, List

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI(title="Streaming Nova Manga API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MANGAPI_URL = os.environ.get("MANGAPI_URL", "").rstrip("/")


SOURCE_URLS: Dict[str, str] = {
    "0": "https://api.mangadex.org",
    "7": "https://mangahere.cc",
    "8": "https://mangapill.com",
    "9": "https://bato.si",
}

BATO_SEARCH_QUERY = """
query Search($select: Search_Comic_Select) {
  get_search_comic(select: $select) {
    items {
      data {
        id
        name
        urlCover300
      }
    }
  }
}
"""

BATO_CHAPTERS_QUERY = """
query Chapters($comicId: ID!, $start: Int) {
  get_comic_chapterList(comicId: $comicId, start: $start) {
    data {
      id
      volume
      serial
      order
    }
  }
}
"""

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


def _ensure_consumet() -> None:
    if not MANGAPI_URL:
        raise HTTPException(
            status_code=500,
            detail="MANGAPI_URL is not configured. Add it in Vercel env variables.",
        )


def _as_sorted_list(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Frontends usually expect arrays; this normalizes numeric-key dicts.
    return [results[k] for k in sorted(results.keys(), key=lambda x: int(x))]


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": "Streaming Nova API online",
        "supported_sources": list(SOURCE_URLS.keys()),
        "endpoints": [
            "/search",
            "/chapters",
            "/read/chapter",
            "/proxy-image",
            "/health",
            "/status",
        ],
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/status")
def status() -> Dict[str, Dict[str, str]]:
    # Lightweight source status indicator.
    return {"status": {k: "ok" for k in SOURCE_URLS.keys()}}


@app.get("/search")
def search(title: str = Query(...), source: str = Query(...)) -> Dict[str, Any]:
    try:
        if source == "0":
            r = requests.get(
                "https://api.mangadex.org/manga",
                params={"title": title, "includes[]": ["cover_art"]},
                timeout=20,
            )
            r.raise_for_status()
            data = r.json().get("data", [])
            items: Dict[str, Any] = {}
            idx = 0
            for comic in data:
                comic_id = comic.get("id")
                if not comic_id:
                    continue
                title_map = comic.get("attributes", {}).get("title", {"en": "Unknown"})
                rel = comic.get("relationships", [])
                cover_name = ""
                for entry in rel:
                    if entry.get("type") == "cover_art":
                        cover_name = entry.get("attributes", {}).get("fileName", "")
                        break
                if not cover_name:
                    continue
                cover = (
                    f"/proxy-image?url=https://uploads.mangadex.org/covers/"
                    f"{comic_id}/{cover_name}.256.jpg&hd="
                )
                items[str(idx)] = {
                    "id": comic_id,
                    "title": title_map,
                    "cover_art": cover,
                    "availableLanguages": comic.get("attributes", {}).get(
                        "availableTranslatedLanguages", ["en"]
                    ),
                }
                idx += 1
            return {"results": _as_sorted_list(items)}

        if source == "7":
            _ensure_consumet()
            r = requests.get(f"{MANGAPI_URL}/manga/mangahere/{title}", timeout=20)
            r.raise_for_status()
            data = r.json().get("results", [])
            results = [
                {
                    "id": x.get("id"),
                    "title": {"en": x.get("title", "Unknown")},
                    "cover_art": f"/proxy-image?url={x.get('image','')}&hd={x.get('headerForImage','')}",
                    "availableLanguages": ["en"],
                }
                for x in data
                if x.get("id")
            ]
            return {"results": results}

        if source == "8":
            _ensure_consumet()
            r = requests.get(f"{MANGAPI_URL}/manga/mangapill/{title}", timeout=20)
            r.raise_for_status()
            data = r.json().get("results", [])
            results = [
                {
                    "id": x.get("id"),
                    "title": {"en": x.get("title", "Unknown")},
                    "cover_art": f"/proxy-image?url={x.get('image','')}&hd=https://mangapill.com",
                    "availableLanguages": ["en"],
                }
                for x in data
                if x.get("id")
            ]
            return {"results": results}

        if source == "9":
            r = requests.post(
                "https://bato.si/ap2/",
                json={
                    "query": BATO_SEARCH_QUERY,
                    "variables": {"select": {"word": title}, "operationName": "Search"},
                },
                timeout=20,
            )
            r.raise_for_status()
            data = r.json().get("data", {}).get("get_search_comic", {}).get("items", [])
            results = []
            for item in data:
                d = item.get("data", {})
                if not d.get("id"):
                    continue
                results.append(
                    {
                        "id": d.get("id"),
                        "title": {"en": d.get("name", "Unknown")},
                        "cover_art": f"https://bato.si{d.get('urlCover300', '')}",
                        "availableLanguages": ["en"],
                    }
                )
            return {"results": results}

        raise HTTPException(status_code=400, detail="Unsupported source")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chapters")
def chapters(id: str = Query(...), source: str = Query(...)) -> Dict[str, Any]:
    try:
        if source == "0":
            r = requests.get(
                f"https://api.mangadex.org/manga/{id}/aggregate",
                params={"translatedLanguage[]": ["en"]},
                timeout=20,
            )
            r.raise_for_status()
            volumes = r.json().get("volumes", {})
            out: Dict[str, Any] = {}
            for vol, vol_data in volumes.items():
                vol_name = f"Vol {vol}"
                chapters_map = vol_data.get("chapters", {})
                out[vol_name] = {
                    "volume": vol_name,
                    "chapters": {
                        str(i): {
                            "id": c.get("id"),
                            "chapter": c.get("chapter", str(i)),
                        }
                        for i, c in enumerate(chapters_map.values())
                        if c.get("id")
                    },
                }
            return out

        if source in ("7", "8"):
            _ensure_consumet()
            provider = "mangahere" if source == "7" else "mangapill"
            r = requests.get(
                f"{MANGAPI_URL}/manga/{provider}/info",
                params={"id": id},
                timeout=20,
            )
            r.raise_for_status()
            chapters_raw = r.json().get("chapters", [])
            return {
                "Vol 1": {
                    "volume": "Vol 1",
                    "chapters": {
                        str(i): {"id": c.get("id"), "chapter": c.get("chapter", str(i))}
                        for i, c in enumerate(chapters_raw)
                        if c.get("id")
                    },
                }
            }

        if source == "9":
            start = 1
            last_order = -1
            grouped: Dict[str, Dict[str, Any]] = {}
            while True:
                r = requests.post(
                    "https://bato.si/ap2/",
                    json={
                        "query": BATO_CHAPTERS_QUERY,
                        "variables": {"comicId": id, "start": start, "operationName": "Chapters"},
                    },
                    timeout=20,
                )
                r.raise_for_status()
                data = r.json().get("data", {}).get("get_comic_chapterList", [])
                if not data:
                    break
                page_last = data[-1]["data"].get("order")
                if page_last == last_order:
                    break
                last_order = page_last
                for row in data:
                    d = row.get("data", {})
                    vol = f"Vol {d.get('volume')}" if d.get("volume") is not None else "Vol 1"
                    if vol not in grouped:
                        grouped[vol] = {"volume": vol, "chapters": {}}
                    chapter_key = str(len(grouped[vol]["chapters"]))
                    grouped[vol]["chapters"][chapter_key] = {
                        "id": str(d.get("id")),
                        "chapter": str(d.get("serial", chapter_key)),
                    }
                start = int(last_order) + 1 if last_order is not None else start + 1
            return grouped

        raise HTTPException(status_code=400, detail="Unsupported source")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/read/chapter")
def read_chapter(chapter_id: str = Query(...), source: str = Query(...)) -> Dict[str, Any]:
    try:
        if source == "0":
            r = requests.get(f"https://api.mangadex.org/at-home/server/{chapter_id}", timeout=20)
            r.raise_for_status()
            data = r.json()
            base = data.get("baseUrl")
            chapter = data.get("chapter", {})
            hash_url = chapter.get("hash")
            pages = chapter.get("data", [])
            if not base or not hash_url:
                return {"pages": []}
            return {
                "pages": [
                    {"url": f"{base}/data/{hash_url}/{img}", "referer": ""} for img in pages
                ]
            }

        if source in ("7", "8"):
            _ensure_consumet()
            provider = "mangahere" if source == "7" else "mangapill"
            r = requests.get(
                f"{MANGAPI_URL}/manga/{provider}/read",
                params={"chapterId": chapter_id},
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
            if source == "7":
                pages = [
                    {
                        "url": p.get("img"),
                        "referer": p.get("headerForImage", {}).get("Referer", ""),
                    }
                    for p in data
                    if p.get("img")
                ]
            else:
                pages = [
                    {"url": p.get("img"), "referer": "https://mangapill.com"}
                    for p in data
                    if p.get("img")
                ]
            return {"pages": pages}

        if source == "9":
            r = requests.post(
                "https://bato.si/ap2/",
                json={
                    "query": BATO_IMAGES_QUERY,
                    "variables": {"getChapterNodeId": chapter_id, "operationName": "Images"},
                },
                timeout=20,
            )
            r.raise_for_status()
            images = (
                r.json()
                .get("data", {})
                .get("get_chapterNode", {})
                .get("data", {})
                .get("imageFile", {})
                .get("urlList", [])
            )
            return {"pages": [{"url": x, "referer": ""} for x in images]}

        raise HTTPException(status_code=400, detail="Unsupported source")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/proxy-image")
def proxy_image(url: str = Query(...), hd: str = Query("")) -> StreamingResponse:
    try:
        headers = {"Referer": hd} if hd else None
        response = requests.get(url, headers=headers, stream=True, timeout=20)
        response.raise_for_status()
        return StreamingResponse(
            response.iter_content(chunk_size=1024 * 64),
            media_type=response.headers.get("content-type", "image/jpeg"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy image failed: {e}")
