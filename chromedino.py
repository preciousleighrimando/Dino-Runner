# !/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import random
import threading
import uuid  # <-- add
import secrets  # <-- add
import time  # <-- add

import pygame

pygame.init()

# Load button sound globally
BUTTON_SOUND = pygame.mixer.Sound(os.path.join("assets/Music", "button.mp3"))

if not os.path.exists("score.txt"):
    with open("score.txt", "w") as f:
        f.write("0\n")

# Global Constants

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1300
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

SCALE_FACTOR = 0.75  # Adjust as needed

def scale_image(image, factor):
    width = int(image.get_width() * factor)
    height = int(image.get_height() * factor)
    return pygame.transform.scale(image, (width, height))

pygame.display.set_caption("Chrome Dino Runner")

Ico = scale_image(pygame.image.load("assets/DinoWallpaper.png"), SCALE_FACTOR)
pygame.display.set_icon(Ico)

RUNNING = [
    scale_image(pygame.image.load(os.path.join("assets/Dino2", "DinoRun1.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Dino2", "DinoRun2.png")), SCALE_FACTOR),
]
JUMPING = scale_image(pygame.image.load(os.path.join("assets/Dino2", "DinoJump.png")), SCALE_FACTOR)
DUCKING = [
    scale_image(pygame.image.load(os.path.join("assets/Dino2", "DinoDuck1.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Dino2", "DinoDuck2.png")), SCALE_FACTOR),
]

SMALL_CACTUS = [
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus1.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus2.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus3.png")), SCALE_FACTOR),
]
LARGE_CACTUS = [
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus1.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus2.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus3.png")), SCALE_FACTOR),
]

CLOUD = scale_image(pygame.image.load(os.path.join("assets/Other", "Cloud.png")), SCALE_FACTOR)

BG = scale_image(pygame.image.load(os.path.join("assets/Level2/Ground2", "sand1.png")), SCALE_FACTOR)

FONT_COLOR=(0,0,0)

# Add a vertical offset constant among Global Constants
VERTICAL_OFFSET = 320

# Load BG animation frames (a1.png to a178.png) at startup
BG_ANIMATION_FRAMES = []

BG_ANIMATION_FRAME_COUNT = len(BG_ANIMATION_FRAMES)
BG_ANIMATION_FPS = 10  # ~10 frames per second (slower animation)
BG_ANIMATION_INTERVAL = int(1000 / BG_ANIMATION_FPS)

# At the top (after your imports), add a global font file path:
FONT_FILE = os.path.join("assets/Font", "monogram.ttf")

def draw_text_with_shadow(surface, text, font, color, pos, shadow_offset=(2,2), shadow_color=(0,0,0)):
    # Draw shadow
    shadow = font.render(text, True, shadow_color)
    shadow_rect = shadow.get_rect(center=pos)
    surface.blit(shadow, (shadow_rect.x + shadow_offset[0], shadow_rect.y + shadow_offset[1]))
    # Draw main text
    main = font.render(text, True, color)
    main_rect = main.get_rect(center=pos)
    surface.blit(main, main_rect)

# Bold+shadow function (move to top-level for reuse)
def draw_bold_text_with_shadow(surface, text, font, color, pos, shadow_offset=(2,2), shadow_color=(0,0,0)):
    shadow = font.render(text, True, shadow_color)
    shadow_rect = shadow.get_rect(center=pos)
    surface.blit(shadow, (shadow_rect.x + shadow_offset[0], shadow_rect.y + shadow_offset[1]))
    main = font.render(text, True, color)
    main_rect = main.get_rect(center=pos)
    surface.blit(main, (main_rect.x, main_rect.y))
    surface.blit(main, (main_rect.x+1, main_rect.y))

class Dinosaur:

    X_POS = 80
    Y_POS = 310 + VERTICAL_OFFSET
    Y_POS_DUCK = 340 + VERTICAL_OFFSET
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        # Update only the y coordinate (do not reset the rect)
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[(self.step_index // 5) % len(self.run_img)]
        # Keep the existing rect.x and update only y
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            # Subtract from current y without resetting rect
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))
        # Draw the player's name above the dino head with shadow, always white
        name_font = pygame.font.Font(FONT_FILE, 20)
        draw_text_with_shadow(SCREEN, "Player1", name_font, (255,255,255), (self.dino_rect.centerx, self.dino_rect.top - 10))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100) + VERTICAL_OFFSET
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Lower all small cacti by 30px
        self.rect.y = 325 + VERTICAL_OFFSET + 30

class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Lower all large cacti by 30px
        if self.type == 0:
            self.rect.y = 320 + VERTICAL_OFFSET + 20
        elif self.type == 1:
            self.rect.y = 315 + VERTICAL_OFFSET + 20
        else:  # self.type == 2 (LargeCactus3.png)
            self.rect.y = 310 + VERTICAL_OFFSET + 20

