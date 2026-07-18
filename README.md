# 🎓 RAG-Professor

> **知行合一 (Zhī Xíng Hé Yī)**
>
> *Knowledge and action are one.*

Offline Document Intelligence powered by Ollama, FastAPI, React, ChromaDB, and modern Retrieval-Augmented Generation (RAG).

Upload one PDF or TXT file at a time, ask questions about it, and get streamed answers with page citations — entirely on your own machine after setup. No internet is used at query time.

---

## ✨ Features
## 功能特点

- 📄 Upload PDF and TXT documents
- 🔍 Hybrid Search (Vector + BM25 + RRF)
- 🤖 Local AI using Ollama
- 🧠 Multiple LLM support
- 👁 Automatic OCR for scanned PDFs
- 📖 Page citations in every answer
- ⚡ Streaming responses
- 🌙 Modern React interface
- 📋 Copy answers
- 🔊 Text-to-Speech
- 📊 Live CPU / RAM / GPU monitoring
- 🔄 Switch models without restarting
- 🔒 Completely offline after setup

---

## 🏗 Architecture
## 系统架构

```
                PDF / TXT
                    │
                    ▼
            Document Extraction
                    │
          OCR (if required)
                    │
                    ▼
          Text Chunking
                    │
                    ▼
     SentenceTransformer Embeddings
                    │
                    ▼
      ChromaDB + BM25 Hybrid Search
                    │
                    ▼
            Context Compression
                    │
                    ▼
          Ollama Local LLM
                    │
                    ▼
         Streamed Answer + Citations
```

---

## 📚 Supported Files
## 支持的文件格式

Currently supported:

- PDF
- TXT

Planned:

- DOCX
- Markdown
- HTML

---

## 💻 Recommended Hardware
## 推荐硬件

| Hardware | Recommendation |
|---|---|
| CPU | Intel i5 / Ryzen 5+ |
| RAM | 16GB |
| GPU | RTX 3050 6GB+ |
| Storage | SSD |
| Python | 3.11 |
| Node | Latest LTS |

### Suggested Models by Hardware

| Hardware                 | Recommended Model         |
|---------------------------|----------------------------|
| 8 GB RAM, No GPU          | qwen3:1.7b                |
| 8–16 GB RAM, No GPU       | qwen3:4b                  |
| 16 GB RAM + RTX 3050 6GB  | qwen3:8b                  |
| 16 GB RAM + RTX 4060+     | qwen3:8b / DeepSeek-R1 8B |
| 32 GB RAM + RTX 4070+     | qwen2.5:14b               |
| 64 GB RAM + High-End GPU  | DeepSeek-R1 14B+          |

**No GPU? No problem** — RAG-Professor works perfectly on CPU-only systems. Just use a smaller model:
```bash
ollama pull qwen3:4b
```
```env
LLM_MODEL=qwen3:4b
```

**⚠️ Heat & thermals (especially on laptops):** running 8B+ models pushes sustained CPU/GPU load for the whole time an answer streams — on laptops this shows up as fan noise, heat, and throttling. If that happens, drop to `qwen3:4b` / `gemma3:4b` / `qwen3:1.7b`, lower `LLM_NUM_CTX` (e.g. `4096`), and avoid 14B+ models on laptop-class hardware.

**⏳ Be patient** — everything runs on your own CPU/GPU, so response time depends entirely on your hardware. The first query after startup or after switching models is always slower (model loading into memory).

---

## 🧩 Software Requirements
## 环境要求

Required:
- Python 3.10 or 3.11 (3.12+ can have wheel-availability issues)
- Node.js 20+
- npm
- Ollama

Recommended:
- Git
- VS Code

---

## 🛠 Installation
## 安装指南

### 1. Python
```bash
python --version
```

