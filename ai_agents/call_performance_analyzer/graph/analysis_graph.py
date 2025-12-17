"""
LangGraph workflow for call performance analysis
"""
from langgraph.graph import StateGraph, END
from graph.state import AnalysisState
from agents.analysis_nodes import (
    prepare_batch_node,
    analyze_call_node,
    accumulate_metrics_node,
    check_completion_node
)
from utils.logger import logger


def create_analysis_graph() -> StateGraph:
    """
    Create the LangGraph workflow for call analysis
    
    Returns:
        Compiled StateGraph
    """
    logger.info("Creating analysis graph")
    
    # Create graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("prepare_batch", prepare_batch_node)
    workflow.add_node("analyze_calls", analyze_call_node)
    workflow.add_node("accumulate_metrics", accumulate_metrics_node)
    workflow.add_node("check_completion", check_completion_node)
    
    # Define edges
    workflow.set_entry_point("prepare_batch")
    workflow.add_edge("prepare_batch", "analyze_calls")
    workflow.add_edge("analyze_calls", "accumulate_metrics")
    workflow.add_edge("accumulate_metrics", "check_completion")
    
    # Conditional edge from check_completion
    def should_continue(state: AnalysisState) -> str:
        """Determine if we should continue processing or end"""
        if state.get('ready_for_report', False):
            return "end"
        return "continue"
    
    workflow.add_conditional_edges(
        "check_completion",
        should_continue,
        {
            "end": END,
            "continue": END  # Will be handled by orchestrator
        }
    )
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Analysis graph created successfully")
    return graph

