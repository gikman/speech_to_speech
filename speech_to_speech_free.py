import os
import whisper  # pip install openai-whisper
import pyaudio
import wave
import keyboard
from pydub import AudioSegment
from pydub.playback import play
import pyautogui as pag
import time
import pyperclip
from gtts import gTTS

model = whisper.load_model("tiny") # tiny / base / small / medium / large

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

                # transcript audio using whisper
                result = model.transcribe("recorded.wav", fp16=False)
                transcript = result["text"]
                # print(transcript)

                # pass transcript into chatgpt and get the response
                pag.moveTo(x=710, y=950)      # pag.moveTo(x=710, y=950, duration=0.2)
                pag.click(x=715, y=955)
                pyperclip.copy(transcript)
                pag.hotkey('ctrl', 'v')
                pag.press('tab')
                pag.press('enter')
                pag.click(x=697, y=540)

                condition = False
                while not condition:
                    time.sleep(0.4)
                    pag.hotkey('ctrl', 'a', 'c')
                    copy_all_text_old = pyperclip.paste()
                    time.sleep(0.5)
                    pag.hotkey('ctrl', 'a', 'c')
                    copy_all_text = pyperclip.paste()
                    if copy_all_text_old == copy_all_text:
                        condition = True

                pag.click(x=697, y=540)
                pag.hotkey('ctrl', 'shift', 'c')

                chatgpt_message = pyperclip.paste()
                pag.moveTo(x=710, y=950)

                # text-to-speech
                tts = gTTS(text=chatgpt_message, lang='en')
                tts_file_path = 'tts_output.mp3'
                tts.save(tts_file_path)

                audio = AudioSegment.from_file('tts_output.mp3', format="mp3")
                play(audio)

                # Remove the temporary audio file
                os.remove('tts_output.mp3')
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




