from langgraph.graph import StateGraph, END
from .state import PaperState
from .nodes.fetcher import fetch_node
from .nodes.filter import filter_node
from .nodes.summarizer import summarize_node
from .nodes.reporter import report_node
from .nodes.notify import notify_node

def create_graph():
    workflow = StateGraph(PaperState)
    
    # Add nodes
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("report", report_node)
    workflow.add_node("notify", notify_node)
    
    # Define edges
    workflow.set_entry_point("fetch")
    workflow.add_edge("fetch", "filter")
    workflow.add_edge("filter", "summarize")
    workflow.add_edge("summarize", "report")
    workflow.add_edge("report", "notify")
    workflow.add_edge("notify", END)
    
    return workflow.compile()
