# 📚 Manga & Manhwa Downloader

![nhbadge](https://img.shields.io/badge/made%20for%20neighborhood-bf8f73?style=for-the-badge&logo=hackclub&logoColor=ffffff)

A full-stack WIP (work-in-progress) project that allows users to search manga/manhwa titles from multiple sources, view available chapters, and prepare for chapter downloading with **background task processing**.

> ⚠️ This project is under **active development**.
> 
> Currently working sources:
> - MangaDex ✅
> - Bato ✅
> - Mangapill ✅
> - Mangahere ✅
> - Weebcentral ✅
> - Manhuaus ✅ 
> - Yakshascans ✅
> - Asurascan ✅
> - Kunmanga ✅
> - Toonily 🔄 *working on downloads*
> - Toongod 🔄 *working on downloads*

---

## ✨ Features

### Frontend (React)

- 🔍 Title search from multiple sources like MangaDex, Asurascan, Toonily, etc.
- 🌗 Fully functional dark/light mode toggle.
- 🎨 Smooth animations via Framer Motion.
- 📚 Shows available chapters grouped by volume with dynamic dropdowns.
- ✅ Select individual chapters or select all in preparation for downloads.
- 📱 Responsive and visually modern UI with Tailwind CSS.
- ✨ Live source status checking.
- 🔄 **Real-time background task monitoring** with progress tracking.
- 📊 **Task status dashboard** showing active downloads.
- 📏 **Chapter range slider** for quick chapter selection.
- 📦 **Format selection dropdown** (PDF, CBZ, CBR, EPUB) connected to download button.

### Backend (FastAPI + Celery)

- 📡 API endpoints:
  - `/search/` – Fetch titles from supported sources.
  - `/chapters/` – Retrieve volume and chapter information for a given title.
  - `/download` - **Start background download tasks**.
  - `/download/status/{task_id}` - **Check task progress**.
  - `/download/file/{task_id}` - **Download completed files**.
  - `/proxy-image` - Proxy cover art image through backend.
  - `/status` - Check health status of all sources.
  - `/health` - **System health check**.
- 🔄 **Background task processing** with Celery and Redis.
- 📥 **Asynchronous download architecture**.
- 🧼 Clean HTML scraping with BeautifulSoup.
- 🗑️ **Automatic cleanup** of temporary files.
- 📄 **Multiple format support**: PDF, CBZ, CBR, EPUB.

---

## 🧰 Tech Stack

| Layer     | Tech                                                                 |
|-----------|----------------------------------------------------------------------|
| Frontend  | Vite, React, Tailwind CSS, Framer Motion, FontAwesome                |
| Backend   | FastAPI, Uvicorn, Celery, Redis, BeautifulSoup, img2pdf, requests, aiohttp |
| Queue     | Redis (broker), Celery (task queue)                                  |
| Container | Docker, Docker Compose                                               |

---

## 🚀 Getting Started

### 🔧 Prerequisites

- Node.js (>=14)
- Python (>=3.10)
- npm or yarn
- pip
- **Redis** (for background task processing)
- Self-hosted [Consumet API](https://github.com/consumet/api.consumet.org)
- **Docker & Docker Compose** (optional, for containerized setup)

---

## 🐳 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/manga-downloader.git
cd manga-downloader/server

# Start all services (web, worker, redis) with your desired port
WEB_PORT=8000 docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

For frontend setup, see the manual setup instructions below.

---

## 📦 Manual Setup

### Backend Setup

Before running the backend, you need to create a `.env` file in the `server` directory with the following keys:

```env
MANGAPI_URL=<address_of_your_self_hosted_consumet_api>

# Redis Configuration (for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from [Redis.io](https://redis.io/download)

#### Setup Backend

```bash
# Clone repository
git clone https://github.com/yourusername/manga-downloader.git
cd manga-downloader/server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install Python dependencies
pip install -r requirements.txt

# Terminal 1: Start Celery worker
python celery_worker.py

# Terminal 2: Start FastAPI server
uvicorn main:app --reload --port <your_port>

# Terminal 3: Start frontend (see below)
```

---

### 🎨 Frontend Setup

Before running the frontend, you also need to create a `.env` file in the `client` directory with the same keys:

```env
VITE_API_URL=http://localhost:<your_port>
```

Then run:

```bash
cd ../client  # or wherever your React code lives

# Install Node dependencies
npm install

# Start development server
npm run dev
```

---

## 🔄 Background Task System

The application now uses **Celery with Redis** for background task processing:

### How it works:
1. **User selects chapters** and chooses format (PDF, CBZ, CBR, EPUB)
2. **Task is queued** in Redis via Celery
3. **Background worker** processes the download
4. **Real-time progress** is shown in the UI
5. **File is available** for download when complete
6. **Temporary files** are automatically cleaned up

### Benefits:
- ⚡ **Non-blocking UI** - users can continue browsing while downloads process
- 📊 **Progress tracking** - real-time status updates
- 🔄 **Scalable** - multiple workers can handle concurrent downloads
- 🛡️ **Reliable** - failed tasks can be retried
- 🗑️ **Clean** - automatic cleanup prevents disk space issues
- 📄 **Flexible** - support for multiple output formats

### Monitoring:
- **Health Check**: `http://localhost:8000/health`
- **Task Status**: Visible in the UI task dashboard

---

## 🛠️ To-Do

- ✅ Title search from multiple sources
- ✅ Animated dark mode toggle
- ✅ Display chapter list under each comic with dropdown
- ✅ Chapter selection UI
- ✅ Implement backend support for chapter image retrieval
- ✅ Add "Download" functionality (PDF/image bundles)
- ✅ Add live source status checker
- ✅ Deploy frontend & backend
- ✅ **Background task processing with Celery**
- ✅ **Real-time progress tracking**
- ✅ **Automatic file cleanup**
- ✅ **Chapter range slider** for quick selection
- ✅ **Format selection dropdown** (PDF, CBZ, CBR, EPUB)
- ✅ **Docker configuration** for easy deployment
- 🔄 Write tests and error handling
- 🔄 Check [TODO.md](./TODO.md) to see future features/improvements

---

## 🤝 Contributions

Pull requests, suggestions, and feedback are welcome! Open an issue or fork the project to get started.

---

## 👨‍💻 Author

Created by [Infinity](https://github.com/serplay) — feel free to reach out or fork this project!

[![Neighborhood Badge](https://images.fillout.com/orgid-81/flowpublicid-2d6RsxRU3ius/widgetid-gHXJ/wLL8YM3u5TEHNwmmey7cHo/summer25.png?a=4hit9PajYRUKJJYwW78gvU)](http://neighborhood.hackclub.com/)

---


---

### Support

If you enjoy this project and want to support more builds, you can optionally [support me on Ko-fi](https://ko-fi.com/yorusayano).
