"""Abstract base class for TTS engines"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import numpy as np
import soundfile as sf
from io import BytesIO


class BaseTTSEngine(ABC):
    """Abstract base class for all TTS engines"""
    
    @abstractmethod
    def synthesize(self, text: str, **kwargs) -> bytes:
        """Generate speech audio from text
        
        Args:
            text: Input text to convert to speech
            **kwargs: Engine-specific parameters
        
        Returns:
            Audio bytes in WAV format
        """
        pass
    
    @abstractmethod
    def supports_voice_cloning(self) -> bool:
        """Check if engine supports voice cloning"""
        pass
    
    @abstractmethod
    def get_quality_metrics(self) -> Dict[str, float]:
        """Get quality metrics for this engine
        
        Returns:
            Dict with metrics:
            - naturalness: 0-1
            - clarity: 0-1
            - expressiveness: 0-1
            - voice_cloning: 0-1
        """
        pass
    
    def _audio_to_bytes(self, audio: np.ndarray, sample_rate: int = 24000) -> bytes:
        """Convert audio array to WAV bytes
        
        Args:
            audio: Audio waveform as numpy array
            sample_rate: Sample rate in Hz
        
        Returns:
            WAV format audio bytes
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Normalize if needed
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val
        
        # Write to bytes buffer
        buffer = BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        return buffer.getvalue()
    
    def _normalize_audio(self, audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """Normalize audio to target loudness
        
        Args:
            audio: Audio waveform
            target_db: Target loudness in dB
        
        Returns:
            Normalized audio
        """
        # Calculate RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            # Convert target dB to linear
            target_linear = 10 ** (target_db / 20.0)
            audio = audio * (target_linear / rms)
        
        return audio
