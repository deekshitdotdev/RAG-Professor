# Docbench — Offline Document Assistant

Upload one PDF or TXT file at a time, ask questions about it, get streamed
answers with page citations — entirely on your own machine after setup.
No internet is used at query time.

Built and tuned specifically for your machine:

| Component | Yours            | Notes |
|-----------|-------------------|-------|
| GPU       | RTX 3050 Laptop (6GB VRAM) | LLM runs here via Ollama |
| RAM       | 16GB DDR5 (⚠ only 833MB free when checked — see note below) | Embeddings run here |
| CPU       | Intel, Acer Nitro V15 | |
| OS        | Windows 11 Home  | |

> **Before you do anything else:** your `systeminfo` showed only 833MB of
> RAM free and 26GB of virtual memory (page file) in use out of 27GB
> available. That's heavy memory pressure — almost certainly from Brave
> browser tabs, based on your `nvidia-smi` output. Close what you don't
> need before running this. No RAG stack will feel fast if Windows is
> already swapping to disk.

---

## 1. One-time setup

### 1.1 Python
Install Python 3.10 or 3.11 (3.12+ can have wheel-availability issues with
some of these packages). Confirm with:
```
python --version
```

### 1.2 Ollama (runs the LLM on your GPU)
Your `nvidia-smi` output shows `llama-server.exe` already running, so
Ollama is likely already installed. If not, get it from https://ollama.com/download.

