from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

s1 = """
AFTER GETTING TRANSFERRED HIS CAT IS TO THE CHARGE OF THE LORD MARK WALLACE WENT
ALONE TO THE CHAMBER OF MY MEMORY TO SEE WHETHER THE STATE OF HIS ONES WOULD
ALLOW HIM TO MARCH ON THE MORROW WHILE HE WAS YET THEY ARE AN INVITATION RIDE
FROM THE COUNTESS OF MAR
"""


s2 = """
AFTER HAVING TRANSFERRED HIS CAPTIVES TO THE CHARGE OF LORD MAR WALLACE
WENT ALONE TO THE CHAMBER OF MONTGOMERY TO SEE WHETHER THE STATE OF HIS WOUNDS
WOULD ALLOW HIM TO MARCH ON THE MORROW WHILE HE WAS YET THERE AN INVITATION
ARRIVED FROM THE COUNTESS OF MAR"""


def align(s1, s2):
    # Create sequences to be aligned.
    a = Sequence(s1.split())
    b = Sequence(s2.split())

    # Create a vocabulary and encode the sequences.
    v = Vocabulary()
    aEncoded = v.encodeSequence(a)
    bEncoded = v.encodeSequence(b)

    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(2, -1)
    aligner = GlobalSequenceAligner(scoring, -2)
    score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
    encoded = encodeds[0]
    alignment = v.decodeSequenceAlignment(encoded)
    correct_words = []
    offset = 0
    for i, (x, y) in enumerate(encoded):
        if x == y:
            correct_words.append(a[i - offset])
        elif x == 0:
            offset += 1

    return correct_words


if __name__ == '__main__':
    print(align(s1, s2))
