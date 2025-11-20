# Modern Robotics RAG Chatbot

A local RAG (Retrieval-Augmented Generation) chatbot that uses Ollama to query Modern Robotics PDF documents as a knowledge base.

## Features

- 📚 **PDF Knowledge Base**: Automatically indexes all PDF files in the repository
- 🤖 **Local LLM**: Uses Ollama (fully local, no API keys needed)
- 💾 **Vector Database**: ChromaDB for efficient semantic search
- 🔍 **Source Citations**: Shows which PDF pages were used to answer questions
- 💬 **Interactive Chat**: Ask questions in natural language

## Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)

2. **Pull required models**:
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements_rag.txt
   ```

## Usage

### Interactive Mode (Recommended)

Start the chatbot in interactive mode:

```bash
python rag_chatbot.py
```

Then ask questions like:
- "What is the forward kinematics equation?"
- "Explain the twist representation of velocity"
- "How do I calculate the Jacobian matrix?"
- "What is the difference between body and space frames?"

### Single Query Mode

Ask a single question without entering interactive mode:

```bash
python rag_chatbot.py --query "What is the product of exponentials formula?"
```

### Options

```bash
# Use a different Ollama model
python rag_chatbot.py --model llama3.1

# Use a different embedding model
python rag_chatbot.py --embedding-model mxbai-embed-large

# Rebuild the vector database (if PDFs changed)
python rag_chatbot.py --rebuild
```

### Interactive Commands

When in interactive mode:
- Type your question and press Enter
- Type `rebuild` to rebuild the vector database
- Type `quit`, `exit`, or `q` to stop

## How It Works

1. **Indexing**: PDFs are loaded and split into chunks
2. **Embedding**: Chunks are embedded using Ollama's embedding model
3. **Storage**: Embeddings are stored in ChromaDB (local vector database)
4. **Retrieval**: User questions are embedded and matched against the database
5. **Generation**: Relevant chunks are sent to Ollama LLM for answer generation

## PDF Sources

The chatbot automatically finds and indexes these PDFs:
- `MR.pdf` - Modern Robotics textbook
- `doc/MRlib.pdf` - Modern Robotics library documentation

## Customization

### Using Different Models

**Recommended LLM Models** (ordered by size):
- `llama3.2` (3B) - Fast, good for quick queries
- `llama3.1` (8B) - Balanced performance
- `mistral` (7B) - Good reasoning
- `mixtral` (47B) - High quality, slower

**Recommended Embedding Models**:
- `nomic-embed-text` (default) - 768 dimensions, good balance
- `mxbai-embed-large` - 1024 dimensions, higher quality

### Adjusting Retrieval

Edit `setup_qa_chain()` in `rag_chatbot.py`:

```python
retriever=self.vectorstore.as_retriever(
    search_kwargs={"k": 4}  # Increase for more context
)
```

### Chunk Size

Edit `load_and_process_pdfs()` in `rag_chatbot.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Increase for more context per chunk
    chunk_overlap=200,    # Increase for better continuity
)
```

## Performance Tips

1. **First Run**: Initial indexing takes a few minutes
2. **Subsequent Runs**: Vector database is cached (instant startup)
3. **GPU**: Ollama automatically uses GPU if available
4. **Memory**: Larger models need more RAM (8GB+ recommended)

## Troubleshooting

**"Connection refused" error**:
- Make sure Ollama is running: `ollama serve`

**"Model not found" error**:
- Pull the model: `ollama pull llama3.2`

**Slow responses**:
- Try a smaller model: `--model llama3.2`
- Reduce retrieved chunks: edit `search_kwargs={"k": 2}`

**Rebuild database**:
- If PDFs changed: `python rag_chatbot.py --rebuild`
- Or in interactive mode: type `rebuild`

## Example Questions

**Kinematics**:
- "What is the product of exponentials formula?"
- "Explain forward kinematics using exponential coordinates"
- "How do I transform between body and space frames?"

**Jacobians**:
- "What is the spatial Jacobian?"
- "How do I calculate the body Jacobian?"
- "Explain the relationship between Jacobians in different frames"

**Dynamics**:
- "What is the Newton-Euler inverse dynamics algorithm?"
- "Explain the mass matrix in dynamics"
- "How do I calculate forward dynamics?"

**Trajectory Planning**:
- "What is a quintic time scaling?"
- "How do I plan a straight-line trajectory in task space?"

## License

Same as parent repository (Modern Robotics course materials).
