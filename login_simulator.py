import re

import os
import google.generativeai as genai

from auth_service import AuthService
from classical_agent import ClassicalAgent
from gen_ai_agent import GenAIAgent


class LoginSimulator:
    @staticmethod
    def start_genai_recovery_chat(user_message, username):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('models/gemma-3-12b-it')

        if username:
            account_status = AuthService.check_account_status(username)
        else:
            account_status = "unknown"

        if account_status == "active":
            recovery_prompt = f"""
            You are a friendly assistant. The user's account is active.
            Respond in under 25 words, politely informing the user that their account is not locked and no recovery is needed.
            User message: {user_message}
            """
        elif account_status == "locked":
            recovery_prompt = f"""
            You are a polite and concise account recovery assistant.

            Task:
            - Help the user recover their locked account in 2–3 short exchanges.
            - Use a friendly, professional tone.
            - Ask only one thing at a time.
            - Keep responses under 25 words.

            Steps:
            1. Greet and ask for registered email or phone.
            2. Ask for last transaction amount.
            3. Confirm and say the account is unlocked with a reset link.

            User message: {user_message}
            """
        else:
            recovery_prompt = f"""
            You are a helpful assistant. The username is not found or unclear.
            Politely ask the user to provide their registered email or phone number.
            User message: {user_message}
            """

        try:
            response = model.generate_content(recovery_prompt)
            return response.text
        except Exception as e:
            return f"Could not start GenAI recovery chat: {e}"

    @staticmethod
    def get_block_explanation(username, agent_type):
        if agent_type == "Classical Agent":
            return ClassicalAgent.get_classical_block_explanation(username)
        else:
            return GenAIAgent.get_genai_block_explanation(username)

    @staticmethod
    def genai_chat_response(message, chat_history, username):
        """
        Simplified 3-step recovery flow with dummy password reset link before unlocking account.
        """
        if not chat_history:
            chat_history = []

        account_status = AuthService.check_account_status(username)
        last_user_msg = message.strip().lower()

        # Track progress from previous assistant messages
        step1_done = any("step 1 complete" in m["content"].lower() for m in chat_history if m["role"] == "assistant")
        step2_done = any("step 2 complete" in m["content"].lower() for m in chat_history if m["role"] == "assistant")

        if account_status == "locked":
            if not step1_done:
                if re.search(r"@|[\d]{7,}", last_user_msg):  # basic email or phone match
                    if ClassicalAgent.validate_recovery_info(username, "contact", last_user_msg):
                        return (
                            "✅ Step 1 complete!\n"
                            " Step 2 of 3:\n"
                            "Please enter the amount of your last transaction."
                        )
                    else:
                        return (
                            "❌ That contact doesn't match our records.\n"
                            "Please try again with your correct email or phone number."
                        )
                else:
                    return (
                        " Step 1 of 3:\n"
                        "Please enter your registered email or phone number."
                    )

            if step1_done and not step2_done:
                if re.search(r"\d+[.,]?\d*", last_user_msg):
                    if ClassicalAgent.validate_recovery_info(username, "transaction", last_user_msg):
                        return (
                            "✅ Step 2 complete!\n"
                            " Step 3 of 3:\n"
                            "Please enter your new password (minimum 6 characters)."
                        )
                    else:
                        return (
                            "❌ That transaction amount couldn't be verified.\n"
                            "Please try again or contact support."
                        )
                else:
                    return (
                        " Step 2 of 3:\n"
                        "Please enter the amount of your last transaction."
                    )

            if step2_done:
                if len(last_user_msg) >= 6:
                    AuthService.update_password(username, last_user_msg)
                    AuthService.unlock_account(username)
                    return (
                        "✅ Your password has been successfully updated and your account is now unlocked!\n"
                        "You can now log in with your new password.\n"
                        "Let me know if you need any more help."
                    )
                else:
                    return (
                        "Step 3 of 3:\n"
                        "Please enter your new password (minimum 6 characters)."
                    )

            return "I'm here to help! Let's continue the recovery process."

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('models/gemma-3-12b-it')

        # Build conversation history into prompt
        chat_messages = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
        )

        prompt = f"""
        You are a helpful assistant. The user's account is active.
        Continue the conversation based on the chat history.
        Stay concise, friendly, and helpful.

        Conversation so far:
        {chat_messages}
        User: {message}
        Assistant:
        """

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error generating response: {e}"
