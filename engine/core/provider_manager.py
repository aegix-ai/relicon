# type: ignore

"""
Central provider manager for AI service abstraction.
Enables seamless switching between providers via configuration.
"""

import os
from typing import Optional, Any
from config.settings import settings


class ProviderManager:
    """Central manager for AI service providers."""

    def __init__(self):
        self._video_provider: Optional[Any] = None
        self._audio_provider: Optional[Any] = None
        self._text_provider: Optional[Any] = None

    def get_video_generator(self) -> Any:
        """Get the configured video generation provider."""
        if self._video_provider is None:
            provider_name = getattr(settings, 'VIDEO_PROVIDER', 'luma').lower()
            self._video_provider = self._create_video_provider(provider_name)
        return self._video_provider

    def get_audio_generator(self) -> Any:
        """Get the configured audio generation provider."""
        if self._audio_provider is None:
            provider_name = getattr(settings, 'AUDIO_PROVIDER', 'elevenlabs').lower()
            self._audio_provider = self._create_audio_provider(provider_name)
        return self._audio_provider

    def get_text_generator(self) -> Any:
        """Get the configured text generation provider."""
        if self._text_provider is None:
            provider_name = getattr(settings, 'TEXT_PROVIDER', 'openai').lower()
            self._text_provider = self._create_text_provider(provider_name)
        return self._text_provider

    def _create_video_provider(self,
                               provider_name: str) -> Any:
        """Create video provider instance based on configuration."""
        # Check for mock mode
        mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        if mock_mode:
            from providers.mock_video import MockVideoProvider
            print("🎭 Using MOCK video provider (no API calls)")
            return MockVideoProvider()

        if provider_name == 'luma':
            from providers.luma import LumaProvider
            return LumaProvider()
        else:
            raise ValueError(f"Unknown video provider: {provider_name}")

    def _create_audio_provider(self,
                               provider_name: str) -> Any:
        """Create audio provider instance based on configuration."""
        # Check for mock mode
        mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        if mock_mode:
            from providers.mock_audio import MockAudioProvider
            print("🎭 Using MOCK audio provider (no API calls)")
            return MockAudioProvider()

        if provider_name == 'elevenlabs':
            from providers.elevenlabs import ElevenLabsProvider
            return ElevenLabsProvider()
        else:
            raise ValueError(f"Unknown audio provider: {provider_name}")

    def _create_text_provider(self,
                              provider_name: str) -> Any:
        """Create text provider instance based on configuration."""
        # Check for mock mode
        mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        if mock_mode:
            from providers.mock_text import MockTextProvider
            print("🎭 Using MOCK text provider (no API calls)")
            return MockTextProvider()

        if provider_name == 'openai':
            from providers.openai import OpenAIProvider
            return OpenAIProvider()
        else:
            raise ValueError(f"Unknown text provider: {provider_name}")

    def set_video_provider(self,
                           provider_name: str) -> None:
        """Change video provider at runtime."""
        self._video_provider = self._create_video_provider(provider_name)

    def set_audio_provider(self,
                           provider_name: str) -> None:
        """Change audio provider at runtime."""
        self._audio_provider = self._create_audio_provider(provider_name)

    def set_text_provider(self,
                          provider_name: str) -> None:
        """Change text provider at runtime."""
        self._text_provider = self._create_text_provider(provider_name)


# Global provider manager instance
provider_manager = ProviderManager()
