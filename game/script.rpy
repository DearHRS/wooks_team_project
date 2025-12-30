# ============================================================================
# ОПРЕДЕЛЕНИЯ ИЗОБРАЖЕНИЙ
# ============================================================================

# Основные фоны (с масштабированием под размер экрана)
image bgBlack = Transform("images/bgBlack.jpg", size=(1920, 1080), fit="contain")
image bgPrologBackground = Transform("images/backgrounds/prolog-bg.jpg", size=(1920, 1080), fit="contain")
image bgMainCRT = Transform("images/backgrounds/main_background_crt.png", size=(1920, 1080), fit="contain")
image bgQuiz = Transform("images/backgrounds/quizbg.png", size=(1920, 1080), fit="contain")

# Спрайты персонажей
image hero idle = "images/characters/main_character.png"
image hero smile = "images/characters/main_character_smiling.png"

image assistant idle:
    "images/characters/ai_assistant.png"

image assistant smile:
    "images/characters/ai_assistant_smile_expression.png"

image assistant surprised:
    "images/characters/ai_assistant_surprised.png"
image assistant open:
    "images/characters/ai_assistant_open_mouth.png"

transform assistantPos:
    xzoom -1
    xalign 0.0
    ycenter 0.58

image hacker idle: 
    "images/characters/main_villain.png"
    zoom 1.3
    ycenter 0.7

transform heroRight:
    xycenter (0.9, 0.56)

transform hackerRight:
    xycenter (0.89, 0.7)

transform hackerLeft:
    xzoom -1
    xycenter (0.12, 0.7)

transform hackerCentre:
    xycenter (0.5, 0.7)

transform move(x, y, time):
    linear time xpos x ypos y

# Отключаем систему сохранений для аркадной игры
define config.has_quicksave = False
define config.has_autosave = False
define config.autosave_on_quit = False
define config.autosave_on_choice = False

#text related shenanigins after entering game
default isInGame = False
default textProperties = {"pos":(0.9, 0.8), "align": 1.0, "xsize": 800}

# Определения персонажей для диалогов
define h = Character("Герой")
define a = Character("Помощник")
define x = Character("Хакер")

label start:
    # Начало игры - запуск пролога
    call prologue_main from _call_prologue_main
    return