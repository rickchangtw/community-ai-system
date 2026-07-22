#!/usr/bin/env python3
"""
Silero VAD + Whisper 語音處理模組
Phase 3: 語音識別完整實現
"""
import logging
import os
import sys
import time
import tempfile
import json
from datetime import datetime

# ── 日誌 ─────────────────────────────────────────────────────────────────────
LOG_FILE = "/tmp/voice_processing.log"
sys.stdout = open(LOG_FILE, "a", encoding="utf-8")
sys.stderr = open(LOG_FILE, "a", encoding="utf-8")
logger = logging.getLogger("voice_processing")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

# ── 語音段配置 ───────────────────────────────────────────────────────────────
VOICE_SEGMENT_CONFIG = {
    "min_silence": 0.5,   # 最短靜音 (秒)
    "silence_threshold": 0.3,  # 語音活動閾值
    "max_segment_duration": 30,  # 最大語音段 (秒)
    "sample_rate": 16000,
    "frame_size": 512,
    "hop_length": 128
}

# ── Silero VAD 載入 ──────────────────────────────────────────────────────────
def load_silero_vad():
    """載入 Silero VAD 模型"""
    try:
        import torch
        model, options = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            onnx=False
        )
        return model, options
    except Exception as e:
        logger.error(f"Silero VAD 載入失敗: {e}")
        return None, None

# ── Silero VAD 檢測 ──────────────────────────────────────────────────────────
def vad_detect(audio_path_or_bytes, sr=16000, threshold=0.5):
    """
    Silero VAD 語音活動檢測
    
    Args:
        audio_path_or_bytes: 音頻文件路徑或字节
        sr: 采樣率
        threshold: 語音活動閾值 (0.0-1.0)
    
    Returns:
        list: 語音段列表 [{start, end, duration}]
    """
    try:
        import torch
        import torchaudio
        
        # 載入模型
        model, options = load_silero_vad()
        if model is None:
            return []
        
        # 讀取音頻
        if isinstance(audio_path_or_bytes, (str, bytes)):
            wave, sr = torchaudio.load(audio_path_or_bytes)
        else:
            wave = torch.frombuffer(audio_path_or_bytes, dtype=torch.float32)
        
        # 重采樣到 16kHz
        if sr != 16000:
            wave = torchaudio.functional.resample(wave, sr, 16000)
        
        # 轉換為單通道
        if wave.shape[0] > 1:
            wave = wave[0]
        
        # VAD 檢測
        with torch.no_grad():
            # Silero VAD 返回 [batch, 1] tensor
            prediction = model(wave.unsqueeze(0))
            prediction = prediction.squeeze(0).squeeze(1).cpu().numpy()
        
        # 後處理：提取語音段
        segments = []
        in_speech = False
        start_idx = 0
        
        for i, pred in enumerate(prediction):
            if pred > threshold:
                if not in_speech:
                    in_speech = True
                    start_idx = i
            else:
                if in_speech:
                    # 語音結束
                    end_idx = i
                    start_time = start_idx / sr
                    end_time = end_idx / sr
                    duration = end_time - start_time
                    
                    if duration > 0.1:  # 最短語音段 100ms
                        segments.append({
                            'start': round(start_time, 3),
                            'end': round(end_time, 3),
                            'duration': round(duration, 3)
                        })
                    
                    in_speech = False
        
        # 最後一個語音段
        if in_speech:
            end_idx = len(prediction)
            start_time = start_idx / sr
            end_time = end_idx / sr
            duration = end_time - start_time
            
            if duration > 0.1:
                segments.append({
                    'start': round(start_time, 3),
                    'end': round(end_time, 3),
                    'duration': round(duration, 3)
                })
        
        logger.info(f"檢測到 {len(segments)} 個語音段")
        return segments
    
    except Exception as e:
        logger.error(f"VAD 檢測失敗: {e}")
        return []

