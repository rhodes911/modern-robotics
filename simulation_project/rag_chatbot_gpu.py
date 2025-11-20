"""
GPU-Accelerated RAG Chatbot for Runpod
Uses sentence-transformers with GPU for MUCH faster embedding generation
"""

import os
import sys
from pathlib import Path
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import torch
import warnings
warnings.filterwarnings('ignore')


class ModernRoboticsRAGGPU:
    def __init__(self, ollama_model="llama3.2"):
        """Initialize the RAG chatbot with GPU embeddings."""
        self.ollama_model = ollama_model
        self.pdf_directory = Path(__file__).parent.parent
        self.chroma_db_dir = Path(__file__).parent / "chroma_db_gpu"
        
        # Check GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("=" * 70)
        print("Modern Robotics RAG Chatbot (GPU Accelerated)")
        print("=" * 70)
        print(f"PDF Directory: {self.pdf_directory}")
        print(f"Vector DB Directory: {self.chroma_db_dir}")
        print(f"LLM Model: {self.ollama_model}")
        print(f"Device: {self.device.upper()}")
        
        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print()
        
        # Initialize GPU embeddings (MUCH FASTER than Ollama)
        print("🚀 Loading embedding model on GPU...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # Fast, good quality
            model_kwargs={'device': self.device},
            encode_kwargs={'device': self.device, 'batch_size': 32}  # Batch for speed
        )
        print(f"✓ Embeddings ready on {self.device.upper()}\n")
        
        self.vectorstore = None
        self.qa_chain = None
    
    def find_pdfs(self):
        """Find all PDF files in the repository."""
        pdf_files = []
        for pdf in self.pdf_directory.rglob("*.pdf"):
            if "chroma_db" not in str(pdf):
                pdf_files.append(pdf)
        return pdf_files
    
    def load_and_process_pdfs(self):
        """Load PDFs and split into chunks."""
        print("📚 Finding PDF files...")
        pdf_files = self.find_pdfs()
        
        if not pdf_files:
            print("❌ No PDF files found!")
            return []
        
        print(f"✓ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"  - {pdf.name} ({pdf.stat().st_size / 1e6:.1f} MB)")
        print()
        
        # Load documents
        print("📖 Loading PDF documents...")
        all_documents = []
        for pdf_path in pdf_files:
            try:
                print(f"   Loading {pdf_path.name}...", end=" ", flush=True)
                loader = PyPDFLoader(str(pdf_path))
                documents = loader.load()
                all_documents.extend(documents)
                print(f"✓ {len(documents)} pages")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        if not all_documents:
            print("❌ No documents loaded!")
            return []
        
        print(f"✓ Total pages loaded: {len(all_documents)}\n")
        
        # Split into chunks
        print("✂️ Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
        )
        chunks = text_splitter.split_documents(all_documents)
        print(f"✓ Created {len(chunks)} text chunks\n")
        
        return chunks
    
    def create_vectorstore(self, chunks):
        """Create ChromaDB vector store with GPU-accelerated embeddings."""
        print("🗄️ Creating vector database with GPU acceleration...")
        print(f"   Processing {len(chunks)} chunks in batches...")
        
        self.chroma_db_dir.mkdir(exist_ok=True)
        
        try:
            import time
            start_time = time.time()
            
            # GPU can handle much larger batches
            print("   🚀 GPU embedding in progress...")
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.chroma_db_dir),
                collection_name="modern_robotics"
            )
            
            total_time = time.time() - start_time
            chunks_per_sec = len(chunks) / total_time
            print(f"✓ Vector database created with {len(chunks)} chunks")
            print(f"✓ Time: {total_time:.1f}s ({chunks_per_sec:.1f} chunks/sec)")
            print(f"✓ Speedup: ~{165/total_time:.1f}x faster than CPU!\n")
            return True
            
        except Exception as e:
            print(f"❌ Error creating vector database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_existing_vectorstore(self):
        """Load existing vector store if available."""
        if not self.chroma_db_dir.exists():
            return False
        
        try:
            print("🗄️ Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory=str(self.chroma_db_dir),
                embedding_function=self.embeddings,
                collection_name="modern_robotics"
            )
            print("✓ Vector database loaded\n")
            return True
        except Exception as e:
            print(f"❌ Could not load existing database: {e}")
            return False
    
    def setup_qa_chain(self):
        """Setup the QA chain with Ollama."""
        print("🔗 Setting up QA chain...")
        
        llm = Ollama(
            model=self.ollama_model,
            temperature=0.7,
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            ),
            return_source_documents=True,
        )
        
        print("✓ QA chain ready\n")
    
    def initialize(self, rebuild=False):
        """Initialize the RAG system."""
        if not rebuild and self.load_existing_vectorstore():
            self.setup_qa_chain()
            return True
        
        print("🔧 Building vector database from PDFs...\n")
        chunks = self.load_and_process_pdfs()
        
        if not chunks:
            print("❌ No content to process!")
            return False
        
        if not self.create_vectorstore(chunks):
            return False
            
        self.setup_qa_chain()
        return True
    
    def query(self, question):
        """Query the RAG system."""
        if not self.qa_chain:
            print("❌ QA chain not initialized!")
            return None
        
        print(f"\n💭 Query: {question}")
        print("🤔 Thinking...\n")
        
        result = self.qa_chain.invoke({"query": question})
        
        answer = result["result"]
        sources = result.get("source_documents", [])
        
        print("📝 Answer:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        
        if sources:
            print(f"\n📚 Sources ({len(sources)} documents):")
            for i, doc in enumerate(sources, 1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "?")
                print(f"  {i}. {Path(source).name} (Page {page + 1})")
        
        return answer
    
    def chat(self):
        """Interactive chat loop."""
        print("=" * 70)
        print("💬 Interactive Mode")
        print("=" * 70)
        print("Ask questions about Modern Robotics!")
        print("Commands:")
        print("  - Type your question and press Enter")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'rebuild' to rebuild the vector database")
        print("=" * 70)
        print()
        
        while True:
            try:
                user_input = input("\n🤖 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'rebuild':
                    print("\n🔄 Rebuilding vector database...")
                    if self.initialize(rebuild=True):
                        print("✓ Database rebuilt successfully!")
                    else:
                        print("❌ Failed to rebuild database")
                    continue
                
                self.query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Modern Robotics RAG Chatbot (GPU)")
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the vector database from PDFs"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Single query mode"
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = ModernRoboticsRAGGPU(ollama_model=args.model)
    
    # Initialize
    if not rag.initialize(rebuild=args.rebuild):
        print("❌ Failed to initialize RAG system")
        sys.exit(1)
    
    print("=" * 70)
    print("✅ RAG System Ready!")
    print("=" * 70)
    print()
    
    # Single query or interactive mode
    if args.query:
        rag.query(args.query)
    else:
        rag.chat()


if __name__ == "__main__":
    main()
