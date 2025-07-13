import os
import google.generativeai as genai
from auth_service import AuthService


class GenAIAgent:

    @staticmethod
    def get_genai_block_explanation(username):
        account_status = AuthService.check_account_status(username)

        if account_status == "not_found":
            return "This username does not exist."

        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('models/gemma-3-12b-it')

            if account_status == "locked":
                prompt = (
                    f"Explain very concisely why the account '{username}' was locked "
                    f"due to multiple failed login attempts. Provide the explanation in both English and Nepali. "
                    f"Keep it clear and reassuring."
                )
            else:
                prompt = (
                    f"Explain very concisely that the account '{username}' is currently active and not locked. "
                    f"Provide this information in both English and Nepali. "
                    f"Keep it clear and reassuring."
                )

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1
                )
            )
            explanation = response.text
            return explanation
        except Exception as e:
            return f"Could not get explanation from LLM: {e}"
