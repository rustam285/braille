import pyttsx3
import json
import datetime
from dictionaries import letters_for_dictations, dictations

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
        self.attempts = 3
        
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
        completed_letters = self.student_data[self.student_id][self.today].keys()
        if len(completed_letters) >= 2:
            self.say_phrase("Вы уже прошли два диктанта сегодня. Новые диктанты недоступны.")
            return iter([])
        
        available_letters = [letter for letter in letters_for_dictations if letter not in completed_letters]
        return iter(available_letters[:2])

    def start_dictation(self):
        self.next_letter()

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
            self.say_phrase("Диктант завершен.")
            self.current_letter = None
            self.current_word = None

    def next_word(self):
        if not hasattr(self, 'word_queue') or self.word_queue is None:
            self.next_letter()
            return
        try:
            self.current_word = next(self.word_queue)
            self.say_phrase(f"Наберите слово {self.current_word}")
        except StopIteration:
            self.next_letter()

    def check_word(self, user_word):
        if not self.current_word:
            return
        
        if user_word == self.current_word:
            self.say_phrase("Правильно!")
            self.update_student_progress(self.current_word, correct=True)
            self.reset_attempts()
            self.clear_win()
            self.next_word()
        else:
            self.attempts -= 1
            if self.attempts > 0:
                self.say_phrase(f"Неправильно! Осталось попыток: {self.attempts}")
                self.update_student_progress(self.current_word, correct=False, mistake=user_word)
            else:
                self.say_phrase("Неправильно! Попытки закончились. Переход к следующему слову.")
                self.update_student_progress(self.current_word, correct=False, mistake=user_word)
                self.reset_attempts()
                self.clear_win()
                self.next_word()

    def reset_attempts(self):
        self.attempts = 3

    def update_student_progress(self, word, correct, mistake=None):
        if self.current_letter not in self.student_data[self.student_id][self.today]:
            self.student_data[self.student_id][self.today][self.current_letter] = {
                "errors": 0,
                "mistakes": [],
                "grade": 10
            }

        if not correct:
            self.student_data[self.student_id][self.today][self.current_letter]["errors"] += 1
            self.student_data[self.student_id][self.today][self.current_letter]["mistakes"].append(mistake)
            self.student_data[self.student_id][self.today][self.current_letter]["grade"] = max(
                1, self.student_data[self.student_id][self.today][self.current_letter]["grade"] - 1
            )

        self.save_progress()