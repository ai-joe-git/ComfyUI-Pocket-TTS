"""
ComfyUI-Pocket-TTS - Lightweight CPU-based Text-to-Speech nodes
Fast, efficient TTS running on CPU without GPU requirements
"""

import torch
import numpy as np
import folder_paths
import os
from pathlib import Path

print("\n" + "="*70)
print("🎙️ ComfyUI-Pocket-TTS - Loading...")
print("="*70)

# Try to import pocket_tts
try:
    from pocket_tts import TTSModel
    POCKET_TTS_AVAILABLE = True
    print("✅ Pocket TTS library imported successfully")
except ImportError as e:
    POCKET_TTS_AVAILABLE = False
    print(f"❌ [Pocket-TTS] Critical Import Error: {e}")
    print("   Please install: pip install pocket-tts")
    TTSModel = None

# Global model cache
_model_cache = {}
_voice_cache = {}

# Built-in voices from Pocket TTS
BUILTIN_VOICES = [
    "alba",      # Alba Mackenna
    "marius",    # Marius Pontmercy
    "javert",    # Inspector Javert
    "jean",      # Jean Valjean
    "fantine",   # Fantine
    "cosette",   # Cosette
    "eponine",   # Eponine
    "azelma",    # Azelma
]

def get_audio_folder():
    """Get the audio input folder path"""
    return folder_paths.get_input_directory()


