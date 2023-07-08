import pandas as pd
import PySimpleGUI as sg
import os
import sqlite3
import datetime
from random import randint
#%%
DICTIONARY_1 = {"a": "あ", "i": "い", "u": "う", "e": "え", "o": "お"}
DICTIONARY_2 = {"ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
                "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
                "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
                "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
                "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
                "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",
                "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
                "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
                "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
                "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
                "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
                "ya": "や", "yu": "ゆ", "yo": "よ",
                "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
                "wa": "わ", "wo": "を",
                "nn": "ん",
                "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
}
DICTIONARY_3 = {"kka": "っか", "kki": "っき", "kku": "っく", "kke": "っけ", "kko": "っこ",
    "gga": "っが", "ggi": "っぎ", "ggu": "っぐ", "gge": "っげ", "ggo": "っご",
    "ssa": "っさ", "sshi": "っし", "ssu": "っす", "sse": "っせ", "sso": "っそ",
    "zza": "っざ", "jji": "っじ", "zzu": "っず", "zze": "っぜ", "zzo": "っぞ",
    "tta": "った", "cchi": "っち", "ttsu": "っつ", "tte": "って", "tto": "っと",
    "dda": "っだ", "ddi": "っぢ", "ddu": "っづ", "dde": "っで", "ddo": "っど",
    "nna": "っな", "nni": "っに", "nnu": "っぬ", "nne": "っね", "nno": "っの",
    "hha": "っは", "hhi": "っひ", "ffu": "っふ", "hhe": "っへ", "hho": "っほ",
    "bba": "っば", "bbi": "っび", "bbu": "っぶ", "bbe": "っべ", "bbo": "っぼ",
    "ppa": "っぱ", "ppi": "っぴ", "ppu": "っぷ", "ppe": "っぺ", "ppo": "っぽ",
    "mma": "っま", "mmi": "っみ", "mmu": "っむ", "mme": "っめ", "mmo": "っも",
    "yya": "っや", "yyu": "っゆ", "yyo": "っよ",
    "rra": "っら", "rri": "っり", "rru": "っる", "rre": "っれ", "rro": "っろ",
    "wwa": "っわ", "wwo": "っを",
    "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
    "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
    "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
    "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
    "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
    "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
    "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
    "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
    "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
}


def InitiateProgram():
    def OpenVocabulary():
        def ReadFile(fname):
            df = pd.read_csv("vocabulary\\" + fname)
            df.index = fname[:-4]+":" + df.index.astype(str)
            return df
        vocabulary = pd.concat([ReadFile(fname) for fname in os.listdir('vocabulary')] )
        return vocabulary
    
    def OpenStats(con):
        cur = con.cursor()
        cur.execute("create table if not exists stats(id, correct, incorrect, streak, last_review, next_review)")
        stats = pd.read_sql("select * from stats",con, index_col="id", parse_dates=('last_review', 'next_review'))
        return stats
    
    def UpdateStatsForMissingVocabulary(stats, vocabulary, con):
        missing_items = vocabulary.index.difference(stats.index)
        df = pd.DataFrame(index=missing_items).assign(
                   correct = 0, incorrect = 0, streak = 0, last_review = datetime.datetime.now(), next_review = datetime.datetime.now()
                                                    )
        df.index.name = 'id'
        df.to_sql('stats', con, if_exists='append')
        stats = pd.concat([stats, df])
        return stats
                                                    
    con = sqlite3.connect("database.db")
    vocabulary = OpenVocabulary()
    stats = OpenStats(con)
    stats = UpdateStatsForMissingVocabulary(stats, vocabulary, con)

i = randint(0,len(vocabulary)-1)

r = vocabulary.iloc[i]
# Define the window's contents
layout = [  [sg.Text(r['kanji'],size=(40, 1), font=('Arial Bold', 60))],     # Part 2 - The Layout
            [sg.Input(key="--1--", enable_events=True, font = ('Arial Bold', 30) )],
            [sg.Input(key="--2--")],
            [sg.Button('Ok')] ]

# Create the window
window = sg.Window('Window Title', layout)      # Part 3 - Window Defintion

# Display and interact with the Window
while True:
    
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    print(event)
    if event == "Ok" or event == sg.WIN_CLOSED:
        break                 

    if event == "--1--":
        if values["--1--"][-3:] in DICTIONARY_3:
            print("test")
            updated_value = values["--1--"][:-3] + DICTIONARY_3[values["--1--"][-3:]]
            window["--1--"].update(updated_value)

        elif values["--1--"][-2:] in DICTIONARY_2:
            print("test2")
            updated_value = values["--1--"][:-2] + DICTIONARY_2[values["--1--"][-2:]]
            window["--1--"].update(updated_value)

        elif values["--1--"][-1:] in DICTIONARY_1:
            print("tes3")
            updated_value = values["--1--"][:-1] + DICTIONARY_1[values["--1--"][-1:]]
            window["--1--"].update(updated_value)

 # Part 4 - Event loop or Window.read call


# Do something with the information gathered

if values["--1--"] == r['reading']:
    print("Ok, great success")
else:
    print("WRONG!!!")

# Finish up by removing from the screen
window.close()      