### 2. Ollama (runs the LLM)
Get it from https://ollama.com/download, then pull the models you need (one-time, needs internet):
```bash
ollama pull qwen3:8b
ollama pull qwen3-vl:2b
```
- The chat model (default `qwen3:8b`) answers your questions.
- `qwen3-vl:2b` is used automatically only when a PDF page has little or no extractable text (scanned/image-only) — it OCRs that page before chunking.

Verify installed models any time:
```bash
ollama list
```

### 3. PyTorch (CPU build recommended)
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```
The embedding model runs on CPU by default, so the multi-GB CUDA build isn't needed. If you want GPU embeddings, install the CUDA build matching your driver and set `EMBEDDING_DEVICE=cuda`.

### 4. Backend dependencies
```bash
cd rag_project
pip install -r requirements.txt
```
First run downloads the embedding model (`BAAI/bge-base-en-v1.5`, ~440MB) — needs internet once, then it's cached and fully offline.

### 5. Frontend dependencies
```bash
cd frontend
npm install
```

---

## 🚀 How to Use
## 使用方法

1. Start Ollama:
```bash
ollama serve
```
2. Run:
```bash
run.bat
```
3. Open:
```
http://localhost:5173
```
4. Upload a PDF or TXT.
5. Wait until indexing completes (watch the CPU meter — that's embedding running).
6. Ask anything.

Example prompts:

> Explain Chapter 5
>
> Summarize this paper
>
> List all equations
>
> Give me interview questions from this document
>
> Translate page 8
>
> Find all references to neural networks

Every answer streams in live with clickable page citations, plus **Copy** and **Read aloud** buttons. Past questions appear in the sidebar history. Uploading a new file replaces the current one — RAG-Professor works with one document at a time, and the original file is deleted from disk right after indexing (only the searchable index remains).

---

## 🖥 Example Workflow
## 工作流程示例

```
PDF
 ↓
Upload
 ↓
Index
 ↓
Ask Question
 ↓
Retrieve Chunks
 ↓
LLM
 ↓
Answer
 ↓
Citation
```

---

## ⚙️ Configuration
## 配置说明

Everything tunable lives in `backend/config.py`, overridable via environment variables:
```powershell
$env:LLM_MODEL="qwen3:4b"
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
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Swap for `BAAI/bge-small-en-v1.5` for faster/lighter |
| `USE_RERANKER` | `false` | Adds a cross-encoder rerank pass (more accurate, more compute) |
| `TOP_K` | `5` | How many chunks are sent to the LLM as context |
| `CHUNK_SIZE_TOKENS` | `700` | Target chunk size |
| `LLM_NUM_CTX` | `8192` | Context window given to Ollama |
| `MAX_FILE_SIZE_MB` | `200` | Upload size cap |

Chat and vision models can also be switched live from the sidebar dropdowns — no restart required.

---

## 🌐 Offline Usage
## 离线运行

Internet is required only for:
- Installing Ollama and Node.js
- Pulling models (`ollama pull`)
- Downloading the embedding model on first launch
- Installing npm/pip dependencies

After setup, RAG-Professor runs entirely offline.

---

## 🧠 Design Choices & Why
## 设计理念

- **Embeddings on CPU, LLM on GPU (when present)** — keeps VRAM free for the LLM instead of two processes fighting over it.
- **Match the chat model to your VRAM** — an 8B model at Q4 is ~5.5GB; drop `LLM_NUM_CTX` or the model size if it's tight.
- **Vision model for OCR only** — swapped in briefly during ingestion, then unloaded.
- **No reranker by default** — hybrid search (vector + BM25 with RRF) already covers most of the accuracy gain for single-document, top-5 retrieval; enable `USE_RERANKER=true` if you want it.

---

## 🩺 Troubleshooting
## 常见问题排查

