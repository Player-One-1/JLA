import pandas as pd
import PySimpleGUI as sg
import os
import sqlite3
import datetime
import random
#%%

LEVELS_TIMINGS = {-1:"0s",0:"0s",1:"1h",2:"12h",3:"1d",4:"2d",5:"4d",6:"7d",7:"14d",8:"4w",9:"8w",10:"26w"}
MINIMUM_INTERVAL = 5
MAXIMUM_INTERVAL = 10

def convert_to_hiragana(string:str):
    """function converts string to hiragana.
    It really converts only last set of letters in hiragana character, but when applies after ever character, it is enough.
    !!!to do: Complete the 4 length dictionary. Currently I ad a 4 letter combination whenever encountered, only one so far.
    """
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
                    "shi": "し", "chi": "ち", 'tsu':'つ'
                }
    DICTIONARY_4 = {"sshu" : "っしゅ"}

    if string[-4:] in DICTIONARY_4:
        updated_value = string[:-4] + DICTIONARY_4[string[-4:]]    
    elif string[-3:] in DICTIONARY_3:
        updated_value = string[:-3] + DICTIONARY_3[string[-3:]]
    elif string[-2:] in DICTIONARY_2:
        updated_value = string[:-2] + DICTIONARY_2[string[-2:]]
    elif string[-1:] in DICTIONARY_1:
        updated_value = string[:-1] + DICTIONARY_1[string[-1:]]
    else:
        updated_value = string
    return updated_value

def fetch_data_from_db(con):
    """Gets data from database. 
    In case of db not-set-up, it creates required table.
    Function supposed to run several times, whenever refreshed data is necessary"""
    cur = con.cursor()
    cur.execute("create table if not exists data(id, kanji, reading, meaning, folder, is_active, level_kanji, next_review_kanji, level_translate, next_review_translate)")
    con.commit()
    data = pd.read_sql("select * from data",con, index_col="id", parse_dates=('next_review_kanji', 'next_review_translate'))
    return data

class DatabaseUpdater:
    def __init__(self,con):
        self.con = con
        self.update_stats = {}
        self.data = fetch_data_from_db(con)
        self.vocabulary = DatabaseUpdater.read_vocabulary_from_text_files()

    def read_vocabulary_from_text_files():
        """Read vocabulary from text files in vocabulary folder.
        does some basic cleaning on the file. Much can be improved here.
        Intended to run only once, when updating database."""
        def read_single_vocabulary_file(fname):
            df = pd.read_csv("vocabulary\\" + fname).fillna("")
            df['kanji'] = df['kanji'].str.strip()
            df['reading'] = df['reading'].str.strip()
            df['meaning'] = df['meaning'].str.replace("​","")
            df = df.assign(folder = fname[:-4])
            return df
        
        vocabulary = pd.concat([read_single_vocabulary_file(fname) for fname in os.listdir('vocabulary')] )
        vocabulary.index = vocabulary['kanji'] + "#" + vocabulary['reading']
        vocabulary.index.name = "id"
        if not vocabulary.index.is_unique:
            print(vocabulary.index.duplicated(keep=False))
            raise TypeError("duplicate vocabulary identified. Please fix.") 
        return vocabulary

    def upload_missing_vocabulary(self):
        missing_indexes = self.vocabulary.index.difference(self.data.index)
        upload = self.vocabulary.loc[missing_indexes]
        upload = upload.assign(is_active = True,
                            level_kanji = 0,
                            next_review_kanji = datetime.datetime.now() , 
                            level_translate = 0,
                            next_review_translate =  datetime.datetime.now()
                            )
        upload.to_sql('data',self.con, if_exists = 'append')
        self.update_stats['added'] = len(upload)

    def deactivate_excessive_vocabulary(self):
        excessive_indexes = self.data[self.data["is_active"]==1].index.difference(self.vocabulary.index)
        cur = self.con.cursor()
        for index in excessive_indexes:
            cur.execute("update data set is_active = False where id = '{}'".format(index))
        self.con.commit()
        self.update_stats['deactivated'] = len(excessive_indexes)

    def reactivate_returning_vocabulary(self):
        returning_indexes = self.data[self.data['is_active'] == False].index.intersection(self.vocabulary.index)
        cur = self.con.cursor()
        for index in returning_indexes:
            cur.execute("update data set is_active = True where id = '{}'".format(index))
        self.con.commit()
        self.update_stats['reactivated'] = len(returning_indexes)

    def update_meanings(self):
        tmp = pd.concat([self.data["meaning"],self.vocabulary['meaning']], axis=1)
        tmp.columns = ['data', 'vocabulary']
        tmp = tmp[(tmp['data'] != tmp['vocabulary']) &(~tmp['data'].isna()) &(~tmp['vocabulary'].isna())]
        to_update_indexes = tmp.index

        cur = self.con.cursor()
        for index in to_update_indexes:
            cur.execute("update data set meaning = '{}' where id = '{}'".format(self.vocabulary.loc[index, 'meaning'],index))
        self.con.commit()
        self.update_stats['updated'] = len(to_update_indexes)

    def run_update(self):
        self.upload_missing_vocabulary()
        self.deactivate_excessive_vocabulary()
        self.reactivate_returning_vocabulary()
        self.update_meanings()

