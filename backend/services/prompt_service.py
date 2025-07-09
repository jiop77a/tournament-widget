from flask import abort
from services.openai_service import openai_service


class PromptService:
    """Service for handling prompt-related operations"""

    def remove_duplicate_prompts(self, prompts):
        """Remove duplicate prompts while preserving order"""
        unique_prompts = []
        seen = set()
        for prompt in prompts:
            normalized = prompt.lower().strip()
            if normalized not in seen and normalized:  # Also skip empty prompts
                unique_prompts.append(prompt)
                seen.add(normalized)
        return unique_prompts

    def generate_fallback_prompts(
        self, input_question, num_prompts_needed, existing_prompts=None
    ):
        """Generate simple fallback prompts if AI generation fails"""
        fallback_templates = [
            f"Please tell me: {input_question}",
            f"I would like to know: {input_question}",
            f"Could you explain: {input_question}",
            f"Help me understand: {input_question}",
            f"What is the answer to: {input_question}",
            f"Can you provide information about: {input_question}",
            f"I need to know: {input_question}",
            f"Please clarify: {input_question}",
            f"Can you help me with: {input_question}",
            f"I'm curious about: {input_question}",
            f"Could you describe: {input_question}",
            f"What can you tell me about: {input_question}",
        ]

        # Filter out any that are similar to existing prompts
        if existing_prompts:
            existing_normalized = {
                prompt.lower().strip() for prompt in existing_prompts
            }
            fallback_templates = [
                template
                for template in fallback_templates
                if template.lower().strip() not in existing_normalized
            ]

        # Return the needed number of fallback prompts
        return fallback_templates[:num_prompts_needed]

    def generate_prompts_with_ai(
        self, input_question, num_prompts_needed, existing_prompts=None
    ):
        """Generate additional prompts using ChatGPT API"""
        try:
            return openai_service.generate_prompts(
                input_question, num_prompts_needed, existing_prompts
            )
        except Exception as e:
            print(f"AI prompt generation failed: {e}")
            # Fall back to simple variations
            return self.generate_fallback_prompts(
                input_question, num_prompts_needed, existing_prompts
            )

    def test_prompt_with_openai(self, data):
        """Test a prompt with OpenAI and return formatted response"""
        # Validate required fields
        prompt_text = data.get("prompt")
        if not prompt_text or not prompt_text.strip():
            abort(400, description="Prompt is required and cannot be empty")

        # Optional parameters with defaults
        model = data.get("model", "gpt-3.5-turbo")
        max_tokens = data.get("max_tokens", 150)
        temperature = data.get("temperature", 0.7)

        try:
            return openai_service.test_prompt(
                prompt_text, model, max_tokens, temperature
            )
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            abort(500, description=f"Failed to test prompt: {str(e)}")


# Create a singleton instance for use across the application
prompt_service = PromptService()
