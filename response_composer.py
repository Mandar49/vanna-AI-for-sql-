"""
Response Composer - Dynamic persona-based response generation
Blends data analysis with human tone and strategic reasoning
"""
import ollama
from typing import Dict, Optional
from context_memory import memory

class Persona:
    """Base persona class"""
    def __init__(self, name: str, description: str, style: str):
        self.name = name
        self.description = description
        self.style = style

# Define three personas
ANALYST = Persona(
    name="Analyst",
    description="Precise, SQL-aware data analyst who provides factual observations",
    style="Professional, data-driven, technical. Focus on facts, numbers, and clear observations."
)

STRATEGIST = Persona(
    name="Strategist",
    description="CEO-level thinker who interprets impact, trends, and forecasts",
    style="Strategic, forward-thinking, business-focused. Emphasize implications, opportunities, and next steps."
)

WRITER = Persona(
    name="Writer",
    description="Communicator who creates human-sounding emails, reports, and updates",
    style="Conversational, empathetic, professional. Write naturally as a human would."
)

class ResponseComposer:
    def __init__(self):
        self.model = "mistral:7b-instruct"
        self.personas = {
            'analyst': ANALYST,
            'strategist': STRATEGIST,
            'writer': WRITER
        }
    
    def detect_persona(self, query: str) -> str:
        """
        Automatically detect which persona to use based on query
        
        Args:
            query: User's question
        
        Returns:
            Persona name ('analyst', 'strategist', or 'writer')
        """
        query_lower = query.lower()
        
        # Writer keywords
        writer_keywords = ['write', 'email', 'letter', 'message', 'compose', 'draft', 
                          'thank', 'congratulate', 'inform', 'notify']
        if any(keyword in query_lower for keyword in writer_keywords):
            return 'writer'
        
        # Strategist keywords
        strategist_keywords = ['strategy', 'trend', 'forecast', 'predict', 'recommend',
                              'should we', 'what if', 'impact', 'opportunity', 'risk',
                              'future', 'next quarter', 'growth', 'improve']
        if any(keyword in query_lower for keyword in strategist_keywords):
            return 'strategist'
        
        # Default to analyst
        return 'analyst'
    
    def compose_response(self, persona: str, query: str, analysis: Dict, 
                        raw_data: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        Compose a persona-specific response
        
        Args:
            persona: Persona to use ('analyst', 'strategist', 'writer')
            query: User's question
            analysis: Analysis results from business_analyst
            raw_data: Raw data summary (optional)
            context: Recent conversation context (optional)
        
        Returns:
            Formatted response string
        """
        persona_obj = self.personas.get(persona, ANALYST)
        
        # Get recent context if not provided
        if context is None:
            context = memory.recall_context(last_n=3)
        
        # Build prompt based on persona
        prompt = self._build_prompt(persona_obj, query, analysis, raw_data, context)
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {persona_obj.description}. {persona_obj.style}"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            composed = response['message']['content']
            
            # Add persona indicator
            persona_emoji = {
                'analyst': '📊',
                'strategist': '🧭',
                'writer': '✍️'
            }
            
            return f"{persona_emoji.get(persona, '💬')} **{persona_obj.name} Response:**\n\n{composed}"
            
        except Exception as e:
            # Fallback to analysis insight
            return analysis.get('insight', f"Error composing response: {str(e)}")
    
    def _build_prompt(self, persona: Persona, query: str, analysis: Dict, 
                     raw_data: Optional[str], context: Optional[str]) -> str:
        """Build persona-specific prompt"""
        
        prompt_parts = []
        
        # Add context if available
        if context and "No previous context" not in context:
            prompt_parts.append(f"Previous Context:\n{context}\n")
        
        prompt_parts.append(f"Current Question: {query}\n")
        
        # Add data and analysis
        if raw_data:
            prompt_parts.append(f"Data Retrieved:\n{raw_data}\n")
        
        if analysis.get('insight'):
            prompt_parts.append(f"Analysis Insight:\n{analysis['insight']}\n")
        
        # Persona-specific instructions
        if persona.name == "Analyst":
            prompt_parts.append("""
Your task as an Analyst:
1. Present the data clearly and accurately
2. Highlight key observations
3. Provide factual insights
4. Keep it professional and data-driven

Format your response with:
- **Key Finding:** [Main takeaway]
- **Observations:** [2-3 bullet points]
- **Data Summary:** [Brief summary]
""")
        
        elif persona.name == "Strategist":
            prompt_parts.append("""
Your task as a Strategist:
1. Interpret the business implications
2. Identify trends and patterns
3. Forecast potential outcomes
4. Recommend strategic actions

Format your response with:
- **Strategic Insight:** [High-level interpretation]
- **Trends & Implications:** [What this means for the business]
- **Recommendations:** [2-3 actionable next steps]
- **Forecast:** [Future outlook if applicable]
""")
        
        elif persona.name == "Writer":
            prompt_parts.append("""
Your task as a Writer:
1. Write in a natural, human tone
2. Be empathetic and professional
3. Structure the message appropriately
4. Make it ready to send/use

If writing an email/message:
- Include appropriate greeting
- Clear, friendly body
- Professional closing
- Natural language throughout
""")
        
        return "\n".join(prompt_parts)
    
    def compose_email(self, recipient: str, purpose: str, data: Dict) -> str:
        """
        Specialized method for composing emails
        
        Args:
            recipient: Name of recipient
            purpose: Purpose of email (thank you, update, etc.)
            data: Relevant data about recipient
        
        Returns:
            Formatted email
        """
        prompt = f"""
Write a professional email to {recipient}.

Purpose: {purpose}

Relevant Information:
{json.dumps(data, indent=2)}

Write a complete, ready-to-send email with:
- Appropriate greeting
- Clear, friendly message body
- Professional closing
- Natural, human tone
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business writer. Write clear, friendly, human emails."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return f"✍️ **Email Draft:**\n\n{response['message']['content']}"
            
        except Exception as e:
            return f"Error composing email: {str(e)}"

# Global composer instance
composer = ResponseComposer()
