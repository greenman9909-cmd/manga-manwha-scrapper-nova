# Vercel API Deployment

This repo is prepared to deploy a public API on Vercel using `api/index.py`.

## 1) Push to your GitHub repository

```bash
git remote add origin https://github.com/greenman9909-cmd/manga-manwha-scrapper-nova.git
git branch -M main
git add .
git commit -m "Add Vercel API deployment setup"
git push -u origin main
```

## 2) Create project on Vercel

1. Go to [Vercel](https://vercel.com/new)
2. Import `greenman9909-cmd/manga-manwha-scrapper-nova`
3. Framework preset: `Other`
4. Root directory: repository root

## 3) Add environment variables

Set this variable in Vercel Project Settings -> Environment Variables:

- `MANGAPI_URL` = URL of your Consumet-compatible API (for sources 7 and 8)

Example:

```env
MANGAPI_URL=https://your-consumet-instance.example.com
```

## 4) Deploy

Click `Deploy`.

After deploy, your API base URL will look like:

`https://your-project-name.vercel.app/api`

## 5) Test endpoints

- `GET /api/health`
- `GET /api/search?title=one%20piece&source=0`
- `GET /api/chapters?id=<comic-id>&source=0`
- `GET /api/read/chapter?chapter_id=<chapter-id>&source=0`

## Supported sources in this Vercel API

- `0` MangaDex
- `7` Mangahere (requires `MANGAPI_URL`)
- `8` Mangapill (requires `MANGAPI_URL`)
- `9` Bato

