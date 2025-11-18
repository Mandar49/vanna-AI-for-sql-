"""
DB-INTELLIGENCE-V1: Hybrid Reasoning Engine
Combines SQL accuracy with business intelligence frameworks
"""

class HybridReasoner:
    """
    Advanced reasoning layer that interprets SQL results and provides strategic insights
    using business frameworks like RFM, cohort analysis, margin/volume matrices, etc.
    """
    
    def __init__(self):
        self.frameworks = {
            'rfm': self._rfm_analysis,
            'cohort': self._cohort_logic,
            'margin_volume': self._margin_volume_matrix,
            'growth_stability': self._growth_stability_matrix,
            'retention': self._retention_guidance,
            'swot': self._swot_analysis
        }
    
    def interpret_result(self, sql_result, query_context, question):
        """
        Main interpretation engine that adds business intelligence to SQL results
        
        Args:
            sql_result: Raw SQL output (can be empty, partial, or complete)
            query_context: Metadata about the query
            question: Original user question
            
        Returns:
            dict with insight, recommendation, and reasoning
        """
        # Check if result is empty (handle DataFrame properly)
        if self._is_empty_result(sql_result):
            return self._handle_empty_result(question, query_context)
        
        # Analyze the result and apply appropriate framework
        insight = self._generate_insight(sql_result, query_context, question)
        recommendation = self._generate_recommendation(sql_result, query_context, question)
        
        return {
            'insight': insight,
            'recommendation': recommendation,
            'framework_used': self._detect_framework(question)
        }
    
    def _is_empty_result(self, result):
        """Check if SQL result is empty or null"""
        if result is None:
            return True
        # Handle pandas DataFrame
        if hasattr(result, 'empty'):
            return result.empty
        if isinstance(result, list) and len(result) == 0:
            return True
        if isinstance(result, dict) and not result:
            return True
        return False
    
    def _handle_empty_result(self, question, context):
        """Provide intelligent fallback when SQL returns no data"""
        insight = self._reason_about_empty_data(question, context)
        recommendation = self._suggest_next_action(question, context)
        
        return {
            'insight': insight,
            'recommendation': recommendation,
            'framework_used': 'fallback_reasoning'
        }
    
    def _reason_about_empty_data(self, question, context):
        """Interpret what empty data means in business context"""
        if 'customer' in question.lower() and 'repeat' in question.lower():
            return "No repeat customers found indicates a retention challenge. This suggests customers are not returning after initial purchase, which is critical for long-term profitability."
        elif 'revenue' in question.lower() or 'sales' in question.lower():
            return "No revenue data in the specified period suggests either no transactions occurred, data collection gaps, or filtering criteria that's too restrictive."
        elif 'growth' in question.lower() or 'trend' in question.lower():
            return "Insufficient data points to establish a trend. This could indicate a new product/market or data collection issues."
        else:
            return "No matching data found. This could indicate: (1) filters are too restrictive, (2) data hasn't been collected yet, or (3) the scenario hasn't occurred in your business."
    
    def _suggest_next_action(self, question, context):
        """Provide strategic recommendations based on empty results"""
        if 'customer' in question.lower():
            return "STRATEGIC RECOMMENDATION: Implement customer retention programs (loyalty rewards, email campaigns, subscription models). Track customer lifecycle metrics and set up automated re-engagement workflows."
        elif 'revenue' in question.lower():
            return "STRATEGIC RECOMMENDATION: Review data collection processes. If data is accurate, analyze market conditions, pricing strategy, and sales funnel effectiveness. Consider expanding target segments."
        elif 'product' in question.lower():
            return "STRATEGIC RECOMMENDATION: Conduct market research to understand product-market fit. Review inventory, pricing, and promotional strategies. Consider A/B testing different approaches."
        else:
            return "STRATEGIC RECOMMENDATION: Broaden search criteria, verify data collection processes, or consider that this scenario may represent an opportunity gap in your business model."
    
    def _generate_insight(self, result, context, question):
        """Generate business insight from SQL result"""
        framework = self._detect_framework(question)
        
        if framework in self.frameworks:
            return self.frameworks[framework](result, question)
        
        # Default insight generation
        return self._default_insight(result, question)
    
    def _generate_recommendation(self, result, context, question):
        """Generate strategic recommendation"""
        if 'customer' in question.lower() and 'value' in question.lower():
            return "Focus on high-value customer segments. Implement personalized marketing, premium service tiers, and account management for top customers."
        elif 'revenue' in question.lower() and ('decline' in question.lower() or 'decrease' in question.lower()):
            return "Address revenue decline through: (1) customer win-back campaigns, (2) pricing optimization, (3) new product launches, (4) market expansion."
        elif 'growth' in question.lower():
            return "Sustain growth momentum by: (1) scaling successful channels, (2) optimizing conversion funnels, (3) expanding to adjacent markets, (4) improving customer lifetime value."
        else:
            return "Continue monitoring these metrics. Set up automated alerts for significant changes and establish regular review cadences with stakeholders."
    
    def _detect_framework(self, question):
        """Detect which business framework to apply"""
        q_lower = question.lower()
        
        if any(word in q_lower for word in ['customer value', 'rfm', 'segment']):
            return 'rfm'
        elif any(word in q_lower for word in ['cohort', 'retention', 'churn']):
            return 'cohort'
        elif any(word in q_lower for word in ['margin', 'profit', 'volume']):
            return 'margin_volume'
        elif any(word in q_lower for word in ['growth', 'stability', 'risk']):
            return 'growth_stability'
        elif 'swot' in q_lower or 'strength' in q_lower or 'weakness' in q_lower:
            return 'swot'
        
        return 'default'
    
    def _rfm_analysis(self, result, question):
        """RFM (Recency, Frequency, Monetary) framework"""
        return "RFM ANALYSIS: Segment customers by Recency (last purchase), Frequency (purchase count), and Monetary value (total spend). High-value customers (high F+M, low R) need retention focus. Low-value customers (low F+M) may need re-engagement or pruning."
    
    def _cohort_logic(self, result, question):
        """Cohort analysis framework"""
        return "COHORT INSIGHT: Track customer groups by acquisition period to identify retention patterns. Strong cohorts show sustained engagement over time. Weak cohorts indicate onboarding or product-market fit issues."
    
    def _margin_volume_matrix(self, result, question):
        """Margin vs Volume strategic matrix"""
        return "MARGIN-VOLUME MATRIX: High-margin, high-volume products are stars (invest heavily). High-margin, low-volume are niche opportunities (test scaling). Low-margin, high-volume need efficiency improvements. Low-margin, low-volume should be discontinued."
    
    def _growth_stability_matrix(self, result, question):
        """Growth vs Stability framework"""
        return "GROWTH-STABILITY ANALYSIS: Balance aggressive growth initiatives with stable revenue streams. High-growth segments require investment but carry risk. Stable segments provide predictable cash flow for funding innovation."
    
    def _retention_guidance(self, result, question):
        """Customer retention strategy"""
        return "RETENTION STRATEGY: Acquiring new customers costs 5-25x more than retaining existing ones. Focus on: (1) reducing early churn, (2) increasing purchase frequency, (3) expanding wallet share, (4) building switching costs."
    
    def _swot_analysis(self, result, question):
        """SWOT framework"""
        return "SWOT PERSPECTIVE: Analyze Strengths (what's working), Weaknesses (gaps/issues), Opportunities (market potential), and Threats (competitive/external risks). Use this to prioritize strategic initiatives."
    
    def _default_insight(self, result, question):
        """Default insight when no specific framework applies"""
        return "BUSINESS INSIGHT: The data shows measurable results that require strategic interpretation. Consider trends, outliers, and business context when making decisions based on these numbers."
    
    def should_use_sql(self, question):
        """
        Determine if question requires SQL execution
        
        Returns:
            bool: True if SQL needed, False if general knowledge sufficient
        """
        sql_indicators = [
            'how many', 'total', 'sum', 'count', 'average', 'revenue', 'sales',
            'customer', 'order', 'product', 'top', 'bottom', 'highest', 'lowest',
            'trend', 'growth', 'decline', 'compare', 'last month', 'last year',
            'show me', 'list', 'find', 'get', 'calculate', 'what is the'
        ]
        
        q_lower = question.lower()
        return any(indicator in q_lower for indicator in sql_indicators)
    
    def answer_general_question(self, question):
        """
        Answer general business/knowledge questions without SQL
        """
        q_lower = question.lower()
        
        # Business concept questions
        if 'what is' in q_lower or 'define' in q_lower:
            return self._define_concept(question)
        
        # How-to questions
        if 'how to' in q_lower or 'how do i' in q_lower:
            return self._provide_guidance(question)
        
        # Best practice questions
        if 'best practice' in q_lower or 'should i' in q_lower:
            return self._best_practice_advice(question)
        
        return "I can help you with that. Could you provide more context about what specific aspect you'd like to explore?"
    
    def _define_concept(self, question):
        """Define business concepts"""
        q_lower = question.lower()
        
        if 'churn' in q_lower:
            return "Customer churn is the rate at which customers stop doing business with you. It's calculated as (customers lost / total customers) over a period. High churn indicates retention problems and directly impacts profitability."
        elif 'ltv' in q_lower or 'lifetime value' in q_lower:
            return "Customer Lifetime Value (LTV) is the total revenue a customer generates over their entire relationship with your business. Calculate as: (Average Purchase Value × Purchase Frequency × Customer Lifespan). Use LTV to determine customer acquisition cost limits."
        elif 'cac' in q_lower or 'acquisition cost' in q_lower:
            return "Customer Acquisition Cost (CAC) is the total cost of acquiring a new customer, including marketing, sales, and onboarding expenses. Healthy businesses maintain LTV:CAC ratio of 3:1 or higher."
        
        return "That's an important business concept. Let me know if you'd like specific metrics or analysis related to it."
    
    def _provide_guidance(self, question):
        """Provide how-to guidance"""
        return "I can guide you through that process. For data-driven decisions, I'll analyze your actual business data. For strategic questions, I'll provide frameworks and best practices."
    
    def _best_practice_advice(self, question):
        """Provide best practice recommendations"""
        return "Best practices depend on your specific business context. I can analyze your data to provide tailored recommendations, or discuss general strategic frameworks if you prefer."
