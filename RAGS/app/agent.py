"""
PolicyAgent implementation for single-policy RAG specialist.
Handles vector store operations and implements strict NOT_FOUND contract.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .config import Config


# Strict prompt template that enforces NOT_FOUND contract
STRICT_PROMPT = (
    "You are a {policy_label} policy specialist. Answer the user's question using ONLY the "
    "context below, which is taken from the {policy_label} Policy document.\n\n"
    "STRICT RULES:\n"
    "1. If the context clearly contains the answer, provide a concise, factual answer and "
    "quote the most relevant phrase.\n"
    "2. If the context does NOT contain enough information to answer, you MUST reply with "
    "exactly this token and nothing else: NOT_FOUND\n"
    "3. Never use outside knowledge. Never guess.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n"
    "Answer:"
)


def _format_docs(docs) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n---\n\n".join(d.page_content for d in docs)


class PolicyAgent:
    """
    A single-policy RAG specialist.
    Returns either a grounded answer with sources or 'NOT_FOUND'.
    """
    
    def __init__(
        self,
        name: str,
        vectorstore: FAISS,
        llm: ChatOpenAI,
        k: int = 4,
        prompt_template: str = STRICT_PROMPT
    ):
        """
        Initialize PolicyAgent.
        
        Args:
            name: Policy name (e.g., "Medical" or "Dental")
            vectorstore: FAISS vector store for this policy
            llm: Language model for generation
            k: Number of documents to retrieve
            prompt_template: Prompt template with strict NOT_FOUND contract
        """
        self.name = name
        self.vectorstore = vectorstore
        self.llm = llm
        self.k = k
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        
        # Create prompt with policy label
        self._prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template.replace("{policy_label}", name),
        )
        
        # Build LCEL chain: prompt → llm → parser
        self._chain = self._prompt | llm | StrOutputParser()
    
    def ask(self, question: str) -> dict:
        """
        Ask a question to this policy specialist.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with:
                - answer: The generated answer or "NOT_FOUND"
                - found: Boolean indicating if answer was found
                - sources: List of source documents with metadata
        """
        # Retrieve relevant documents
        docs = self.retriever.invoke(question)
        
        # Format context
        context = _format_docs(docs)
        
        # Generate answer
        answer = self._chain.invoke({
            "context": context,
            "question": question
        }).strip()
        
        # Check if answer was found (NOT_FOUND token not present)
        found = "NOT_FOUND" not in answer.upper().split()
        
        # Extract source information with provenance
        sources = [
            {
                "page": d.metadata.get("page"),
                "policy": d.metadata.get("policy", self.name),
                "source_file": d.metadata.get("source_file"),
                "snippet": d.page_content[:220].replace("\n", " ") + "...",
            }
            for d in docs
        ]
        
        return {
            "answer": answer,
            "found": found,
            "sources": sources
        }


def build_or_load_vectorstore(
    pdf_path: Path,
    label: str,
    index_path: Path,
    config: Config
) -> FAISS:
    """
    Build or load a FAISS vector store for a policy document.
    
    If the index already exists on disk, it will be loaded.
    Otherwise, the PDF will be processed and a new index created.
    
    Args:
        pdf_path: Path to PDF document
        label: Policy label (e.g., "Medical" or "Dental")
        index_path: Path where index should be saved/loaded
        config: Configuration object
        
    Returns:
        FAISS vector store
    """
    embeddings = OpenAIEmbeddings(model=config.EMBED_MODEL)
    
    # Try to load existing index
    if index_path.exists():
        print(f"[{label}] Reloading existing index from {index_path} ...")
        vs = FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print(f"[{label}]   Loaded.\n")
        return vs
    
    # Build new index
    print(f"[{label}] Building new index from {pdf_path} ...")
    
    # Load PDF
    loader = PyMuPDFLoader(str(pdf_path))
    pages = loader.load()
    print(f"[{label}]   {len(pages)} pages loaded.")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)
    
    # Tag each chunk with provenance metadata
    for c in chunks:
        c.metadata["policy"] = label
        c.metadata["source_file"] = os.path.basename(str(pdf_path))
    
    print(f"[{label}]   {len(chunks)} chunks created, all tagged with policy='{label}'.")
    
    # Create FAISS index
    vs = FAISS.from_documents(chunks, embeddings)
    
    # Save to disk for future use
    vs.save_local(str(index_path))
    print(f"[{label}]   Index saved to {index_path}.\n")
    
    return vs


def clear_indexes(config: Config) -> None:
    """
    Delete persisted indexes so the next build re-embeds the PDFs.
    
    Args:
        config: Configuration object
    """
    for p in (config.get_medical_index_path(), config.get_dental_index_path()):
        if p.exists():
            shutil.rmtree(p)
            print(f"Removed {p}")

# Made with Bob
