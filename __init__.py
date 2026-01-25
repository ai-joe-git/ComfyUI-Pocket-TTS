"""
ComfyUI-Pocket-TTS - Lightweight CPU-based Text-to-Speech
Fast, efficient TTS without GPU requirements
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
__version__ = "1.0.2"

print(f"✅ ComfyUI-Pocket-TTS v{__version__} loaded")
