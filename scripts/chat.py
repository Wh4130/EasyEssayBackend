from scripts.pinecone_manager import PineconeManager
from litellm import completion
import re

class ChatBot():

    def __init__(self, 
                 model_key = "gpt-oss-120b", 
                 temperature = 0,
                 RAG = True):
        
        self.pc              = PineconeManager()
        self.model_key       = model_key
        self.RAG             = RAG
        self.temperature     = temperature

    def _clean_content(self, text):
        """清洗層：移除 HTML 與特殊字元"""
        if not text: return ""
        # 1. 移除 HTML 標籤
        text = re.sub(r'<[^>]+>', '', text)
        # 2. 移除 BOM 和特殊 Unicode 空格
        text = text.replace('\ufeff', '').replace('\u202f', ' ').replace('\u00a0', ' ')
        # 3. 只保留可列印字元 (移除奇怪的控制字元)
        text = "".join(ch for ch in text if ch.isprintable() or ch == '\n')
        return text.strip()

    def changeTemperature(self, new_temperature):
        self.temperature = new_temperature


    def checkRagAvailability(self, doc_id):
        all_docIDs = self.pc.list_namespaces("easyessay")
        if doc_id not in all_docIDs:
            return False 
        else:
            return True
        
    def changeModel(self, new_model_key):
        self.model_key = new_model_key

    def apiCall(self, in_messages, similar_text_ls = None, doc_summary = None, additional_prompt = None):
        
        # instruction = PromptManager.chat_rag(doc_summary, similar_text_ls)
        instruction = "Chat with me."

        # if additional_prompt:
        #     instruction += "\n\n" + additional_prompt

        instruction = self._clean_content(instruction)
        msgs = [
            {"role": "system", "content": instruction},
            *in_messages[-1:]
        ]


        # * Call API
        full_model_name = f"cerebras/{self.model_key}"
        response_stream = completion(
            model=full_model_name,
            messages=msgs,
            max_tokens=40000,
            stream = True,
            temperature=self.temperature,
            top_p=1
        )

        # # * Get Response
        for part in response_stream:

            content = part.choices[0].delta.content
            
            # * the last element in the stream may be None
            if content is not None:
                yield content