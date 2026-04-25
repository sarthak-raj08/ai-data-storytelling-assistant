import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class InsightEngine:
    def __init__(self):
        # IMPORTANT: Load from environment variable, NOT hardcoded
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
    
    def generate_insights(self, data_context, stats, correlations, outliers, trends):
        """Generate AI-powered insights from data analysis"""
        
        prompt = f"""
        You are a senior data analyst. Based on the following data analysis, provide 5-7 key business insights.
        
        DATA CONTEXT: {data_context}
        
        STATISTICS: {stats}
        
        CORRELATIONS: {correlations}
        
        OUTLIERS: {outliers}
        
        TRENDS: {trends}
        
        For each insight:
        1. State the finding clearly
        2. Explain why it matters
        3. Suggest what action to take
        
        Format as bullet points with bold headers.
        Keep language business-friendly and actionable.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst who explains insights in clear, actionable business language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ AI Insight generation error: {str(e)}\n\nUsing fallback insights.\n\n**Key Observations:**\n• Review the charts above for data patterns\n• Check correlations for relationships between variables\n• Investigate any outliers detected"
    
    def generate_story(self, insights, dataset_name):
        """Convert insights into narrative story format"""
        
        prompt = f"""
        Convert these data insights into a compelling business story/narrative for {dataset_name}.
        
        INSIGHTS: {insights}
        
        Create a professional executive summary that:
        1. Opens with the overall data story
        2. Highlights 3-4 key moments/trends
        3. Identifies opportunities and risks
        4. Ends with a forward-looking conclusion
        
        Keep it under 400 words. Use natural, engaging language.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a business storyteller who transforms data into compelling narratives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=600
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ Story generation error: {str(e)}\n\n**Quick Summary:**\nThe data shows various patterns worth exploring further through the visualizations above."
    
    def generate_recommendations(self, insights, data_summary):
        """Generate business recommendations"""
        
        prompt = f"""
        Based on this data analysis, provide 5 actionable business recommendations.
        
        DATA SUMMARY: {data_summary}
        
        INSIGHTS: {insights}
        
        For each recommendation:
        - Specific action
        - Expected impact
        - Priority level (High/Medium/Low)
        
        Format as a numbered list.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a business consultant providing strategic recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ Recommendation generation error: {str(e)}\n\n**Suggested Actions:**\n1. Focus on high-performing metrics identified in charts\n2. Investigate any negative trends further\n3. Consider A/B testing for key variables"