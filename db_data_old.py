import csv
from collections import Counter
import os
from os import listdir
from os.path import isfile, join
import json

class Utterance(object):

    def __init__(self, raw_sentence, spkr_type='participant'):
        self.spkr_type = spkr_type
        self.raw_sentence = raw_sentence
        self._parse_sentence

class CHATFile(object):

    def __init__(self, file_path):
        with open(file_path) as f:
            self._parse_chat(f)

    def _parse_chat(self, f):
        self.c = Counter()
        for line in f:
            if line[:4] == "*PAR":
                inline = line[4:line.find('.')]
                words = inline.split(" ")
                self.c = self.c + Counter(words)
        return self.c

class CookieFile(object):

    def __init__(self, file_path):
        with open(file_path) as f:
            self._parse_chat(f)

    def _parse_chat(self, f):
        self.c = Counter()
        self.lines = []
        self.question = "Describe what is going on in the picture."
        for line in f:
            if line[:4] == "*PAR":
                inline = line[6:line.find('.')]
                self.lines.append(inline)
                words = inline.split(" ")
                self.c = self.c + Counter(words)
        return self.c

    def extras(self, idd, diag, visit, dx1):
        self.idd = idd
        self.diag = diag
        self.visit = visit
        self.dx1 = dx1

    def dicty(self):
        return {
            "participant_id": self.idd,
            "diagnosis": self.diag,
            "question": self.question,
            "response": self.lines,
            "repeat": self.visit,
            "dx1": self.dx1
        }

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

    def get_example(self, par_id, t, visit):
        t_path = 2
        ret = DBExample(
            par_id,
            t,
            visit,
            t_path,
            a_path
        )


    def compute_breakers(self):
        all_cookies = []
        dementia_cookie = os.path.join(
            self.transcript_folder,
            "Dementia",
            "cookie"
        )
        control_cookie = os.path.join(
            self.transcript_folder,
            "Control",
            "cookie"
        )

        lookup = {
            "0": "Robot",
            "1": "ProbableAD",
            "2": "PossibleAD",
            "3": "Vascular",
            "4": "Parkinson",
            "5": "Complains",
            "8": "Control",
            "6": "MCI",
            "7": "MCI",
            "9": "olivopontocerebellar_degeneration"
        }

        for ex in self.dementia:
            i = int(ex["id"])
            diagnosis = lookup[ex["basedx"]]
            for j in range(4):
                fn = "{:0>2d}-{}.cha".format(i, j)
                full = os.path.join(self.transcript_folder, "Dementia", "cookie", fn)
                if isfile(full):
                    cf = CookieFile(full)
                    cf.extras(i, diagnosis, j, int(ex["dx1"]))
                    all_cookies.append(cf.dicty())

        for ex in self.control:
            i = int(ex["id"])
            diagnosis = "Control"
            for j in range(4):
                fn = "{:0>2d}-{}.cha".format(i, j)
                full = os.path.join(self.transcript_folder, "Control", "cookie", fn)
                if isfile(full):
                    cf = CookieFile(full)
                    cf.extras(i, diagnosis, j, int(ex["dx1"]))
                    all_cookies.append(cf.dicty())

        for x in all_cookies:
            print(x)
            print()

        with open('result.json', 'w') as fp:
            json.dump(all_cookies, fp)


        # cc = Counter()
        # dc = Counter()
        #
        # for f in control_files:
        #     cf = CHATFile(f)
        #     cc = cc + cf.c
        # for f in dementia_files:
        #     cf = CHATFile(f)
        #     dc = dc + cf.c

        # l = ["&hm", "&uh", "&um", "[//]", "[/]", "+//"]
        # print("Control\n")
        # print("non word strings: {}".format(len([x for x in cc if x and x[0] == "&"])))
        # for x in l:
        #     print("{}:{}".format(x, cc[x]))
        # print("distinct words, {}".format(len([c for c in cc if c.isalpha()])))
        # print("\nDementia\n")
        # print("non word strings: {}".format(len([x for x in dc if x and x[0] == "&"])))
        # for x in l:
        #     print("{}:{}".format(x, dc[x]))
        # print("distinct words, {}".format(len([x for x in dc if x.isalpha()])))

        # dementia_fluency = os.path.join(
        #     self.transcript_folder,
        #     "Dementia",
        #     "fluency"
        # )
        # fluency_files = [
        #     os.path.join(self.transcript_folder, "Dementia", "fluency", f)
        #     for f in listdir(dementia_fluency) if isfile(join(dementia_fluency, f))
        # ]
        # fc = Counter()
        # for f in fluency_files:
        #     cf = CHATFile(f)
        #     fc = fc + cf.c
        # print("\nDementia Fluency\n")
        # print("non word strings: {}".format(len([x for x in fc if x and x[0] == "&"])))
        # for x in l:
        #     print("{}:{}".format(x, fc[x]))
        # print("distinct words, {}".format(len([x for x in fc if x.isalpha()])))
        #
        #
        # dementia_recall = os.path.join(
        #     self.transcript_folder,
        #     "Dementia",
        #     "recall"
        # )
        # recall_files = [
        #     os.path.join(self.transcript_folder, "Dementia", "recall", f)
        #     for f in listdir(dementia_recall) if isfile(join(dementia_recall, f))
        # ]
        # rc = Counter()
        # for f in recall_files:
        #     cf = CHATFile(f)
        #     rc = rc + cf.c
        # print("\nDementia Recall\n")
        # print("non word strings: {}".format(len([x for x in rc if x and x[0] == "&"])))
        # for x in l:
        #     print("{}:{}".format(x, rc[x]))
        # print("distinct words, {}".format(len([x for x in rc if x.isalpha()])))
        #
        # dementia_sentence = os.path.join(
        #     self.transcript_folder,
        #     "Dementia",
        #     "sentence"
        # )
        # sentence_files = [
        #     os.path.join(self.transcript_folder, "Dementia", "sentence", f)
        #     for f in listdir(dementia_sentence) if isfile(join(dementia_sentence, f))
        # ]
        # sc = Counter()
        # for f in sentence_files:
        #     cf = CHATFile(f)
        #     sc = sc + cf.c
        # print("\nDementia Sentence\n")
        # print("non word strings: {}".format(len([x for x in sc if x and x[0] == "&"])))
        # for x in l:
        #     print("{}:{}".format(x, sc[x]))
        # print("distinct words, {}".format(len([x for x in sc if x.isalpha()])))



