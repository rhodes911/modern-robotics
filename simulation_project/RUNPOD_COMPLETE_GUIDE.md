# Complete Runpod Setup Guide - Modern Robotics RAG

## Step 1: Create Runpod Account

1. Go to [runpod.io](https://runpod.io)
2. Sign up / Login
3. Add billing (requires $10-20 minimum)

---

## Step 2: Deploy a GPU Pod

### Choose Pod Settings:

1. Click **"Deploy"** → **"GPU Pods"**

2. **Select GPU Type** (any of these work):
   - 🔥 **RTX 5090** (32GB VRAM) - **BEAST MODE** ($0.89/hr) - Will finish in ~2-3 min!
   - ✅ **RTX 4090** (24GB VRAM) - **RECOMMENDED** ($0.39-0.77/hr) 
   - RTX 3090 (24GB VRAM) - ($0.30/hr)
   - A40 (48GB VRAM) - ($0.45/hr)
   - Even RTX 3060 (12GB) works fine ($0.20/hr)

3. **Select Template**:
   - Choose **"RunPod PyTorch 2.1"** or **"PyTorch"**
   - OR choose **"Start From Scratch"** with Ubuntu 22.04

4. **Storage**:
   - Set to **30GB** (enough for models + PDFs)

5. **Deploy Type**:
   - Choose **"Secure Cloud"** (cheaper) or **"Community Cloud"** (cheapest)

6. Click **"Deploy On-Demand"**

7. Wait 30-60 seconds for pod to start

---

## Step 3: Connect to Your Pod

### Option A: Web Terminal (Easiest)

1. Click **"Connect"** button on your pod
2. Click **"Start Web Terminal"**
3. A terminal will open in your browser

### Option B: SSH (Better for file transfers)

1. Click **"Connect"** → **"TCP Port Mappings"**
2. Copy the SSH command (looks like):
   ```bash
   ssh root@<pod-ip> -p <port> -i ~/.ssh/id_ed25519
   ```
3. Run in your local terminal

---

## Step 4: Setup Environment on Runpod

### 4.1 Update System and Install Dependencies

```bash
# Update system
apt-get update && apt-get install -y curl git wget

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in background
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Wait a moment for Ollama to start
sleep 5

# Pull the LLM model
ollama pull llama3.2
```

### 4.2 Clone Your Repository

```bash
# Navigate to workspace
cd /workspace

# Clone your repo (if not already there)
git clone https://github.com/rhodes911/modern-robotics.git
cd modern-robotics/simulation_project
```

### 4.3 Install Python Dependencies

```bash
# Install GPU requirements
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements_gpu.txt
```

### 4.4 Verify GPU is Available

```bash
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Should output:
```
GPU Available: True
GPU Name: NVIDIA GeForce RTX 3090
```

---

## Step 5: Upload PDFs to Runpod

### Option A: Clone from GitHub (EASIEST - PDFs already in your repo!)

Since your PDFs are already in the GitHub repo, just pull them:

```bash
# In your Runpod Web Terminal
cd /workspace/modern-robotics
git pull

# Verify PDFs are there
ls -lh MR.pdf doc/MRlib.pdf
```

Done! Skip to Step 6.

### Option B: Using Jupyter Lab (If Available)

1. In Runpod pod page, look for **HTTP Services** section
2. Click **"Jupyter Lab"** link (Port 8888)
3. Navigate to `/workspace/modern-robotics/`
4. Click the Upload button (↑ icon) in the file browser
5. Upload `MR.pdf` to `/workspace/modern-robotics/`
6. Upload `MRlib.pdf` to `/workspace/modern-robotics/doc/`

### Option C: Using SCP (From Your Local Machine)

```bash
# From the Connect tab, copy the SSH command shown
# It looks like: ssh root@149.36.1.79 -p 38112 -i ~/.ssh/id_ed25519

# On your LOCAL machine, upload PDFs:
scp -P 38112 -i ~/.ssh/id_ed25519 MR.pdf root@149.36.1.79:/workspace/modern-robotics/
scp -P 38112 -i ~/.ssh/id_ed25519 doc/MRlib.pdf root@149.36.1.79:/workspace/modern-robotics/doc/
```

Replace `38112` and `149.36.1.79` with your actual port and IP from the "SSH over exposed TCP" section.

### Option D: Direct Download in Terminal

```bash
# If PDFs are accessible via URL, download directly
cd /workspace/modern-robotics
wget https://your-url.com/MR.pdf
cd doc
wget https://your-url.com/MRlib.pdf
```

---

## Step 6: Build Vector Database (THE MAIN EVENT!)

```bash
cd /workspace/modern-robotics/simulation_project

# Run GPU-accelerated version
python rag_chatbot_gpu.py --rebuild
```

**Expected Output:**
```
======================================================================
Modern Robotics RAG Chatbot (GPU Accelerated)
======================================================================
Device: CUDA
GPU: NVIDIA GeForce RTX 5090
GPU Memory: 32.0 GB

🚀 Loading embedding model on GPU...
✓ Embeddings ready on CUDA

📚 Finding PDF files...
✓ Found 2 PDF file(s):
  - MR.pdf (15.2 MB)
  - MRlib.pdf (0.3 MB)

📖 Loading PDF documents...
   Loading MR.pdf... ✓ 589 pages
   Loading MRlib.pdf... ✓ 16 pages
✓ Total pages loaded: 605

✂️ Splitting documents into chunks...
✓ Created 2847 text chunks

🗄️ Creating vector database with GPU acceleration...
   🚀 GPU embedding in progress...
✓ Vector database created with 2847 chunks
✓ Time: 45.2s (63.0 chunks/sec)
✓ Speedup: ~50x faster than CPU!

✅ RAG System Ready!
```

**Time estimate:**
- Full MR.pdf + MRlib.pdf on **RTX 5090**: **~2-3 minutes** ⚡⚡⚡
- Full MR.pdf + MRlib.pdf on **RTX 4090**: **~3-5 minutes** ⚡⚡
- Full MR.pdf + MRlib.pdf on **RTX 3090**: **~5-10 minutes** ⚡
- Cost on RTX 5090: **~$0.05** at $0.89/hour (so fast it's basically free!)

---

## Step 7: Test the Chatbot

Once built, try asking questions:

```
🤖 You: What is forward kinematics?

🤖 You: Explain the product of exponentials formula

🤖 You: How do I calculate a Jacobian matrix?
```

Press Ctrl+C or type `quit` to exit.

---

## Step 8: Download Vector Database to Your Local Machine

### 8.1 Create Archive on Runpod

```bash
cd /workspace/modern-robotics/simulation_project

# Create compressed archive
tar -czf chroma_db_gpu.tar.gz chroma_db_gpu/

# Check size
ls -lh chroma_db_gpu.tar.gz
```

### 8.2 Download to Local Machine

**Option A: SCP (Recommended)**

```bash
# On your local machine
scp -P <port> root@<pod-ip>:/workspace/modern-robotics/simulation_project/chroma_db_gpu.tar.gz .

# Extract
tar -xzf chroma_db_gpu.tar.gz
```

**Option B: Runpod File Browser**

1. Go to pod dashboard
2. Click "File Browser"
3. Navigate to `/workspace/modern-robotics/simulation_project/`
4. Right-click `chroma_db_gpu.tar.gz` → Download

### 8.3 Use Locally

```bash
# Copy to your local repo
cp -r chroma_db_gpu ~/Repos/modern-robotics/simulation_project/

# Install requirements locally (if not already)
pip install sentence-transformers transformers torch

# Run locally (will use existing database)
cd ~/Repos/modern-robotics/simulation_project
python rag_chatbot_gpu.py
```

Queries will be fast even on CPU since you're just searching the pre-built database!

---

## Step 9: Stop or Destroy Pod

### When You're Done:

1. **Stop Pod** (keeps storage, stop paying for GPU):
   - Click pod → "Stop"
   - Storage cost: ~$0.10/GB/month
   - Restart anytime

2. **Destroy Pod** (delete everything):
   - Click pod → "Terminate"
   - No further charges
   - Do this after downloading the database

---

## Cost Breakdown

**With RTX 5090 (FASTEST):**
- Pod startup: 1 min ($0.01)
- Setup + installs: 3 min ($0.04)
- Building database: 3 min ($0.04)
- Testing: 2 min ($0.03)
- **Total: ~$0.12 for full setup!**

**With RTX 4090 (FAST):**
- Complete session: ~15 min
- **Total: ~$0.10-0.20**

**With RTX 3090 (RECOMMENDED BUDGET):**
- Complete session: ~25 min
- **Total: ~$0.12**

**If you keep pod running:**
- RTX 5090: $0.89/hour (overkill, but blazing fast!)
- RTX 4090: $0.39-0.77/hour
- RTX 3090: $0.30/hour

**If you stop (not destroy):**
- Storage only: ~$0.10/GB/month (~$3/month for 30GB)

---

## Troubleshooting

### GPU Not Available

```bash
# Check CUDA
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Ollama Connection Failed

```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5
ollama pull llama3.2
```

### Out of Memory

```bash
# Edit batch size in rag_chatbot_gpu.py
# Line ~38, change batch_size from 32 to 16:
encode_kwargs={'device': self.device, 'batch_size': 16}
```

### Files Not Found

```bash
# Verify PDFs exist
ls -lh /workspace/modern-robotics/*.pdf
ls -lh /workspace/modern-robotics/doc/*.pdf

# Check current directory
pwd
cd /workspace/modern-robotics/simulation_project
```

---

## Quick Command Summary

```bash
# Complete setup (copy-paste friendly)
apt-get update && apt-get install -y curl git wget
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5
ollama pull llama3.2
cd /workspace/modern-robotics/simulation_project
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements_gpu.txt
python rag_chatbot_gpu.py --rebuild

# After completion, create archive
tar -czf chroma_db_gpu.tar.gz chroma_db_gpu/

# Download from local machine
scp -P <port> root@<pod-ip>:/workspace/modern-robotics/simulation_project/chroma_db_gpu.tar.gz .
```

---

## Pro Tips

1. **Use RTX 3090** - Best price/performance ratio
2. **Secure Cloud** - Cheaper than Community/On-Demand
3. **Build once, use everywhere** - Download the database and reuse locally
4. **Don't forget to stop/terminate** - Avoid surprise bills!
5. **Use tmux** - Your session persists if connection drops:
   ```bash
   apt-get install tmux
   tmux new -s rag
   # Run your commands
   # Disconnect: Ctrl+B then D
   # Reconnect: tmux attach -t rag
   ```

---

## Alternative: Build Locally on CPU (Not Recommended)

If you want to wait ~2 hours instead of paying $0.12:

```bash
cd simulation_project
python rag_chatbot.py --rebuild
# Go make dinner, watch a movie, etc.
```

But seriously, just use Runpod. It's worth 12 cents. 😄

---

## Need Help?

**Runpod Docs:** https://docs.runpod.io/
**Ollama Docs:** https://ollama.ai/

**Common Issues:**
- Pod won't start → Try different region/GPU type
- Out of money → Add more credits to account
- Can't connect → Check firewall/VPN settings
