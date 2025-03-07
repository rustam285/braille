import pygame
from pygame.locals import *
import sys
import json
import random
from resources import letters, images
import pyttsx3

# Константы
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 70, 225)
GRAY = (200, 200, 200)

# Загрузка базы данных учеников
def load_students():
    try:
        with open('students.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохранение базы данных учеников
def save_students(students):
    with open('students.json', 'w', encoding='utf-8') as file:
        json.dump(students, file, ensure_ascii=False, indent=4)

class BrailleApp:
    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.init_variables()
        self.init_tts()
        self.students = load_students()  # Загружаем базу данных учеников
        self.dictation_mode = False  # Режим диктанта
        self.current_student_id = None  # ID текущего ученика

    def init_pygame(self):
        pygame.init()
        pygame.mixer.init()

    def init_screen(self):
        screen_info = pygame.display.Info()
        self.W = int(screen_info.current_w * 0.75)  # 75% от ширины экрана
        self.H = int(screen_info.current_h * 0.8)   # 80% от высоты экрана
        self.sc = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

    def init_variables(self):
        self.pin = 0
        self.s_word = []
        self.update_positions()

    def init_tts(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("voice", "russian")

    def update_positions(self):
        """Обновляет координаты элементов в зависимости от размера окна"""
        self.circle_radius = int(self.W * 0.05)
        self.circle_positions = [
            (int(self.W * 0.09), int(self.H * 0.15)),  # ЛВ
            (int(self.W * 0.09), int(self.H * 0.5)),   # ЛВ
            (int(self.W * 0.09), int(self.H * 0.85)),  # ЛН
            (int(self.W * 0.27), int(self.H * 0.15)),  # ПВ
            (int(self.W * 0.27), int(self.H * 0.5)),   # ПС
            (int(self.W * 0.27), int(self.H * 0.85))   # ПН
        ]
        self.letter_start_x = int(self.W * 0.35)
        self.letter_start_y = int(self.H * 0.01)

    def clear_win(self):
        self.sc.fill(GRAY)

    def clear_braille_dots(self):
        """Очищает только кружки, не трогая слово на экране"""
        for pos in self.circle_positions:
            pygame.draw.circle(self.sc, GRAY, pos, self.circle_radius)

    def get_letter_symbol(self, pin):
        """Возвращает текстовое представление буквы по её коду"""
        letter_map = {
            1: 'А', 11: 'Б', 111010: 'В', 11011: 'Г', 11001: 'Д',
            10001: 'Е', 100001: 'Ё', 11010: 'Ж', 110101: 'З', 1010: 'И',
            101111: 'Й', 101: 'К', 111: 'Л', 1101: 'М', 11101: 'Н',
            10101: 'О', 1111: 'П', 10111: 'Р', 1110: 'С', 11110: 'Т',
            100101: 'У', 1011: 'Ф', 10011: 'Х', 1001: 'Ц', 11111: 'Ч',
            110001: 'Ш', 101101: 'Щ', 110111: 'Ъ', 101110: 'Ы', 111110: 'Ь',
            101010: 'Э', 110011: 'Ю', 101011: 'Я', 0: ' '
        }
        return letter_map.get(pin, '?')  # '?' если символ не найден

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == VIDEORESIZE:
                self.handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
        return True

    def quit(self):
        pygame.quit()
        sys.exit()

    def handle_resize(self, event):
        self.W, self.H = event.w, event.h
        self.sc = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.update_positions()

    def handle_keydown(self, event):
        """Обрабатывает нажатия клавиш и рисует кружки"""
        key_map = {
            K_KP7: (1, 0),   K_KP8: (1000, 3),
            K_KP4: (10, 1),  K_KP5: (10000, 4),
            K_KP1: (100, 2), K_KP2: (100000, 5)
        }

        if event.key in key_map:
            value, idx = key_map[event.key]
            self.pin += value
            pygame.draw.circle(self.sc, BLUE, self.circle_positions[idx], self.circle_radius)

        elif event.key == K_KP_ENTER:
            self.handle_enter_key()

        elif event.key == K_KP_PERIOD:
            self.handle_phrase_output()

        elif event.key == K_KP_MINUS:
            print("".join([char for _, char in self.s_word]))

        elif event.key == K_KP_PLUS:
            self.handle_plus_key()

        elif event.key == K_KP0:
            self.clear_win()
            self.s_word.clear()
            self.pin = 0

        elif event.key == K_SPACE:  # Переход в режим диктанта
            self.dictation_mode = True
            self.engine.say("Включен режим диктанта")
            self.engine.runAndWait()
            self.start_dictation()

    def start_dictation(self):
        """Запуск режима диктанта"""
        # Запрос ID ученика
        self.engine.say("Введите код ученика")
        self.engine.runAndWait()
        student_id = input("Введите код ученика: ").strip()

        if student_id in self.students:
            self.current_student_id = student_id
            self.engine.say(f"Ученик {student_id} найден.")
            self.check_completed_dictations()
        else:
            self.engine.say("Ученик не найден. Создаем нового ученика.")
            self.students[student_id] = {}
            self.current_student_id = student_id
            save_students(self.students)

        self.run_dictation()

    def check_completed_dictations(self):
        """Проверка пройденных диктантов"""
        student_data = self.students[self.current_student_id]
        completed_letters = list(student_data.keys())
        if completed_letters:
            self.engine.say(f"Вы прошли диктанты на следующие буквы: {', '.join(completed_letters)}")
        else:
            self.engine.say("Вы еще не прошли ни одного диктанта.")
        self.engine.runAndWait()

    def run_dictation(self):
        """Запуск диктанта"""
        from dictionaries import letters_for_dictations, dictations

        for letter in letters_for_dictations:
            if letter not in self.students[self.current_student_id]:
                self.engine.say(f"Теперь у вас диктант на букву {letter}.")
                self.engine.runAndWait()
                self.run_letter_dictation(letter)

    def run_letter_dictation(self, letter):
        """Запуск диктанта для конкретной буквы"""
        from dictionaries import dictations

        words = dictations[letter]
        random.shuffle(words)  # Перемешиваем слова

        for word in words:
            self.engine.say(f"Наберите слово {word}")
            self.engine.runAndWait()
            user_input = input().strip().lower()
            if user_input == word:
                self.engine.say("Правильно!")
            else:
                self.engine.say("Неправильно!")
            self.engine.runAndWait()

    def handle_enter_key(self):
        if self.pin in letters:
            letters[self.pin].play_sound()
        else:
            letters[-1].play_sound()
            print(letters, self.pin)
            self.clear_braille_dots()
            self.pin = 0

    def handle_phrase_output(self):
        """Собирает всю фразу из массива букв и выводит в консоль"""
        phrase = "".join([char for _, char in self.s_word])
        if phrase:
            self.engine.say(phrase)
            self.engine.runAndWait()

    def handle_plus_key(self):
        """Добавляет букву в массив s_word и отображает её на экране"""
        if self.pin in letters:
            letter = letters[self.pin]
            letter.play_sound()
            letter_symbol = self.get_letter_symbol(self.pin)

            # Сохраняем конкретное изображение буквы
            letter_image = images.get(self.pin)  # Получаем изображение по ключу
            if letter_image:  # Если изображение найдено
                self.s_word.append((letter_image, letter_symbol))

                self.clear_win()

                # Отображаем все буквы
                x, y = self.letter_start_x, self.letter_start_y
                for img, char in self.s_word:
                    self.sc.blit(img, (x, y))
                    letter_width, letter_height = img.get_size()
                    x += letter_width + 5
                    if x > self.W - letter_width:
                        x, y = self.letter_start_x, y + letter_height + 5

                self.pin = 0

    def run(self):
        self.clear_win()
        while self.handle_events():
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    app = BrailleApp()
    app.run()