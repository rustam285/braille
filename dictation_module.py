import pyttsx3
import json
import datetime
import pygame
from dictionaries import letters_for_dictations, dictations, letter_code_map, sounds, play_sound
from resources import letters, words_for_dict

DB_FILE = "students_db.json"

class DictationModule:
    def __init__(self, student_id, braille_app):
        self.student_id = student_id
        self.braille_app = braille_app
        self.today = datetime.date.today().strftime("%d-%m-%Y")
        self.load_student_progress()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 120)
        self.engine.setProperty("voice", "russian")
        self.current_letter = None
        self.current_word = None
        self.dictation_queue = self.get_today_dictations()
        self.is_first_dictation = True  # Флаг для первого диктанта
        self.word_queue = None
        
    def load_student_progress(self):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                self.student_data = json.load(f)
        except FileNotFoundError:
            self.student_data = {}
        
        if self.student_id not in self.student_data:
            self.student_data[self.student_id] = {}
        
        if self.today not in self.student_data[self.student_id]:
            self.student_data[self.student_id][self.today] = {}

    def save_progress(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.student_data, f, ensure_ascii=False, indent=4)

    def say_phrase(self, phrase):
        self.engine.say(phrase)
        self.engine.runAndWait()

    def get_today_dictations(self):
        completed = self.student_data[self.student_id][self.today].keys()
        available = []
        
        # Проверяем начальный диктант
        if "Начальный диктант" not in completed:
            available.append("Начальный диктант")
        
        # Добавляем остальные буквы
        available.extend([letter for letter in letters_for_dictations 
                        if letter != "Начальный диктант" and letter not in completed])
        
        return iter(available)

    def clear_win(self):
        self.braille_app.clear_win()
        self.braille_app.s_word.clear()
        self.braille_app.pin = 0

    def next_letter(self):
        try:
            self.current_letter = next(self.dictation_queue)
            self.word_queue = iter(dictations[self.current_letter])
            self.next_word()
        except StopIteration:
            self.clear_win()
            play_sound(sounds[0])  # Звук завершения
            self.current_letter = None
            self.current_word = None

    def next_word(self):
        if not hasattr(self, 'word_queue') or self.word_queue is None:
            self.next_letter()
            return
        try:
            self.current_word = next(self.word_queue)
            # Проигрываем "наберите слово" + само слово
            pygame.time.delay(2500)
            play_sound(sounds[2])
            pygame.time.delay(2500)
            play_sound(words_for_dict[self.current_word])
        except StopIteration:
            self.next_letter()

    def check_word(self, user_word):
        if user_word.lower() == "стоп":
            play_sound(sounds[0])
            self.braille_app.clear_win()
            self.braille_app.s_word.clear()
            self.braille_app.pin = 0
            self.current_letter = None
            self.current_word = None
            return

        if not self.current_word:
            return

        if user_word == self.current_word:
            play_sound(sounds[5])
            self.update_student_progress(self.current_word, correct=True)
            self.next_word()
        else:
            play_sound(sounds[4])
            self.next_word()

        # Очистка экрана и задержка
        self.braille_app.clear_win()
        self.braille_app.s_word.clear()
        self.braille_app.pin = 0

    def update_student_progress(self, word, correct, mistake=None):
        # Используем "Начальный диктант" как ключ, если это первый диктант
        dictation_key = "Начальный диктант" if self.current_letter == "Начальный диктант" else self.current_letter

        if dictation_key not in self.student_data[self.student_id][self.today]:
            self.student_data[self.student_id][self.today][dictation_key] = {
                "errors": 0,
                "mistakes": [],
                "grade": 10
            }

        if not correct:
            self.student_data[self.student_id][self.today][dictation_key]["errors"] += 1
            self.student_data[self.student_id][self.today][dictation_key]["mistakes"].append(mistake)
            self.student_data[self.student_id][self.today][dictation_key]["grade"] = max(
                1, self.student_data[self.student_id][self.today][dictation_key]["grade"] - 1
            )

        self.save_progress()