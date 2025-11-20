# Runpod Setup Guide for GPU-Accelerated RAG

## Quick Start on Runpod

### 1. Deploy Runpod Pod

Choose template:
- **PyTorch 2.x** or **RunPod PyTorch** template
- GPU: RTX 3090, RTX 4090, or A40 (any will work, even a cheap one)
- Storage: 20GB minimum

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements_gpu.txt

# Install Ollama (for LLM generation)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in background
nohup ollama serve &

# Pull the model
ollama pull llama3.2
```

### 3. Upload PDFs

Upload your PDFs to the pod:
```bash
# Via scp
scp MR.pdf root@<your-pod-ip>:/workspace/modern-robotics/

# Or use Runpod's file browser
```

### 4. Run GPU Version

```bash
cd /workspace/modern-robotics/simulation_project
python rag_chatbot_gpu.py --rebuild
```

## Speed Comparison

**CPU (Local Ollama embeddings)**:
- MRlib.pdf (16 pages, 78 chunks): ~165 seconds
- Rate: ~0.47 chunks/second
- Full MR.pdf (~600 pages): ~90 minutes

**GPU (Runpod with RTX 3090)**:
- MRlib.pdf (16 pages, 78 chunks): ~5-10 seconds
- Rate: ~8-15 chunks/second
- Full MR.pdf (~600 pages): ~5-10 minutes
- **Speedup: 15-30x faster!**

## Runpod Best Practices

### Cost Optimization

1. **Use Secure Cloud** (cheaper than On-Demand)
2. **Stop pod when not in use** (only pay for storage)
3. **RTX 3090 is sweet spot** (cheap + fast enough)
4. **Build database once, download it** (reuse locally)

### Download Vector Database After Building

Once built on Runpod, download for local use:

```bash
# On Runpod, create archive
cd /workspace/modern-robotics/simulation_project
tar -czf chroma_db_gpu.tar.gz chroma_db_gpu/

# Download to local machine
scp root@<pod-ip>:/workspace/modern-robotics/simulation_project/chroma_db_gpu.tar.gz .

# Extract locally
tar -xzf chroma_db_gpu.tar.gz
```

Now you can use the database locally without rebuilding!

## Alternative: Build on Runpod, Use Locally

1. **Build vector DB on Runpod** (fast with GPU)
2. **Download the `chroma_db_gpu` folder**
3. **Use locally with CPU for queries** (queries are fast anyway)

This gives you the best of both worlds!

## Dockerfile for Runpod (Optional)

```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages
COPY requirements_gpu.txt .
RUN pip install -r requirements_gpu.txt

# Copy application
COPY . /workspace/modern-robotics/

WORKDIR /workspace/modern-robotics/simulation_project

# Start Ollama and run chatbot
CMD ollama serve & sleep 5 && ollama pull llama3.2 && python rag_chatbot_gpu.py
```

## Troubleshooting

**GPU not detected**:
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # Should show GPU name
```

**Out of memory**:
- Reduce batch size in `rag_chatbot_gpu.py`:
  ```python
  encode_kwargs={'device': self.device, 'batch_size': 16}  # Lower from 32
  ```

**Ollama connection failed**:
- Make sure Ollama is running: `ollama serve`
- Check port 11434 is accessible

## Cost Estimate

**Runpod Secure Cloud (RTX 3090)**:
- ~$0.30/hour
- Building full MR.pdf database: ~10 minutes = **$0.05**
- Interactive usage (1 hour): **$0.30**

**Total cost for complete setup: < $1**

Much better than waiting 2+ hours on CPU!
