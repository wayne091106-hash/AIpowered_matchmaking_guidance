# 🎙️ 全能語音軍師 (The Greasy Mastermind)

這不是普通的 AI，這是一個**臉皮比防彈衣還厚**、**說話比麻油還順**的即時語音互動系統。我們整合了最強的 ASR、LLM 與 TTS 技術，目標只有一個：讓你在相親或聊天場景中，用最油的方式震撼全場。

## ✨ 核心大招 (Core Features)

* **⚡ 速度就是一切 (Ultra-fast Response)**：採用串流斷句，LLM 才剛開口，TTS 就已經在熱身了，絕不讓氣氛冷掉。
* **🛡️ 拒絕回音 (Anti-Feedback)**：軍師很有禮貌，他會等自己說完遺言（？）後，才開啟麥克風聽你說話。
* **🚀 硬體壓榨 (Hardware Acceleration)**：支援 CUDA 加速的 `Faster-Whisper`，讓辨識速度快到你以為軍師會讀心。
* **🔊 1.6 倍速撩妹 (Optimized Playback)**：內建 1.6 倍速播放優化，節奏緊湊，不給對方思考拒絕的時間。
* **🤡 靈魂人格 (Soulful Personality)**：內建「頂級油男」設定，輸出內容絕對不含任何「AI 味」。

---

## 🛠️ 技術組件 (Tech Stack)

* **LLM:** Groq API (Kimi-K2-Instruct) —— 負責出謀劃策。
* **ASR:** Faster-Whisper (Turbo) —— 負責側耳傾聽。
* **TTS:** gTTS + Pydub —— 負責舌燦蓮花。
* **Audio:** Pygame + PyAudio —— 負責發聲與收音。

---

## 🚀 快速上路 (Quick Start)

### 1. 準備材料 (Requirements)

請確保你的電腦裡有 Python 3.10+ 以及 **FFmpeg**。

### 2. 安裝裝備 (Installation)

```bash
pip install pygame numpy pyaudio gtts pydub groq faster-whisper python-dotenv

```

### 3. 設定密鑰 (Configuration)

建立 `.env` 檔案並填入你的 Groq API：

```env
GROQ_API=your_groq_api_key_here

```

### 4. 啟動軍師 (Run)

```bash
python LLM_TTS_ASR.py

```

---

## 🇺🇸 English Version

### **The Greasy Mastermind: Real-time Voice AI**

A voice-to-voice interaction system designed for those who want to master the art of "smooth talking." Powered by high-speed inference and optimized audio pipelines.

#### **Key Highlights:**

* **Real-time Streaming:** Processes text and speech in parallel to minimize latency.
* **Intelligent Feedback Control:** Automatically manages microphone states to prevent echo loops.
* **Turbo-charged ASR:** Uses `Faster-Whisper` with CUDA support for near-instant transcription.
* **High-Octane Personality:** Pre-configured with a "Smooth Talker" persona that’s more human than humans.

---

## ⚠️ 警語 (Disclaimer)

本程式僅供技術交流與娛樂使用。若因使用本軍師提供的「油話」導致相親失敗或被對方封鎖，本作者概不負責。

---

**需要我幫你把這段文字直接寫入一個 `README.md` 檔案供你下載嗎？**
