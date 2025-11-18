"""
Query Router - DB-INTELLIGENCE-V1 Hybrid System
Routes queries intelligently between SQL execution and business reasoning
Combines strict data accuracy with advanced business intelligence
"""
import ollama
from common import vn
from hybrid_reasoner import HybridReasoner

class QueryRouter:
    def __init__(self):
        # Initialize hybrid reasoning engine
        self.hybrid_reasoner = HybridReasoner()
        
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
    
    def detect_person_query(self, question: str) -> bool:
        """
        Detect if query is asking about a specific person
        Returns: True if person query detected
        """
        person_patterns = [
            'tell me about',
            'who is',
            'what company does',
            'phone number',
            'email',
            'contact',
            'works at',
            'employee named',
            'customer named'
        ]
        question_lower = question.lower()
        return any(pattern in question_lower for pattern in person_patterns)
    
    def classify_query(self, question: str) -> str:
        """
        DB-INTELLIGENCE-V1: Classify query type with hybrid intelligence
        Returns: 'sql', 'person', 'hybrid', or 'general'
        """
        question_lower = question.lower()
        
        # Check for person queries first (must search DB before answering)
        if self.detect_person_query(question):
            return "person"
        
        # Use hybrid reasoner to determine if SQL is needed
        if self.hybrid_reasoner.should_use_sql(question):
            return "sql"
        
        # Check for SQL-related keywords
        if any(keyword in question_lower for keyword in self.sql_keywords):
            return "sql"
        
        # Check for question patterns that suggest data retrieval
        data_patterns = ["how many", "how much", "what is the", "who are", "which", "list all"]
        if any(pattern in question_lower for pattern in data_patterns):
            # Could be either - check if it mentions database entities
            if any(keyword in question_lower for keyword in ["customer", "employee", "order", "sales", "department"]):
                return "sql"
        
        # General knowledge/business concept questions
        return "general"
    
    def route_query(self, question: str, conversation_history: list = None):
        """
        Route the query to the appropriate brain
        Returns: dict with 'type', 'answer', and optionally 'sql'
        """
        query_type = self.classify_query(question)
        
        if query_type == "person":
            # Person query - must search database first
            return {
                "type": "person",
                "question": question
            }
        elif query_type == "sql":
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
        DB-INTELLIGENCE-V1: Handle general queries with business intelligence
        No longer blocks questions - provides knowledgeable answers
        """
        question_lower = question.lower()
        
        # System/help queries
        help_keywords = ['help', 'how to use', 'what can you', 'commands', 'features']
        if any(keyword in question_lower for keyword in help_keywords):
            return {
                "type": "general",
                "answer": "I am DB-INTELLIGENCE-V1, a hybrid AI Business Analyst. I combine strict SQL accuracy for data queries with advanced business intelligence for interpretation and strategy. Ask me about your data, business concepts, or strategic recommendations.",
                "sql": None
            }
        
        # Use hybrid reasoner for general business questions
        answer = self.hybrid_reasoner.answer_general_question(question)
        
        return {
            "type": "general",
            "answer": answer,
            "sql": None
        }

# Global router instance
router = QueryRouter()
