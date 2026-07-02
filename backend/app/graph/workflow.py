
from typing import Dict, Any
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from app.graph.state import AgentState
from app.agents.supervisor import SupervisorAgent
from app.agents.spending_agent import SpendingAgent
from app.agents.merchant_agent import MerchantAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.statistics_agent import StatisticsAgent
from app.agents.coach_agent import CoachAgent
from app.llm.groq_client import groq_client
from app.llm.prompts import get_system_prompt, format_analytics_for_llm

class FinPilotWorkflow:
    """Main LangGraph workflow for FinPilot"""
    
    def __init__(self, db: Session):
        self.db = db
        self.supervisor = SupervisorAgent(db)
        self.spending = SpendingAgent(db)
        self.merchant = MerchantAgent(db)
        self.budget = BudgetAgent(db)
        self.statistics = StatisticsAgent(db)
        self.coach = CoachAgent(db)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self.route)
        workflow.add_node("spending", self.process_spending)
        workflow.add_node("merchant", self.process_merchant)
        workflow.add_node("budget", self.process_budget)
        workflow.add_node("statistics", self.process_statistics)
        workflow.add_node("coach", self.process_coach)
        workflow.add_node("generate_response", self.generate_response)
        
        # Add edges
        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self.route_condition,
            {
                "spending": "spending",
                "merchant": "merchant",
                "budget": "budget",
                "statistics": "statistics",
                "coach": "coach"
            }
        )
        
        # All agents go to response generation
        workflow.add_edge("spending", "generate_response")
        workflow.add_edge("merchant", "generate_response")
        workflow.add_edge("budget", "generate_response")
        workflow.add_edge("statistics", "generate_response")
        workflow.add_edge("coach", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def route(self, state: AgentState) -> AgentState:
        """Route the question to the appropriate agent"""
        return self.supervisor.route(state)
    
    def route_condition(self, state: AgentState) -> str:
        """Conditional routing based on intent"""
        return state.get("agent", "coach")
    
    def process_spending(self, state: AgentState) -> AgentState:
        """Process spending queries"""
        return self.spending.process(state)
    
    def process_merchant(self, state: AgentState) -> AgentState:
        """Process merchant queries"""
        return self.merchant.process(state)
    
    def process_budget(self, state: AgentState) -> AgentState:
        """Process budget queries"""
        return self.budget.process(state)
    
    def process_statistics(self, state: AgentState) -> AgentState:
        """Process statistics queries"""
        return self.statistics.process(state)
    
    def process_coach(self, state: AgentState) -> AgentState:
        """Process coaching queries"""
        return self.coach.process(state)
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate final response using Groq"""
        question = state.get("question", "")
        results = state.get("tool_results", {})
        
        # If coach already generated a response, use it
        if state.get("agent") == "coach" and state.get("response"):
            return state
        
        # Otherwise, use Groq or fallback
        if groq_client.is_available():
            analytics_data = format_analytics_for_llm(results)
            prompt = f"""
            User question: {question}
            
            Financial data:
            {analytics_data}
            
            Provide a clear, helpful response.
            """
            state["response"] = groq_client.generate_response(
                get_system_prompt(),
                prompt
            )
        else:
            # Simple fallback response
            parts = ["📊 Here's your financial data:"]
            for key, value in results.items():
                if key == "category":
                    parts.append("\nSpending by category:")
                    for item in value.get("summary", [])[:5]:
                        parts.append(f"  • {item['category']}: ₹{item['total']:,.2f}")
                elif key == "statistics":
                    stats = value.get("statistics", {})
                    parts.append(f"\nTotal: ₹{stats.get('total_spending', 0):,.2f}")
                    parts.append(f"Average: ₹{stats.get('average_amount', 0):,.2f}")
                elif key == "budget":
                    budget = value.get("budget_status", {})
                    parts.append(f"\nBudget: ₹{budget.get('budget', 0):,.2f}")
                    parts.append(f"Spent: ₹{budget.get('spent', 0):,.2f}")
                    parts.append(f"Remaining: ₹{budget.get('remaining', 0):,.2f}")
            
            state["response"] = "\n".join(parts) if len(parts) > 1 else "No data available."
        
        return state
    
    def process(self, question: str) -> Dict[str, Any]:
        """Process a question through the workflow"""
        initial_state = {
            "question": question,
            "intent": "",
            "agent": "",
            "tool_calls": [],
            "tool_results": {},
            "response": "",
            "error": None,
            "context": {}
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "question": question,
            "intent": result.get("intent", ""),
            "agent": result.get("agent", ""),
            "response": result.get("response", ""),
            "data": result.get("tool_results", {})
        }