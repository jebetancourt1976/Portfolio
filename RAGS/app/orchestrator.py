"""
ToolCallingOrchestrator implementation for LLM-driven intent-based routing.
Manages tool execution, fallback mechanism, and chain-of-thought tracking.
"""

from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

from .agent import PolicyAgent


# Module-level references to agents (set by main.py)
_medical_agent: Optional[PolicyAgent] = None
_dental_agent: Optional[PolicyAgent] = None


def set_agents(medical: PolicyAgent, dental: PolicyAgent) -> None:
    """Set the global agent references for tool functions."""
    global _medical_agent, _dental_agent
    _medical_agent = medical
    _dental_agent = dental


# Tool definitions exposed to the LLM
@tool
def search_medical_policy(query: str) -> str:
    """
    Search the MEDICAL policy knowledge base. Use for questions about medical coverage,
    hospitalization, prescriptions, imaging, specialists, deductibles, etc.
    Returns either a grounded answer or the literal token 'NOT_FOUND'.
    """
    if _medical_agent is None:
        return "ERROR: Medical agent not initialized. Call build_system() first."
    return _medical_agent.ask(query)["answer"]


@tool
def search_dental_policy(query: str) -> str:
    """
    Search the DENTAL policy knowledge base. Use for questions about dental coverage,
    cleanings, fillings, crowns, root canals, orthodontia, periodontics, etc.
    Returns either a grounded answer or the literal token 'NOT_FOUND'.
    """
    if _dental_agent is None:
        return "ERROR: Dental agent not initialized. Call build_system() first."
    return _dental_agent.ask(query)["answer"]


# System prompt for the orchestrator
ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are an insurance benefits orchestrator with access to two tools: "
    "`search_medical_policy` and `search_dental_policy`.\n\n"
    "ROUTING POLICY:\n"
    "1. Read the user's question and pick the tool whose policy is more likely to contain the "
    "answer. Dental-specific queries (cleanings, fillings, crowns, root canals, orthodontia, "
    "periodontics, dentures) → search_dental_policy. Medical-specific queries (hospitalization, "
    "prescriptions, imaging, specialists, surgery, mental health) → search_medical_policy. "
    "Ambiguous queries → start with search_medical_policy.\n"
    "2. If the first tool returns 'NOT_FOUND', you MUST call the OTHER tool before answering.\n"
    "3. If both tools return 'NOT_FOUND', your final answer must be exactly: "
    "Not found in any policy.\n"
    "4. When a tool returns a real answer, return that answer to the user — do not paraphrase "
    "away the cited phrase.\n"
    "5. Never invent coverage details. Never use outside knowledge."
)


class ToolCallingOrchestrator:
    """
    LLM-driven orchestrator that picks tools by intent and falls back on NOT_FOUND.
    Implements intelligent routing with automatic fallback mechanism.
    """
    
    NOT_FOUND_FINAL = "Not found in any policy."
    
    def __init__(self, medical: PolicyAgent, dental: PolicyAgent, llm: ChatOpenAI):
        """
        Initialize the orchestrator.
        
        Args:
            medical: Medical policy agent
            dental: Dental policy agent
            llm: Language model for tool calling
        """
        self.medical = medical
        self.dental = dental
        
        # Bind both tools to the LLM
        self.tools = [search_medical_policy, search_dental_policy]
        self.tools_by_name = {t.name: t for t in self.tools}
        self.llm = llm.bind_tools(self.tools)
        
        # Set global agent references for tool functions
        set_agents(medical, dental)
    
    def _run_tool_with_sources(self, name: str, query: str) -> dict:
        """
        Run a specialist by name and capture sources.
        
        Args:
            name: Tool name ("search_medical_policy" or "search_dental_policy")
            query: Query string
            
        Returns:
            Dictionary with answer, found status, and sources
        """
        agent = self.medical if name == "search_medical_policy" else self.dental
        return agent.ask(query)
    
    def answer(self, question: str, max_iters: int = 4) -> dict:
        """
        Answer a question using tool-calling orchestration.
        
        Args:
            question: User's question
            max_iters: Maximum number of LLM iterations
            
        Returns:
            Dictionary with:
                - final_answer: The final answer
                - source_policy: Which policy provided the answer ("Medical", "Dental", or None)
                - sources: List of source documents
                - chain_of_thought: List of reasoning steps
        """
        cot: List[str] = []
        all_sources: List[dict] = []
        policies_consulted: List[str] = []
        
        cot.append(f"**Step 1 — User question:** _{question}_")
        cot.append("**Step 2 — Sending question to the LLM orchestrator with two tools bound.**")
        
        messages = [
            SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
        
        for it in range(max_iters):
            # Get LLM response
            ai_msg: AIMessage = self.llm.invoke(messages)
            messages.append(ai_msg)
            
            # Check if LLM produced final answer (no tool calls)
            if not ai_msg.tool_calls:
                # Handle content which can be string or list
                content = ai_msg.content
                if isinstance(content, list):
                    final = " ".join(str(item) for item in content).strip()
                else:
                    final = (content or "").strip()
                cot.append(f"**Step {len(cot)+1} — LLM produced final answer:** _{final}_")
                
                # Determine which policy was the actual source
                source_policy = None
                if policies_consulted and final != self.NOT_FOUND_FINAL:
                    # The last successful tool call is the source
                    for p in reversed(policies_consulted):
                        source_policy = p
                        break
                
                return {
                    "final_answer": final,
                    "source_policy": source_policy if final != self.NOT_FOUND_FINAL else None,
                    "sources": all_sources,
                    "chain_of_thought": cot,
                }
            
            # Execute every tool call the LLM requested this turn
            for call in ai_msg.tool_calls:
                tname = call["name"]
                targs = call["args"]
                query = targs.get("query", question)
                policy_label = "Medical" if tname == "search_medical_policy" else "Dental"
                
                cot.append(
                    f"**Step {len(cot)+1} — LLM chose tool `{tname}`** with query "
                    f"_{query}_ → calling {policy_label} agent."
                )
                
                # Run the tool and get results
                result = self._run_tool_with_sources(tname, query)
                answer_text = result["answer"]
                
                # Truncate long answers in COT
                display_answer = answer_text if len(answer_text) < 220 else answer_text[:200] + "..."
                cot.append(
                    f"**Step {len(cot)+1} — {policy_label} agent returned:** "
                    f"_{display_answer}_"
                )
                
                # Track successful queries and sources
                if result["found"]:
                    policies_consulted.append(policy_label)
                    all_sources.extend(result["sources"])
                else:
                    cot.append(
                        f"**Step {len(cot)+1} — `NOT_FOUND` from {policy_label}.** "
                        f"Orchestrator should call the other tool next."
                    )
                
                # Send tool result back to LLM
                messages.append(ToolMessage(content=answer_text, tool_call_id=call["id"]))
        
        # Safety net: ran out of iterations
        cot.append(f"**Step {len(cot)+1} — Reached max_iters={max_iters} without a final answer.**")
        return {
            "final_answer": self.NOT_FOUND_FINAL,
            "source_policy": None,
            "sources": all_sources,
            "chain_of_thought": cot,
        }

# Made with Bob
