"""
ComfyUI-Pocket-TTS - Simple CPU-based TTS nodes
FIXED: Simple structure matching Qwen3-TTS exactly
"""

import torch
import torchaudio
import numpy as np
import os
import tempfile

print("\n" + "="*70)
print("🎙️ ComfyUI-Pocket-TTS - Loading...")
print("="*70)

# Import pocket_tts
try:
    from pocket_tts import TTSModel
    POCKET_TTS_AVAILABLE = True
    print("✅ Pocket TTS library imported successfully")
except ImportError as e:
    POCKET_TTS_AVAILABLE = False
    print(f"❌ [Pocket-TTS] Import Error: {e}")
    print("   Install with: pip install pocket-tts")
    TTSModel = None

# Global cache
_model_cache = None
_voice_cache = {}

# Built-in voices
VOICES = ["alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"]


class PocketTTSGenerate:
    """Generate speech with built-in voices (Simple)"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True
                }),
                "voice": (VOICES, {"default": "alba"}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate"
    CATEGORY = "audio/Pocket-TTS"

    def generate(self, text, voice):
        global _model_cache, _voice_cache

        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("❌ pocket-tts not installed. Run: pip install pocket-tts")

        # Load model once
        if _model_cache is None:
            print("🔄 Loading Pocket TTS model...")
            _model_cache = TTSModel.load_model()
            print("✅ Model loaded!")

        model = _model_cache

        # Get voice state
        cache_key = f"voice_{voice}"
        if cache_key not in _voice_cache:
            print(f"🎤 Loading voice: {voice}")
            voice_prompt = f"hf://kyutai/tts-voices/{voice}/casual.wav"
            _voice_cache[cache_key] = model.get_state_for_audio_prompt(voice_prompt)

        voice_state = _voice_cache[cache_key]

        # Generate
        print(f"🎙️ Generating: {len(text)} chars with voice '{voice}'")
        audio = model.generate_audio(voice_state, text)

        # Convert to ComfyUI format
        waveform = audio.unsqueeze(0).cpu()  # [1, samples]

        return ({"waveform": waveform, "sample_rate": model.sample_rate},)


class PocketTTSClone:
    """Clone voice from audio input"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),  # AUDIO INPUT - like Qwen3-TTS!
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate_clone"
    CATEGORY = "audio/Pocket-TTS"

    def generate_clone(self, audio, text):
        global _model_cache

        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("❌ pocket-tts not installed. Run: pip install pocket-tts")

        # Load model once
        if _model_cache is None:
            print("🔄 Loading Pocket TTS model...")
            _model_cache = TTSModel.load_model()
            print("✅ Model loaded!")

        model = _model_cache

        # Get audio from ComfyUI AUDIO type
        waveform = audio["waveform"].squeeze(0)  # [samples] or [channels, samples]
        sample_rate = audio["sample_rate"]

        # Handle stereo to mono
        if waveform.dim() == 2:
            waveform = waveform.mean(dim=0)

        # Save to temp file (Pocket TTS needs file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            torchaudio.save(tmp_path, waveform.unsqueeze(0), sample_rate)

        try:
            # Get voice state from audio
            print(f"🎤 Analyzing reference audio...")
            voice_state = model.get_state_for_audio_prompt(tmp_path)

            # Generate
            print(f"🎙️ Generating: {len(text)} chars with cloned voice")
            audio_out = model.generate_audio(voice_state, text)

            # Convert to ComfyUI format
            waveform_out = audio_out.unsqueeze(0).cpu()

            return ({"waveform": waveform_out, "sample_rate": model.sample_rate},)

        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Register nodes
NODE_CLASS_MAPPINGS = {
    "PocketTTSGenerate": PocketTTSGenerate,
    "PocketTTSClone": PocketTTSClone,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PocketTTSGenerate": "🎙️ Pocket TTS Generate",
    "PocketTTSClone": "🎙️ Pocket TTS Clone Voice",
}

print("="*70)
print("✅ Pocket TTS nodes registered (FIXED)")
print("="*70 + "\n")
