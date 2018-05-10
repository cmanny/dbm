import csv
from collections import Counter
import os
from os import listdir
from os.path import isfile, join
import json
from scipy.io import wavfile
from random import shuffle
from signal_utils import spectrogram
import numpy as np
from queue import Queue
import itertools
import enchant
import sklearn


# @UTF8
# @PID:	11312/t-00002178-1
# @Begin
# @Languages:	eng
# @Participants:	PAR Participant, INV Investigator
# @ID:	eng|UPMC|PAR|58;|female|Control||Participant|30||
# @ID:	eng|UPMC|INV|||||Investigator|||
# @Media:	002-0c, audio

class Interview(object):

    # Example is prepped here

    def __init__(self, pid, chat_file, audio_file, scores):
        self.pid = pid
        self.chat_file = chat_file
        self.audio_file = audio_file
        self.scores = scores
        for k, v in scores.items():
            if v == "":
                scores[k] = '0'
        self.loaded = False

    def _audio_spectrogram(self, wav_segment, fft_size, win_size, thresh):
        data = wav_spectrogram = spectrogram(
            wav_segment.astype('float64'),
            fft_size=fft_size,
            step_size=win_size,
            log=True,
            thresh=thresh
        )
        return data

    def audio_segments(self, fft_size, win_size, thresh):
        print(self.audio_file)
        wav = wavfile.read(self.audio_file)
        self.sample_rate = wav[0]
        adj = self.sample_rate // 1000
        self.audio = wav[1].astype('float64')
        segments = []
        lines = self.text_segments()
        if lines == None:
            return []
        times = []
        for line in lines:
            times.append((line[1], line[2]))
        for st, et in times:
            if not (st.isdigit() and et.isdigit()):
                continue
            stadj = int(st) * adj
            etadj = int(et) * adj
            audio_segment = self.audio[stadj : etadj]
            if len(audio_segment.shape) > 1:
                audio_segment = np.sum(audio_segment, axis=1) // 2
            try:
                segments.append(
                    self._audio_spectrogram(
                        audio_segment,
                        fft_size, win_size, thresh
                    )
                )
            except:
                print(audio_segment.shape)
        return segments

    def text_segments(self):
        self.cf = CHATFile(self.chat_file, self.pid)
        return self.cf._get_chat_lines()

    def __repr__(self):
        return "id: {}, cha_file: {}, aud_file: {}, scores: {}".format(self.pid, self.chat_file, self.audio_file, self.scores)

class CHATFile(object):

    # Chat file functionality

    def __init__(self, file_path, pid):
        self.encoding = "UTF8"
        self.pid = None
        self.begin = None
        self.languages = None
        self.participant = None
        self.inv = None
        self.file_path = file_path

    def _get_chat_lines(self):
        with open(self.file_path) as f:
            c = Counter()
            self.lines = []
            my_dict = DictWithPWL("en_US", "mywords.txt")
            my_checker = SpellChecker(my_dict)
            for line in f:
                if line[:4] == "*PAR":
                    inline = line[6:line.find('\x15')]
                    print(inline)
                    try:
                        st, et = line[line.find('\x15') + 1: -2].split('_')
                        self.lines.append((inline, st, et))
                    except:
                        return None
                    words = inline.split(" ")
            return self.lines

    def _get_usable_words(self):
        lines = self._get_chat_lines()
        edited_lines = []
        d = enchant.Dict("en_US")
        for line in lines:
            words = lines.split(" ")
            rebuilt_line = []
            for w in words:
                if d.check(w) or w in ["&hm", "&uh", "&um", "[//]", "[/]", "."]:
                    rebuild_line.append("w")
            edited_lines.append(rebuilt_line)
        return edited_lines

    def tokens(self):
        return [x.split() for x in self.lines]

