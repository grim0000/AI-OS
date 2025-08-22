# 🎤 Xeno Voice Chatbot

Ultra-fast speech-to-text and text-to-speech chatbot using Cohere or Groq API with minimal lag.

## 🚀 Features

- **Two Versions Available:**
  - **Fast Voice Chatbot**: Uses existing STT/TTS modules
  - **Ultra-Fast Voice Chatbot**: Optimized for speed with faster speech recognition and TTS

- **API Support:**
  - Groq API (Llama 3 70B model)
  - Cohere API (Command R+ model)
  - Automatic switching based on configuration

- **Optimizations:**
  - Streaming responses for faster generation
  - Asynchronous chat history saving
  - Reduced token limits for voice responses
  - Optimized speech recognition parameters
  - Fast TTS with higher speech rate

## 📋 Requirements

### Dependencies
```bash
pip install -r Requirements.txt
```

### Additional Dependencies for Ultra-Fast Version
```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

### Environment Variables (.env file)
```env
Username=your_name
AssistantName=Xeno
GroqAPIKey=your_groq_api_key
CohereAPIKey=your_cohere_api_key
USE_COHERE=false
Input_Language=en
AssistantVoice=en-US-AriaNeural
```

## 🎯 Usage

### Option 1: Use the Launcher (Recommended)
```bash
cd Backend
python LaunchVoiceChatbot.py
```

Then choose:
1. **Fast Voice Chatbot** - Uses existing STT/TTS modules
2. **Ultra-Fast Voice Chatbot** - Optimized for speed

### Option 2: Direct Execution

#### Fast Version
```bash
cd Backend
python FastVoiceChatbot.py
```

#### Ultra-Fast Version
```bash
cd Backend
python UltraFastVoiceChatbot.py
```

## 🔧 Configuration

### API Selection
- Set `USE_COHERE=true` in `.env` to use Cohere API
- Set `USE_COHERE=false` (default) to use Groq API

### Speech Recognition Settings (Ultra-Fast)
- **Energy Threshold**: 300 (lower for faster detection)
- **Pause Threshold**: 0.5 seconds (shorter for faster response)
- **Dynamic Energy**: Enabled for better adaptation

### Text-to-Speech Settings (Ultra-Fast)
- **Speech Rate**: 200 WPM (faster than normal)
- **Volume**: 0.9 (90% volume)

## ⚡ Performance Optimizations

### Fast Version
- Uses existing STT/TTS modules
- Streaming API responses
- Asynchronous chat history saving
- Limited context (last 4 messages)

### Ultra-Fast Version
- Direct microphone access
- Google Speech Recognition API
- pyttsx3 for faster TTS
- Reduced token limits (100 tokens)
- Early response breaking
- Minimal context (last 2 messages)

## 🎤 Voice Commands

- **Start Speaking**: The chatbot will automatically start listening
- **Stop**: Press Ctrl+C to exit
- **Natural Conversation**: Speak naturally, the chatbot will respond

## 🔍 Troubleshooting

### Common Issues

1. **Microphone Not Working**
   - Check microphone permissions
   - Ensure microphone is set as default device
   - Try running as administrator

2. **API Errors**
   - Verify API keys in `.env` file
   - Check internet connection
   - Ensure API quota is available

3. **Speech Recognition Issues**
   - Speak clearly and at normal volume
   - Reduce background noise
   - Check microphone quality

4. **TTS Not Working**
   - Check system audio settings
   - Ensure speakers/headphones are connected
   - Try different TTS engines

### Performance Tips

1. **For Best Speed:**
   - Use Ultra-Fast version
   - Use Groq API (generally faster)
   - Ensure good internet connection
   - Use wired microphone if possible

2. **For Best Quality:**
   - Use Fast version
   - Use Cohere API
   - Speak clearly and slowly
   - Reduce background noise

## 📁 File Structure

```
Backend/
├── FastVoiceChatbot.py          # Fast version using existing modules
├── UltraFastVoiceChatbot.py     # Ultra-fast version with optimizations
├── LaunchVoiceChatbot.py        # Launcher script
├── SpeechToText.py              # Existing STT module
├── TextToSpeech.py              # Existing TTS module
└── README_VoiceChatbot.md       # This file
```

## 🤝 Contributing

Feel free to contribute by:
- Improving speech recognition accuracy
- Optimizing TTS performance
- Adding new features
- Fixing bugs

## 📄 License

This project is part of the Xeno AI Assistant system. 