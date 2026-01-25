# Quick Start Guide

## 🚀 Installation

### Option 1: ComfyUI Manager
1. Open ComfyUI Manager
2. Search "Simple Pocket TTS"
3. Install
4. Restart

### Option 2: Command Line
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ai-joe-git/ComfyUI-Pocket-TTS
cd ComfyUI-Pocket-TTS
pip install -r requirements.txt
```

## 🎯 First TTS in 30 Seconds

1. **Add Node**: Right-click → Audio → Pocket-TTS → Simple
2. **Set Voice**: Choose from dropdown (try "alba")
3. **Enter Text**: "Hello world!"
4. **Queue Prompt**: Generate!

## 📝 Example Workflows

### Basic TTS
```
[Simple Pocket TTS] → [Preview Audio] → [Save Audio]
```

### Voice Cloning
1. Put `my_voice.wav` in `ComfyUI/input/`
2. Use "Voice Clone" node
3. Select your audio
4. Generate!

### Batch Generation
```
[Text List] → [Pocket TTS Generate] → [Batch Save]
```

## 🎭 Voice Reference

- **alba** - Warm, friendly (default)
- **marius** - Young male
- **javert** - Deep, authoritative
- **jean** - Mature, wise
- **fantine** - Soft, emotional
- **cosette** - Young, bright
- **eponine** - Energetic
- **azelma** - Playful

## ⚡ Tips

1. **Speed**: Use float32 for fastest CPU generation
2. **Quality**: All voices are high quality
3. **Long Text**: No limit on text length!
4. **Memory**: Only ~400MB RAM needed

## 🐛 Troubleshooting

### Module not found
```bash
pip install pocket-tts torch scipy
```

### No audio files
Put `.wav` files in: `ComfyUI/input/`

### Slow generation
- Close other apps
- Use float32 precision
- Check CPU isn't thermal throttling

## 🎬 Next Steps

- Try all 8 voices
- Clone your own voice
- Integrate with video workflows
- Batch process scripts

**Enjoy fast CPU-based TTS! 🎉**
