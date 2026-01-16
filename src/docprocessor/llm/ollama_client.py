"""Ollama LLM client wrapper."""

from typing import Iterator, List, Optional

import ollama

from config.settings import settings
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Wrapper for Ollama LLM interactions."""

    def __init__(
        self,
        model: str = settings.ollama_model,
        base_url: str = settings.ollama_base_url,
        temperature: float = settings.temperature,
    ):
        """
        Initialize Ollama client.

        Args:
            model: Name of the Ollama model to use
            base_url: Ollama API base URL
            temperature: Generation temperature (0.0 to 2.0)
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

        logger.info(f"OllamaClient initialized with model: {model}, base_url: {base_url}")

        # Test connection
        try:
            self.check_model_availability()
        except Exception as e:
            logger.warning(f"Ollama connection test failed: {e}")
            logger.warning("Make sure Ollama is running: ollama serve")

    def check_model_availability(self) -> bool:
        """
        Check if the specified model is available.

        Returns:
            True if model is available, False otherwise

        Raises:
            Exception: If Ollama is not running or unreachable
        """
        try:
            response = ollama.list()
            # Handle different response formats
            if hasattr(response, "models"):
                models_list = response.models
            elif isinstance(response, dict) and "models" in response:
                models_list = response["models"]
            else:
                models_list = response if isinstance(response, list) else []

            # Extract model names
            available_models = []
            for m in models_list:
                if hasattr(m, "model"):
                    available_models.append(m.model)
                elif isinstance(m, dict) and "name" in m:
                    available_models.append(m["name"])
                elif isinstance(m, dict) and "model" in m:
                    available_models.append(m["model"])

            if self.model in available_models or any(self.model in m for m in available_models):
                logger.info(f"Model {self.model} is available")
                return True
            else:
                logger.warning(
                    f"Model {self.model} not found. Available models: {available_models}"
                )
                logger.warning(f"Pull model with: ollama pull {self.model}")
                return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            raise

    def list_models(self) -> List[str]:
        """
        List available Ollama models.

        Returns:
            List of model names
        """
        try:
            response = ollama.list()
            # Handle different response formats
            if hasattr(response, "models"):
                models_list = response.models
            elif isinstance(response, dict) and "models" in response:
                models_list = response["models"]
            else:
                models_list = response if isinstance(response, list) else []

            # Extract model names
            available_models = []
            for m in models_list:
                if hasattr(m, "model"):
                    available_models.append(m.model)
                elif isinstance(m, dict) and "name" in m:
                    available_models.append(m["name"])
                elif isinstance(m, dict) and "model" in m:
                    available_models.append(m["model"])

            return available_models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate text completion using Ollama.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text

        Raises:
            Exception: If generation fails
        """
        temp = temperature if temperature is not None else self.temperature

        logger.debug(f"Generating with model {self.model}, temperature={temp}")

        try:
            if stream:
                return self._generate_stream(prompt, system_prompt, temp, max_tokens)
            else:
                response = ollama.generate(
                    model=self.model,
                    prompt=prompt,
                    system=system_prompt,
                    options={
                        "temperature": temp,
                        "num_predict": max_tokens if max_tokens else -1,
                    },
                )
                generated_text = response["response"]
                logger.debug(f"Generated {len(generated_text)} characters")
                return generated_text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def _generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """
        Generate text with streaming (collects full response).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens

        Returns:
            Complete generated text
        """
        full_response = ""
        stream = ollama.generate(
            model=self.model,
            prompt=prompt,
            system=system_prompt,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens if max_tokens else -1,
            },
        )

        for chunk in stream:
            if "response" in chunk:
                full_response += chunk["response"]

        return full_response

    def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """
        Generate text with streaming iterator (yields chunks).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are generated
        """
        temp = temperature if temperature is not None else self.temperature

        logger.debug(f"Streaming generation with model {self.model}")

        try:
            stream = ollama.generate(
                model=self.model,
                prompt=prompt,
                system=system_prompt,
                stream=True,
                options={
                    "temperature": temp,
                    "num_predict": max_tokens if max_tokens else -1,
                },
            )

            for chunk in stream:
                if "response" in chunk:
                    yield chunk["response"]
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise

    def chat(
        self,
        messages: List[dict],
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        """
        Chat completion using Ollama chat endpoint.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            stream: Whether to stream the response

        Returns:
            Generated response

        Raises:
            Exception: If chat fails
        """
        temp = temperature if temperature is not None else self.temperature

        logger.debug(f"Chat with {len(messages)} messages")

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=stream,
                options={"temperature": temp},
            )

            if stream:
                full_response = ""
                for chunk in response:
                    if "message" in chunk and "content" in chunk["message"]:
                        full_response += chunk["message"]["content"]
                return full_response
            else:
                return response["message"]["content"]
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        return len(text) // 4