if __name__ == "__main__":
    dbm = DementiaBankData()
    dbm.compute_breakers()
#
#     import csv
#     from collections import Counter
#     import os
#     from os import listdir
#     from os.path import isfile, join
#
#
#     class DementiaBankData(object):
#
#         COLUMNS = """
#         id,idate,testigo,year,yearache,pwml,basedx,dx1,dx2,dx3,changedx,intertdx,changdx2,possible,probable,groupdx,curdx1,curdx2,curdx3,currdx4,entryage,onsetage,sex,race,educ,mmsegrp,mms,mattis,cdrfs,blessed,hamilton,htotal,hmtotal,nyu,ddate,psychot1,visit2da,hamilt2,hrs2tota,hrs2m,cdr2,bless2,nyu2,cerad2,mmse2,mattis2,visit3,hamilt3,hrs3tota,hrs3m,cdr3,bless3,nyu3,cerad3,mmse3,mattis3,visit4,hamilt4,hrs4tota,hrs4m,cdr4,bless4,nyu4,cerad4,mmse4,mattis4,visit5,hamilt5,hrs5tota,hrs5m,cdr5,bless5,nyu5,cerad5,mmse5,mattis5,visit6,hamilt6,hrs6tota,hrs6m,cdr6,bless6,nyu6,cerad6,mmse6,mattis6,visit7,hamilt7,hrs7tota,hrs7mo,cdr7,blessed7,nyu7,cerad7,mmse7,mattis7,lastdate,lastdx,lhamilto,lasthrs,lastcdr,lastnyu,eps,lastmms,lamattis,lastbless"""
#
#
#         def __init__(self,
#                     audio_folder='./audio',
#                     transcript_folder='./transcripts',
#                     datasheet_csv='datasheet.csv'):
#             self.audio_folder = audio_folder
#             self.transcript_folder = transcript_folder
#             self.datasheet_csv = datasheet_csv
#             self.columns = [x.strip() for x in self.COLUMNS.split(",")]
#             self._open_csv()
#
#
#         def _open_csv(self):
#             with open(self.datasheet_csv) as f:
#                 self.datareader = csv.reader(f)
#                 self.data_dicts = [
#                     {k: v for k, v in zip(self.columns, row)}
#                     for row in list(self.datareader)[1:]
#                 ]
#             self.control = [x for x in self.data_dicts if x["basedx"] == '8']
#             self.dementia = [x for x in self.data_dicts if x["basedx"] != '8']
#
#         def get_example(self, par_id, t, visit):
#             t_path = 2
#             ret = DBExample(
#                 par_id,
#                 t,
#                 visit,
#                 t_path,
#                 a_path
#             )
#
#         def compute_breakers(self):
#             dementia_cookie = os.path.join(
#                 self.transcript_folder,
#                 "Dementia",
#                 "cookie"
#             )
#             control_cookie = os.path.join(
#                 self.transcript_folder,
#                 "Control",
#                 "cookie"
#             )
#             control_files = [
#                 os.path.join(self.transcript_folder, "Control", "cookie", f)
#                 for f in listdir(control_cookie) if isfile(join(control_cookie, f))
#             ]
#             dementia_files = [
#                 os.path.join(self.transcript_folder, "Dementia", "cookie", f)
#                 for f in listdir(dementia_cookie) if isfile(join(dementia_cookie, f))
#             ]
#
#             cc = Counter()
#             dc = Counter()
#             for f in control_files:
#                 cf = CHATFile(f)
#                 cc = cc + cf.c
#             for f in dementia_files:
#                 cf = CHATFile(f)
#                 dc = dc + cf.c
#
#             l = ["&hm", "&uh", "&um", "[//]", "[/]", "+//"]
#             print("Control\n")
#             print("non word strings: {}".format(len([x for x in cc if x and x[0] == "&"])))
#             for x in l:
#                 print("{}:{}".format(x, cc[x]))
#             print("distinct words, {}".format(len([c for c in cc if c.isalpha()])))
#             print("\nDementia\n")
#             print("non word strings: {}".format(len([x for x in dc if x and x[0] == "&"])))
#             for x in l:
#                 print("{}:{}".format(x, dc[x]))
#             print("distinct words, {}".format(len([x for x in dc if x.isalpha()])))
#
#             dementia_fluency = os.path.join(
#                 self.transcript_folder,
#                 "Dementia",
#                 "fluency"
#             )
#             fluency_files = [
#                 os.path.join(self.transcript_folder, "Dementia", "fluency", f)
#                 for f in listdir(dementia_fluency) if isfile(join(dementia_fluency, f))
#             ]
#             fc = Counter()
#             for f in fluency_files:
#                 cf = CHATFile(f)
#                 fc = fc + cf.c
#             print("\nDementia Fluency\n")
#             print("non word strings: {}".format(len([x for x in fc if x and x[0] == "&"])))
#             for x in l:
#                 print("{}:{}".format(x, fc[x]))
#             print("distinct words, {}".format(len([x for x in fc if x.isalpha()])))
#
#
#             dementia_recall = os.path.join(
#                 self.transcript_folder,
#                 "Dementia",
#                 "recall"
#             )
#             recall_files = [
#                 os.path.join(self.transcript_folder, "Dementia", "recall", f)
#                 for f in listdir(dementia_recall) if isfile(join(dementia_recall, f))
#             ]
#             rc = Counter()
#             for f in recall_files:
#                 cf = CHATFile(f)
#                 rc = rc + cf.c
#             print("\nDementia Recall\n")
#             print("non word strings: {}".format(len([x for x in rc if x and x[0] == "&"])))
#             for x in l:
#                 print("{}:{}".format(x, rc[x]))
#             print("distinct words, {}".format(len([x for x in rc if x.isalpha()])))
#
#             dementia_sentence = os.path.join(
#                 self.transcript_folder,
#                 "Dementia",
#                 "sentence"
#             )
#             sentence_files = [
#                 os.path.join(self.transcript_folder, "Dementia", "sentence", f)
#                 for f in listdir(dementia_sentence) if isfile(join(dementia_sentence, f))
#             ]
#             sc = Counter()
#             for f in sentence_files:
#                 cf = CHATFile(f)
#                 sc = sc + cf.c
#             print("\nDementia Sentence\n")
#             print("non word strings: {}".format(len([x for x in sc if x and x[0] == "&"])))
#             for x in l:
#                 print("{}:{}".format(x, sc[x]))
#             print("distinct words, {}".format(len([x for x in sc if x.isalpha()])))
#
#
#
#     if __name__ == "__main__":
#         dbm = DementiaBankData()
#         dbm.compute_breakers()
