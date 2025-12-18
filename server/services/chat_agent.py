import json
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from server.utils.llm_utils import get_llm

logger = logging.getLogger(__name__)

class BearCartChatAgent:
    """AI Assistant for BearCart Dashboard"""

    def __init__(self):
        self.llm = get_llm(temperature=0.3) # Low temp for factual data
        
    def ask(self, question: str, context_data: dict) -> dict:
        """
        Ask the AI a question about the dashboard data.
        
        Args:
            question: User's question
            context_data: Dictionary containing dashboard metrics
            
        Returns:
            JSON response with 'answer' and optional 'chart_data'
        """
        
        # Prepare context summary to reduce token usage if needed, 
        # but for now, the metrics JSON is small enough.
        context_str = json.dumps(context_data, indent=2)
        
        system_prompt = f"""
        You are BearCart AI, an expert e-commerce data analyst. 
        Your goal is to help the user understand their business performance based on the provided data.
        
        DATA CONTEXT:
        {context_str}
        
        INSTRUCTIONS:
        1. Answer the user's question using ONLY the provided data.
        2. If the data describes a specific metric (e.g., revenue, conversion), cite the exact numbers.
        3. Be concise, professional, and insightful.
        4. If the user asks for a visualization or if a chart would clearly help, provide a JSON description of the chart in a specific format.
        
        RESPONSE FORMAT:
        You must return a valid JSON object with the following structure:
        {{
            "answer": "Your text answer here in markdown format.",
            "chart": {{ (OPTIONAL, set to null if not needed)
                "type": "bar" | "line" | "pie",
                "title": "Chart Title",
                "labels": ["Label1", "Label2"],
                "data": [10, 20]
            }}
        }}
        
        Do not include markdown code blocks (```json) in your response, just the raw JSON string.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Clean potential markdown code blocks if the LLM ignores instructions
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {
                "answer": "I analyzed the data, but I had trouble formatting the output properly. Here is what I found: " + response.content,
                "chart": None
            }
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your request.",
                "chart": None
            }
