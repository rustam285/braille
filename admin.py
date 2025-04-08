import pygame
import json
import sys

# Константы
WIDTH, HEIGHT = 800, 600
LEFT_PANEL_WIDTH = 250
FONT_SIZE = 24

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (173, 216, 230)

# Загрузка базы
with open("students_db.json", encoding="utf-8") as f:
    students_db = json.load(f)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Прогресс учеников")
font = pygame.font.SysFont(None, FONT_SIZE)

clock = pygame.time.Clock()

selected_student = None
scroll_offset = 0

# Получаем список ID учеников
student_ids = list(students_db.keys())

running = True
while running:
    screen.fill(WHITE)

    # Левая панель — список ID
    pygame.draw.rect(screen, GRAY, (0, 0, LEFT_PANEL_WIDTH, HEIGHT))

    y = 10
    for i, student_id in enumerate(student_ids):
        rect = pygame.Rect(10, y, LEFT_PANEL_WIDTH - 20, FONT_SIZE + 10)
        color = BLUE if student_id == selected_student else WHITE
        pygame.draw.rect(screen, color, rect)

        text = font.render(student_id, True, BLACK)
        screen.blit(text, (rect.x + 5, rect.y + 5))
        y += FONT_SIZE + 15

    # Правая панель — прогресс ученика
    if selected_student:
        x = LEFT_PANEL_WIDTH + 20
        y = 20
        student_data = students_db[selected_student]
        for date, dictations in sorted(student_data.items()):
            date_text = font.render(f"{date}", True, BLACK)
            screen.blit(date_text, (x, y))
            y += FONT_SIZE + 5

            for dictation_name, info in dictations.items():
                summary = f"  {dictation_name}: Ошибок {info['errors']}, Оценка {info['grade']}"
                d_text = font.render(summary, True, BLACK)
                screen.blit(d_text, (x + 10, y))
                y += FONT_SIZE + 5

                if info['mistakes']:
                    mistakes = ", ".join(info['mistakes'])
                    m_text = font.render(f"    Ошибки: {mistakes}", True, BLACK)
                    screen.blit(m_text, (x + 20, y))
                    y += FONT_SIZE + 5

            y += 10

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x < LEFT_PANEL_WIDTH:
                clicked_index = mouse_y // (FONT_SIZE + 15)
                if clicked_index < len(student_ids):
                    selected_student = student_ids[clicked_index]

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
