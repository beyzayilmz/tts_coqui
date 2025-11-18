import requests
from TTS.api import TTS
import os
from dotenv import load_dotenv
from openai import OpenAI
import re
import json
import time
import sounddevice as sd

class LLMHandler:
    def __init__(self):
        load_dotenv()
        #self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url="https://openrouter.ai/api/v1")
        self.model_name = os.getenv("MODEL_NAME", "gpt-oss:20b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.chat_url = f"{self.ollama_host}/api/chat"



    def get_respons(self, prompt: str) -> str:
        '''headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }'''
        try:
            self.response = self.client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content":"You are a helpful assistant"},
                {"role": "user", "content" : prompt},
            ],
            stream=False

        )
            return self.response.choices[0].message.content
        except Exception as e:
            return f"llm baglantisi kurulamadi: {e}"    
             

        '''try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"LLM baglantisi kurulamadi: {e}"'''
        

    def get_response(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "stream": True,
                "options": {
                    "temperature": 0.7
                }
            }

            with requests.post(self.chat_url, json=payload, stream=True, timeout=600) as r:
                r.raise_for_status()
                parts = []
                for line in r.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line.decode("utf-8"))
                    # Ollama chat stream formatı
                    msg = data.get("message", {})
                    chunk = msg.get("content", "")
                    if chunk:
                        parts.append(chunk)
                    if data.get("done"):
                        break
                return "".join(parts).strip()

        except Exception as e:
            return f"llm baglantisi kurulamadi: {e}"
    


class TextToSpeech:
    def __init__(self, model_name="tts_models/tr/common-voice/glow-tts"):
        print("TTS modeli yukleniyo")
        self.tts = TTS(model_name=model_name, progress_bar=False)
        print("[TTS] Model yuklendi.")

    def speak(self, text: str, output_path: str = 'turkce.wav'):
        print(f"TTS sese ceviriliyor: {text}")
        self.tts.tts_to_file(text=text, file_path=output_path)
        print(f"TTS dosyaya kaydedildi. {output_path}")
        wav = self.tts.tts(text)
        sr = self.tts.synthesizer.output_sample_rate
        sd.play(wav,sr)
        sd.wait()



def clean_text_notfound(text):
    text = text.lower()
    allowed = "abcçdefgğhıijklmnoöprsştuüvyzx0123456789.,?! \n"
    text = ''.join(c for c in text if c in allowed) #ASCII disi karakterleri kaldir
    text = re.sub(r'[*#+/\-]', '', text) #markdown karakterler

    return text.strip()

class AIPin:
    def __init__(self):
        self.llm = LLMHandler()
        self.tts = TextToSpeech()

    def process_prompt(self, prompt: str):
        response = self.llm.get_respons(prompt)
        print(f"[LLM] Cevap alindi: {response}")
        cleaned_response = clean_text_notfound(response)
        self.tts.speak(cleaned_response)


if __name__ == "__main__":
    ai_pin = AIPin()
    user_input = input(" Komut ver: ")
    ai_pin.process_prompt(user_input)
                
            
