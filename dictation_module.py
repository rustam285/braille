import pyttsx3
from dictionaries import letters_for_dictations, dictations

def say_phrase(phrase, speed=120):
    engine = pyttsx3.init()
    engine.setProperty("rate", speed)
    engine.setProperty("voice", "russian")
    engine.say(phrase)
    engine.runAndWait()

def check_answer(user_input, correct_answer, right_answer, wrong_answer):
    if user_input == correct_answer:
        say_phrase("Правильно!")
        return right_answer + 1, wrong_answer
    elif user_input == "стоп":
        say_phrase(f"Ваше количество правильных ответов {right_answer}")
        say_phrase(f"Ваше количество неправильных ответов {wrong_answer}")
        exit()
    else:
        say_phrase("Неправильно!")
        return right_answer, wrong_answer + 1

right_answer = 0
wrong_answer = 0

say_phrase("Чтобы остановить программу наберите слово СТОП", 240)

for letter in letters_for_dictations:
    if letter == "А":
        say_phrase("Наберите букву а")
        user_input = input().strip().lower()
        right_answer, wrong_answer = check_answer(user_input, "а", right_answer, wrong_answer)
    
    for word in dictations[letter]:
        say_phrase(f"Наберите слово {word}")
        user_input = input().strip().lower()
        right_answer, wrong_answer = check_answer(user_input, word, right_answer, wrong_answer)