import re
import argparse
from string import punctuation
import os

import torch
import yaml
import numpy as np
from torch.utils.data import DataLoader
from g2p_en import G2p # type: ignore
from pypinyin import pinyin, Style # type: ignore
from utils.model import get_model, get_vocoder
from utils.tools import to_device, synth_samples
from dataset import TextDataset
from text import text_to_sequence, clean_vietnamese_text
import text.vietnamese_phonemes as viphonemes
from subprocess import run

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def read_lexicon(lex_path):
    lexicon = {}
    with open(lex_path, 'r', encoding='utf-8') as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            word = temp[0]
            phones = temp[1:]
            if word.lower() not in lexicon:
                lexicon[word.lower()] = phones
    return lexicon


def preprocess_english(text, preprocess_config):
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    g2p = G2p()
    phones = []
    words = re.split(r"([,;.\-\?\!\s+])", text)
    for w in words:
        if w.lower() in lexicon:
            phones += lexicon[w.lower()]
        else:
            phones += list(filter(lambda p: p != " ", g2p(w)))
    phones = "{" + "}{".join(phones) + "}"
    phones = re.sub(r"\{[^\w\s]?\}", "{sp}", phones)
    phones = phones.replace("}{", " ")

    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)


def generate_pronunciation_mfa(word_list, g2p_model_path, temp_dir):
    """Sinh phiên âm cho danh sách từ bằng MFA CLI."""
    input_file = f"{temp_dir}/input_words.txt"
    output_file = f"{temp_dir}/output_words.txt"

    # Ghi từ vào file tạm
    os.makedirs(temp_dir, exist_ok=True)
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("\n".join(word_list))

    # Gọi MFA CLI để sinh phiên âm
    command = ["mfa", "g2p", input_file, g2p_model_path, output_file]
    run(command, check=True)

    # Đọc kết quả từ file output
    pronunciations = {}
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            word, pron = line.strip().split("\t")
            pronunciations[word] = pron.split()

    return pronunciations

def preprocess_vietnamese(text, preprocess_config):
    """Hàm tiền xử lý văn bản tiếng Việt với MFA G2P."""
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])
    g2p_model_path = preprocess_config["path"]["mfa_g2p_model_path"]
    temp_dir = preprocess_config["path"]["temp_dir"]
    # text = text.replace(',', ' ').replace('.', ' ').replace(';', ' ').replace('?', ' ').replace('!', ' ').replace(':', ' ') 
    text = text.replace(',', ' <sp> <sp> <sp> ').replace('.', ' <sp> <sp> <sp> <sp> ').replace(';', ' <sp> <sp> <sp> ').replace('?', ' <sp> <sp> <sp> <sp> ').replace('!', ' <sp> <sp> <sp> <sp> ').replace(':', ' <sp> <sp> <sp> <sp> ')
    
    
    text = clean_vietnamese_text(text)
    phones = []
    words = re.split(r"([,;\.\-\?\!\s+])", text)
    unknown_words = []
    for w in words:
        if w.lower() in lexicon:
            phones += lexicon[w.lower()]
        elif w.strip():
            unknown_words.append(w)
    if unknown_words:
        g2p_results = generate_pronunciation_mfa(unknown_words, g2p_model_path, temp_dir)
        for w in unknown_words:
            phones += g2p_results.get(w, ["spn"])

    phones = "{" + "}{".join(phones) + "}"
    phones = phones.replace("}{", " ")
    

    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))

    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)
def comma_indices(text, preprocess_config):
    """Hàm tiền xử lý văn bản tiếng Việt với MFA G2P."""
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])
    g2p_model_path = preprocess_config["path"]["mfa_g2p_model_path"]
    temp_dir = preprocess_config["path"]["temp_dir"]
    text = text.replace(',', ' <sp> <sp> <sp> ').replace('.', ' <sp> <sp> <sp> <sp> ').replace(';', ' <sp> <sp> <sp> ').replace('?', ' <sp> <sp> <sp> <sp> ').replace('!', ' <sp> <sp> <sp> <sp> ').replace(':', ' <sp> <sp> <sp> <sp> ')
    text = clean_vietnamese_text(text)
    phones = []
    words = re.split(r"([,;\.\-\?\!\s+])", text)
    unknown_words = []
    for w in words:
        if w.lower() in lexicon:
            phones += lexicon[w.lower()]
        elif w.strip():  # Lưu từ không nằm trong từ điển để xử lý sau
            unknown_words.append(w)
    # Sử dụng MFA để tạo phiên âm cho các từ không có trong từ điển
    if unknown_words:
        g2p_results = generate_pronunciation_mfa(unknown_words, g2p_model_path, temp_dir)
        for w in unknown_words:
            phones += g2p_results.get(w, ["sp"])

    phones = "{" + "}{".join(phones) + "}"
    phones = phones.replace("}{", " ")

    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )
    comma_indices = [idx for idx, phoneme in enumerate(sequence) if phoneme == 270] # 270 is index of 'sp'

    return comma_indices