#%%
class KanjiCheck:
    def __init__(self,id) -> None:
        self.id = id
        self.kanji = data.loc[id,'kanji']
        self.reading = data.loc[id,'reading']
        self.meaning = data.loc[id,'meaning']
        self.level = data.loc[id,'level_kanji']
        self.next_review = data.loc[id,'next_review_kanji']

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
            if event == "Ok":
                self.stop = False
                break   

            if event == sg.WIN_CLOSED or event == "Cancel":
                self.stop = True
                break
            
            if event == "kana_input":
                window["kana_input"].update(convert_to_hiragana(values['kana_input']))

            if event == "kana_input" + "_Enter":
                window['meaning_input'].set_focus()

            if event == "meaning_input" + "_Enter":
                event = "Ok"
                self.stop = False
                break
        window.close()
        self.kana_input = values['kana_input']
        self.meaning_input = values['meaning_input']

    def CheckCorectness(self):
        self.kana_correct = (self.kana_input in self.reading.split("/")) and self.kana_input != ""
        self.meaning_correct = (self.meaning_input.lower() in self.meaning.lower().split("/")) and self.meaning_input != ""

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
        if (self.meaning_correct and self.kana_correct):
            self.level = min(10, self.level + 1)
        else:
            self.level = max(-1, self.level -1 -(self.level>3))
        
        self.next_review = (datetime.datetime.now() + pd.Timedelta(LEVELS_TIMINGS[self.level])).replace(minute=0, second=0, microsecond=1)

        sql = "Update data set level_kanji = {}, next_review_kanji = '{}' where id = '{}'".format(self.level, self.next_review, self.id)
        cur = con.cursor()
        cur.execute(sql)
        cur.close()
        con.commit()

def RunKanjiChecking():
    kanji_check_selected_id = data[(data['next_review_kanji'] < datetime.datetime.now()) & (data['kanji'] != '') & data["is_active"]].index
    KanjiChecks = [KanjiCheck(i) for i in kanji_check_selected_id]
    random.shuffle(KanjiChecks)
    while KanjiChecks:
        current_item = KanjiChecks[0]
        current_item.AskInWindow()
        if current_item.stop:
            break

        current_item.CheckCorectness()
        if not (current_item.meaning_correct and current_item.kana_correct):
            current_item.Error_Window()
        
        current_item.UpdateLevel(con)
        if (current_item.meaning_correct and current_item.kana_correct):
            KanjiChecks = KanjiChecks[1:]
        else:
            i = random.randint(MINIMUM_INTERVAL,MAXIMUM_INTERVAL)
            KanjiChecks = KanjiChecks[1:i] + [KanjiChecks[0]] + KanjiChecks[i:]

