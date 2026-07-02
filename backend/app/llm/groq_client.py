import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import GROQ_API_KEY, GROQ_MODEL

class GroqClient:
    """Client for interacting with Groq LLM"""
    
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.client = None
        self.fallback_models = [
            "mixtral-8x7b-32768",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
            "llama3-70b-8192",
            "llama3-8b-8192"
        ]
        self.current_model = self.model
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self, model: Optional[str] = None):
        """Initialize the Groq client with a specific model"""
        model_to_use = model or self.model
        
        try:
            self.client = ChatGroq(
                api_key=self.api_key,
                model=model_to_use,
                temperature=0.1
            )
            self.current_model = model_to_use
            print(f"✅ Groq client initialized with model: {model_to_use}")
            return True
        except Exception as e:
            print(f"⚠️  Error initializing Groq with {model_to_use}: {e}")
            return False
    
    def generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from Groq with automatic fallback"""
        if not self.client:
            return "⚠️ Groq API key not configured. Please set GROQ_API_KEY in .env"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a model-related error
            if "model" in error_msg.lower() and "not" in error_msg.lower():
                # Try fallback models
                for fallback_model in self.fallback_models:
                    if fallback_model != self.current_model:
                        print(f"🔄 Trying fallback model: {fallback_model}")
                        if self._initialize_client(fallback_model):
                            # Retry with the new model
                            try:
                                messages = [
                                    SystemMessage(content=system_prompt),
                                    HumanMessage(content=user_message)
                                ]
                                response = self.client.invoke(messages)
                                return response.content
                            except Exception as retry_error:
                                continue
                
                return f"⚠️ No available models found. Please check your GROQ_API_KEY and available models at https://console.groq.com/docs/models"
            
            return f"Error generating response: {error_msg}"
    
    def is_available(self) -> bool:
        """Check if Groq is available"""
        return self.client is not None

# Singleton instance
groq_client = GroqClient()