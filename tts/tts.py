import sys

import numpy
from scipy.io import wavfile
from sqlalchemy.sql import func

from models import Session, Audio

FREQ = 16000


def read(filename):
    rate, data = wavfile.read(filename)
    return rate, data


def no_sound(time):
    return numpy.array([0 for _ in range(int(time * FREQ))])


def generate_word_sound(word):
    audio_obj = Session.query(Audio).filter_by(word=word).order_by(func.random()).first()
    rate, data = read(audio_obj.audio_file)
    sound = data[int(rate * audio_obj.start):int(rate * audio_obj.end + 1)]
    return sound


def generate_speech(string):
    words = string.lower().split()
    sound = no_sound(0.01)
    for word in words:
        sound = numpy.concatenate((sound, generate_word_sound(word), no_sound(0.005)))

    wavfile.write('out.wav', FREQ, numpy.array(sound, dtype='int16'))


if __name__ == '__main__':
    generate_speech(sys.argv[1])
