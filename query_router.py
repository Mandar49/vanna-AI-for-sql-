"""
Query Router - Dual-Brain Intelligence System
Routes queries between SQL Brain (Vanna) and General Intelligence Brain (Mistral)
"""
import ollama
from common import vn

class QueryRouter:
    def __init__(self):
        # Initialize general LLM for conversational queries
        self.general_model = "mistral:7b-instruct"
        
        # SQL-related keywords that trigger the Vanna brain
        self.sql_keywords = [
            "customer", "order", "sales", "employee", "department",
            "table", "query", "data", "sql", "industry", "amount",
            "total", "average", "count", "record", "show", "list",
            "phone", "email", "address", "contact", "manager",
            "city", "product", "revenue", "profit", "salary",
            "hire", "department", "top", "best", "worst", "highest",
            "lowest", "sum", "calculate", "find", "get", "retrieve"
        ]
    
    def classify_query(self, question: str) -> str:
        """
        Classify whether a query should go to SQL brain or General brain
        Returns: 'sql' or 'general'
        """
        question_lower = question.lower()
        
        # Check for SQL-related keywords
        if any(keyword in question_lower for keyword in self.sql_keywords):
            return "sql"
        
        # Check for question patterns that suggest data retrieval
        data_patterns = ["how many", "how much", "what is the", "who are", "which", "list all"]
        if any(pattern in question_lower for pattern in data_patterns):
            # Could be either - check if it mentions database entities
            if any(keyword in question_lower for keyword in ["customer", "employee", "order", "sales", "department"]):
                return "sql"
        
        return "general"
    
    def route_query(self, question: str, conversation_history: list = None):
        """
        Route the query to the appropriate brain
        Returns: dict with 'type', 'answer', and optionally 'sql'
        """
        query_type = self.classify_query(question)
        
        if query_type == "sql":
            # Use Vanna SQL Brain
            return {
                "type": "sql",
                "question": question
            }
        else:
            # Use General Intelligence Brain
            return self._handle_general_query(question, conversation_history)
    
    def _handle_general_query(self, question: str, conversation_history: list = None):
        """
        Handle general conversational queries using Mistral
        """
        # Build context from conversation history
        context_messages = []
        
        if conversation_history:
            # Include last 5 exchanges for context
            for msg in conversation_history[-10:]:  # Last 5 exchanges (10 messages)
                if msg['role'] == 'user':
                    context_messages.append(f"User: {msg['value']}")
                elif msg['role'] == 'assistant':
                    context_messages.append(f"Assistant: {msg['value']}")
        
        # Build the prompt with context
        system_prompt = """You are a helpful, knowledgeable AI assistant. You provide clear, accurate, and conversational responses to questions on any topic. 
You are friendly, professional, and always aim to be helpful. When you don't know something, you admit it honestly.
You are part of a business intelligence system, but you can also answer general knowledge questions."""
        
        # Combine context and current question
        if context_messages:
            full_prompt = "\n".join(context_messages) + f"\nUser: {question}\nAssistant:"
        else:
            full_prompt = f"User: {question}\nAssistant:"
        
        try:
            # Call Ollama with Mistral model
            response = ollama.chat(
                model=self.general_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            answer = response['message']['content']
            
            return {
                "type": "general",
                "answer": answer,
                "sql": None
            }
        except Exception as e:
            return {
                "type": "general",
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sql": None
            }

# Global router instance
router = QueryRouter()
