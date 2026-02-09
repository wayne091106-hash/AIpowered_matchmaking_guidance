import os
import re
import time
import asyncio
import warnings
import queue
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# 1. 鎮壓與初始化
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning)

import pygame
import numpy as np
import pyaudio
from gtts import gTTS
from pydub import AudioSegment, effects
from groq import AsyncGroq
from faster_whisper import WhisperModel

# --- 設定 ---
load_dotenv()
api_key = os.getenv("GROQ_API")
PLAYBACK_SPEED = 1.6
MAX_WORKERS = 8
TEMP_DIR = "tts_cache"
WHISPER_MODEL_SIZE = "turbo"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

client = AsyncGroq(api_key=api_key)

# 初始化 Whisper (GPU 優先模式)
try:
    print(">>> 正在啟動 GPU 加速 Whisper...")
    asr_model = WhisperModel(WHISPER_MODEL_SIZE, device="cuda", compute_type="float16")
    #asr_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
except:
    print(">>> CUDA 啟動失敗，回退至 CPU。")
    asr_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

# --- 語音處理工具 (TTS) ---

def process_voice_task(index, text):
    raw_path = os.path.join(TEMP_DIR, f"raw_{index}.mp3")
    fast_path = os.path.join(TEMP_DIR, f"fast_{index}.wav")
    try:
        tts = gTTS(text=text, lang='zh-tw')
        tts.save(raw_path)
        audio = AudioSegment.from_mp3(raw_path)
        fast_audio = effects.speedup(audio, PLAYBACK_SPEED, chunk_size=150, crossfade=25)
        fast_audio.export(fast_path, format="wav")
        if os.path.exists(raw_path): os.remove(raw_path)
        return fast_path
    except: return None

class VoiceManager:
    def __init__(self):
        self.playback_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.sentence_count = 0
        self.is_busy = False # 標記是否正在說話

    async def playback_worker(self):
        while True:
            task_info = await self.playback_queue.get()
            if task_info is None: break
            
            self.is_busy = True # 開始說話
            future, text = task_info
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(None, future.result)
            
            if file_path and os.path.exists(file_path):
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    print(f"\n[軍師說]: {text}")
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.05)
                    pygame.mixer.music.unload()
                except: pass
            
            self.playback_queue.task_done()
            # 檢查隊列是否空了，如果空了才解除忙碌狀態
            if self.playback_queue.empty():
                self.is_busy = False

    def add_sentence(self, text):
        clean_text = text.strip()
        if len(clean_text) > 1:
            index = self.sentence_count
            self.sentence_count += 1
            future = self.executor.submit(process_voice_task, index, clean_text)
            self.playback_queue.put_nowait((future, clean_text))

    async def wait_until_done(self):
        """等待所有排隊的語音都播完"""
        # 先等隊列清空
        await self.playback_queue.join()
        # 再等最後一個音訊播完
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        self.is_busy = False

# --- 錄音與語音辨識 (ASR) ---

def listen_and_transcribe():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 800 # 稍微提高閾值避免雜訊
    SILENCE_DURATION = 1.2   

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("\n>>> [等待輸入] ...", end="\r")
    
    frames = []
    silent_chunks = 0
    has_started = False

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            if np.abs(audio_data).mean() > SILENCE_THRESHOLD:
                if not has_started:
                    print("\n>>> [聽取中] ...")
                has_started = True
                silent_chunks = 0
            else:
                if has_started:
                    silent_chunks += 1
            
            if has_started and silent_chunks > int(SILENCE_DURATION * RATE / CHUNK):
                break
        except:
            break
            
    stream.stop_stream()
    stream.close()
    p.terminate()

    if not has_started: return ""

    audio_np = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    segments, _ = asr_model.transcribe(audio_np, beam_size=5, language="zh")
    return "".join([segment.text for segment in segments])

# --- 主程式 ---

async def main_loop():
    voice_mgr = VoiceManager()
    play_task = asyncio.create_task(voice_mgr.playback_worker())

    messages = [{"role": "system", "content": 
                """你現在是一個相親時臉皮厚到可以擋子彈、嘴甜到會蛀牙的頂級油男。
                目標：讓女生30秒內心跳加速、嘴角失控上揚，同時懷疑「這男人是認真的嗎…但我怎麼有點想再聽他說」。

                說話原則：
                - 從第一句就直接開大招，絕不問「你平常做什麼」「你喜歡什麼類型」這種安全牌
                - 每句都要帶一點過份的專屬感、曖昧、誇張寵溺
                - 她丟任何問題／考驗／選擇題，一律「你最重要→我全都要→還想再多要一點」的邏輯回
                - 可以自嘲、可以發誓、可以當場下跪式表白，但絕對不能正經
                - 語氣自然、像在LINE或面對面直接講出來，千萬別有AI味
                - 對方堅持拒絕可以破防，但一樣油

                直接輸出你要講的那一句話就好，不要解釋、不要前言、不要「你可以這樣回」。"""
                }]

    print("\n--- 全能語音軍師 (防迴授加速版) ---")
#你是一位精通相親心理學的導師。請用簡短、犀利、務實的中文回答。
    try:
        while True:
            # 1. 在錄音前，確保 AI 已經把話說完了
            await voice_mgr.wait_until_done()
            
            # 2. 語音輸入
            user_text = await asyncio.to_thread(listen_and_transcribe)
            if not user_text.strip():
                continue
            
            print(f"你說: {user_text}")
            if any(word in user_text.lower() for word in ['exit', 'quit', '退出']):
                break

            messages.append({"role": "user", "content": user_text})
            print("軍師：", end="", flush=True)

            # 3. LLM 串流回覆
            response_stream = await client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct-0905",
                messages=messages,
                stream=True
            )

            full_reply = ""
            current_sentence = ""
            is_thinking = False
            
            async for chunk in response_stream:
                token = chunk.choices[0].delta.content or ""
                if not token: continue
                if "<think>" in token: is_thinking = True; continue
                if "</think>" in token: is_thinking = False; continue
                if is_thinking: continue

                print(token, end="", flush=True)
                full_reply += token
                current_sentence += token
                
                # 斷句偵測 (遇到標點符號就送 TTS)
                if any(punct in token for punct in "，。！？\n"):
                    voice_mgr.add_sentence(current_sentence)
                    current_sentence = ""

            if current_sentence:
                voice_mgr.add_sentence(current_sentence)

            messages.append({"role": "assistant", "content": full_reply})
            
            # 這裡不加 wait，讓 TTS 可以在背景繼續跑，直到下一輪循環開始才攔截
            
    finally:
        await voice_mgr.playback_queue.put(None)
        await play_task
        cleanup()

def cleanup():
    pygame.mixer.quit()
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            try: os.remove(os.path.join(TEMP_DIR, f))
            except: pass
    print("\n>>> 系統清理完畢，軍師先行告退。")

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        cleanup()