- **"Cannot reach Ollama"** — make sure `ollama serve` is running and `ollama list` shows your model.
- **Sidebar shows GPU as "n/a"** — `nvidia-smi` isn't on PATH, or drivers aren't installed; the app still works without live GPU stats.
- **First upload is slow** — the embedding model is downloading (one-time).
- **Answers seem to ignore the document** — check the citation chips; if none appear, the question likely isn't covered by the document.
- **Everything feels sluggish** — check the RAM meter; near 100% means the OS is swapping to disk.
- **Upload fails with "No extractable text found"** — check the terminal for `OCR'd page N` lines; confirm the vision model is pulled and `AUTO_OCR` isn't `false`.
- **Chat box stays greyed out** — check the `uvicorn` terminal for the real error.
- **`Failed to send telemetry event ... capture()` in logs** — a harmless ChromaDB telemetry bug, already disabled in this build.

---

## ⚡ Performance Tips
## 性能优化建议

- Use `qwen3:4b` for CPU-only systems.
- Use `qwen3:8b` for RTX 3050/4060.
- Use `qwen2.5:14b` only with 32GB+ RAM.
- Smaller context windows reduce RAM usage.
- Restart Ollama after switching large models.

---

## ❓ FAQ
## 常见问题

**Does this require internet?** Only during installation.

**Can I use my own model?** Yes.

**Can I upload multiple PDFs?** One document at a time.

**Does it send my data online?** Never.

**Can I change the embedding model?** Yes.

**Can I disable OCR?** Yes.

---

## 🛣 Roadmap
## 开发路线图

- [x] PDF support
- [x] TXT support
- [x] Hybrid Search
- [x] OCR
- [x] Streaming
- [ ] DOCX support
- [ ] Multi-document chat
- [ ] Session management
- [ ] Docker support
- [ ] Authentication
- [ ] REST API documentation

---

## 📂 Folder Structure
## 项目结构

```
rag_project/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── ingestion.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   ├── llm.py
│   ├── rag_engine.py
│   └── system_monitor.py
├── frontend/
│   ├── src/
│   │   ├── components
│   │   ├── hooks
│   │   ├── pages
│   │   ├── context
│   │   └── utils
│   └── App.jsx
├── data/
├── requirements.txt
├── run.bat
└── README.md
```

---

## 🤝 Contributing
## 参与贡献

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

## 🟢 Open for Contributors
## 欢迎贡献者

This project is actively open for contributions — issues, PRs, docs, translations, and ideas are all welcome, from first-timers to experienced devs. Good places to start:

- Check the **Roadmap** above for unclaimed items (DOCX support, multi-document chat, Docker, etc.)
- Open an issue before starting large changes so we can align on approach
- Small fixes (typos, docs, bugs) are always welcome without prior discussion
- Tag your PR with what it touches (backend / frontend / docs) to speed up review

欢迎任何形式的贡献——无论是提交 Issue、Pull Request、完善文档还是翻译，新手和资深开发者都同样欢迎。可以从路线图中未认领的功能开始，或先提交 Issue 讨论较大的改动。

---

## ⭐ Support
## 支持项目

If this project helped you, consider giving it a ⭐ on GitHub.

如果这个项目对你有帮助，欢迎在 GitHub 上点个 ⭐。

---


<p align="center">

Built for developers, researchers, and students.

**持续学习 · 持续创新**
## 🟢 Open for Contributors
## 欢迎贡献者

This project is actively open for contributions — issues, PRs, docs, translations, and ideas are all welcome, from first-timers to experienced devs. Good places to start:

- Check the **Roadmap** above for unclaimed items (DOCX support, multi-document chat, Docker, etc.)
- Open an issue before starting large changes so we can align on approach
- Small fixes (typos, docs, bugs) are always welcome without prior discussion
- Tag your PR with what it touches (backend / frontend / docs) to speed up review

欢迎任何形式的贡献——无论是提交 Issue、Pull Request、完善文档还是翻译，新手和资深开发者都同样欢迎。可以从路线图中未认领的功能开始，或先提交 Issue 讨论较大的改动。
*Keep Learning • Keep Innovating*

</p>
