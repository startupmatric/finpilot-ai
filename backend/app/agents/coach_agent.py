
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.llm.groq_client import groq_client
from app.llm.prompts import get_coach_prompt, format_analytics_for_llm
from app.tools.analytics_tools import AnalyticsTools

class CoachAgent:
    """Agent that provides coaching and insights using LLM"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = AnalyticsTools(db)
    
    def process(self, state: AgentState) -> AgentState:
        """Generate coaching response"""
        question = state.get("question", "")
        results = {}
        
        # Gather all analytics for context
        results["category"] = self.tools.get_spending_by_category()
        results["statistics"] = self.tools.get_statistics()
        results["health"] = self.tools.get_health_score()
        
        state["tool_results"] = results
        state["tool_calls"] = list(results.keys())
        
        # Generate response using Groq
        if groq_client.is_available():
            analytics_data = format_analytics_for_llm(results)
            prompt = f"""
            User question: {question}
            
            Financial data:
            {analytics_data}
            
            Provide a helpful, coaching response.
            """
            state["response"] = groq_client.generate_response(
                get_coach_prompt(),
                prompt
            )
        else:
            # Fallback: generate a simple response
            state["response"] = self._generate_fallback_response(results)
        
        return state
    
    def _generate_fallback_response(self, results: dict) -> str:
        """Generate fallback response without LLM"""
        parts = []
        
        # Category breakdown
        if "category" in results:
            parts.append("📊 Spending by Category:")
            for item in results["category"].get("summary", [])[:5]:
                parts.append(f"  • {item['category']}: ₹{item['total']:,.2f} ({item['percentage']}%)")
        
        # Statistics
        if "statistics" in results:
            stats = results["statistics"]["statistics"]
            parts.append("\n📈 Statistics:")
            parts.append(f"  • Total transactions: {stats['total_transactions']}")
            parts.append(f"  • Average: ₹{stats['average_amount']:,.2f}")
            parts.append(f"  • Largest: ₹{stats['largest_amount']:,.2f}")
        
        # Health score
        if "health" in results:
            health = results["health"]["health_score"]
            parts.append(f"\n💚 Health Score: {health['score']}/100")
            if health.get("recommendations"):
                parts.append("   💡 Tips:")
                for rec in health["recommendations"][:2]:
                    parts.append(f"   • {rec}")
        
        return "\n".join(parts) if parts else "No data available. Try uploading some transactions first."