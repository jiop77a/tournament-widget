import os

from openai import OpenAI


class OpenAIService:
    """Service for handling OpenAI API interactions"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def is_available(self):
        """Check if OpenAI service is available (API key is configured)"""
        return self.api_key is not None and self.client is not None

    def test_prompt(
        self, prompt_text, model="gpt-3.5-turbo", max_tokens=150, temperature=0.7
    ):
        """
        Test a prompt with OpenAI and return the response

        Args:
            prompt_text (str): The prompt to test
            model (str): The OpenAI model to use
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation

        Returns:
            dict: Response data including AI response and usage statistics

        Raises:
            Exception: If OpenAI API call fails or service is not available
        """
        # Check if OpenAI service is available
        if not self.is_available():
            raise Exception(
                "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable to use this feature."
            )

        # Validate parameters
        if not prompt_text or not prompt_text.strip():
            raise ValueError("Prompt is required and cannot be empty")

        if not isinstance(max_tokens, int) or max_tokens <= 0 or max_tokens > 4000:
            raise ValueError("max_tokens must be an integer between 1 and 4000")

        if (
            not isinstance(temperature, (int, float))
            or temperature < 0
            or temperature > 2
        ):
            raise ValueError("temperature must be a number between 0 and 2")

        if model not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
            raise ValueError("model must be one of: gpt-3.5-turbo, gpt-4, gpt-4-turbo")

        try:
            # Send prompt to OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt_text,
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract the response
            ai_response = response.choices[0].message.content.strip()

            return {
                "prompt": prompt_text,
                "response": ai_response,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            print(f"Error testing prompt with OpenAI: {e}")
            raise Exception(f"Failed to test prompt: {str(e)}")

    def generate_prompts(
        self, input_question, num_prompts_needed, existing_prompts=None
    ):
        """
        Generate additional prompts using ChatGPT API

        Args:
            input_question (str): The base question to generate variations for
            num_prompts_needed (int): Number of prompts to generate
            existing_prompts (list): List of existing prompts to avoid duplicating

        Returns:
            list: List of generated prompt strings

        Raises:
            Exception: If OpenAI API call fails or service is not available
        """
        # Check if OpenAI service is available
        if not self.is_available():
            raise Exception(
                "OpenAI API key not configured. Cannot generate AI prompts."
            )

        try:
            prompt_content = self._build_ai_prompt_content(
                input_question, num_prompts_needed, existing_prompts
            )

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates diverse prompt variations for AI testing. Generate prompts that ask the same question in different ways, with varying styles, formality levels, and approaches.",
                    },
                    {
                        "role": "user",
                        "content": prompt_content,
                    },
                ],
                max_tokens=500,
                temperature=0.8,
            )

            # Parse the response to extract individual prompts
            generated_text = response.choices[0].message.content.strip()
            prompts = [
                prompt.strip()
                for prompt in generated_text.split("\n")
                if prompt.strip()
            ]

            # Return only the number of prompts we need
            return prompts[:num_prompts_needed]

        except Exception as e:
            print(f"Error generating prompts with AI: {e}")
            raise e

    def _build_ai_prompt_content(
        self, input_question, num_prompts_needed, existing_prompts
    ):
        """Build the content for the AI prompt, including existing prompts to avoid"""
        base_content = f"Generate {num_prompts_needed} different ways to ask this question: '{input_question}'. Each prompt should be unique and ask for the same information but with different phrasing, tone, or approach."

        if existing_prompts:
            existing_list = "\n".join(f"- {prompt}" for prompt in existing_prompts)
            base_content += f"\n\nAVOID creating prompts similar to these existing ones:\n{existing_list}"

        base_content += "\n\nReturn only the prompts, one per line, without numbering or bullet points."
        return base_content


# Create a singleton instance for use across the application
openai_service = OpenAIService()
