from google import genai


class GeminiClient:
    """
    Handles communication with the Gemini API.
    """

    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-3.8-flash"

    def ask(self, prompt):
        """
        Send a question to Gemini and return the response.
        """

        if not prompt or not prompt.strip():
            return "Please enter a question."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt.strip()
            )

            return response.text

        except Exception as error:
            return f"Gemini error: {error}"