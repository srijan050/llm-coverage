# local_llm_wrapper.py  
import requests  
from typing import List  
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  
  
class LocalLLMChat:  
    def __init__(self, model: str = "llama3.3", api_key: str = "", endpoint: str = ""):  
        self.model = model  
        self.api_key = api_key  
        self.endpoint = endpoint or "http://dvt-aiml.wv.mentorg.com:4000/v1/chat/completions"  
        self.headers = {  
            "Authorization": f"Bearer {self.api_key}",  
            "Content-Type": "application/json"  
        }  
  
    def invoke(self, messages):  
        chat_history = []  
          
        for msg in messages:  
            if isinstance(msg, HumanMessage):  
                chat_history.append({"role": "user", "content": msg.content})  
            elif isinstance(msg, AIMessage):  
                chat_history.append({"role": "assistant", "content": msg.content})  
            elif isinstance(msg, SystemMessage):  
                chat_history.append({"role": "system", "content": msg.content})  
            else:  
                # Fallback for other message types  
                chat_history.append({"role": "system", "content": str(msg.content)})  
  
        payload = {  
            "model": self.model,  
            "messages": chat_history,  
            "max_tokens": 600,  
            "temperature": 0.4,  # Increased from 0.1 to match working examples  
        }  
  
        try:  
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=30)  
            response.raise_for_status()  
            result = response.json()  
              
            choice = result.get("choices", [{}])[0]  
            message = choice.get("message", {})  
            content = message.get("content", "")  
              
            # Debug logging to see what your LLM is generating  
            print(f"LLM Response Content: '{content}'")  
              
            # Create AI message  
            ai_message = AIMessage(content=content or "")  
            return ai_message  
              
        except requests.exceptions.Timeout:  
            print("LLM request timed out")  
            return AIMessage(content="")  
        except requests.exceptions.RequestException as e:  
            print(f"LLM request error: {str(e)}")  
            return AIMessage(content="")  
        except Exception as e:  
            print(f"Unexpected LLM error: {str(e)}")  
            return AIMessage(content="")  
  
    def with_structured_output(self, schema):  
        """For compatibility with LangChain structured output."""  
        return self