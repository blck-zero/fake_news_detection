# Fake News Detection System (Full Stack + ML)

Detect whether a news article is **REAL** or **FAKE** using an **NLP + TF-IDF + Logistic Regression** model, with:
- `POST /predict-text` for text-based detection
- `POST /predict-url` for URL-based detection (scrape -> predict)
- `GET /history` for stored prediction history
- `GET /admin/stats` for aggregate admin stats

Frontend is a responsive React + Tailwind UI. Backend is Flask with SQLite persistence.

---

## Project Structure

```text
fake-news-project/
├── backend/
│   ├── app.py
│   ├── model/
│   │   ├── train.py
│   │   └── artifacts/        (saved model + vectorizer)
│   ├── utils/
│   ├── routes/
│   ├── services/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   └── index.html
└── README.md
```

---

## Backend (Flask + SQLite + ML)

### 1) Create & activate a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Train (or re-train) the model

The repo includes a small sample dataset for quick testing:
`backend/model/data/sample_dataset.csv`

Train and save artifacts to:
`backend/model/artifacts/`

```bash
python -m backend.model.train \
  --csv backend/model/data/sample_dataset.csv \
  --out-dir backend/model/artifacts
```

> For a larger dataset, provide a CSV with:
> - a text column named `text` (or `statement`, `content`, `article`)
> - a label column named `label` (or `target`, `class`)
> - label values such as `true/false`, `real/fake`, or `1/0`

### 4) Run the backend

```bash
export PORT=5000
export DATABASE_URL="sqlite:///fake_news.db"
# For stricter CORS, set your deployed frontend origin (optional)
# export FRONTEND_ORIGIN="http://localhost:5173"
python -m backend.app
```

Backend health check:
- `GET http://localhost:5000/health`

---

## Frontend (React + Tailwind)

### 1) Install dependencies

```bash
cd frontend
npm install
```

### 2) Run the frontend

Since the backend is on a different port, you must set `VITE_API_BASE_URL`:

```bash
export VITE_API_BASE_URL="http://localhost:5000"
npm run dev
```

Frontend:
- `http://localhost:5173`

---

## API Reference

### `POST /predict-text`

Request body:
```json
{ "text": "paste news article text here..." }
```

Response:
```json
{
  "prediction": "REAL",
  "confidence": 83.12,
  "sentiment": "positive",
  "keywords": ["keyword1", "keyword2", "..."]
}
```

### `POST /predict-url`

Request body:
```json
{ "url": "https://example.com/news-article" }
```

Response includes extracted article text:
```json
{
  "prediction": "FAKE",
  "confidence": 67.42,
  "sentiment": "neutral",
  "keywords": ["..."],
  "extracted_text": "scraped article content..."
}
```

### `GET /history`

Response:
```json
{
  "history": [
    {
      "id": 1,
      "created_at": "2026-04-16T12:34:56.000Z",
      "input_type": "text",
      "input_value": "....",
      "extracted_text": null,
      "prediction": "REAL",
      "confidence": 64.9,
      "sentiment": "neutral",
      "keywords": ["..."]
    }
  ]
}
```

### `GET /admin/stats`

Response:
```json
{
  "total_predictions": 123,
  "fake_count": 40,
  "real_count": 83,
  "fake_percentage": 32.52,
  "real_percentage": 67.48,
  "input_type_breakdown": { "text": 80, "url": 43 },
  "recent": [ ... ]
}
```

---

## Deployment

### Backend on Render

1. Create a Render web service from this repository.
2. Ensure the environment variables are set:
   - `PORT` (Render provides this)
   - `DATABASE_URL` (set to a writable location; SQLite is file-based)
   - `FRONTEND_ORIGIN` = your Vercel frontend URL (recommended)
3. Use a start command like:

```bash
gunicorn "backend.app:create_app()" -b 0.0.0.0:$PORT
```

4. Confirm that `backend/model/artifacts/` is present in the deployed build output.
   - This repo includes generated artifacts after running the training command.
   - If you prefer training during deployment, run the training command as a Render build step instead.

> Note on SQLite in production:
> SQLite works well for demos, but for a production multi-instance setup consider a managed DB (or migrate to MongoDB).

### Frontend on Vercel

1. Import the repo into Vercel.
2. Point Vercel to the `frontend/` directory for the React project build.
3. Build command:
   - `npm run build`
4. Set environment variable:
   - `VITE_API_BASE_URL` to your Render backend URL (e.g. `https://your-render-backend.onrender.com`)

---

## One-click deploy on Render (Blueprint)

This repo includes `render.yaml`, which deploys the **backend** on Render (Blueprint).

- **Backend**: Python web service (`gunicorn`). On the free plan, SQLite is **ephemeral** (no persistent disk).

After the backend deploy, set these in the Render dashboard:

- **Backend (`fake-news-backend`)**: set `FRONTEND_ORIGIN` to your Vercel frontend URL for stricter CORS (optional)

For Vercel, this repo includes `frontend/vercel.json` so React Router routes work on refresh/deep links.

---

## Notes / Troubleshooting

- If you get `model_missing`, run the training command to generate `backend/model/artifacts/model.joblib` and `vectorizer.pkl`.
- URL scraping depends on network access and the target site HTML structure.
- CORS is enabled in the backend for all routes; set `FRONTEND_ORIGIN` for stricter deployments.

