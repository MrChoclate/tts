from __future__ import print_function

from multiprocessing import Pool
import subprocess
import os
import glob
import datetime

from aligner import align
from models import Session, Word, Audio


BASEDIR = '/home/choclate/LibriSpeech/train-clean-360/'

try:
    from subprocess import DEVNULL # python3
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def read_audio(audio_file, transcript):
    args = ['pocketsphinx_continuous', '-time', 'yes', '-infile', audio_file]
    out = subprocess.check_output(args, stderr=DEVNULL)
    is_text = True
    reconized_text = ""
    words = []

    # Parse ugly output
    for line in out.split('\n'):
        if '!!!' in line:
            continue
        if '<s>' in line:
            is_text = False
        if is_text:
            reconized_text += " " + line
        if '</s>' in line:
            is_text = True
        if not is_text:
            data = line.split(' ')
            word = data[0].strip('(0123456789)')
            start = float(data[1])
            end = float(data[2])
            if word.isalpha():
                words.append((word, start, end))

    # Remove unreconized word
    known_words = align(reconized_text.upper(), transcript)
    i = 0
    res_words = []
    for word in known_words:
        if i == len(words):
            break
        while i < len(words) and word != words[i][0].upper():
            i += 1
        if i < len(words):
            res_words.append(words[i])

    return res_words

def save_audio(words, speaker_id, audio_file):
    for word, start, end in words:

        # Get or create word
        word_obj = Session.query(Word).filter_by(word=word).first()
        if not word_obj:
            word_obj = Word(word=word)
            Session.add(word_obj)

        # Add audio
        Session.add(Audio(
            word=word_obj.word,
            audio_file=audio_file,
            start=start,
            end=end,
            speaker_id=speaker_id
        ))
    Session.commit()
    print("Saved {} audios ".format(len(words)), end="")

def read_trans(filename):
    res = []
    with open(filename) as f:
        for line in f:
            data = line.split(' ')
            number = data[0].split('-')[2]
            trans = " ".join(data[1:]).strip()
            trans = "".join([c for c in trans if c != "'"])
            res.append((number, trans))
    return res

def async_job(audio_file, transcript, speaker_id):
    print("Doing {}".format(audio_file))
    time = datetime.datetime.now()
    words = read_audio(audio_file, transcript)
    save_audio(words, speaker_id, audio_file)
    print("in {} seconds".format((datetime.datetime.now() - time).seconds))

if __name__ == '__main__':
    pool = Pool(processes=4)  # start 4 worker processes

    for speaker_id in os.listdir(BASEDIR):
        path = os.path.join(BASEDIR, speaker_id)
        for book_id in os.listdir(path):
            new_path = os.path.join(path, book_id)
            transcripts = read_trans(os.path.join(new_path, speaker_id + '-' + book_id + '.trans.txt'))
            for number, trans in transcripts:
                audio_file = os.path.join(new_path, '{}-{}-{}.flac.wav'.format(speaker_id, book_id, number))
                pool.apply_async(async_job, (audio_file, trans, speaker_id))

    pool.close()
    pool.join()
