from src.config import GEMINI_KEY
import google.generativeai as genai
import os

import anthropic

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]


class GeminiModel:
    def __init__(self):
        genai.configure(api_key=GEMINI_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(
            max_output_tokens=4000,
            temperature=0.4, ))

    def get_response(self, input_prompt):
        response = self.model.generate_content(input_prompt, safety_settings=safety_settings)
        return {'response': response.text}

# class ClaudeModel:
#     def __init__(self):
#         self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_KEY'))
#
#     def get_response(self, input_prompt):
#         message = self.client.messages.create(
#             model="claude-3-haiku-20240307",
#             max_tokens=4096,
#             temperature=0.3,
#             system="You are an intelligent assistant who answers questions related to research papers on various topics.",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": input_prompt
#                         }
#                     ]
#                 }
#             ]
#         )
#         return {'response': message.content}
