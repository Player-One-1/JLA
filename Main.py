import pandas as pd
import PySimpleGUI as sg
import os
import sqlite3
import datetime
import random
#%%
LEVELS_TIMINGS = {-1:"0s",0:"0s",1:"1h",2:"2h",3:"6h",4:"1d",5:"2d",6:"4d",7:"7d",8:"4w",9:"8w",10:"26w"}

def ConverToHiragana(string:str):
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
                    "shi": "し", "chi": "ち"
                }

    if string[-3:] in DICTIONARY_3:
        updated_value = string[:-3] + DICTIONARY_3[string[-3:]]

    elif string[-2:] in DICTIONARY_2:
        updated_value = string[:-2] + DICTIONARY_2[string[-2:]]

    elif string[-1:] in DICTIONARY_1:
        updated_value = string[:-1] + DICTIONARY_1[string[-1:]]
    else:
        updated_value = string
    return updated_value

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
        cur.execute("create table if not exists stats(id, level_kanji, next_review_kanji, level_translate, next_review_translate)")
        stats = pd.read_sql("select * from stats",con, index_col="id", parse_dates=('next_review_kanji', 'next_review_translate'))
        return stats

    def UpdateStatsForMissingVocabulary(stats, vocabulary, con):
        missing_items = vocabulary.index.difference(stats.index)
        df = pd.DataFrame(index=missing_items).assign(
                    level_kanji = 0, next_review_kanji = datetime.datetime.now(), level_translate = 0, next_review_translate = datetime.datetime.now()
                                                    )
        df.index.name = 'id'
        df.to_sql('stats', con, if_exists='append')
        stats = pd.concat([stats, df])
        return stats
                                                
    con = sqlite3.connect("database.db")
    vocabulary = OpenVocabulary()
    stats = OpenStats(con)
    stats = UpdateStatsForMissingVocabulary(stats, vocabulary, con)

    return stats,vocabulary, con

#%%
class KanjiCheck:
    def __init__(self,id) -> None:
        self.id = id
        self.kanji = vocabulary.loc[id,'kanji']
        self.reading = vocabulary.loc[id,'reading']
        self.meaning = vocabulary.loc[id,'meaning']
        self.level = stats.loc[id,'level_kanji']
        self.next_review = stats.loc[id,'next_review_kanji']

    def AskInWindow(self):
        layout = [  [sg.Text(self.kanji, font=('Arial Bold', 80), text_color='white', background_color='purple', justification='center')],     # Part 2 - The Layout
                [sg.Input(key="kana_input", enable_events=True, font = ('Arial Bold', 20) , size=(20,10))],
                [sg.Input(key="meaning_input", font= ('Arial Bold', 20), size=(20,10))],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

        # Create the window
        window = sg.Window('JLA', layout, background_color="Purple", finalize=True)      # Part 3 - Window Defintion
        window['kana_input'].bind("<Return>", "_Enter")
        window['meaning_input'].bind("<Return>", "_Enter")
        window.force_focus()
        window['kana_input'].set_focus()

        # Display and interact with the Window
        while True:
            
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == "Ok" or event == sg.WIN_CLOSED:
                break                 

            if event == "kana_input":
                window["kana_input"].update(ConverToHiragana(values['kana_input']))

            if event == "kana_input" + "_Enter":
                window['meaning_input'].set_focus()

            if event == "meaning_input" + "_Enter":
                event = "Ok"
                break
        window.close()
        self.kana_input = values['kana_input']
        self.meaning_input = values['meaning_input']

        if event == "Ok":
            self.stop = False
        else:
            self.stop = True

    def CheckCorectness(self):
        self.kana_correct = self.kana_input in self.reading.split("/") and self.kana_input != ""
        self.meaning_correct = self.meaning_input.lower() in self.meaning_input.lower().split("/") and self.meaning_input

    def Error_Window(self):
        layout = [[sg.Text(self.kanji, font=('Arial Bold', 80), text_color='white', background_color='purple', justification='center')]]
        
        if self.kana_correct:
            layout.append([sg.Text("✓", text_color="Green", font=('Arial Bold', 20), background_color="white"), sg.Button("Show",key="show_kana"), sg.Text("",key="kana", font=('Arial Bold', 20), background_color="white", text_color="Black")])
        else:
            layout.append([sg.Text("reading wrong X: "+ self.kana_input, text_color="Red", font=('Arial Bold', 20), background_color="white"), sg.Button("Show",key="show_kana"), sg.Text("",key="kana", font=('Arial Bold', 20), background_color="white", text_color="Black")])

        if self.meaning_correct:
            layout.append([sg.Text("✓", text_color="Green", font=('Arial Bold', 20), background_color="white"), sg.Button("Show",key="show_meaning"), sg.Text("",key="meaning", font=('Arial Bold', 20), background_color="white", text_color="Black")])
        else:
            layout.append([sg.Text("meaning wrong X: "+ self.meaning_input, text_color="Red", font=('Arial Bold', 20), background_color="white"), sg.Button("Show",key="show_meaning"), sg.Text("",key="meaning", font=('Arial Bold', 20), background_color="white", text_color="Black")])

        layout.append([sg.Button('Ok'),sg.Button('Force Correct') ])
        window = sg.Window('JLA Error Window', layout, background_color="Purple", finalize=True)      # Part 3 - Window Defintion
        window.force_focus()

        while True:
            
            event, values = window.read()
            if event == "Ok" or event == sg.WIN_CLOSED:
                break
            if event == "show_kana":
                window["kana"].update(self.reading)
            if event == "show_meaning":
                window['meaning'].update(self.meaning)
            if event == 'Force Correct':
                self.kana_correct = True
                self.meaning_correct = True
                break
        window.close()

    def UpdateLevel(self, con):
        if (a.meaning_correct and a.kana_correct):
            self.level = min(10, self.level + 1)
        else:
            self.level = max(-1, self.level -1)
        
        self.next_review = (datetime.datetime.now() + pd.Timedelta(LEVELS_TIMINGS[self.level])).replace(minute=0, second=0, microsecond=1)

        sql = "Update stats set level_kanji = {}, next_review_kanji = '{}' where id = '{}'".format(self.level, self.next_review, self.id)
        cur = con.cursor()
        cur.execute(sql)
        cur.close()
        con.commit()
        return sql

#%%

if __name__ == "__main__":
    stats,vocabulary, con = InitiateProgram()
    stats_filtered = stats[ (stats['next_review_kanji'] < datetime.datetime.now()) & ~vocabulary['kanji'].isnull()]
    KanjiChecks = [KanjiCheck(i) for i in stats_filtered.index]
    random.shuffle(KanjiChecks)

    while KanjiChecks:
        a = KanjiChecks[0]
        a.AskInWindow()
        a.CheckCorectness()
        if not (a.meaning_correct and a.kana_correct):
            a.Error_Window()
        
        a.UpdateLevel(con)
        if (a.meaning_correct and a.kana_correct):
            KanjiChecks = KanjiChecks[1:]
        else:
            random.shuffle(KanjiChecks)



# %%
