import os

import librosa
import numpy as np
from scipy.io import wavfile
from tqdm import tqdm

from text import _clean_text

def prepare_align(config):
    raw_data_path = "./input/infore"
    in_dir = config["path"]["corpus_path"]
    out_dir = config["path"]["raw_path"]
    sampling_rate = config["preprocessing"]["audio"]["sampling_rate"]
    max_wav_value = config["preprocessing"]["audio"]["max_wav_value"]
    cleaners = config["preprocessing"]["text"]["text_cleaners"]
    speaker = "ViSSpeech"
    for wave_name in tqdm(os.listdir(raw_data_path)):
        if ".wav" not in wave_name:
            continue
        base_name = wave_name.split(".")[0]

        wav_path = os.path.join(raw_data_path, "{}.wav".format(base_name))
        text_path = os.path.join(raw_data_path, "{}.txt".format(base_name))
        if os.path.exists(wav_path) and os.path.exists(text_path):
            with open(text_path, 'r', encoding='utf-8') as file:
                text = file.read()
            text = _clean_text(text, cleaners)
            os.makedirs(os.path.join(out_dir, speaker), exist_ok=True)
            wav, _ = librosa.load(wav_path, sr=sampling_rate)
            wav = wav / max(abs(wav)) * max_wav_value
            wavfile.write(
                os.path.join(out_dir, speaker, "{}.wav".format(base_name)),
                sampling_rate,
                wav.astype(np.int16),
            )
            with open(
                os.path.join(out_dir, speaker, "{}.lab".format(base_name)),
                "w", encoding='utf-8'
            ) as f1:
                f1.write(text)