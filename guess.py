import pygame
import random
import sys
from pygame.locals import *

# PyGame ni ishga tushirish
pygame.init()

# O'yin konfiguratsiyasi
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# Ranglar
BACKGROUND_COLOR = (25, 25, 40)
TEXT_COLOR = (240, 240, 255)
ACCENT_COLOR = (70, 130, 180)
CORRECT_COLOR = (100, 200, 100)
WRONG_COLOR = (220, 80, 80)
BUTTON_COLOR = (60, 100, 150)
BUTTON_HOVER_COLOR = (80, 130, 190)
GALLOWS_COLOR = (200, 180, 140)

# So'zlar bazasi (turli mavzularda)
WORDS = {
    "Texnologiya": ["KOMPYUTER", "PROGRAMMA", "INTERNET", "TELEFON", "ROBOT", "ALGORITM"],
    "Hayvonlar": ["KIYIK", "ARSLON", "FIL", "ZEBRA", "TIMSOH", "BALIQ"],
    "Mamlakatlar": ["OZBEKISTON", "AMERIKA", "ROSSIYA", "YAPONIYA", "KANADA", "BRAZILIYA"],
    "Fan": ["KIMYO", "FIZIKA", "BIOLOGIYA", "ASTRONOMIYA", "MATEMATIKA", "GEOLOGIYA"],
    "Mevalar": ["OLMA", "BANAN", "APELSIN", "ANOR", "UZUM", "QOVUN"]
}

# Fontlar
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Arial", 60, bold=True)
WORD_FONT = pygame.font.SysFont("Arial", 48, bold=True)
LETTER_FONT = pygame.font.SysFont("Arial", 32)
INFO_FONT = pygame.font.SysFont("Arial", 26)
CATEGORY_FONT = pygame.font.SysFont("Arial", 28, bold=True)
BUTTON_FONT = pygame.font.SysFont("Arial", 28)

class HangmanGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hangman O'yini")
        self.clock = pygame.time.Clock()
        self.reset_game()
        
        # O'yin holatlari: "menu", "playing", "game_over"
        self.game_state = "menu"
        self.selected_category = "Texnologiya"
        
        # Gallows qismlari (7 xato uchun)
        self.gallows_parts = [
            self.draw_base,      # 0 - poydevor
            self.draw_pole,      # 1 - ustun
            self.draw_beam,      # 2 - tirgak
            self.draw_rope,      # 3 - arqon
            self.draw_head,      # 4 - bosh
            self.draw_body,      # 5 - badan
            self.draw_left_arm,  # 6 - chap qo'l
            self.draw_right_arm, # 7 - o'ng qo'l
            self.draw_left_leg,  # 8 - chap oyoq
            self.draw_right_leg  # 9 - o'ng oyoq
        ]
        
    def reset_game(self):
        """O'yinni qayta boshlash"""
        # So'z va kategoriyani tanlash
        self.category = random.choice(list(WORDS.keys()))
        self.word = random.choice(WORDS[self.category]).upper()
        
        # O'yin holatlari
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.max_wrong_guesses = 9
        self.game_won = False
        self.game_over = False
        
        # O'yin statistikasi
        self.games_played = 0
        self.games_won = 0
    
    def draw_gallows(self):
        """Gallows (darvoza) ni chizish"""
        # Gallows maydoni
        gallows_area = pygame.Rect(50, 150, 350, 400)
        
        # Fon
        pygame.draw.rect(self.screen, (35, 35, 50), gallows_area)
        pygame.draw.rect(self.screen, (60, 60, 80), gallows_area, 3)
        
        # Gallows qismlarini chizish (xatolar soniga qarab)
        for i in range(self.wrong_guesses):
            if i < len(self.gallows_parts):
                self.gallows_parts[i]()
    
    def draw_base(self):
        """Poydevor"""
        pygame.draw.rect(self.screen, GALLOWS_COLOR, (150, 450, 150, 20))
    
    def draw_pole(self):
        """Ustun"""
        pygame.draw.rect(self.screen, GALLOWS_COLOR, (220, 200, 20, 250))
    
    def draw_beam(self):
        """Tirgak"""
        pygame.draw.rect(self.screen, GALLOWS_COLOR, (220, 200, 100, 20))
    
    def draw_rope(self):
        """Arqon"""
        pygame.draw.line(self.screen, (160, 140, 100), (315, 200), (315, 230), 3)
    
    def draw_head(self):
        """Bosh"""
        pygame.draw.circle(self.screen, (220, 200, 180), (315, 250), 20, 3)
        # Ko'zlar
        pygame.draw.circle(self.screen, (50, 50, 100), (310, 245), 3)
        pygame.draw.circle(self.screen, (50, 50, 100), (320, 245), 3)
        # Og'iz (achchiq)
        pygame.draw.arc(self.screen, (200, 100, 100), (310, 255, 10, 10), 0, 3.14, 2)
    
    def draw_body(self):
        """Badan"""
        pygame.draw.line(self.screen, (220, 200, 180), (315, 270), (315, 340), 3)
    
    def draw_left_arm(self):
        """Chap qo'l"""
        pygame.draw.line(self.screen, (220, 200, 180), (315, 290), (290, 320), 3)
    
    def draw_right_arm(self):
        """O'ng qo'l"""
        pygame.draw.line(self.screen, (220, 200, 180), (315, 290), (340, 320), 3)
    
    def draw_left_leg(self):
        """Chap oyoq"""
        pygame.draw.line(self.screen, (220, 200, 180), (315, 340), (290, 380), 3)
    
    def draw_right_leg(self):
        """O'ng oyoq"""
        pygame.draw.line(self.screen, (220, 200, 180), (315, 340), (340, 380), 3)
    
    def draw_word_display(self):
        """Topilishi kerak bo'lgan so'zni ko'rsatish"""
        # So'zni harflarga ajratib, to'g'ri taxmin qilinganlarini ko'rsatish
        display_text = ""
        for letter in self.word:
            if letter in self.guessed_letters or self.game_over:
                display_text += letter + " "
            else:
                display_text += "_ "
        
        # So'zni ekranga chiqarish
        word_surface = WORD_FONT.render(display_text, True, TEXT_COLOR)
        word_rect = word_surface.get_rect(center=(SCREEN_WIDTH // 2 + 100, 300))
        self.screen.blit(word_surface, word_rect)
        
        # Chiziq chizish
        pygame.draw.line(self.screen, ACCENT_COLOR, 
                        (word_rect.left, word_rect.bottom + 10),
                        (word_rect.right, word_rect.bottom + 10), 3)
        
        # Kategoriyani ko'rsatish
        category_text = f"Kategoriya: {self.category}"
        category_surface = CATEGORY_FONT.render(category_text, True, ACCENT_COLOR)
        category_rect = category_surface.get_rect(center=(SCREEN_WIDTH // 2 + 100, 250))
        self.screen.blit(category_surface, category_rect)
    
    def draw_letter_buttons(self):
        """Harflar tugmachalari"""
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        # Harflar maydoni
        letters_area = pygame.Rect(450, 350, 400, 250)
        pygame.draw.rect(self.screen, (35, 35, 50), letters_area)
        pygame.draw.rect(self.screen, (60, 60, 80), letters_area, 3)
        
        # Harflarni chizish
        for i, letter in enumerate(letters):
            row = i // 9
            col = i % 9
            
            x = 470 + col * 45
            y = 370 + row * 50
            
            # Tugma holati
            if letter in self.guessed_letters:
                if letter in self.word:
                    color = CORRECT_COLOR
                else:
                    color = WRONG_COLOR
                border_color = color
            else:
                color = (60, 60, 80)
                border_color = (100, 100, 120)
            
            # Tugmani chizish
            button_rect = pygame.Rect(x, y, 35, 35)
            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=5)
            
            # Harfni chizish
            letter_surface = LETTER_FONT.render(letter, True, TEXT_COLOR)
            letter_rect = letter_surface.get_rect(center=button_rect.center)
            self.screen.blit(letter_surface, letter_rect)
    
    def draw_game_info(self):
        """O'yin ma'lumotlarini ko'rsatish"""
        # Xatolar soni
        wrong_text = f"Xatolar: {self.wrong_guesses} / {self.max_wrong_guesses}"
        wrong_surface = INFO_FONT.render(wrong_text, True, TEXT_COLOR)
        wrong_rect = wrong_surface.get_rect(topleft=(450, 150))
        self.screen.blit(wrong_surface, wrong_rect)
        
        # Taxmin qilingan harflar
        guessed_text = "Taxmin qilingan harflar: " + ", ".join(self.guessed_letters) if self.guessed_letters else "Hech qanday harf taxmin qilinmagan"
        guessed_surface = INFO_FONT.render(guessed_text, True, TEXT_COLOR)
        guessed_rect = guessed_surface.get_rect(topleft=(450, 190))
        self.screen.blit(guessed_surface, guessed_rect)
        
        # O'yin statistikasi
        stats_text = f"O'yinlar: {self.games_played} | Yutuqlar: {self.games_won}"
        stats_surface = INFO_FONT.render(stats_text, True, ACCENT_COLOR)
        stats_rect = stats_surface.get_rect(topleft=(450, 230))
        self.screen.blit(stats_surface, stats_rect)
    
    def draw_game_over_screen(self):
        """O'yin tugaganda ekran"""
        # Fon qorong'ulash
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Natija xabari
        if self.game_won:
            result_text = "TABRIKLAYMIZ! SIZ YUTDINGIZ!"
            result_color = CORRECT_COLOR
        else:
            result_text = "O'YIN TUGADI!"
            result_color = WRONG_COLOR
            
        result_surface = TITLE_FONT.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(result_surface, result_rect)
        
        # To'g'ri so'z
        word_text = f"So'z: {self.word}"
        word_surface = WORD_FONT.render(word_text, True, TEXT_COLOR)
        word_rect = word_surface.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(word_surface, word_rect)
        
        # Qayta o'ynash tugmasi
        replay_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, replay_button, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, replay_button, 3, border_radius=10)
        
        replay_text = "YANA O'YNAISH" if self.game_won else "QAYTA URINISH"
        replay_surface = BUTTON_FONT.render(replay_text, True, TEXT_COLOR)
        replay_rect = replay_surface.get_rect(center=replay_button.center)
        self.screen.blit(replay_surface, replay_rect)
        
        # Menyuga qaytish tugmasi
        menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 430, 300, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, menu_button, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, menu_button, 3, border_radius=10)
        
        menu_text = "ASOSIY MENYU"
        menu_surface = BUTTON_FONT.render(menu_text, True, TEXT_COLOR)
        menu_rect = menu_surface.get_rect(center=menu_button.center)
        self.screen.blit(menu_surface, menu_rect)
        
        return replay_button, menu_button
    
    def draw_menu_screen(self):
        """Asosiy menyu ekrani"""
        # Sarlavha
        title_surface = TITLE_FONT.render("HANGMAN O'YINI", True, ACCENT_COLOR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # O'yin qoidalari
        rules = [
            "O'yin qoidalari:",
            "1. Tasodifiy tanlangan so'zni topish kerak",
            "2. Har bir harfni alohida taxmin qiling",
            "3. Noto'g'ri harflar gallows qurilishiga olib keladi",
            "4. Gallows to'liq qurilishidan oldin so'zni toping!"
        ]
        
        for i, rule in enumerate(rules):
            color = ACCENT_COLOR if i == 0 else TEXT_COLOR
            rule_surface = INFO_FONT.render(rule, True, color)
            rule_rect = rule_surface.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 40))
            self.screen.blit(rule_surface, rule_rect)
        
        # Kategoriya tanlash
        category_text = "Kategoriyani tanlang:"
        category_surface = CATEGORY_FONT.render(category_text, True, TEXT_COLOR)
        category_rect = category_surface.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(category_surface, category_rect)
        
        # Kategoriya tugmalari
        categories = list(WORDS.keys())
        category_buttons = []
        
        for i, category in enumerate(categories):
            button_rect = pygame.Rect(200 + i * 150, 430, 140, 50)
            
            # Tugma rangini belgilash (tanlangan kategoriya)
            if category == self.selected_category:
                color = ACCENT_COLOR
                border_color = TEXT_COLOR
            else:
                color = BUTTON_COLOR
                border_color = ACCENT_COLOR
            
            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, button_rect, 3, border_radius=8)
            
            # Kategoriya nomi
            cat_surface = BUTTON_FONT.render(category, True, TEXT_COLOR)
            cat_rect = cat_surface.get_rect(center=button_rect.center)
            self.screen.blit(cat_surface, cat_rect)
            
            category_buttons.append((button_rect, category))
        
        # Boshlash tugmasi
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 520, 300, 70)
        pygame.draw.rect(self.screen, BUTTON_COLOR, start_button, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, start_button, 4, border_radius=10)
        
        start_text = "O'YINNI BOSHLASH"
        start_surface = BUTTON_FONT.render(start_text, True, TEXT_COLOR)
        start_rect = start_surface.get_rect(center=start_button.center)
        self.screen.blit(start_surface, start_rect)
        
        return category_buttons, start_button
    
    def check_letter(self, letter):
        """Har bir harfni tekshirish"""
        if letter not in self.guessed_letters and not self.game_over:
            self.guessed_letters.append(letter)
            
            if letter not in self.word:
                self.wrong_guesses += 1
            
            # O'yin tugashini tekshirish
            self.check_game_status()
    
    def check_game_status(self):
        """O'yin holatini tekshirish"""
        # So'zni topishni tekshirish
        word_found = all(letter in self.guessed_letters for letter in self.word)
        
        if word_found:
            self.game_won = True
            self.game_over = True
            self.games_played += 1
            self.games_won += 1
        elif self.wrong_guesses >= self.max_wrong_guesses:
            self.game_won = False
            self.game_over = True
            self.games_played += 1
    
    def handle_click(self, pos):
        """Foydalanuvchi bosgan joyni aniqlash"""
        if self.game_state == "menu":
            category_buttons, start_button = self.draw_menu_screen()
            
            # Kategoriya tugmalarini tekshirish
            for button_rect, category in category_buttons:
                if button_rect.collidepoint(pos):
                    self.selected_category = category
                    return
            
            # Boshlash tugmasini tekshirish
            if start_button.collidepoint(pos):
                self.category = self.selected_category
                self.word = random.choice(WORDS[self.category]).upper()
                self.game_state = "playing"
                self.reset_game()
        
        elif self.game_state == "playing":
            # Harf tugmalarini tekshirish
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for i, letter in enumerate(letters):
                row = i // 9
                col = i % 9
                
                x = 470 + col * 45
                y = 370 + row * 50
                
                button_rect = pygame.Rect(x, y, 35, 35)
                if button_rect.collidepoint(pos):
                    self.check_letter(letter)
        
        elif self.game_state == "game_over":
            replay_button, menu_button = self.draw_game_over_screen()
            
            if replay_button.collidepoint(pos):
                self.reset_game()
                self.game_state = "playing"
            elif menu_button.collidepoint(pos):
                self.game_state = "menu"
    
    def run(self):
        """Asosiy o'yin tsikli"""
        running = True
        
        while running:
            # Hodisalarni qayta ishlash
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if self.game_state == "playing" and not self.game_over:
                        if event.key >= K_a and event.key <= K_z:
                            letter = chr(event.key - 32)  # Katta harfga o'tkazish
                            self.check_letter(letter)
                        elif event.key == K_RETURN and self.game_over:
                            self.reset_game()
                    elif event.key == K_ESCAPE:
                        self.game_state = "menu"
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Chap sichqoncha bosish
                        self.handle_click(event.pos)
            
            # Ekranni tozalash
            self.screen.fill(BACKGROUND_COLOR)
            
            # O'yin holatiga qarab ekran chizish
            if self.game_state == "menu":
                self.draw_menu_screen()
            elif self.game_state == "playing":
                # Gallows chizish
                self.draw_gallows()
                
                # So'zni ko'rsatish
                self.draw_word_display()
                
                # Harf tugmalari
                self.draw_letter_buttons()
                
                # O'yin ma'lumotlari
                self.draw_game_info()
                
                # O'yin tugaganda
                if self.game_over:
                    self.game_state = "game_over"
            elif self.game_state == "game_over":
                self.draw_gallows()
                self.draw_word_display()
                self.draw_game_info()
                self.draw_game_over_screen()
            
            # O'yin nomi va muallif
            author_text = "Python Hangman O'yini"
            author_surface = INFO_FONT.render(author_text, True, (100, 100, 120))
            author_rect = author_surface.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
            self.screen.blit(author_surface, author_rect)
            
            # Ekranni yangilash
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# O'yinni ishga tushirish
if __name__ == "__main__":
    game = HangmanGame()
    game.run()