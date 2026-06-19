"""
Gradio user interface for Multi-Policy RAG Application.
Provides web interface for loading policies and asking questions.
"""

import io
import contextlib
from typing import Optional, Tuple

import gradio as gr

from .config import Config
from .agent import PolicyAgent, build_or_load_vectorstore, clear_indexes
from .orchestrator import ToolCallingOrchestrator
from langchain_openai import ChatOpenAI


# Global references (set by create_interface)
_orchestrator: Optional[ToolCallingOrchestrator] = None
_config: Optional[Config] = None


def set_orchestrator(orchestrator: ToolCallingOrchestrator, config: Config) -> None:
    """Set global orchestrator and config references."""
    global _orchestrator, _config
    _orchestrator = orchestrator
    _config = config


def ui_build(medical_file, dental_file) -> str:
    """
    Build or load the system from uploaded files or default paths.
    
    Args:
        medical_file: Uploaded medical PDF (or None to use default)
        dental_file: Uploaded dental PDF (or None to use default)
        
    Returns:
        Build log as string
    """
    global _orchestrator, _config
    
    if _config is None:
        return "❌ Configuration not initialized."
    
    try:
        # Determine paths
        med_path = medical_file.name if medical_file is not None else _config.get_medical_pdf_path()
        den_path = dental_file.name if dental_file is not None else _config.get_dental_pdf_path()
        
        # Capture output
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            # Build vector stores
            llm = ChatOpenAI(model=_config.LLM_MODEL, temperature=0)
            
            med_vs = build_or_load_vectorstore(
                med_path,
                "Medical",
                _config.get_medical_index_path(),
                _config
            )
            den_vs = build_or_load_vectorstore(
                den_path,
                "Dental",
                _config.get_dental_index_path(),
                _config
            )
            
            # Create agents
            medical_agent = PolicyAgent("Medical", med_vs, llm, k=_config.TOP_K)
            dental_agent = PolicyAgent("Dental", den_vs, llm, k=_config.TOP_K)
            
            # Create orchestrator
            _orchestrator = ToolCallingOrchestrator(medical_agent, dental_agent, llm)
            
            print("System ready. Tool-calling orchestrator is online.")
        
        return buf.getvalue() or "✅ System ready."
    
    except Exception as e:
        return f"❌ Build failed: {e}"


def ui_rebuild(medical_file, dental_file) -> str:
    """
    Clear indexes and rebuild from scratch.
    
    Args:
        medical_file: Uploaded medical PDF (or None to use default)
        dental_file: Uploaded dental PDF (or None to use default)
        
    Returns:
        Rebuild log as string
    """
    global _config
    
    if _config is None:
        return "❌ Configuration not initialized."
    
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            # Clear existing indexes
            clear_indexes(_config)
            print("\nRebuilding indexes...\n")
        
        # Build system
        result = ui_build(medical_file, dental_file)
        return buf.getvalue() + "\n" + result
    
    except Exception as e:
        return f"❌ Rebuild failed: {e}\n\n{buf.getvalue()}"


def ui_ask(question: str) -> Tuple[str, str, str]:
    """
    Send a question to the orchestrator.
    
    Args:
        question: User's question
        
    Returns:
        Tuple of (answer_markdown, chain_of_thought_markdown, sources_markdown)
    """
    global _orchestrator
    
    if _orchestrator is None:
        msg = "⚠️ Build the system first using the button in Tab 1."
        return msg, "", ""
    
    if not question or not question.strip():
        return "⚠️ Please type a question.", "", ""
    
    try:
        result = _orchestrator.answer(question.strip())
    except Exception as e:
        return f"❌ Error: {e}", "", ""
    
    # Format final answer with policy badge
    if result["source_policy"] == "Medical":
        badge = "🩺 **Medical Policy**"
    elif result["source_policy"] == "Dental":
        badge = "🦷 **Dental Policy**"
    else:
        badge = "🚫 **No policy match**"
    
    answer_md = f"### Final Answer\n{badge}\n\n> {result['final_answer']}"
    
    # Format chain of thought
    cot_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(result["chain_of_thought"]))
    
    # Format sources with provenance
    if result["sources"]:
        lines = []
        for i, s in enumerate(result["sources"], 1):
            file_tag = f" · `{s.get('source_file','?')}`" if s.get("source_file") else ""
            lines.append(
                f"**[{i}]** _{s['policy']}_{file_tag} — page {s['page']}  \n"
                f"<small>{s['snippet']}</small>"
            )
        sources_md = "\n\n".join(lines)
    else:
        sources_md = "_No sources — nothing was retrieved._"
    
    return answer_md, cot_md, sources_md


def create_interface(orchestrator: ToolCallingOrchestrator, config: Config) -> gr.Blocks:
    """
    Create the Gradio interface.
    
    Args:
        orchestrator: Initialized orchestrator
        config: Configuration object
        
    Returns:
        Gradio Blocks interface
    """
    # Set global references
    set_orchestrator(orchestrator, config)
    
    # Create interface
    with gr.Blocks(
        title="Multi-Policy RAG Orchestrator",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown(
            "# 🩺🦷 Multi-Policy RAG Orchestrator\n"
            "Tool-calling orchestrator over Medical + Dental policies, with persistent FAISS indexes."
        )
        
        with gr.Tab("1. Load Policies"):
            gr.Markdown(
                "Upload both PDFs (or leave blank to use default files in `data/pdfs/`), "
                "then click **Build / Load System**. "
                "Indexes are persisted in `data/faiss_indexes/` and reloaded on subsequent runs."
            )
            
            with gr.Row():
                medical_pdf_in = gr.File(label="Medical PDF", file_types=[".pdf"])
                dental_pdf_in = gr.File(label="Dental PDF", file_types=[".pdf"])
            
            with gr.Row():
                build_btn = gr.Button("Build / Load System", variant="primary")
                rebuild_btn = gr.Button("Clear & Rebuild Indexes", variant="secondary")
            
            build_log = gr.Textbox(label="Build Log", lines=12, interactive=False)
            
            # Wire up buttons
            build_btn.click(
                ui_build,
                inputs=[medical_pdf_in, dental_pdf_in],
                outputs=build_log
            )
            rebuild_btn.click(
                ui_rebuild,
                inputs=[medical_pdf_in, dental_pdf_in],
                outputs=build_log
            )
        
        with gr.Tab("2. Ask Questions"):
            question_in = gr.Textbox(
                label="Question",
                placeholder="Ask a question about the medical or dental policy...",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")
            
            answer_out = gr.Markdown(label="Answer")
            
            with gr.Accordion("🧠 Chain of Thought", open=True):
                cot_out = gr.Markdown()
            
            with gr.Accordion("📄 Retrieved Source Snippets (with provenance)", open=False):
                sources_out = gr.Markdown()
            
            # Wire up ask button
            ask_btn.click(
                ui_ask,
                inputs=question_in,
                outputs=[answer_out, cot_out, sources_out]
            )
            question_in.submit(
                ui_ask,
                inputs=question_in,
                outputs=[answer_out, cot_out, sources_out]
            )
            
            # Example questions
            gr.Examples(
                examples=[
                    "Is a root canal covered?",
                    "What is the annual out-of-pocket maximum?",
                    "Does the plan cover orthodontia for adults?",
                    "Are MRI scans covered?",
                    "What are the copays for specialist visits?",
                    "Does the plan cover dental cleanings?",
                ],
                inputs=question_in,
            )
    
    return demo

# Made with Bob
