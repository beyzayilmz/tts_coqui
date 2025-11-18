from TTS.api import TTS

# Modeli indir (ilk çalıştırmada internet gerekir)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True)

# Yazıyı sese çevir
tts.tts_to_file(text="Hello, this is AI Pin speaking.", file_path="output.wav")
