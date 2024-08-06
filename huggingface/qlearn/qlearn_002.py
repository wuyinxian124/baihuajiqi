import torch
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf
from pydub import AudioSegment
import os

# 加载GPT-2模型和tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# 加载Wav2Vec2模型和processor
asr_model_name = "facebook/wav2vec2-base-960h"
asr_processor = Wav2Vec2Processor.from_pretrained(asr_model_name)
asr_model = Wav2Vec2ForCTC.from_pretrained(asr_model_name)

# 加载TTS模型
tts_pipeline = pipeline("text-to-speech", model="facebook/fastspeech2-en-ljspeech")


def transcribe_audio(file_path):
    # 读取音频文件
    speech, rate = sf.read(file_path)
    input_values = asr_processor(speech, return_tensors="pt", sampling_rate=rate).input_values
    with torch.no_grad():
        logits = asr_model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = asr_processor.decode(predicted_ids[0])
    return transcription


def generate_sentence(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1)
    sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sentence


def text_to_speech(text, output_path):
    tts_output = tts_pipeline(text)
    tts_output[0]["array"].tofile(output_path)


def main():
    # 输入音频文件路径
    audio_file_path = "/Users/runzhouwu/aigc_project/python/sourcecode-cn/huggingface/qlearn/sources/demo1.flac"

    # 转录音频
    prompt = transcribe_audio(audio_file_path)
    print(f"Transcribed text: {prompt}")

    # 生成句子
    sentence = generate_sentence(prompt)
    print(f"Generated sentence: {sentence}")

    # 生成语音
    output_audio_path = "output.wav"
    text_to_speech(sentence, output_audio_path)
    print(f"Generated speech saved to {output_audio_path}")


if __name__ == "__main__":
    main()