# ── Whisper 語音轉文字 ───────────────────────────────────────────────────────
def process_voice(audio_path, model_size="base", language="zh"):
    """
    Whisper 語音轉文字
    
    Args:
        audio_path: 音頻文件路徑
        model_size: Whisper 模型大小 (tiny, base, small, medium, large)
        language: 語言代碼 (zh, en, ja, ko)
    
    Returns:
        dict: 轉文字結果 {segments, full_transcription}
    """
    try:
        import whisper
        import torch
        
        # 載入 Whisper 模型
        logger.info(f"載入 Whisper {model_size} 模型...")
        model = whisper.load_model(model_size)
        
        # 轉文字
        logger.info(f"開始轉文字 (語言: {language})...")
        result = model.transcribe(audio_path, language=language)
        
        # 提取語音段
        segments = []
        for seg in result['segments']:
            segments.append({
                'start': seg['start'],
                'end': seg['end'],
                'duration': seg['end'] - seg['start'],
                'text': seg['text'],
                'confidence': seg['avg_logprob'] if 'avg_logprob' in seg else 0.0
            })
        
        logger.info(f"轉文字完成: {len(segments)} 段, {result['text'][:100]}")
        
        return {
            'segments': segments,
            'full_transcription': result['text'],
            'language': result.get('language', language),
            'duration': result['segments'][-1]['end'] if result['segments'] else 0
        }
    
    except Exception as e:
        logger.error(f"Whisper 轉文字失敗: {e}")
        return {
            'segments': [],
            'full_transcription': '',
            'error': str(e)
        }

# ── 完整語音處理流程 ─────────────────────────────────────────────────────────
def voice_pipeline(audio_path, sr=16000):
    """
    完整語音處理流程：VAD + Whisper
    
    流程：
    1. 使用 Silero VAD 檢測語音段
    2. 對每個語音段使用 Whisper 轉文字
    3. 返回完整轉文字結果
    
    Args:
        audio_path: 音頻文件路徑
        sr: 采樣率
    
    Returns:
        dict: 完整處理結果
    """
    logger.info("=" * 50)
    logger.info(f"開始語音處理: {audio_path}")
    logger.info("=" * 50)
    
    # 1. VAD 檢測語音段
    logger.info("步驟 1: Silero VAD 語音活動檢測...")
    vad_segments = vad_detect(audio_path, sr=sr)
    
    if not vad_segments:
        logger.warning("未檢測到語音段")
        return {
            'vad_segments': [],
            'whisper_segments': [],
            'full_transcription': '',
            'status': 'no_speech',
            'error': '未檢測到語音'
        }
    
    logger.info(f"檢測到 {len(vad_segments)} 個語音段:")
    for seg in vad_segments:
        logger.info(f"  - [{seg['start']:.1f}s ~ {seg['end']:.1f}s] ({seg['duration']:.1f}s)")
    
    # 2. Whisper 轉文字
    logger.info("步驟 2: Whisper 語音轉文字...")
    whisper_result = process_voice(audio_path)
    
    logger.info(f"轉文字結果: {whisper_result['full_transcription'][:100]}")
    
    return {
        'vad_segments': vad_segments,
        'whisper_segments': whisper_result.get('segments', []),
        'full_transcription': whisper_result.get('full_transcription', ''),
        'language': whisper_result.get('language', 'zh'),
        'status': 'success' if not whisper_result.get('error') else 'error',
        'error': whisper_result.get('error')
    }