#%%
class MeaningCheck:
    def __init__(self,id) -> None:
        self.id = id
        self.reading = data.loc[id,'reading']
        self.meaning = data.loc[id,'meaning']
        self.level = data.loc[id,'level_translate']
        self.next_review = data.loc[id,'next_review_translate']    

    def AskInWindow(self):
        layout = [  [sg.Text(self.meaning, font=('Arial Bold', 80), text_color='white', background_color='purple', justification='center')],     # Part 2 - The Layout
                [sg.Input(key="kana_input", enable_events=True, font = ('Arial Bold', 20) , size=(20,10))],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

        # Create the window
        window = sg.Window('JLA', layout, background_color="Purple", finalize=True)
        window['kana_input'].bind("<Return>", "_Enter")

        window.force_focus()
        window['kana_input'].set_focus()

        # Display and interact with the Window
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == "Ok":
                self.stop = False
                break   

            if event == sg.WIN_CLOSED or event == "Cancel":
                self.stop = True
                break
            
            if event == "kana_input":
                window["kana_input"].update(convert_to_hiragana(values['kana_input']))

            if event == "kana_input" + "_Enter":
                event = "Ok"
                self.stop = False
                break
        window.close()
        self.kana_input = values['kana_input']

    def CheckCorectness(self):
        self.kana_correct = (self.kana_input.lower() in self.reading.lower().split("/")) and self.kana_input != ""
    
    def Error_Window(self):
        layout = [[sg.Text(self.meaning, font=('Arial Bold', 80), text_color='white', background_color='purple', justification='center')],
                  [sg.Text("reading wrong X: "+ self.kana_input, text_color="Red", font=('Arial Bold', 20), background_color="white"), sg.Button("Show",key="show_kana"), sg.Text("",key="kana", font=('Arial Bold', 20), background_color="white", text_color="Black")]
                  
                  ]
        layout.append([sg.Button('Ok'),sg.Button('Force Correct') ])
        window = sg.Window('JLA Error Window', layout, background_color="Purple", finalize=True)      # Part 3 - Window Defintion
        window.force_focus()

        while True:
            
            event, values = window.read()
            if event == "Ok" or event == sg.WIN_CLOSED:
                break
            if event == "show_kana":
                window["kana"].update(self.reading)
            if event == 'Force Correct':
                self.kana_correct = True
                break
        window.close()

    def UpdateLevel(self, con):
        if self.kana_correct:
            self.level = min(10, self.level + 1)
        else:
            self.level = max(-1, self.level -1 - (self.level>3))
        
        self.next_review = (datetime.datetime.now() + pd.Timedelta(LEVELS_TIMINGS[self.level])).replace(minute=0, second=0, microsecond=1)

        sql = "Update data set level_translate = {}, next_review_translate = '{}' where id = '{}'".format(self.level, self.next_review, self.id)
        cur = con.cursor()
        cur.execute(sql)
        cur.close()
        con.commit()

class MeaningChecker:
    def __init__(self,data,con) -> None:
            self.data = data
            self.con = con
            self.selected_ids = data[ (data['next_review_translate'] < datetime.datetime.now()) & ~data['reading'].isnull() & data["is_active"]].index
            self.len = len(self.selected_ids)
    
    def run(self):
        MeaningChecks = [MeaningCheck(id, self.data, self.con) for id in self.selected_ids]
    

def RunMeaningCheck():
    Meaning_check_selected_id = data[ (data['next_review_translate'] < datetime.datetime.now()) & ~data['reading'].isnull() & data["is_active"]].index
    MeaningChecks = [MeaningCheck(id) for id in Meaning_check_selected_id]
    random.shuffle(MeaningChecks)
    while MeaningChecks:
        current_item = MeaningChecks[0]
        current_item.AskInWindow()
        if current_item.stop:
            break

        current_item.CheckCorectness()
        if not current_item.kana_correct:
            current_item.Error_Window()
        
        current_item.UpdateLevel(con)
        if current_item.kana_correct:
            MeaningChecks = MeaningChecks[1:]
        else:
            i = random.randint(MINIMUM_INTERVAL,MAXIMUM_INTERVAL)
            MeaningChecks = MeaningChecks[1:i] + [MeaningChecks[0]] + MeaningChecks[i:]

#%%
def CalculateCohorts(data):
    cohorts = pd.DataFrame(index = range(0,11))
    cohorts['level_kanji'] = data['level_kanji'].value_counts()
    cohorts['level_translate'] = data['level_translate'].value_counts()
    cohorts = cohorts.fillna(0)
    cohorts = cohorts.astype(int)
    cohorts.index.name = "level"
    cohorts = cohorts.reset_index()
    return cohorts
    

#%%
def Main_Window(con,data):
    kanji_backlog = str(len(data[ (data['next_review_kanji'] < datetime.datetime.now()) & (data['kanji'] != '') & data["is_active"]].index))
    translate_backlog = str(len(data[ (data['next_review_translate'] < datetime.datetime.now()) & ~data['reading'].isnull() & data["is_active"] ].index))
    cohorts = CalculateCohorts(data)

    layout = [[sg.Text("items: " + kanji_backlog, font=('Arial Bold', 30)), sg.Button("Kanji", font=('Arial Bold', 30))]
              ,[sg.Text("items: " + translate_backlog, font=('Arial Bold', 30)), sg.Button("Translate", font=('Arial Bold', 30))]
              ,[sg.Button("Close"), [sg.Table(values=cohorts.values.tolist(), headings=cohorts.columns.tolist(), size=(1000,11))]]
            ]
    
    window = sg.Window("Japanese Learning App",layout)

    event, values = window.read()
    if event == "Kanji":
        RunKanjiChecking()

    if event == "Translate":
        RunMeaningCheck()
    window.close()

    return event

def run_db_update(con):
    updater = DatabaseUpdater(con)
    updater.run_update()
    msg = "Database Updated.\nRecords added: {}\nRecords deactivated: {}\nRecords reactivated: {}\nRecords updated: {}".format(updater.update_stats['added'], updater.update_stats['deactivated'], updater.update_stats['reactivated'],updater.update_stats['updated'])
    sg.popup(msg)


#%%

if __name__ == "__main__":
    con = sqlite3.connect("database.db")
    run_db_update(con)

    while True:
        data = fetch_data_from_db(con)
        event = Main_Window(con,data)
        if event == "Close" or event == None:
            break


# %%
