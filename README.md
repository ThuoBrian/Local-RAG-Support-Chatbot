# Helpdesk RAG — Knowledge Assistant

Ask questions about your IT support documents and get instant answers. Everything runs on your own computer — no data leaves your machine.

![Python 3.11–3.13](https://img.shields.io/badge/python-3.11%E2%80%933.13-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## What it does

- Drop your PDF, Word, Markdown, or text documents into a folder
- The app reads them, learns the content, and answers questions
- Responses are based only on your documents, so answers stay accurate and private
- Works completely offline once the model is downloaded

## What you need

1. A computer running macOS, Windows, or Linux
2. Python 3.11, 3.12, or 3.13 installed
3. [Ollama](https://ollama.com) installed and running
4. [uv](https://docs.astral.sh/uv/) package manager

> Not sure about Python or uv? Ask your IT team, or see the [detailed guide](docs/README.md).

## The easy way: run the menu

Open your terminal, go to the project folder, and run:

```bash
./scripts/helpdesk.sh
```

You will see a numbered menu:

```text
1. Setup Project (one-time)
2. Check Ollama Status
3. Add / Update Documents
4. Start Chat Server
5. Run Tests
6. View Project Status
0. Exit
```

Just follow the steps in order:

1. **Setup Project** — installs everything automatically
2. **Check Ollama Status** — verifies the AI models are ready
3. **Add / Update Documents** — copy files into `data/documents/`, then ingest them
4. **Start Chat Server** — opens the chat page at **http://localhost:8000**

## Step-by-step for first-time users

### 1. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com), then open it. You only need to do this once.

### 2. Pull the AI models

In your terminal, run:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

These download the AI models to your computer.

> **Tip:** `llama3.2` is a small, fast model. If you want better answers and have more RAM, try `qwen2.5:7b` or `mistral:7b`.

### 3. Start the interactive menu

```bash
./scripts/helpdesk.sh
```

Choose option **1** to set up the project. This creates the environment and installs dependencies automatically.

### 4. Add your documents

Copy your files into:

```text
data/documents/
```

Supported files:
- PDF (`.pdf`)
- Word (`.docx`)
- Markdown (`.md`)
- Text (`.txt`)

### 5. Ingest the documents

In the menu, choose option **3**. This teaches the app what is in your documents.

### 6. Start chatting

In the menu, choose option **4**. Then open your browser at:

```text
http://localhost:8000
```

## Troubleshooting

| Problem | What to do |
|---|---|
| "Ollama is not running" | Start the Ollama app first |
| "Virtual environment not found" | Run `./scripts/helpdesk.sh` and choose **1. Setup Project** |
| The chat gives wrong answers | Add more documents or try a larger model |
| Port already in use | Set a different port: `PORT=8080 ./scripts/start.sh` |
| No documents found | Check that files are inside `data/documents/` |

## For developers

If you want to modify the code, run tests, or understand the architecture, see [docs/README.md](docs/README.md).

## License

[MIT](LICENSE)
