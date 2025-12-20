# ============================================================================
# ОПРЕДЕЛЕНИЯ ИЗОБРАЖЕНИЙ
# ============================================================================

# Основные фоны (с масштабированием под размер экрана)
image bgBlack = im.Scale("images/bgBlack.jpg", 1920, 1080)
image bgSpaceBackground = im.Scale("images/bgSpaceBackground.jpg", 1920, 1080)
image bgPrologBackground = im.Scale("images/backgrounds/prolog-bg.jpg", 1920, 1080)
image bgMainCRT = im.Scale("images/backgrounds/main_background_crt.png", 1920, 1080)

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

image hacker idle = "images/characters/main_villain.png"

# Отключаем систему сохранений для аркадной игры
define config.has_quicksave = False
define config.has_autosave = False
define config.autosave_on_quit = False
define config.autosave_on_choice = False

# Определения персонажей для диалогов
define h = Character("Герой")
define a = Character("Помощник")
define x = Character("Хакер")

label start:
    # Начало игры - запуск пролога
    call prologue_main
    return