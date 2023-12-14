import requests
import os
import pyaudio
import wave
import keyboard
from pydub import AudioSegment
from pydub.playback import play
from openai import OpenAI
import random

client = OpenAI(api_key="openai_api")
voice_id_list = ["voice_id", "voice_id", "voice_id", "voice_id"]

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Start recording...")

frames = []
recording = False

try:
    while True:
        if keyboard.is_pressed('r'):
            if recording:
                print("Recording stopped.")
                recording = False

                # Save the recorded audio
                wf = wave.open("recorded.wav".format(len(frames)//(RATE*CHUNK)), 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                audio_file= open("recorded.wav", "rb")
                transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
                completion = client.chat.completions.create(      
                    messages=[
                        {'role': 'system', 'content': 'Short sentence like in the real people conversation!!!'},
                        {'role': 'user', 'content': transcript}
                    ],
                    model="gpt-4",
                    temperature=0.3
                )       
                chatgpt_message = completion.choices[0].message.content

                # pass chatgpt_message into elevenlab
                headers = {"Content-Type": "application/json", "xi-api-key": "elevenlabs_api"}

                payload = {
                    "text": chatgpt_message,
                    "model_id": "eleven_turbo_v2", # eleven_monolingual_v1 , eleven_multilingual_v2
                    "voice_settings": {"stability": 1, "similarity_boost": 1}
                }

                random_id = random.choice(voice_id_list)
                url = "https://api.elevenlabs.io/v1/text-to-speech/{}".format(random_id)               

                response = requests.post(url, json=payload, headers=headers)
                with open('elevenlab_output.mp3', 'wb') as f:
                    f.write(response.content)

                audio = AudioSegment.from_file('elevenlab_output.mp3', format="mp3")
                play(audio)

                # Remove the temporary audio file
                os.remove('elevenlab_output.mp3')
                audio_file.close()
                os.remove('recorded.wav')

                frames = []
            else:
                print("Recording started...")
                recording = True
            # Avoid multiple key presses in a single press
            while keyboard.is_pressed('r'):
                pass
        elif keyboard.is_pressed('q'):
            break

        if recording:
            data = stream.read(CHUNK)
            frames.append(data)

except KeyboardInterrupt:
    pass

finally:
    print("Program terminated.")
    stream.stop_stream()
    stream.close()
    p.terminate()