class Bird(Obstacle):
    # Add a higher bird height at dino's jump apex
    BIRD_HEIGHTS = [
        250 + VERTICAL_OFFSET, 
        290 + VERTICAL_OFFSET, 
        320 + VERTICAL_OFFSET,
        200 + VERTICAL_OFFSET,  # Higher than before (near jump apex)
        170 + VERTICAL_OFFSET   # Even higher (forces ducking)
    ]
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        # Choose from the extended heights, so some birds fly higher
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.initial_y = self.rect.y    # Store initial y-position for bounce
        self.speed_y = 2                # Vertical speed for up-and-down movement
        self.index = 0
    def update(self):
        # Vertical movement (bounce within ±20 pixels)
        self.rect.y += self.speed_y
        if abs(self.rect.y - self.initial_y) > 20:
            self.speed_y *= -1
        # Horizontal update (similar to Obstacle.update)
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()
    def draw(self, SCREEN):
        # Animate through all 8 bat frames
        if self.index >= 8 * 2:
            self.index = 0
        SCREEN.blit(self.image[self.index // 2], self.rect)
        self.index += 1

def settings_menu(from_pause=False, frozen_bg=None):
    # Use animated background like menu
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    settings_bg_frames = load_bg_animation_frames(1)
    settings_ground_img = get_ground_image(1)
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10

    running = True
    font = pygame.font.Font(FONT_FILE, 30)
    button_font = pygame.font.Font(FONT_FILE, 32)
    # Button setup
    btn_w, btn_h = 250, 40
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2
    start_y = SCREEN_HEIGHT // 2 - btn_h
    profile_rect = pygame.Rect(btn_x, start_y + 70, btn_w, btn_h)
    show_profile = False

    # UID variables
    uuid_id = ""
    custom_id = ""
    secrets_id = ""

    # Volume variable (ensure it's defined)
    global volume
    if 'volume' not in globals():
        volume = 0.5
        pygame.mixer.music.set_volume(volume)

    # --- Volume slider setup ---
    slider_w, slider_h = 300, 12
    slider_x = SCREEN_WIDTH // 2 - slider_w // 2
    slider_y = SCREEN_HEIGHT // 2 + 120  # moved further down (was +60)
    knob_radius = 16
    dragging = False

    while running:
        # Draw background (frozen if from_pause, else animated)
        if from_pause and frozen_bg is not None:
            SCREEN.blit(frozen_bg, (0, 0))
        else:
            # Animated background and moving tracks
            SCREEN.fill((255, 255, 255))
            draw_bg_animation(bg_anim_state, settings_bg_frames)
            x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, settings_ground_img)
            # --- Add dark overlay ---
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            SCREEN.blit(overlay, (0, 0))
        # Draw settings UI
        title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 58)
        draw_text_with_shadow(SCREEN, "Settings", title_font, FONT_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))

        # Draw Profile button
        profile_font = pygame.font.Font(FONT_FILE, 40)
        draw_bold_text_with_shadow(SCREEN, "Profile", profile_font, (255,255,255), profile_rect.center)

        # --- Draw Volume Slider ---
        # Slider bar
        pygame.draw.rect(SCREEN, (80,80,80), (slider_x, slider_y, slider_w, slider_h), border_radius=6)
        # Slider fill
        fill_w = int(slider_w * volume)
        pygame.draw.rect(SCREEN, (255, 215, 0), (slider_x, slider_y, fill_w, slider_h), border_radius=6)
        # Knob
        knob_x = slider_x + fill_w
        pygame.draw.circle(SCREEN, (255,255,255), (knob_x, slider_y + slider_h//2), knob_radius)
        pygame.draw.circle(SCREEN, (180,180,180), (knob_x, slider_y + slider_h//2), knob_radius, 2)
        # Volume text (centered above slider)
        vol_font = pygame.font.Font(FONT_FILE, 28)
        vol_text = vol_font.render(f"Volume: {int(volume*100)}%", True, (255,255,255))
        vol_text_rect = vol_text.get_rect(center=(slider_x + slider_w // 2, slider_y - 24))
        SCREEN.blit(vol_text, vol_text_rect)

        # If profile popup is open, draw it
        if show_profile:
            popup_w, popup_h = 600, 220
            popup_x = SCREEN_WIDTH // 2 - popup_w // 2
            popup_y = SCREEN_HEIGHT // 2 - popup_h // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
            pygame.draw.rect(SCREEN, (30,30,30), popup_rect)
            popup_title = font.render("Profile - Unique IDs", True, (255,255,0))
            SCREEN.blit(popup_title, (popup_x + 20, popup_y + 15))
            id_font = pygame.font.Font(FONT_FILE, 24)
            # Improved vertical spacing for ID rows
            id_row_y = popup_y + 60
            id_row_gap = 38
            SCREEN.blit(id_font.render("uuid4():", True, (255,255,255)), (popup_x + 20, id_row_y))
            SCREEN.blit(id_font.render(uuid_id, True, (180,255,180)), (popup_x + 160, id_row_y))
            SCREEN.blit(id_font.render("time+random:", True, (255,255,255)), (popup_x + 20, id_row_y + id_row_gap))
            SCREEN.blit(id_font.render(custom_id, True, (180,255,180)), (popup_x + 160, id_row_y + id_row_gap))
            SCREEN.blit(id_font.render("secrets.token_hex(8):", True, (255,255,255)), (popup_x + 20, id_row_y + 2*id_row_gap))
            SCREEN.blit(id_font.render(secrets_id, True, (180,255,180)), (popup_x + 260, id_row_y + 2*id_row_gap))
            close_font = pygame.font.Font(FONT_FILE, 22)
            close_text = close_font.render("Press ENTER or click to close", True, (255,255,0))
            SCREEN.blit(close_text, (popup_x + 20, popup_y + popup_h - 35))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # --- Volume slider knob drag start ---
                if (slider_x - knob_radius <= pos[0] <= slider_x + slider_w + knob_radius and
                    slider_y - knob_radius <= pos[1] <= slider_y + slider_h + knob_radius):
                    dragging = True
                    # Set volume immediately on click
                    volume = min(1.0, max(0.0, (pos[0] - slider_x) / slider_w))
                    pygame.mixer.music.set_volume(volume)
                # Profile button
                elif profile_rect.collidepoint(pos) and not show_profile:
                    BUTTON_SOUND.play()
                    uuid_id = str(uuid.uuid4())
                    custom_id = f"{int(time.time() * 1000)}-{random.randint(1000,9999)}"
                    secrets_id = secrets.token_hex(8)
                    show_profile = True
                elif show_profile:
                    BUTTON_SOUND.play()
                    show_profile = False
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                pos = pygame.mouse.get_pos()
                volume = min(1.0, max(0.0, (pos[0] - slider_x) / slider_w))
                pygame.mixer.music.set_volume(volume)
            if event.type == pygame.KEYDOWN:
                if show_profile and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    BUTTON_SOUND.play()
                    show_profile = False
                elif not show_profile:
                    if event.key == pygame.K_LEFT:
                        volume = max(0.0, volume - 0.05)
                        pygame.mixer.music.set_volume(volume)
                    elif event.key == pygame.K_RIGHT:
                        volume = min(1.0, volume + 0.05)
                        pygame.mixer.music.set_volume(volume)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        BUTTON_SOUND.play()
                        running = False
    # If from_pause, return to pause menu
    if from_pause:
        return 'pause'
    else:
        return 'menu'

def pause_menu(frozen_bg):
    # Button rects
    btn_w, btn_h = 250, 40
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2
    start_y = SCREEN_HEIGHT // 2 - 2 * btn_h - 15
    resume_rect = pygame.Rect(btn_x, start_y, btn_w, btn_h)
    playagain_rect = pygame.Rect(btn_x, start_y + btn_h + 1, btn_w, btn_h)
    settings_rect = pygame.Rect(btn_x, start_y + 2 * (btn_h + 1), btn_w, btn_h)
    home_rect = pygame.Rect(btn_x, start_y + 3 * (btn_h + 1), btn_w, btn_h)
    button_font = pygame.font.Font(FONT_FILE, 40)
    title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 70)
    running = True
    in_settings = False

    # Add selection logic
    pause_options = ["Resume", "Play Again", "Settings", "Home"]
    pause_rects = [resume_rect, playagain_rect, settings_rect, home_rect]
    selected = 0

    while running:
        # Draw frozen gameplay as background
        SCREEN.blit(frozen_bg, (0, 0))
        # Semi-transparent dark overlay (change from white to black)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA: black with alpha
        SCREEN.blit(overlay, (0, 0))
        # Draw title with shadow
        draw_text_with_shadow(SCREEN, "Paused", title_font, FONT_COLOR, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180))
        # Draw buttons with selection highlight
        for idx, (text, rect) in enumerate(zip(pause_options, pause_rects)):
            color = (255,255,0) if idx == selected else (200,200,200)
            draw_bold_text_with_shadow(SCREEN, text, button_font, color, rect.center)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    BUTTON_SOUND.play()
                    selected = (selected - 1) % len(pause_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    BUTTON_SOUND.play()
                    selected = (selected + 1) % len(pause_options)
                elif event.key == pygame.K_RETURN:
                    BUTTON_SOUND.play()
                    if selected == 0:
                        return 'resume'
                    elif selected == 1:
                        return 'playagain'
                    elif selected == 2:
                        settings_menu(from_pause=True, frozen_bg=frozen_bg)
                    elif selected == 3:
                        return 'home'
                elif event.key == pygame.K_ESCAPE:
                    BUTTON_SOUND.play()
                    return 'resume'
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, rect in enumerate(pause_rects):
                    if rect.collidepoint(pos):
                        BUTTON_SOUND.play()
                        if idx == 0:
                            return 'resume'
                        elif idx == 1:
                            return 'playagain'
                        elif idx == 2:
                            settings_menu(from_pause=True, frozen_bg=frozen_bg)
                        elif idx == 3:
                            return 'home'
        pygame.time.delay(30)

def load_bg_animation_frames(level):
    frames = []
    if level == 1:
        # Level 1: static grass.jpg
          for i in range(1, 71):
            img = pygame.image.load(os.path.join("assets/Level1/BGe", f"a{i}.png"))
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frames.append(img)
    elif level == 2:
        # Level 2: beach1 to beach12 animation
        for i in range(1, 13):
            img = pygame.image.load(os.path.join("assets/Level2/BG2", f"beach{i}.png"))
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frames.append(img)
    elif level == 3:
        # Level 3: q1 to q120 animation
        for i in range(1, 121):
            img = pygame.image.load(os.path.join("assets/Level3/BG3", f"q{i}.png"))
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frames.append(img)
    elif level == 4:
        # Level 4: static w.jpg
        img = pygame.image.load(os.path.join("assets/Level4", "w.jpg"))
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frames = [img] * 30
    elif level == 5:
        # Level 5: static sp.jpg
        img = pygame.image.load(os.path.join("assets/Level5", "sp.jpg"))
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frames = [img] * 30
    else:
        # Default fallback (white)
        img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        img.fill((255, 255, 255))
        frames = [img] * 30
    return frames

def draw_bg_animation(state, frames):
    now = pygame.time.get_ticks()
    frame_count = len(frames)
    if frame_count == 0:
        return  # Prevent IndexError if frames is empty
    if 'frame' not in state:
        state['frame'] = 0
    if 'fade' not in state:
        state['fade'] = 0.0
        state['prev_frame'] = state['frame']
    if state['frame'] >= frame_count:
        state['frame'] = 0
    if state.get('prev_frame', 0) >= frame_count:
        state['prev_frame'] = 0
    if now - state['last_update'] > BG_ANIMATION_INTERVAL:
        state['prev_frame'] = state['frame']
        state['frame'] = (state['frame'] + 1) % frame_count
        state['last_update'] = now
        state['fade'] = 0.0
    # Fade progress (0.0 to 1.0)
    fade_speed = 1  # Adjust for faster/slower fade
    if state['fade'] < 1.0:
        state['fade'] = min(1.0, state['fade'] + fade_speed)
    prev_img = frames[state['prev_frame']]
    next_img = frames[state['frame']]
    # Create a faded blend between prev_img and next_img
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
    surf.blit(prev_img, (0, 0))
    temp = next_img.copy().convert_alpha()
    temp.set_alpha(int(255 * state['fade']))
    surf.blit(temp, (0, 0))
    SCREEN.blit(surf, (0, 0))

def get_ground_image(level):
    if level == 1:
        return scale_image(pygame.image.load(os.path.join("assets/Level1/Ground1", "grass.png")), SCALE_FACTOR)
    elif level == 2:
        return scale_image(pygame.image.load(os.path.join("assets/Level2/Ground2", "sand1.png")), SCALE_FACTOR)
    elif level == 3:
        return scale_image(pygame.image.load(os.path.join("assets/Level3/Ground3", "track.png")), SCALE_FACTOR)
    elif level == 4:
        return scale_image(pygame.image.load(os.path.join("assets/Level4/Ground4", "track.png")), SCALE_FACTOR)
    elif level == 5:
        return scale_image(pygame.image.load(os.path.join("assets/Level5/Ground5", "track.png")), SCALE_FACTOR)
    else:
        return scale_image(pygame.image.load(os.path.join("assets/Level1/Ground1", "grass.png")), SCALE_FACTOR)

def draw_tracks(x_pos_bg, y_pos_bg, game_speed, ground_img):
    image_width = ground_img.get_width()
    SCREEN.blit(ground_img, (x_pos_bg, y_pos_bg))
    SCREEN.blit(ground_img, (x_pos_bg + image_width, y_pos_bg))
    x_pos_bg -= game_speed
    if x_pos_bg <= -image_width:
        x_pos_bg = 0
    return x_pos_bg

def fade_between_bg_only(SCREEN, old_frames, new_frames, duration=120):
    """Fade smoothly from old_frames to new_frames over duration (ms), only for background."""
    clock = pygame.time.Clock()
    fade_steps = int(duration / (1000 / BG_ANIMATION_FPS))
    old_img = old_frames[0]
    new_img = new_frames[0]
    for step in range(fade_steps + 1):
        alpha = step / fade_steps
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        surf.blit(old_img, (0, 0))
        temp = new_img.copy().convert_alpha()
        temp.set_alpha(int(255 * alpha))
        surf.blit(temp, (0, 0))
        SCREEN.blit(surf, (0, 0))
        pygame.display.update()
        clock.tick(BG_ANIMATION_FPS)

def get_bird_frames(level):
    frames = []
    if level == 1:
        for i in range(1, 21):
            img = scale_image(pygame.image.load(os.path.join("assets/Level1/Fly1", f"pg{i}.png")), 1.5)
            frames.append(img)
    elif level == 2:
        for i in range(1, 21):
            img = scale_image(pygame.image.load(os.path.join("assets/Level2/Fly2", f"pg{i}.png")), 1.5)
            frames.append(img)
    elif level == 3:
        for i in range(1, 9):
            img = scale_image(pygame.image.load(os.path.join("assets/Level3/Fly3", f"bat{i}.png")), 1.5)
            frames.append(img)
    elif level == 4:
        for i in range(1, 21):
            img = scale_image(pygame.image.load(os.path.join("assets/Level4/Fly4", f"pg{i}.png")), 1.5)
            frames.append(img)
    elif level == 5:
        for i in range(1, 16):
            img = scale_image(pygame.image.load(os.path.join("assets/Level5/Fly5", f"al{i}.png")), 1.5)
            frames.append(img)
    return frames

def get_rock_images(level):
    if level == 1:
        BIG_SCALE = SCALE_FACTOR * 1.5
        Y_OFFSET = 30
        def load_and_offset(path, scale, y_offset):
            img = scale_image(pygame.image.load(path), scale)
            surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            surf.blit(img, (0, -y_offset))
            return surf
        return [
            load_and_offset(os.path.join("assets/Level1/grass", "LargeCactus1.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level1/grass", "LargeCactus2.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level1/grass", "LargeCactus3.png"), BIG_SCALE, Y_OFFSET),
            scale_image(pygame.image.load(os.path.join("assets/Level1/grass", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1/grass", "SmallCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1/grass", "SmallCactus3.png")), SCALE_FACTOR),
        ]
    elif level == 2:
        BIG_SCALE = SCALE_FACTOR * 1.5
        Y_OFFSET = 30  # pixels to move up
        def load_and_offset(path, scale, y_offset):
            img = scale_image(pygame.image.load(path), scale)
            surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            surf.blit(img, (0, -y_offset))
            return surf
        return [
            load_and_offset(os.path.join("assets/Level2/sand", "LargeCactus1.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level2/sand", "LargeCactus2.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level2/sand", "LargeCactus3.png"), BIG_SCALE, Y_OFFSET),
            scale_image(pygame.image.load(os.path.join("assets/Level2/sand", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level2/sand", "SmallCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level2/sand", "SmallCactus3.png")), SCALE_FACTOR),
        ]
    elif level == 3:
        return [
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "LargeCactus3.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level3/rock", "SmallCactus3.png")), SCALE_FACTOR),
        ]
    elif level == 4:
        BIG_SCALE = SCALE_FACTOR * 1.5
        Y_OFFSET = 30
        def load_and_offset(path, scale, y_offset):
            img = scale_image(pygame.image.load(path), scale)
            surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            surf.blit(img, (0, -y_offset))
            return surf
        return [
            load_and_offset(os.path.join("assets/Level4/city", "LargeCactus1.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level4/city", "LargeCactus2.png"), BIG_SCALE, Y_OFFSET),
            load_and_offset(os.path.join("assets/Level4/city", "LargeCactus3.png"), BIG_SCALE, Y_OFFSET),
            scale_image(pygame.image.load(os.path.join("assets/Level4/city", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level4/city", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level4/city", "SmallCactus1.png")), SCALE_FACTOR),
        ]
    elif level == 5:
        return [
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "LargeCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "LargeCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "LargeCactus3.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "SmallCactus1.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "SmallCactus2.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level5/space", "SmallCactus3.png")), SCALE_FACTOR),
        ]
    else:
        # fallback to level 1
        return [
            scale_image(pygame.image.load(os.path.join("assets/Level1", "bk.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1", "clam.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1", "crab.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1", "she.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1", "san.png")), SCALE_FACTOR),
            scale_image(pygame.image.load(os.path.join("assets/Level1", "ice.png")), SCALE_FACTOR),
        ]

def play_welcome_music():
    music_path = os.path.join("assets", "Music", "welcome.mp3")
    if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Loop forever

def play_game_music():
    music_path = os.path.join("assets", "Music", "game.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop forever

def stop_music():
    pygame.mixer.music.stop()

def main(difficulty_speed):
    stop_music()
    play_game_music()
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = difficulty_speed
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    points = 0
    font = pygame.font.Font(FONT_FILE, 20)
    obstacles = []
    death_count = 0
    pause = False

    # Add level tracking
    level = 1
    MAX_LEVEL = 5
    WIN_POINTS = 2500  # 5 levels * 500 points per level

    # BG animation state for main game
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    bg_frames = load_bg_animation_frames(level)
    ground_img = get_ground_image(level)
    bird_frames = get_bird_frames(level)
    rock_images = get_rock_images(level)

    def score():
        nonlocal level, bg_frames, ground_img, bird_frames, rock_images
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        # Level up every 500 points, max 5
        new_level = min(points // 500 + 1, MAX_LEVEL)
        if new_level != level:
            old_frames = bg_frames
            level = new_level
            new_frames = load_bg_animation_frames(level)
            fade_between_bg_only(SCREEN, old_frames, new_frames, duration=700)
            bg_frames = new_frames
            ground_img = get_ground_image(level)
            bird_frames = get_bird_frames(level)
            rock_images = get_rock_images(level)
            bg_anim_state['frame'] = 0
            bg_anim_state['last_update'] = pygame.time.get_ticks()
        big_font = pygame.font.Font(FONT_FILE, 30)  # Increased font size
        draw_bold_text_with_shadow(SCREEN, f"Level: {level}", big_font, FONT_COLOR, (65, 20), shadow_offset=(2,2))
        draw_bold_text_with_shadow(SCREEN, "Points: " + str(points), big_font, FONT_COLOR, (75, 40), shadow_offset=(2,2))
        # --- WIN POPUP ---
        if level == MAX_LEVEL and points >= WIN_POINTS:
            show_win_popup()
            menu(0)
            return

    def background():
        draw_bg_animation(bg_anim_state, bg_frames)
        draw_tracks(x_pos_bg, y_pos_bg, 0, ground_img)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Pause on P or ESC
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
                # Take frozen screenshot
                frozen_bg = SCREEN.copy()
                action = pause_menu(frozen_bg)
                if action == 'resume':
                    continue  # Resume game
                elif action == 'playagain':
                    diff_speed = choose_difficulty()
                    main(diff_speed)
                    return
                elif action == 'settings':
                    settings_menu(from_pause=True, frozen_bg=frozen_bg)
                    # After settings, return to pause menu (handled in pause_menu)
                elif action == 'home':
                    menu(0)
                    return

        FONT_COLOR = (255, 255, 255)
        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        # --- Draw animated background before everything ---
        background()

        # --- Move tracks position here ---
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, game_speed, ground_img)

        # --- Then draw clouds ---
        cloud.draw(SCREEN)
        cloud.update()

        if len(obstacles) == 0:
            spawn = random.randint(0, 4)
            if spawn < 3:
                obstacles.append(random.choice([SmallCactus(rock_images), LargeCactus(rock_images)]))
            else:
                obstacles.append(Bird(bird_frames))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                # Position dino even closer to the enemy (almost touching enemy's left side)
                player.dino_rect.x = obstacle.rect.x - player.dino_rect.width + 1
                pygame.time.delay(1000)  # shorter delay for collision effect
                death_count += 1

                # Read the current high score from file (default to 0 if missing or invalid)
                try:
                    with open("score.txt", "r") as f:
                        stored_high = int(f.read())
                except:
                    stored_high = 0

                # Update high score only if current points is higher
                if points > stored_high:
                    with open("score.txt", "w") as f:
                        f.write(str(points))
                menu(death_count)

        player.update(userInput)
        player.draw(SCREEN)

        # --- Score display on top of everything ---
        score()

        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    play_welcome_music()
    global points, FONT_COLOR
    run = True

    # BG animation state for menu
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    # Load level 1 background for menu
    menu_bg_frames = load_bg_animation_frames(1)
    menu_ground_img = get_ground_image(1)

    # Instantiate a dinosaur for preview
    preview_dino = Dinosaur()
    preview_dino.dino_jump = False
    preview_dino.dino_duck = False
    preview_dino.dino_run = True

    # Animated button menu setup
    menu_options = ["Start", "Settings"]
    selected = 0
    button_font = pygame.font.Font(FONT_FILE, 45)
    option_spacing = 60
    start_y = SCREEN_HEIGHT // 2 - 50

    in_settings = False

    # Add tracks position for menu screen
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10

    while run:
        FONT_COLOR = (255, 255, 255)
        SCREEN.fill((255, 255, 255))

        # --- Draw animated background ---
        draw_bg_animation(bg_anim_state, menu_bg_frames)

        # Draw and update moving tracks
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, menu_ground_img)

        if in_settings:
            settings_menu(from_pause=False)
            in_settings = False
        else:
            # --- Overlay Menu UI ---
            title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 70)
            draw_text_with_shadow(SCREEN, "Dinosaur Runner", title_font, FONT_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

            # Animated menu options (UP/DOWN to select, ENTER to activate)
            for idx, text in enumerate(menu_options):
                color = (255, 255, 0) if idx == selected else (200, 200, 200)
                draw_bold_text_with_shadow(
                    SCREEN,
                    text,
                    button_font,
                    color,
                    (SCREEN_WIDTH // 2, start_y + idx * option_spacing)
                )

            # --- Draw preview dinosaur animation ---
            preview_dino.run()
            preview_dino.draw(SCREEN)

            # Draw score info below the buttons
            if death_count > 0:
                score_font = pygame.font.Font(FONT_FILE, 40)
                # Read high score from file
                try:
                    with open("score.txt", "r") as f:
                        stored_high = int(f.read())
                except:
                    stored_high = 0

                draw_bold_text_with_shadow(SCREEN, "Your Score: " + str(points), score_font, FONT_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
                draw_bold_text_with_shadow(SCREEN, "High Score: " + str(stored_high), score_font, FONT_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Removed ESC button handling here
                if not in_settings:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        BUTTON_SOUND.play()
                        selected = (selected - 1) % len(menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        BUTTON_SOUND.play()
                        selected = (selected + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        BUTTON_SOUND.play()
                        if selected == 0:  # Start
                            run = False
                            player_selection_screen()
                        elif selected == 1:  # Settings
                            in_settings = True
            if not in_settings:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Calculate button rects for mouse click
                    for idx, text in enumerate(menu_options):
                        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, start_y + idx * option_spacing - 25, 150, 50)
                        if btn_rect.collidepoint(pos):
                            BUTTON_SOUND.play()
                            if idx == 0:
                                run = False
                                player_selection_screen()
                            elif idx == 1:
                                in_settings = True

        pygame.time.delay(30)

def choose_difficulty():
    play_welcome_music()
    choosing = True
    # BG animation state for difficulty screen
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    # Load level 1 background for difficulty selection
    diff_bg_frames = load_bg_animation_frames(1)
    diff_ground_img = get_ground_image(1)
    dino = Dinosaur()
    
    # Add tracks position for difficulty screen
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10
    
    # Animated button setup
    options = ["Easy", "Medium", "Hard"]
    selected = 0
    font = pygame.font.Font(FONT_FILE, 40)
    option_spacing = 60
    start_y = SCREEN_HEIGHT // 2 - 30

    # Use the same font and style as the "Dinosaur Runner" title on the start screen
    title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 70)
    title_color = FONT_COLOR  # (0,0,0)
    
    while choosing:
        SCREEN.fill((255, 255, 255))
        # Animate BG animation
        draw_bg_animation(bg_anim_state, diff_bg_frames)
        
        # Draw and update moving tracks
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, diff_ground_img)
        
        # --- Add dark overlay ---
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        SCREEN.blit(overlay, (0, 0))
        
        # Draw dino walking animation
        dino.run()
        dino.draw(SCREEN)
        
        # Draw "Difficulty" title with shadow
        draw_text_with_shadow(SCREEN, "Difficulty", title_font, title_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 170))
        
        # Draw animated difficulty buttons
        for idx, text in enumerate(options):
            color = (255,255,0) if idx == selected else (200,200,200)
            draw_bold_text_with_shadow(
                SCREEN,
                text,
                font,
                color,
                (SCREEN_WIDTH//2, start_y + idx * option_spacing)
            )
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    BUTTON_SOUND.play()
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    BUTTON_SOUND.play()
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    BUTTON_SOUND.play()
                    if selected == 0:
                        return 15   # Easy speed (slower)
                    elif selected == 1:
                        return 20  # Medium speed (moderate)
                    elif selected == 2:
                        return 25  # Hard speed (faster)
                elif event.key == pygame.K_ESCAPE:
                    BUTTON_SOUND.play()
                    return None  # Signal to go back to player selection
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, text in enumerate(options):
                    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, start_y + idx * option_spacing - 25, 150, 50)
                    if btn_rect.collidepoint(pos):
                        BUTTON_SOUND.play()
                        if idx == 0:
                            return 15
                        elif idx == 1:
                            return 20
                        elif idx == 2:
                            return 25
        pygame.time.delay(30)

def welcome():
    play_welcome_music()
    run = True
    # BG animation state for welcome screen
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    # Load level 1 background for welcome screen
    welcome_bg_frames = load_bg_animation_frames(1)
    welcome_ground_img = get_ground_image(1)
    # Use slkscrb.ttf for the welcome text
    welcome_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 70)
    hint_font = pygame.font.Font(FONT_FILE, 32)
    dino = Dinosaur()  # instantiate dinosaur for walking animation
    # Add tracks position for welcome screen
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10
    while run:
        FONT_COLOR = (255, 255, 255)
        SCREEN.fill((255, 255, 255))
        # Animate BG animation
        draw_bg_animation(bg_anim_state, welcome_bg_frames)
        # Draw and update moving tracks
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, welcome_ground_img)
        # update and draw dinosaur walking animation
        dino.run()
        dino.draw(SCREEN)
        draw_text_with_shadow(SCREEN, "Welcome, Players", welcome_font, FONT_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        # Only show "Press ENTER to continue"
        draw_bold_text_with_shadow(
            SCREEN,
            "Press ENTER to continue",
            hint_font,
            (255, 255, 0),  # Yellow color
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
        )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False
        pygame.time.delay(30)

def get_player2_frames():
    # Load te1-te12 from Bird folder (not Player2)
    folder = os.path.join("assets", "Bird")
    frames = []
    for i in range(1, 13):
        path = os.path.join(folder, f"te{i}.png")
        if os.path.exists(path):
            frames.append(scale_image(pygame.image.load(path), 1.0))
    return frames

class Player2:
    X_POS = 80
    Y_POS = 310 + VERTICAL_OFFSET

    def __init__(self):
        self.frames = get_player2_frames()
        self.frame_idx = 0
        self.image = self.frames[0] if self.frames else None
        self.rect = self.image.get_rect() if self.image else pygame.Rect(0,0,0,0)
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

    def update(self, userInput):
        if userInput[pygame.K_w]:
            self.rect.y -= 10
        if userInput[pygame.K_s]:
            self.rect.y += 10
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
        if self.frames:
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.image = self.frames[self.frame_idx]

    def draw(self, SCREEN):
        if self.image:
            SCREEN.blit(self.image, (self.rect.x, self.rect.y))
            # Draw the player's name above the player 2 image, always white
            name_font = pygame.font.Font(FONT_FILE, 20)
            draw_text_with_shadow(SCREEN, "Player2", name_font, (255,255,255), (self.rect.centerx, self.rect.top - 10))

def player_selection_screen():
    play_welcome_music()
    # Use same animated background as welcome()
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    menu_bg_frames = load_bg_animation_frames(1)
    menu_ground_img = get_ground_image(1)
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10

    run = True
    font = pygame.font.Font(FONT_FILE, 50)
    selected = 0
    options = ["1 Player", "2 Player"]
    # Add a preview dino for animation
    preview_dino = Dinosaur()
    preview_dino.dino_jump = False
    preview_dino.dino_duck = False
    preview_dino.dino_run = True

    while run:
        # Draw animated background (same as welcome)
        SCREEN.fill((255,255,255))
        draw_bg_animation(bg_anim_state, menu_bg_frames)
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, menu_ground_img)
        # --- Add dark overlay ---
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        SCREEN.blit(overlay, (0, 0))
        # Draw preview dino animation
        preview_dino.run()
        preview_dino.draw(SCREEN)

        # Change font for "Select Player" to slkscrb.ttf
        title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 70)
        draw_text_with_shadow(SCREEN, "Select Player", title_font, (255,255,255), (SCREEN_WIDTH//2, 180))
        # Draw options closer together and in bold
        option_spacing = 50  # Reduced spacing for closer options
        start_y = 320
        for idx, text in enumerate(options):
            color = (255,255,0) if idx == selected else (200,200,200)
            draw_bold_text_with_shadow(
                SCREEN,
                text,
                font,
                color,
                (SCREEN_WIDTH//2, start_y + idx * option_spacing)
            )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    BUTTON_SOUND.play()
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    BUTTON_SOUND.play()
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    BUTTON_SOUND.play()
                    run = False
                    show_how_to_play(selected)
                    diff_speed = choose_difficulty()
                    if diff_speed is None:
                        run = True
                        continue  # Go back to player selection if ESC pressed in difficulty
                    if selected == 0:
                        main(diff_speed)
                    else:
                        main_player2(diff_speed)
                elif event.key == pygame.K_ESCAPE:
                    BUTTON_SOUND.play()
                    run = False
                    menu(0)
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for idx, text in enumerate(options):
                    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, start_y + idx * option_spacing - 25, 150, 50)
                    if btn_rect.collidepoint(pos):
                        BUTTON_SOUND.play()
                        if idx == 0:
                            run = False
                            show_how_to_play(idx)
                            diff_speed = choose_difficulty()
                            main(diff_speed)
                        elif idx == 1:
                            run = False
                            show_how_to_play(idx)
                            diff_speed = choose_difficulty()
                            main_player2(diff_speed)
        pygame.time.delay(30)

def show_how_to_play(player_mode):
    # Use same animated background as welcome()
    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    howto_bg_frames = load_bg_animation_frames(1)
    howto_ground_img = get_ground_image(1)
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    tracks_speed = 10
    # Add a preview dino for animation
    preview_dino = Dinosaur()
    preview_dino.dino_jump = False
    preview_dino.dino_duck = False
    preview_dino.dino_run = True

    run = True
    font = pygame.font.Font(FONT_FILE, 40)
    title_font = pygame.font.Font(FONT_FILE, 60)
    while run:
        # Draw animated background (same as welcome)
        SCREEN.fill((255, 255, 255))
        draw_bg_animation(bg_anim_state, howto_bg_frames)
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, tracks_speed, howto_ground_img)
        # --- Add dark overlay ---
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        SCREEN.blit(overlay, (0, 0))
        # Draw preview dino animation
        preview_dino.run()
        preview_dino.draw(SCREEN)

        title_font = pygame.font.Font(os.path.join("assets", "Font", "slkscrb.ttf"), 60)
        draw_text_with_shadow(SCREEN, "How to Play", title_font, (255,255,255), (SCREEN_WIDTH//2, 180))
        base_y = SCREEN_HEIGHT // 2 - 30  # Center the paragraph block
        if player_mode == 0:
            draw_bold_text_with_shadow(SCREEN, "Player 1: Arrow Keys (↑/↓) to move", font, (200,200,255), (SCREEN_WIDTH//2, base_y))
        else:
            draw_bold_text_with_shadow(SCREEN, "Player 1: Arrow Keys (↑/↓) to move", font, (200,200,255), (SCREEN_WIDTH//2, base_y + -40))
            draw_bold_text_with_shadow(SCREEN, "Player 2: W = Fly Up, S = Fly Down", font, (255,200,200), (SCREEN_WIDTH//2, base_y))
        draw_bold_text_with_shadow(SCREEN, "Avoid obstacles, collect points, survive!", font, (255,255,255), (SCREEN_WIDTH//2, base_y + 40))
        draw_bold_text_with_shadow(SCREEN, "Press ENTER to continue", font, (255,255,0), (SCREEN_WIDTH//2, base_y + 80))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                run = False
            elif event.key == pygame.K_ESCAPE:
                BUTTON_SOUND.play()
                run = False
                player_selection_screen()
                return
        pygame.time.delay(30)

def main_player2(difficulty_speed):
    stop_music()
    play_game_music()
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player1 = Dinosaur()  # Always add Player 1 (Dino)
    player2 = Player2()   # Player 2 (te images)
    cloud = Cloud()
    game_speed = difficulty_speed
    x_pos_bg = 0
    y_pos_bg = 360 + VERTICAL_OFFSET
    points = 0
    font = pygame.font.Font(FONT_FILE, 20)
    obstacles = []
    death_count = 0
    pause = False

    level = 1
    MAX_LEVEL = 5
    WIN_POINTS = 2500  # 5 levels * 500 points per level

    bg_anim_state = {'frame': 0, 'last_update': pygame.time.get_ticks()}
    bg_frames = load_bg_animation_frames(level)
    ground_img = get_ground_image(level)
    bird_frames = get_bird_frames(level)
    rock_images = get_rock_images(level)

    def score():
        nonlocal level, bg_frames, ground_img, bird_frames, rock_images
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        new_level = min(points // 500 + 1, MAX_LEVEL)
        if new_level != level:
            old_frames = bg_frames
            level = new_level
            new_frames = load_bg_animation_frames(level)
            fade_between_bg_only(SCREEN, old_frames, new_frames, duration=700)
            bg_frames = new_frames
            ground_img = get_ground_image(level)
            bird_frames = get_bird_frames(level)
            rock_images = get_rock_images(level)
            bg_anim_state['frame'] = 0
            bg_anim_state['last_update'] = pygame.time.get_ticks()
        big_font = pygame.font.Font(FONT_FILE, 30)
        draw_bold_text_with_shadow(SCREEN, f"Level: {level}", big_font, FONT_COLOR, (65, 20), shadow_offset=(2,2))
        draw_bold_text_with_shadow(SCREEN, "Points: " + str(points), big_font, FONT_COLOR, (75, 40), shadow_offset=(2,2))
        # --- WIN POPUP ---
        if level == MAX_LEVEL and points >= WIN_POINTS:
            show_win_popup()
            player_selection_screen()
            return

    def background():
        draw_bg_animation(bg_anim_state, bg_frames)
        draw_tracks(x_pos_bg, y_pos_bg, 0, ground_img)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
                frozen_bg = SCREEN.copy()
                action = pause_menu(frozen_bg)
                if action == 'resume':
                    continue
                elif action == 'playagain':
                    diff_speed = choose_difficulty()
                    main_player2(diff_speed)
                    return
                elif action == 'settings':
                    settings_menu(from_pause=True, frozen_bg=frozen_bg)
                elif action == 'home':
                    player_selection_screen()
                    return

        FONT_COLOR = (255, 255, 255)
        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        background()
        x_pos_bg = draw_tracks(x_pos_bg, y_pos_bg, game_speed, ground_img)
        cloud.draw(SCREEN)
        cloud.update()

        if len(obstacles) == 0:
            spawn = random.randint(0, 4)
            if spawn < 3:
                obstacles.append(random.choice([SmallCactus(rock_images), LargeCactus(rock_images)]))
            else:
                bird = Bird(bird_frames)
                # Randomly choose between normal bird heights and top of the screen
                if random.random() < 0.5:
                    # Top spawn (randomize a bit along the top)
                    bird.rect.y = VERTICAL_OFFSET + random.randint(10, 60)
                    bird.initial_y = bird.rect.y
                # else: use default random height from Bird.BIRD_HEIGHTS
                obstacles.append(bird)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            # Player 1 collision
            if player1.dino_rect.colliderect(obstacle.rect):
                # Only "kill" Player 1 if not already "dead"
                if player1.dino_rect.x != -9999:
                    player1.dino_rect.x = -9999  # Move off-screen to mark as dead
            # Player 2 collision
            if player2.image and player2.rect.colliderect(obstacle.rect):
                if player2.rect.x != -9999:
                    player2.rect.x = -9999  # Move off-screen to mark as dead

        # If both players are "dead", end game
        if player1.dino_rect.x == -9999 and (not player2.image or player2.rect.x == -9999):
            pygame.time.delay(1000)
            try:
                with open("score.txt", "r") as f:
                    stored_high = int(f.read())
            except:
                stored_high = 0
            if points > stored_high:
                with open("score.txt", "w") as f:
                    f.write(str(points))
            player_selection_screen()
            return

        # Update and draw both players (only if not "dead")
        if player1.dino_rect.x != -9999:
            player1.update(userInput)
            player1.draw(SCREEN)
        if player2.image and player2.rect.x != -9999:
            player2.update(userInput)
            player2.draw(SCREEN)
        score()
        clock.tick(30)
        pygame.display.update()

def show_win_popup():
    # Show a simple "You Win!" popup and wait for user to press ENTER or ESC
    popup_w, popup_h = 500, 200
    popup_x = SCREEN_WIDTH // 2 - popup_w // 2
    popup_y = SCREEN_HEIGHT // 2 - popup_h // 2
    font = pygame.font.Font(FONT_FILE, 60)
    info_font = pygame.font.Font(FONT_FILE, 32)
    running = True
    while running:
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))
        # Draw popup
        pygame.draw.rect(SCREEN, (30, 30, 30), (popup_x, popup_y, popup_w, popup_h), border_radius=20)
        draw_text_with_shadow(SCREEN, "YOU WIN!", font, (255, 255, 0), (SCREEN_WIDTH // 2, popup_y + 70))
        draw_bold_text_with_shadow(SCREEN, "Press ENTER or ESC", info_font, (255,255,255), (SCREEN_WIDTH // 2, popup_y + 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    BUTTON_SOUND.play()
                    running = False
        pygame.time.delay(30)

if __name__ == "__main__":
    welcome()
    menu(0)

