"""
Local Ollama RAG Chatbot for Modern Robotics PDFs
Uses ChromaDB for vector storage and Ollama for embeddings and generation
"""

import os
import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
import warnings
warnings.filterwarnings('ignore')


class ModernRoboticsRAG:
    def __init__(self, ollama_model="llama3.2", embedding_model="nomic-embed-text"):
        """Initialize the RAG chatbot with Ollama."""
        self.ollama_model = ollama_model
        self.embedding_model = embedding_model
        self.pdf_directory = Path(__file__).parent.parent
        self.chroma_db_dir = Path(__file__).parent / "chroma_db"
        
        print("=" * 70)
        print("Modern Robotics RAG Chatbot")
        print("=" * 70)
        print(f"PDF Directory: {self.pdf_directory}")
        print(f"Vector DB Directory: {self.chroma_db_dir}")
        print(f"LLM Model: {self.ollama_model}")
        print(f"Embedding Model: {self.embedding_model}")
        print()
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=self.embedding_model)
        
        # Initialize vector store
        self.vectorstore = None
        self.qa_chain = None
    
    def find_pdfs(self):
        """Find all PDF files in the repository."""
        pdf_files = []
        # For now, just use MRlib.pdf for faster testing
        mrlib = self.pdf_directory / "doc" / "MRlib.pdf"
        if mrlib.exists():
            pdf_files.append(mrlib)
            print(f"   [DEBUG] Found: {mrlib}")
        else:
            print(f"   [DEBUG] MRlib.pdf not found at: {mrlib}")
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
            print(f"  - {pdf.name}")
        print()
        
        # Load documents
        print("📖 Loading PDF documents...")
        all_documents = []
        for pdf_path in pdf_files:
            try:
                print(f"   [DEBUG] Loading {pdf_path.name}...")
                loader = PyPDFLoader(str(pdf_path))
                print(f"   [DEBUG] PyPDFLoader created, calling load()...")
                documents = loader.load()
                print(f"   [DEBUG] Loaded {len(documents)} pages")
                all_documents.extend(documents)
                print(f"  ✓ Loaded {len(documents)} pages from {pdf_path.name}")
            except Exception as e:
                print(f"  ❌ Error loading {pdf_path.name}: {e}")
                import traceback
                traceback.print_exc()
        
        if not all_documents:
            print("❌ No documents loaded!")
            return []
        
        print(f"✓ Total pages loaded: {len(all_documents)}\n")
        
        # Split into chunks
        print("✂️ Splitting documents into chunks...")
        print(f"   [DEBUG] Creating text splitter with chunk_size=500, overlap=100")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # Smaller chunks for faster processing
            chunk_overlap=100,
            length_function=len,
        )
        print(f"   [DEBUG] Splitting {len(all_documents)} documents...")
        chunks = text_splitter.split_documents(all_documents)
        print(f"✓ Created {len(chunks)} text chunks\n")
        
        return chunks
    
    def create_vectorstore(self, chunks):
        """Create or load ChromaDB vector store."""
        print("🗄️ Creating vector database...")
        print(f"   [DEBUG] Processing {len(chunks)} chunks...")
        print(f"   [DEBUG] This will call Ollama embedding model: {self.embedding_model}")
        print("   This may take a few minutes on first run...")
        
        # Create directory if it doesn't exist
        self.chroma_db_dir.mkdir(exist_ok=True)
        print(f"   [DEBUG] Vector DB directory: {self.chroma_db_dir}")
        
        try:
            # Test embedding connection first
            print("   [DEBUG] Testing Ollama connection with sample text...")
            test_embedding = self.embeddings.embed_query("test")
            print(f"   [DEBUG] ✓ Ollama responded! Embedding dimension: {len(test_embedding)}")
            
            # Create vector store with progress
            print(f"   [DEBUG] Now embedding all {len(chunks)} chunks...")
            print("   [DEBUG] This is the slow part - Ollama processes each chunk...")
            
            import time
            start_time = time.time()
            
            # Process in smaller batches to show progress
            batch_size = 10
            all_ids = []
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(chunks) + batch_size - 1) // batch_size
                print(f"   [DEBUG] Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
                
                if i == 0:
                    # Create on first batch
                    self.vectorstore = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        persist_directory=str(self.chroma_db_dir),
                        collection_name="modern_robotics"
                    )
                else:
                    # Add to existing
                    self.vectorstore.add_documents(batch)
                
                elapsed = time.time() - start_time
                print(f"   [DEBUG] Elapsed: {elapsed:.1f}s, Progress: {min(i+batch_size, len(chunks))}/{len(chunks)}")
            
            total_time = time.time() - start_time
            print(f"✓ Vector database created with {len(chunks)} chunks in {total_time:.1f}s\n")
            return True
        except Exception as e:
            print(f"❌ Error creating vector database: {e}")
            print(f"   Make sure Ollama is running and has the embedding model")
            print(f"   Try: ollama pull {self.embedding_model}")
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
        
        # Initialize Ollama LLM
        llm = Ollama(
            model=self.ollama_model,
            temperature=0.7,
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}  # Retrieve top 4 most relevant chunks
            ),
            return_source_documents=True,
        )
        
        print("✓ QA chain ready\n")
    
    def initialize(self, rebuild=False):
        """Initialize the RAG system."""
        # Check if we can load existing vectorstore
        if not rebuild and self.load_existing_vectorstore():
            self.setup_qa_chain()
            return True
        
        # Otherwise, build from scratch
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
    
    parser = argparse.ArgumentParser(description="Modern Robotics RAG Chatbot")
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--embedding-model",
        default="nomic-embed-text",
        help="Ollama embedding model (default: nomic-embed-text)"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the vector database from PDFs"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Single query mode (don't start interactive chat)"
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = ModernRoboticsRAG(
        ollama_model=args.model,
        embedding_model=args.embedding_model
    )
    
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