class PocketTTSModelLoader:
    """Load Pocket TTS model into memory"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "precision": (["float32", "float16", "bfloat16"], {
                    "default": "float32",
                    "tooltip": "Model precision (float32 recommended for CPU)"
                }),
            },
        }

    RETURN_TYPES = ("POCKET_TTS_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "audio/Pocket-TTS"
    DESCRIPTION = "Load Pocket TTS model (100M params, optimized for CPU)"

    def load_model(self, precision):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError(
                "❌ Pocket TTS library not available. "
                "Install with: pip install pocket-tts"
            )

        cache_key = f"model_{precision}"

        if cache_key in _model_cache:
            print(f"✅ Using cached Pocket TTS model ({precision})")
            return (_model_cache[cache_key],)

        print(f"\n🔄 Loading Pocket TTS model ({precision})...")

        # Load model
        model = TTSModel.load_model()

        # Set precision
        if precision == "float16":
            model = model.half()
        elif precision == "bfloat16":
            model = model.to(torch.bfloat16)

        _model_cache[cache_key] = model

        print(f"✅ Pocket TTS model loaded successfully!")
        print(f"   Parameters: ~100M")
        print(f"   Precision: {precision}")
        print(f"   Device: CPU (optimized)")

        return (model,)


class PocketTTSGenerate:
    """Generate speech from text using built-in voices"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("POCKET_TTS_MODEL", {
                    "tooltip": "Pocket TTS model from loader"
                }),
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True,
                    "tooltip": "Text to convert to speech"
                }),
                "voice": (BUILTIN_VOICES, {
                    "default": "alba",
                    "tooltip": "Built-in voice preset"
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "audio/Pocket-TTS"
    DESCRIPTION = "Generate speech using built-in voices (fast, ~200ms latency)"

    def generate(self, model, text, voice):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("❌ Pocket TTS library not available")

        print(f"\n🎙️ Generating speech with voice: {voice}")
        print(f"   Text length: {len(text)} characters")

        # Get or create voice state
        cache_key = f"voice_{voice}"
        if cache_key not in _voice_cache:
            print(f"   Loading voice preset: {voice}")
            voice_prompt = f"hf://kyutai/tts-voices/{voice}/casual.wav"
            voice_state = model.get_state_for_audio_prompt(voice_prompt)
            _voice_cache[cache_key] = voice_state
        else:
            voice_state = _voice_cache[cache_key]

        # Generate audio
        import time
        start_time = time.time()

        audio = model.generate_audio(voice_state, text)

        generation_time = time.time() - start_time
        audio_duration = len(audio) / model.sample_rate
        rtf = generation_time / audio_duration if audio_duration > 0 else 0

        print(f"✅ Audio generated!")
        print(f"   Duration: {audio_duration:.2f}s")
        print(f"   Generation time: {generation_time:.2f}s")
        print(f"   Real-time factor: {rtf:.2f}x")
        print(f"   Sample rate: {model.sample_rate}Hz")

        # Convert to ComfyUI audio format
        # ComfyUI expects: {"waveform": tensor, "sample_rate": int}
        audio_tensor = audio.unsqueeze(0).unsqueeze(0)  # [batch, channels, samples]

        audio_output = {
            "waveform": audio_tensor,
            "sample_rate": model.sample_rate
        }

        return (audio_output,)


class PocketTTSVoiceClone:
    """Generate speech with voice cloning from audio file"""

    @classmethod
    def INPUT_TYPES(cls):
        # Get audio files from input directory
        audio_files = []
        audio_dir = get_audio_folder()
        if os.path.exists(audio_dir):
            for file in os.listdir(audio_dir):
                if file.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
                    audio_files.append(file)

        if not audio_files:
            audio_files = ["No audio files found"]

        return {
            "required": {
                "model": ("POCKET_TTS_MODEL", {
                    "tooltip": "Pocket TTS model from loader"
                }),
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True,
                    "tooltip": "Text to convert to speech"
                }),
                "reference_audio": (audio_files, {
                    "tooltip": "Reference audio for voice cloning"
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_with_clone"
    CATEGORY = "audio/Pocket-TTS"
    DESCRIPTION = "Clone voice from audio file and generate speech"

    def generate_with_clone(self, model, text, reference_audio):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("❌ Pocket TTS library not available")

        if reference_audio == "No audio files found":
            raise ValueError("❌ No audio files in input directory")

        audio_path = os.path.join(get_audio_folder(), reference_audio)

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"❌ Audio file not found: {audio_path}")

        print(f"\n🎙️ Generating speech with voice cloning")
        print(f"   Reference: {reference_audio}")
        print(f"   Text length: {len(text)} characters")

        # Get or create voice state from audio file
        cache_key = f"clone_{reference_audio}"
        if cache_key not in _voice_cache:
            print(f"   Analyzing reference audio...")
            voice_state = model.get_state_for_audio_prompt(audio_path)
            _voice_cache[cache_key] = voice_state
        else:
            print(f"   Using cached voice state")
            voice_state = _voice_cache[cache_key]

        # Generate audio
        import time
        start_time = time.time()

        audio = model.generate_audio(voice_state, text)

        generation_time = time.time() - start_time
        audio_duration = len(audio) / model.sample_rate
        rtf = generation_time / audio_duration if audio_duration > 0 else 0

        print(f"✅ Audio generated with cloned voice!")
        print(f"   Duration: {audio_duration:.2f}s")
        print(f"   Generation time: {generation_time:.2f}s")
        print(f"   Real-time factor: {rtf:.2f}x")

        # Convert to ComfyUI audio format
        audio_tensor = audio.unsqueeze(0).unsqueeze(0)  # [batch, channels, samples]

        audio_output = {
            "waveform": audio_tensor,
            "sample_rate": model.sample_rate
        }

        return (audio_output,)


class PocketTTSSimple:
    """All-in-one node: Load model and generate speech in one step"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True,
                    "tooltip": "Text to convert to speech"
                }),
                "voice": (BUILTIN_VOICES, {
                    "default": "alba",
                    "tooltip": "Built-in voice preset"
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_simple"
    CATEGORY = "audio/Pocket-TTS"
    DESCRIPTION = "Simple TTS: Just text and voice, everything else is automatic"

    def generate_simple(self, text, voice):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("❌ Pocket TTS library not available")

        # Load model if not cached
        if "model_simple" not in _model_cache:
            print("\n🔄 Loading Pocket TTS model...")
            _model_cache["model_simple"] = TTSModel.load_model()
            print("✅ Model loaded!")

        model = _model_cache["model_simple"]

        # Get or create voice state
        cache_key = f"voice_{voice}"
        if cache_key not in _voice_cache:
            voice_prompt = f"hf://kyutai/tts-voices/{voice}/casual.wav"
            voice_state = model.get_state_for_audio_prompt(voice_prompt)
            _voice_cache[cache_key] = voice_state
        else:
            voice_state = _voice_cache[cache_key]

        # Generate audio
        audio = model.generate_audio(voice_state, text)

        # Convert to ComfyUI audio format
        audio_tensor = audio.unsqueeze(0).unsqueeze(0)

        audio_output = {
            "waveform": audio_tensor,
            "sample_rate": model.sample_rate
        }

        return (audio_output,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "PocketTTSModelLoader": PocketTTSModelLoader,
    "PocketTTSGenerate": PocketTTSGenerate,
    "PocketTTSVoiceClone": PocketTTSVoiceClone,
    "PocketTTSSimple": PocketTTSSimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PocketTTSModelLoader": "🎙️ Pocket TTS Model Loader",
    "PocketTTSGenerate": "🎙️ Pocket TTS Generate",
    "PocketTTSVoiceClone": "🎙️ Pocket TTS Voice Clone",
    "PocketTTSSimple": "🎙️ Pocket TTS (Simple)",
}

print("="*70)
print("✅ ComfyUI-Pocket-TTS nodes registered")
print("="*70 + "\n")