# ── 語音段處理 ──────────────────────────────────────────────────────────────
def process_voice_segment(segment, audio_path, model_size="base", language="zh"):
    """
    處理單一語音段
    
    Args:
        segment: 語音段 {start, end, duration}
        audio_path: 音頻文件路徑
        model_size: Whisper 模型大小
        language: 語言代碼
    
    Returns:
        dict: 語音段轉文字結果
    """
    try:
        import whisper
        import torch
        
        # 載入 Whisper 模型
        model = whisper.load_model(model_size)
        
        # 提取語音段
        import torchaudio
        wave, sr = torchaudio.load(audio_path)
        
        if sr != 16000:
            wave = torchaudio.functional.resample(wave, sr, 16000)
        
        if wave.shape[0] > 1:
            wave = wave[0]
        
        # 裁剪語音段
        start_idx = int(segment['start'] * sr)
        end_idx = int(segment['end'] * sr)
        segment_audio = wave[start_idx:end_idx]
        
        # 保存臨時文件
        tmp_path = tempfile.mktemp(suffix=".wav")
        torchaudio.save(tmp_path, segment_audio, sr)
        
        # 轉文字
        result = model.transcribe(tmp_path, language=language)
        
        # 清理
        os.remove(tmp_path)
        
        return {
            'segment': segment,
            'text': result['text'],
            'start': result['segments'][0]['start'] if result['segments'] else 0,
            'end': result['segments'][-1]['end'] if result['segments'] else 0,
            'duration': result['segments'][-1]['end'] - result['segments'][0]['start'] if result['segments'] else 0
        }
    
    except Exception as e:
        logger.error(f"語音段處理失敗: {e}")
        return {
            'segment': segment,
            'text': '',
            'error': str(e)
        }

# ── 測試函數 ─────────────────────────────────────────────────────────────────
def test_vad():
    """測試 VAD 功能"""
    logger.info("測試 Silero VAD...")
    
    # 測試音頻文件路徑
    test_audio_path = "/tmp/test_voice.wav"
    
    if os.path.exists(test_audio_path):
        segments = vad_detect(test_audio_path, sr=16000, threshold=0.5)
        logger.info(f"VAD 測試結果: {len(segments)} 個語音段")
        
        for seg in segments:
            logger.info(f"  語音段: {seg['start']:.1f}s ~ {seg['end']:.1f}s ({seg['duration']:.1f}s)")
        
        return segments
    else:
        logger.warning(f"測試音頻文件不存在: {test_audio_path}")
        return []

def test_whisper():
    """測試 Whisper 功能"""
    logger.info("測試 Whisper...")
    
    # 測試音頻文件路徑
    test_audio_path = "/tmp/test_voice.wav"
    
    if os.path.exists(test_audio_path):
        result = process_voice(test_audio_path, model_size="base")
        logger.info(f"Whisper 測試結果: {result['full_transcription'][:100]}")
        return result
    else:
        logger.warning(f"測試音頻文件不存在: {test_audio_path}")
        return None

def test_pipeline():
    """測試完整流程"""
    logger.info("測試完整語音處理流程...")
    
    test_audio_path = "/tmp/test_voice.wav"
    
    if os.path.exists(test_audio_path):
        result = voice_pipeline(test_audio_path)
        logger.info(f"流程測試結果:")
        logger.info(f"  VAD 語音段: {len(result['vad_segments'])}")
        logger.info(f"  Whisper 語音段: {len(result['whisper_segments'])}")
        logger.info(f"  轉文字: {result['full_transcription'][:100]}")
        logger.info(f"  狀態: {result['status']}")
        return result
    else:
        logger.warning(f"測試音頻文件不存在: {test_audio_path}")
        return None

# ── 主函數 ───────────────────────────────────────────────────────────────────
def main():
    """測試語音處理模組"""
    logger.info("=" * 50)
    logger.info("Silero VAD + Whisper 語音處理模組測試")
    logger.info("=" * 50)
    
    # 測試 VAD
    logger.info("-" * 30)
    logger.info("測試 VAD...")
    vad_result = test_vad()
    
    # 測試 Whisper
    logger.info("-" * 30)
    logger.info("測試 Whisper...")
    whisper_result = test_whisper()
    
    # 測試完整流程
    logger.info("-" * 30)
    logger.info("測試完整流程...")
    pipeline_result = test_pipeline()
    
    logger.info("=" * 50)
    logger.info("測試完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
