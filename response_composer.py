"""
Response Composer - Structured plain text response generation
Outputs clean, markdown-free responses with COMPACT and DETAILED modes
"""
import re
import ollama
from typing import Dict, Optional
from context_memory import memory
from output_formatter import output_formatter

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
        self.mode = "DETAILED"  # Default mode
        self.hybrid_mode = True  # DB-INTELLIGENCE-V1: Enable hybrid output
    
    def set_mode(self, mode: str):
        """Set response mode: COMPACT or DETAILED"""
        if mode.upper() in ["COMPACT", "DETAILED"]:
            self.mode = mode.upper()
    
    def compose_hybrid_response(self, sql_result: str, insight: str, recommendation: str, 
                               sql_query: str = None, mode: str = None) -> str:
        """
        DB-INTELLIGENCE-V1: Compose hybrid response with SQL + reasoning
        
        Args:
            sql_result: Formatted SQL result
            insight: Business insight from hybrid reasoner
            recommendation: Strategic recommendation
            sql_query: SQL query executed (optional)
            mode: COMPACT or DETAILED
        
        Returns:
            Formatted hybrid response
        """
        mode = mode or self.mode
        response_parts = []
        
        # SQL RESULT section
        response_parts.append(self._format_section_header("SQL RESULT"))
        response_parts.append(sql_result)
        
        # INSIGHT section
        response_parts.append("\n" + self._format_section_header("INSIGHT"))
        response_parts.append(self._strip_markdown(insight))
        
        # STRATEGIC RECOMMENDATION section
        response_parts.append("\n" + self._format_section_header("STRATEGIC RECOMMENDATION"))
        response_parts.append(self._strip_markdown(recommendation))
        
        # SQL QUERY section (if detailed mode and query provided)
        if mode == "DETAILED" and sql_query:
            response_parts.append("\n" + self._format_section_header("SQL QUERY EXECUTED"))
            response_parts.append(sql_query)
        
        return "\n".join(response_parts)
    
    def compose_general_answer(self, answer: str) -> str:
        """
        DB-INTELLIGENCE-V1: Compose general knowledge answer (no SQL)
        
        Args:
            answer: Answer from hybrid reasoner
        
        Returns:
            Formatted answer
        """
        response_parts = []
        response_parts.append(self._format_section_header("ANSWER"))
        response_parts.append(self._strip_markdown(answer))
        return "\n".join(response_parts)
    
    def _format_section_header(self, title: str, width: int = 60) -> str:
        """Format a section header with separator lines"""
        separator = "─" * width
        return f"{separator}\n{title.upper()}\n{separator}"
    
    def _strip_markdown(self, text: str) -> str:
        """Remove all markdown formatting from text"""
        # Remove bold/italic markers
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold+italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)          # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)          # Bold (underscore)
        text = re.sub(r'_(.+?)_', r'\1', text)            # Italic (underscore)
        
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove code blocks
        text = re.sub(r'```[\w]*\n', '', text)
        text = re.sub(r'```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove links but keep text
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        # Remove list markers (keep the dash for plain lists)
        # text = re.sub(r'^\s*[-*+]\s+', '  ', text, flags=re.MULTILINE)
        
        return text
    
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
    
    def render_forecast_section(self, result: Dict, mode: str = None) -> str:
        """
        Render forecast section with database-calculated values
        
        Args:
            result: Forecast result with scenarios
            mode: COMPACT or DETAILED (uses instance mode if not specified)
        
        Returns:
            Formatted forecast section (plain text)
        """
        if not result.get('forecast'):
            return ""
        
        mode = mode or self.mode
        response_parts = []
        
        response_parts.append("\n" + self._format_section_header("FORECAST RESULTS"))
        response_parts.append("(Direct from Database + CAGR)\n")
        
        # Period and CAGR
        response_parts.append(f"Period: {result['start_year']}–{result['end_year']}")
        response_parts.append(f"CAGR: {result['cagr']}%")
        response_parts.append(f"Base Sales ({result['end_year']}): {result['end_sales']:.2f}\n")
        
        # Forecasts by year
        for year in sorted(result['forecast'].keys()):
            response_parts.append(f"{year} Forecasts:")
            
            if year in result.get('scenarios', {}):
                scenarios = result['scenarios'][year]
                if mode == "COMPACT":
                    response_parts.append(f"  Base: {scenarios['base']:.2f}")
                else:
                    response_parts.append(f"  - Base (CAGR {scenarios['cagr_base']}%): {scenarios['base']:.2f}")
                    response_parts.append(f"  - Optimistic (+10%, CAGR {scenarios['cagr_optimistic']}%): {scenarios['optimistic']:.2f}")
                    response_parts.append(f"  - Pessimistic (-10%, CAGR {scenarios['cagr_pessimistic']}%): {scenarios['pessimistic']:.2f}")
            else:
                response_parts.append(f"  Forecast: {result['forecast'][year]:.2f}")
            
            response_parts.append("")
        
        response_parts.append("Note: All numbers above are calculated directly from the database.")
        
        return "\n".join(response_parts)
    
    def compose_cagr_response(self, analysis: Dict, raw_data: Optional[str] = None, 
                             df=None, mode: str = None) -> str:
        """
        Compose a response for CAGR calculation with database values
        Includes forecast section if available and trend detection
        
        Args:
            analysis: Analysis results with CAGR data
            raw_data: Raw data summary (optional)
            df: DataFrame for trend detection (optional)
            mode: COMPACT or DETAILED (uses instance mode if not specified)
        
        Returns:
            Formatted CAGR response (plain text, no markdown)
        """
        mode = mode or self.mode
        response_parts = []
        
        if analysis.get('cagr') is not None:
            cagr = analysis['cagr']
            details = analysis.get('cagr_details', {})
            
            response_parts.append(self._format_section_header("CAGR ANALYSIS"))
            response_parts.append("(Direct from Database)\n")
            response_parts.append(f"CAGR: {cagr}%")
            
            if details and mode == "DETAILED":
                response_parts.append(f"\nPeriod: {details['start_year']} to {details['end_year']}")
                response_parts.append(f"Starting Sales: {details['start_sales']:.2f}")
                response_parts.append(f"Ending Sales: {details['end_sales']:.2f}")
            
            # Strip markdown from insight
            insight = self._strip_markdown(analysis['insight'])
            response_parts.append(f"\n\nInsight: {insight}")
            
            if analysis.get('recommendations') and mode == "DETAILED":
                response_parts.append("\n\nRecommendations:")
                for rec in analysis['recommendations']:
                    rec_clean = self._strip_markdown(rec)
                    response_parts.append(f"- {rec_clean}")
            
            # Add trend detection if DataFrame provided
            if df is not None and not df.empty:
                from business_analyst import analyst
                trend_summary = analyst.analyze_trends(df)
                if trend_summary and "Insufficient" not in trend_summary:
                    trend_clean = self._strip_markdown(trend_summary)
                    response_parts.append(f"\n\n{trend_clean}")
            
            # Add forecast section if available
            if analysis.get('has_forecast') and analysis.get('forecast'):
                forecast_result = {
                    'start_year': details.get('start_year'),
                    'end_year': details.get('end_year'),
                    'cagr': cagr,
                    'end_sales': details.get('end_sales'),
                    'forecast': analysis.get('forecast', {}),
                    'scenarios': analysis.get('scenarios', {})
                }
                response_parts.append(self.render_forecast_section(forecast_result, mode))
            else:
                response_parts.append("\n\nNote: All numbers above are calculated directly from the database.")
        else:
            response_parts.append(analysis.get('insight', 'CAGR calculation unavailable'))
        
        return "\n".join(response_parts)
    
    def compose_response(self, persona: str, query: str, analysis: Dict, 
                        raw_data: Optional[str] = None, context: Optional[str] = None, 
                        df=None, mode: str = None) -> str:
        """
        Compose a persona-specific response with automatic trend detection
        
        Args:
            persona: Persona to use ('analyst', 'strategist', 'writer')
            query: User's question
            analysis: Analysis results from business_analyst
            raw_data: Raw data summary (optional)
            context: Recent conversation context (optional)
            df: DataFrame for trend detection (optional)
            mode: COMPACT or DETAILED (uses instance mode if not specified)
        
        Returns:
            Formatted response string (plain text, no markdown)
        """
        mode = mode or self.mode
        persona_obj = self.personas.get(persona, ANALYST)
        
        # Get recent context if not provided
        if context is None:
            context = memory.recall_context(last_n=3)
        
        # Build prompt based on persona and mode
        prompt = self._build_prompt(persona_obj, query, analysis, raw_data, context, mode)
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {persona_obj.description}. {persona_obj.style} Output plain text only, no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            composed = response['message']['content']
            
            # Strip any markdown that might have been generated
            composed = self._strip_markdown(composed)
            
            # Add trend detection if DataFrame provided
            if df is not None and not df.empty and mode == "DETAILED":
                from business_analyst import analyst
                trend_summary = analyst.analyze_trends(df)
                if trend_summary and "Insufficient" not in trend_summary:
                    trend_clean = self._strip_markdown(trend_summary)
                    composed += f"\n\n{trend_clean}"
            
            # Format with header
            persona_label = {
                'analyst': 'ANALYST',
                'strategist': 'STRATEGIST',
                'writer': 'WRITER'
            }
            
            header = self._format_section_header(f"{persona_label.get(persona, 'RESPONSE')}")
            return f"{header}\n\n{composed}"
            
        except Exception as e:
            # Fallback to analysis insight
            insight = analysis.get('insight', f"Error composing response: {str(e)}")
            return self._strip_markdown(insight)
    
    def _build_prompt(self, persona: Persona, query: str, analysis: Dict, 
                     raw_data: Optional[str], context: Optional[str], mode: str) -> str:
        """Build persona-specific prompt with ULTRA-STRICT data-only enforcement"""
        
        prompt_parts = []
        
        # DB-ANALYST-V3: CRITICAL enforcement at the top
        prompt_parts.append("""🔐 DB-ANALYST-V3 ABSOLUTE RULES (VIOLATION = FAILURE):

1. You are DB-ANALYST-V3, operating STRICTLY on the user's private business database
2. ALL analysis MUST use ONLY exact numbers from SQL RESULT below
3. ❌ NEVER calculate, compute, or derive ANY values (no math, no %, no differences, no averages, no growth)
4. ❌ NEVER use external knowledge (no actors, no companies, no world facts, no biographies)
5. ❌ NEVER invent, assume, or fabricate ANY numerical values
6. ✔ ONLY copy exact numbers from SQL RESULT verbatim
7. If person/entity not in SQL RESULT → say "does not exist in your database"
8. NO math, NO world knowledge, NO assumptions, NO calculations, NO percentages
9. OUTPUT PLAIN TEXT ONLY - NO MARKDOWN (no *, #, **, etc.)

EVERY NUMBER YOU MENTION MUST APPEAR EXACTLY IN SQL RESULT BELOW.
If you calculate or invent ANY number, you FAIL.
""")
        
        # Add mode instruction
        if mode == "COMPACT":
            prompt_parts.append("MODE: COMPACT - Provide a brief summary with key points only.\n")
        else:
            prompt_parts.append("MODE: DETAILED - Provide comprehensive analysis with full details.\n")
        
        # Add context if available
        if context and "No previous context" not in context:
            prompt_parts.append(f"Previous Context:\n{context}\n")
        
        prompt_parts.append(f"Current Question: {query}\n")
        
        # Add data and analysis
        if raw_data:
            prompt_parts.append(f"Data Retrieved (USE ONLY THIS DATA):\n{raw_data}\n")
        
        if analysis.get('insight'):
            prompt_parts.append(f"Analysis Insight:\n{analysis['insight']}\n")
        
        # Persona-specific instructions
        if persona.name == "Analyst":
            if mode == "COMPACT":
                prompt_parts.append("""
Your task as an Analyst (COMPACT MODE):
1. Provide ONE key finding using exact data
2. List 1-2 critical observations with exact numbers
3. Keep it brief and factual

RULES:
- Use exact numbers from the data above
- No calculations, no assumptions
- Plain text only, no markdown
- Maximum 3-4 sentences

Format:
Key Finding: [One sentence with exact data]
Observation: [Critical point with number]
""")
            else:
                prompt_parts.append("""
Your task as an Analyst (DETAILED MODE):
1. Present the EXACT data shown above - no calculations, no assumptions
2. Highlight key observations using ONLY the numbers provided
3. Provide factual insights based STRICTLY on the data shown
4. Keep it professional and data-driven

RULES:
- Use exact numbers from the data above
- Do not perform calculations not shown in the data
- Do not assume or infer missing values
- Plain text only, no markdown formatting
- If asked about data not present, say "No data available for this query"

Format your response:
Key Finding: [Main takeaway using exact data]
Observations: [2-3 bullet points with exact numbers]
Data Summary: [Brief summary of what the data shows]
""")
        
        elif persona.name == "Strategist":
            if mode == "COMPACT":
                prompt_parts.append("""
Your task as a Strategist (COMPACT MODE):
1. One strategic insight from the data
2. One key recommendation
3. Brief and actionable

RULES:
- Base on exact data provided
- No fabricated numbers
- Plain text only
- Maximum 3-4 sentences

Format:
Strategic Insight: [One sentence]
Recommendation: [One action item]
""")
            else:
                prompt_parts.append("""
Your task as a Strategist (DETAILED MODE):
1. Interpret the business implications of the EXACT data shown
2. Identify trends and patterns FROM THIS DATA ONLY
3. Recommend strategic actions based on what the data actually shows
4. Do not forecast or predict beyond what the data supports

RULES:
- Base all insights on the exact data provided
- Do not fabricate numbers or trends
- Plain text only, no markdown
- If data is insufficient for strategic analysis, state that
- Quote exact numbers when making points

Format your response:
Strategic Insight: [High-level interpretation of actual data]
Trends and Implications: [What this data means for the business]
Recommendations: [2-3 actionable next steps based on data]
Data Limitations: [Note any gaps in the data if relevant]
""")
        
        elif persona.name == "Writer":
            if mode == "COMPACT":
                prompt_parts.append("""
Your task as a Writer (COMPACT MODE):
1. Brief, natural message with exact data
2. Professional and friendly
3. Short and clear

RULES:
- Use exact data only
- Plain text, no markdown
- Natural human tone
- Maximum 3-4 sentences
""")
            else:
                prompt_parts.append("""
Your task as a Writer (DETAILED MODE):
1. Write in a natural, human tone using the EXACT data provided
2. Be empathetic and professional
3. Structure the message appropriately
4. Use only the numbers and facts shown in the data

RULES:
- Do not invent or assume any numerical values
- Use exact data points from the information provided
- Plain text only, no markdown formatting
- If writing about metrics, quote them exactly as shown

If writing an email/message:
- Include appropriate greeting
- Clear, friendly body with exact data
- Professional closing
- Natural language throughout
""")
        
        return "\n".join(prompt_parts)
    
    def compose_email(self, recipient: str, purpose: str, data: Dict, mode: str = None) -> str:
        """
        Specialized method for composing emails
        
        Args:
            recipient: Name of recipient
            purpose: Purpose of email (thank you, update, etc.)
            data: Relevant data about recipient
            mode: COMPACT or DETAILED
        
        Returns:
            Formatted email (plain text)
        """
        import json
        mode = mode or self.mode
        
        prompt = f"""
Write a professional email to {recipient}.

Purpose: {purpose}

Relevant Information:
{json.dumps(data, indent=2)}

{"Write a brief, concise email." if mode == "COMPACT" else "Write a complete, detailed email."}

Requirements:
- Appropriate greeting
- Clear, friendly message body
- Professional closing
- Natural, human tone
- Plain text only, no markdown formatting
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business writer. Write clear, friendly, human emails in plain text (no markdown)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            email_content = self._strip_markdown(response['message']['content'])
            header = self._format_section_header("EMAIL DRAFT")
            return f"{header}\n\n{email_content}"
            
        except Exception as e:
            return f"Error composing email: {str(e)}"

# Global composer instance
composer = ResponseComposer()
