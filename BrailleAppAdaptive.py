import pygame
from pygame.locals import *
import sys
import json
from resources import letters, images
import pyttsx3
from dictation_module import DictationModule

# Константы
FPS = 120
WHITE = (255, 255, 255)
BLUE = (0, 70, 225)
GRAY = (200, 200, 200)
DB_FILE = "students_db.json"

class BrailleApp:
    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.init_variables()
        self.init_tts()

    def init_pygame(self):
        pygame.init()
        pygame.mixer.init()

    def init_screen(self):
        screen_info = pygame.display.Info()
        self.W = int(screen_info.current_w * 0.75)
        self.H = int(screen_info.current_h * 0.8)
        self.sc = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

    def init_variables(self):
        self.pin = 0
        self.s_word = []
        self.mode = "free"  # "free" или "dictation"
        self.student_id = None
        self.dictation_module = None
        self.update_positions()

    def init_tts(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("voice", "russian")

    def update_positions(self):
        self.circle_radius = int(self.W * 0.05)
        self.circle_positions = [
            (int(self.W * 0.09), int(self.H * 0.15)),
            (int(self.W * 0.09), int(self.H * 0.5)),
            (int(self.W * 0.09), int(self.H * 0.85)),
            (int(self.W * 0.27), int(self.H * 0.15)),
            (int(self.W * 0.27), int(self.H * 0.5)),
            (int(self.W * 0.27), int(self.H * 0.85))
        ]
        self.letter_start_x = int(self.W * 0.35)
        self.letter_start_y = int(self.H * 0.01)

    def clear_win(self):
        self.sc.fill(GRAY)

    def switch_mode(self):
        if self.mode == "free":
            self.mode = "dictation"
            self.prompt_student_id()
        else:
            self.mode = "free"
            self.dictation_module = None
            self.student_id = None
            self.clear_win()

    def clear_braille_dots(self):
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

    def prompt_student_id(self):
        self.engine.say("Введите свой код ученика")
        self.engine.runAndWait()
        self.student_id = input("Введите код ученика: ")
        self.load_student_progress()
        self.dictation_module = DictationModule(self.student_id, self)
        self.dictation_module.start_dictation()

    def load_student_progress(self):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                self.student_data = json.load(f)
        except FileNotFoundError:
            self.student_data = {}
        
        if self.student_id not in self.student_data:
            self.student_data[self.student_id] = {}

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

        elif event.key == K_SPACE:
            self.switch_mode()

        elif event.key == K_KP_PLUS:
            self.handle_plus_key()

        elif event.key == K_KP0:
            self.clear_win()
            self.s_word.clear()
            self.pin = 0

        elif event.key == K_KP_MINUS:
            if self.mode == "free":
                print("".join([char for _, char in self.s_word]))
            elif self.mode == "dictation" and self.dictation_module:
                self.dictation_module.check_word("".join([char for _, char in self.s_word]).strip().lower())
                self.s_word.clear()
            
    def handle_enter_key(self):
        if self.pin in letters:
            letters[self.pin].play_sound()
        else:
            letters[-1].play_sound()
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