def preprocess_mandarin(text, preprocess_config):
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    phones = []
    pinyins = [
        p[0]
        for p in pinyin(
            text, style=Style.TONE3, strict=False, neutral_tone_with_five=True
        )
    ]
    for p in pinyins:
        if p in lexicon:
            phones += lexicon[p]
        else:
            phones.append("sp")

    phones = "{" + " ".join(phones) + "}"
    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)


def synthesize(model, step, configs, vocoder , batchs, control_values):
    preprocess_config, model_config, train_config = configs
    pitch_control, energy_control, duration_control = control_values

    for batch in batchs:
        batch = to_device(batch, device)
        with torch.no_grad():
            # Forward
            output = model(
                *(batch[2:]),
                p_control=pitch_control,
                e_control=energy_control,
                d_control=duration_control
            )
            synth_samples(
                batch,
                output,
                vocoder,
                model_config,
                preprocess_config,
                train_config["path"]["result_path"],
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--restore_step", type=int, required=True)
    parser.add_argument(
        "--mode",
        type=str,
        choices=["batch", "single"],
        required=True,
        help="Synthesize a whole dataset or a single sentence",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="path to a source file with format like train.txt and val.txt, for batch mode only",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="raw text to synthesize, for single-sentence mode only",
    )
    parser.add_argument(
        "--speaker_id",
        type=int,
        default=0,
        help="speaker ID for multi-speaker synthesis, for single-sentence mode only",
    )
    parser.add_argument(
        "-p",
        "--preprocess_config",
        type=str,
        required=True,
        help="path to preprocess.yaml",
    )
    parser.add_argument(
        "-m", "--model_config", type=str, required=True, help="path to model.yaml"
    )
    parser.add_argument(
        "-t", "--train_config", type=str, required=True, help="path to train.yaml"
    )
    parser.add_argument(
        "--pitch_control",
        type=float,
        default=1.0,
        help="control the pitch of the whole utterance, larger value for higher pitch",
    )
    parser.add_argument(
        "--energy_control",
        type=float,
        default=1.0,
        help="control the energy of the whole utterance, larger value for larger volume",
    )
    parser.add_argument(
        "--duration_control",
        type=float,
        default=1.0,
        help="control the speed of the whole utterance, larger value for slower speaking rate",
    )
    args = parser.parse_args()

    # Check source texts
    if args.mode == "batch":
        assert args.source is not None and args.text is None
    if args.mode == "single":
        assert args.source is None and args.text is not None

    # Read Config
    preprocess_config = yaml.load(
        open(args.preprocess_config, "r"), Loader=yaml.FullLoader
    )
    model_config = yaml.load(open(args.model_config, "r"), Loader=yaml.FullLoader)
    train_config = yaml.load(open(args.train_config, "r"), Loader=yaml.FullLoader)
    configs = (preprocess_config, model_config, train_config)

    # Get model
    model = get_model(args, configs, device, train=False)

    # Load vocoder
    vocoder = get_vocoder(model_config, device)

    # Preprocess texts
    if args.mode == "batch":
        # Get dataset
        dataset = TextDataset(args.source, preprocess_config)
        batchs = DataLoader(
            dataset,
            batch_size=8,
            collate_fn=dataset.collate_fn,
        )
    if args.mode == "single":
        ids = raw_texts = [args.text[:100]]
        speakers = np.array([args.speaker_id])
        if preprocess_config["preprocessing"]["text"]["language"] == "en":
            texts = np.array([preprocess_english(args.text, preprocess_config)])
        elif preprocess_config["preprocessing"]["text"]["language"] == "zh":
            texts = np.array([preprocess_mandarin(args.text, preprocess_config)])
        elif preprocess_config["preprocessing"]["text"]["language"] == "vi":
            texts = np.array([preprocess_vietnamese(args.text, preprocess_config)])
        text_lens = np.array([len(texts[0])])
        print("texts: ", texts)
        print("test length: ", text_lens)
        # comma_indx = comma_indices(args.text, preprocess_config)
        batchs = [(ids, raw_texts, speakers, texts, text_lens, max(text_lens))]

    control_values = args.pitch_control, args.energy_control, args.duration_control

    synthesize(model, args.restore_step, configs, vocoder, batchs, control_values)