Pull both models (one-time downloads, needs internet):
```
ollama pull qwen3:8b
ollama pull qwen3-vl:2b
```
- **`qwen3:8b`** answers your questions — text chat, coding, math, general Q&A over the document.
- **`qwen3-vl:2b`** is only used automatically when a PDF page has little or no
  extractable text (i.e. it's scanned/image-only) — it OCRs that page before
  chunking. You never call it directly; ingestion decides per-page.

Then leave Ollama's server running in its own terminal window:
```
ollama serve
```
(If you installed Ollama as a Windows service it may already be running in
the background — check with `ollama list`.)

Both models can be changed anytime from the sidebar dropdowns in the app
without restarting anything — useful if you pull a different size later.

### 1.3 PyTorch (needed for embeddings; CPU build is fine and recommended)
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
```
We deliberately install the **CPU** build of PyTorch here — the embedding
model runs on CPU by default (see "Why CPU embeddings?" below), so you
don't need the multi-GB CUDA build of torch at all. This alone saves you
a large, fragile install step.

If you later want GPU embeddings anyway, replace the command above with
the CUDA build matching your driver from https://pytorch.org/get-started/locally/,
and set `EMBEDDING_DEVICE=cuda` (see Configuration below) — but read the
VRAM warning first.

### 1.4 Everything else
```
cd rag_project
pip install -r requirements.txt
```

The first time you run the app, `sentence-transformers` will download the
embedding model (`BAAI/bge-base-en-v1.5`, ~440MB) — this needs internet
**once**. After that, it's cached locally and the app works fully offline.

---

## 2. Running it

Two things need to be running at once, in two terminals:

**Terminal 1 — the LLM server:**
```
ollama serve
```

**Terminal 2 — the app:**
```
run.bat
```
(or manually: `cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000`)

Then open **http://127.0.0.1:8000** in your browser.

---

## 3. Using it

1. Drag a PDF or TXT onto the sidebar (or click to browse).
2. Wait for indexing to finish (a few seconds for a typical document —
   watch the CPU meter, that's the embedding step running).
3. Ask questions in the chat box. Answers stream in live, with clickable
   page citations under each answer.
4. Every AI answer has **Copy** (clipboard) and **Read aloud** (uses your
   browser's built-in text-to-speech, works offline) buttons.
5. Past questions appear in the sidebar history — click one to reuse it.
6. Uploading a new file replaces the current one (this app is designed
   for one document at a time, per your request). The original file is
   deleted from disk immediately after indexing — only the searchable
   index remains.

---

## 4. Why these specific choices for your hardware

- **Embeddings on CPU, LLM on GPU.** Your 6GB of VRAM is the tightest
  resource in this system. Ollama already manages the GPU efficiently for
  the LLM; running the embedding model there too means two processes
  fighting over the same 6GB, which is how you get VRAM overflow, driver
  fallback to shared system memory, and heat/throttling on a laptop chassis.
  CPU embedding of a single document is fast (seconds, not minutes) so
  there's no real cost to keeping it off the GPU.

- **`qwen3:8b` for chat**, per your request. At Q4 it's roughly 5.5GB,
  which is a tight fit in 6GB VRAM once the 8192-token context window's
  KV cache grows during a long answer — it may spill a few layers to CPU
  under load. If it feels slow, the fastest fix is lowering `LLM_NUM_CTX`
  (e.g. to 4096) or switching to `qwen3:4b-instruct` from the sidebar
  dropdown, no restart needed.

- **`qwen3-vl:2b` for OCR/vision**, used only when a PDF page comes back
  with almost no extractable text (scanned pages, photographed pages,
  image-only PDFs). Ollama loads/unloads models from VRAM as needed, so
  this doesn't have to coexist with `qwen3:8b` in memory at the same time
  — it's swapped in briefly during ingestion, then swapped back out.

- **No cross-encoder reranker by default.** It's implemented and you can
  turn it on (`USE_RERANKER=true`), but for a single document with top-5
  retrieval, hybrid search (vector + BM25 fused with Reciprocal Rank
  Fusion) already gets you most of the accuracy benefit without loading
  a third model.

---

## 5. Configuration

Everything tunable lives in `backend/config.py` with environment-variable
overrides. Set these before running `run.bat`, e.g. in PowerShell:
```
$env:LLM_MODEL="qwen3:4b-instruct"
run.bat
```

| Variable | Default | What it does |
|---|---|---|
| `LLM_MODEL` | `qwen3:8b` | Chat model. Any model you've pulled with `ollama pull` |
| `VISION_MODEL` | `qwen3-vl:2b` | Auto-used for OCR of scanned PDF pages |
| `AUTO_OCR` | `true` | Set `false` to disable automatic OCR fallback entirely |
| `OCR_MIN_CHARS_PER_PAGE` | `40` | Below this many extracted chars, a page is treated as scanned |
| `OCR_MAX_PAGES` | `60` | Safety cap on how many pages will be OCR'd per upload |
| `EMBEDDING_DEVICE` | `cpu` | `cpu` or `cuda` |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Swap for `BAAI/bge-small-en-v1.5` if you want faster/lighter |
| `USE_RERANKER` | `false` | Adds a cross-encoder rerank pass (more accurate, more compute) |
| `TOP_K` | `5` | How many chunks are sent to the LLM as context |
| `CHUNK_SIZE_TOKENS` | `700` | Target chunk size |
| `LLM_NUM_CTX` | `8192` | Context window given to Ollama |
| `MAX_FILE_SIZE_MB` | `200` | Upload size cap |

The chat and vision models can also be switched live from the two
dropdowns in the sidebar — this calls `POST /api/model` and takes effect
on your next question/upload, no restart required.

**If you want a lighter/faster setup** (e.g. running while other apps are
open): `LLM_MODEL=qwen3:4b-instruct` (pull it first) — roughly half the
VRAM and noticeably faster generation, with a moderate quality trade-off.

**If you want maximum quality** and are willing to close everything else:
`USE_RERANKER=true` plus a larger model like `qwen2.5:14b-instruct-q4_K_M`
— but 14B at Q4 is ~9GB, which will **not** fit in 6GB VRAM and will run
partly on CPU. Expect it to be slow and to use a lot of your already-tight
RAM. Not recommended given your current system stats.

---

## 6. Troubleshooting

- **"Cannot reach Ollama"** — make sure `ollama serve` is running and
  `ollama list` shows your model.
- **Sidebar shows GPU as "n/a"** — `nvidia-smi` isn't on your PATH, or
  drivers aren't installed. The app still works, just without live GPU
  stats; Ollama will still use the GPU internally.
- **First upload is slow** — the embedding model is downloading (one-time,
  needs internet). Subsequent runs are fast and fully offline.
- **Answers seem to ignore the document** — check the citation chips
  under the answer; if none appear, your question likely isn't covered
  by the document, and the model is told to say so rather than guess.
- **Everything feels sluggish** — check the RAM meter in the sidebar. If
  it's pinned near 100%, close browser tabs/other apps; Windows will be
  swapping to your SSD, which no amount of GPU tuning fixes.
- **Upload fails with "No extractable text found"** — either the file is
  genuinely empty, or (for a scanned PDF) OCR failed. Check the terminal
  log for `OCR'd page N with qwen3-vl:2b` lines; if you don't see them,
  make sure `qwen3-vl:2b` is pulled (`ollama list`) and `AUTO_OCR` isn't
  set to `false`.
- **Chat box stays greyed out / nothing is clickable** — this almost
  always means the upload itself failed silently. Check the terminal
  running `uvicorn` for the actual error; every error is now returned as
  JSON with a real message instead of a generic crash, so the popup
  alert on upload should tell you what went wrong.
- **You see `Failed to send telemetry event ... capture()` in the logs**
  — this is ChromaDB's anonymous usage telemetry hitting a bug in its own
  library, not a problem with your data. It's disabled in this build; if
  you still see it, make sure you're running the latest files.

---

## 7. Project structure

```
rag_project/
├── backend/
│   ├── main.py          FastAPI app & routes
│   ├── config.py        All settings, env-overridable
│   ├── ingestion.py      PDF/TXT extraction, header/footer stripping, chunking
│   ├── embeddings.py     SentenceTransformer wrapper
│   ├── vectorstore.py    ChromaDB + BM25 hybrid search (RRF fusion)
│   ├── llm.py            Streaming Ollama client
│   ├── rag_engine.py     Retrieval → context compression → prompt → generation
│   └── system_monitor.py CPU/RAM/GPU stats for the UI
├── frontend/
│   └── index.html        Single-file UI (no build step)
├── data/                  Chroma DB + chat history live here (gitignore this)
├── requirements.txt
├── run.bat
└── README.md
```
