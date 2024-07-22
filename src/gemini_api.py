from src.config import GEMINI_KEY
import google.generativeai as genai


class GeminiModel:
    def __init__(self):
        genai.configure(api_key=GEMINI_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(
            max_output_tokens=4000,
            temperature=0.4, ))

    def get_response(self, input_prompt):
        response = self.model.generate_content(input_prompt)
        return {'response': response.text}