class DementiaBankData(object):

    COLUMNS = """
    id,idate,testigo,year,yearache,pwml,basedx,dx1,dx2,dx3,changedx,intertdx,changdx2,possible,probable,groupdx,curdx1,curdx2,curdx3,currdx4,entryage,onsetage,sex,race,educ,mmsegrp,mms,mattis,cdrfs,blessed,hamilton,htotal,hmtotal,nyu,ddate,psychot1,visit2da,hamilt2,hrs2tota,hrs2m,cdr2,bless2,nyu2,cerad2,mmse2,mattis2,visit3,hamilt3,hrs3tota,hrs3m,cdr3,bless3,nyu3,cerad3,mmse3,mattis3,visit4,hamilt4,hrs4tota,hrs4m,cdr4,bless4,nyu4,cerad4,mmse4,mattis4,visit5,hamilt5,hrs5tota,hrs5m,cdr5,bless5,nyu5,cerad5,mmse5,mattis5,visit6,hamilt6,hrs6tota,hrs6m,cdr6,bless6,nyu6,cerad6,mmse6,mattis6,visit7,hamilt7,hrs7tota,hrs7mo,cdr7,blessed7,nyu7,cerad7,mmse7,mattis7,lastdate,lastdx,lhamilto,lasthrs,lastcdr,lastnyu,eps,lastmms,lamattis,lastbless"""


    def __init__(self,
                audio_folder='./audio',
                transcript_folder='./transcripts',
                datasheet_csv='datasheet.csv'):
        self.audio_folder = audio_folder
        self.transcript_folder = transcript_folder
        self.datasheet_csv = datasheet_csv
        self.columns = [x.strip() for x in self.COLUMNS.split(",")]
        self._open_csv()

    def _open_csv(self):
        with open(self.datasheet_csv) as f:
            self.datareader = csv.reader(f)
            self.data_dicts = [
                {k: v for k, v in zip(self.columns, row)}
                for row in list(self.datareader)[1:]
            ]
        self.control = [x for x in self.data_dicts if x["basedx"] == '8']
        self.dementia = [x for x in self.data_dicts if x["basedx"] != '8']

    def generate_interviews(self, p_info, types, tf, af):
        sk = [
            ["mms", "mattis", "cdrfs", "blessed", "hamilton", "htotal", "hmtotal", "nyu"],
            ["mmse{}", "mattis{}", "cdr{}", "bless{}", "hamilt{}", "hrs{}tota", "hrs{}m", "nyu{}"]
        ]
        examples = []
        for p in p_info:
            i = int(p["id"])
            for j in range(6):
                for folder in types:
                    acc = folder[0]
                    cha_fn = "{:0>2d}-{}{}.cha".format(i, j, acc if folder != "cookie" else "")
                    aud_fn = "{:0>2d}-{}{}.mp3.wav".format(i, j, acc)
                    cha_path = os.path.join(tf, folder, cha_fn)
                    aud_path = os.path.join(af, folder, aud_fn)
                    cha_path = cha_path if isfile(cha_path) else None
                    aud_path = aud_path if isfile(aud_path) else None
                    scores = {
                        sk[0][ski]: p[sk[1][ski].format(j + 1) if j > 0 else sk[0][ski]]
                        for ski in range(len(sk[0]))
                    }
                    if cha_path != None and aud_path != None:
                        examples.append(Interview(i, cha_path, aud_path, scores))
        return examples

    def load_all_interviews(self):
        control_interviews = self.generate_interviews(
            self.control,
            ["cookie", "fluency"],
            os.path.join(self.transcript_folder, "Control"),
            os.path.join(self.audio_folder, "Control")
        )

        dementia_interviews = self.generate_interviews(
            self.dementia,
            ["cookie", "fluency", "sentence", "recall"],
            os.path.join(self.transcript_folder, "Dementia"),
            os.path.join(self.audio_folder, "Dementia")
        )

        return control_interviews + dementia_interviews

    def batch_generator(self,
        batch_size,
        subset='train',
        audio_parameters=(2048, 2048, 4)):
        while True:
            shuffled_list = self.load_all_interviews()
            shuffle(shuffled_list)
            unused_queue = Queue()
            for x in shuffled_list:
                unused_queue.put(x)
            ex_overflow = []
            while not unused_queue.empty():
                if unused_queue.qsize() < batch_size:
                    break
                interviews = [unused_queue.get() for _ in range(batch_size)]
                pool = ex_overflow + [
                    (y, np.array([float(v) for _, v in x.scores.items()]))
                    for x in interviews
                    for y in x.audio_segments(*audio_parameters)
                ]
                items = []
                while len(pool) > 32:
                    yield pool[:32]
                    pool = pool[32:]
                ex_overflow = list(pool)
        yield None

class SVMCounter(object):

    def __init__(self):
        clf = svm.SVC()

<<<<<<< HEAD
    def fit(X, y):
        pass
=======
    def _train(self, examples):
        X = np.zeros((len(examples), self.n_features))
        y = [np.zeros((len(examples),)) for _ in range(8)]
        for i, x in enumerate(examples):
            ohvx = self._one_hot(x)
            scores = np.array([int(round(float(v))) for k, v in x.scores.items()])
            for j in range(8):
                y[j][i] = scores[j]
        for i in range(8):
            self.lr[i].fit(X, y[i])
>>>>>>> fa33ee249c0e90f97be89a15fd8b06e4f22d1c6c



if __name__ == "__main__":
    # stop word removal
    # tfidf
    # text vectorizer
    dbm = DementiaBankData()
    examples = dbm.load_all_examples()
    for x in examples:
        print(x._get_usable_words())
