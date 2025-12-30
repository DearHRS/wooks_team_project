################################################################################
## МОДУЛЬ ВИКТОРИНЫ
################################################################################
##
## Переиспользуемый модуль для создания викторин с системой жизней
##
## ИСПОЛЬЗОВАНИЕ:
##   define my_quiz = {
##       "title": "Название викторины",
##       "lives": 3,
##       "questions": [
##           ("Вопрос?", ("Вариант1", "Вариант2", "Вариант3", "Вариант4"), 0),
##           ...
##       ]
##   }
##
##   call quiz_game(my_quiz)
##
################################################################################

## Константы конфигурации
define QUIZ_MIN_PASSING_SCORE = 3
define QUIZ_DEFAULT_LIVES = 3
define QUIZ_BUTTON_SIZE = (535, 210)
define QUIZ_BUTTON_SPACING = 10
define QUIZ_FONT_BOLD = "fonts/clacon2.ttf"
define QUIZ_FONT_REGULAR = "fonts/clacon2.ttf"

## Цветовая схема терминала
define QUIZ_COLOR_PRIMARY = "#236243"
define QUIZ_COLOR_ACCENT = "#33ff66"
define QUIZ_COLOR_ERROR = "#ff3333"
define QUIZ_COLOR_PALE = "#99ff99"
define QUIZ_OUTLINE_PRIMARY = "#003311"
define QUIZ_OUTLINE_ERROR = "#330000"

init python:
    class QuizState:
        def __init__(self, quiz_data):
            self.lives = quiz_data.get("lives", QUIZ_DEFAULT_LIVES)
            self.score = 0
            self.current = 0
            self.questions = quiz_data.get("questions", [])
            self.title = quiz_data.get("title", "ВИКТОРИНА")
            self.total = len(self.questions)
        
        def get_current_question(self):
            if self.current >= self.total:
                return None
            
            question_data = self.questions[self.current]
            return {
                "text": question_data[0],
                "answers": question_data[1],
                "correct": question_data[2],
                "number": self.current + 1
            }
        
        def process_answer(self, answer_index):
            question = self.get_current_question()
            if answer_index == question["correct"]:
                self.score += 1
                return True
            else:
                self.lives -= 1
                quiz_data["lives"] = self.lives                     #####dumb haxxcc
                return False
        
        def is_completed(self):
            return self.current >= self.total
        
        def is_game_over(self):
            return self.lives <= 0
        
        def next_question(self):
            self.current += 1

label quiz_game(quiz_data):
    
    # Инициализация состояния викторины
    python:
        _quiz = QuizState(quiz_data)
        # Глобальные переменные для экранов
        quiz_lives = _quiz.lives
        quiz_score = _quiz.score
        quiz_title = _quiz.title
        quiz_total = _quiz.total
    
    jump quiz_game_loop

label quiz_game_loop:
    
    # Проверка условий завершения
    if _quiz.is_completed():
        jump quiz_game_completed
    
    if _quiz.is_game_over():
        jump quiz_game_over
    
    # Получаем текущий вопрос
    python:
        question = _quiz.get_current_question()
        quiz_question_text = question["text"]
        quiz_answers = question["answers"]
        quiz_question_number = question["number"]
        quiz_lives = _quiz.lives
        quiz_score = _quiz.score
    
    # Показываем экран с вопросом
    call screen quiz_game_screen
    
    # Обрабатываем ответ
    python:
        _quiz.process_answer(_return)
        _quiz.next_question()
    
    jump quiz_game_loop

label quiz_game_over:
    call screen quiz_game_over_screen

label quiz_game_completed:
    $ quiz_score = _quiz.score
    call screen quiz_game_completed_screen
    return _quiz.score


################################################################################
## Экраны для модульной викторины
################################################################################

# Основной экран викторины
screen quiz_game_screen():
    modal True
    
    # Фон главного меню
    add "bgQuiz"
    
    # Название викторины (смещено вниз чуть больше размера шрифта)
    text "[quiz_title[0]]" style "quiz_game_theme":
        align (0.5, 0.225)
        size quiz_title[1]
        
    # Горизонтальная линия
    add Solid("#4a4a6a", xysize=(0.45, 0.002)) align (0.5, 0.252)
    #add Solid("#4a4a6a", xysize=(0.279, 0.195)) xycenter (0.359, 0.581) alpha 0.5
    #add Solid("#0707cc", xysize=(535, 210)) xycenter (0.359, 0.581) alpha 0.5
    
    # Жизни (слева вверху)
    text "❤️ x[quiz_lives]" style "quiz_game_lives" align (0.24, 0.198)
    
    # Номер вопроса (справа)
    text "Вопрос [quiz_question_number]/[quiz_total]" style "quiz_game_info" align (0.748, 0.2)
    
    # Вопрос по центру экрана
    vbox:
        align (0.5, 0.33)
        
        # Вопрос
        text quiz_question_text[0]:
            style "quiz_game_question"
            size quiz_question_text[1]
    

    #plan was to get pixel size for buttons via current screensize and then send that instead of relative size, relative size reduces button size
    # Кнопки ответов (два ряда по два ответа)
    vbox:
        xysize (0.561, 0.4)
        xycenter (0.5, 0.682)
        spacing QUIZ_BUTTON_SPACING
        
        for row in range(2):
            hbox:
                ycenter 0.5
                spacing QUIZ_BUTTON_SPACING
                
                for col in range(2):
                    $ answer_index = row * 2 + col
                    button:
                        xysize QUIZ_BUTTON_SIZE
                        hover_background Frame("gui/button/hover_backgroundQuiz.png")
                        activate_sound "<volume 0.5>audio/buttonClick.wav"
                        hover_sound "<volume 0.2>audio/buttonHowerSound.wav"
                        action [Return(answer_index), renpy.block_rollback()]
                        
                        text quiz_answers[answer_index][0]:
                            style "quiz_game_answer_text"
                            size quiz_answers[answer_index][1]
                            xycenter (0.5, 0.5)


# Экран результата ответа
screen quiz_game_result_screen(message, is_correct):
    modal True
    timer 2.0 action Return()
    
    add "main_background_crt"
    
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 30
        
        if is_correct:
            text "✓ ПРАВИЛЬНО!" style "quiz_game_result_correct"
            text "Вы получили +1 очко" style "quiz_game_result_message"
        else:
            text "✗ НЕПРАВИЛЬНО!" style "quiz_game_result_incorrect"
            text message style "quiz_game_result_message"
        
        text "Жизней осталось: [quiz_lives]" style "quiz_game_result_info"


# Экран конца игры (потеря всех жизней)
screen quiz_game_over_screen():
    modal True
    timer 3.0 action Return()
    
    add "main_background_crt"
    
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 40
        
        $renpy.block_rollback()
        if _quiz.lives >= 3:
            text "Вы успешно ответили на [quiz_score] вопросов" style "quiz_game_gameover_title"
        else:
            text "Повтори материал и попробуй ещё раз" style "quiz_game_gameover_message"


# Экран завершения викторины
screen quiz_game_completed_screen():
    modal True
    timer 4.0 action Return()
    
    add "main_background_crt"
    $renpy.block_rollback()
    
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 40
        
        text "В И К Т О Р И Н А  З А В Е Р Ш Е Н А!" style "quiz_game_completed_title"
        text "Ваш результат: [quiz_score]/[quiz_total]" style "quiz_game_completed_score"
        
        if quiz_score == quiz_total:
            text "Отлично! Вы ответили правильно на все вопросы!" style "quiz_game_completed_excellent"
        elif quiz_score >= quiz_total // 2:
            text "Хорошо! Вы ответили правильно на большинство вопросов." style "quiz_game_completed_good"
        else:
            text "Нужно еще потренироваться!" style "quiz_game_completed_bad"
        
        text "Спасибо за игру!" style "quiz_game_completed_thanks"


################################################################################
## Стили для модульной викторины (Terminal/Hacker стиль)
################################################################################

# Базовый стиль для текста терминала
style quiz_base:
    color QUIZ_COLOR_PRIMARY
    bold False
    xalign 0.5
    font QUIZ_FONT_REGULAR

# Заголовки и основные элементы
style quiz_game_theme is quiz_base:
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_info is quiz_base:
    size 28
    font QUIZ_FONT_REGULAR
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_lives is quiz_base:
    size 22
    color QUIZ_COLOR_ERROR
    bold True
    outlines [(2, QUIZ_OUTLINE_ERROR, 0, 0)]

style quiz_game_question is quiz_base:
    xysize (1045, 131)
    text_align 0.5
    layout "subtitle"
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_answer_text is quiz_base:
    xysize (494, 171)
    text_align 0.5
    layout "subtitle"
    font QUIZ_FONT_REGULAR
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]

# Экраны результатов
style quiz_game_result_correct is quiz_base:
    size 60
    bold True
    outlines [(3, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_result_incorrect is quiz_base:
    size 60
    color QUIZ_COLOR_ERROR
    bold True
    outlines [(3, QUIZ_OUTLINE_ERROR, 0, 0)]

style quiz_game_result_message is quiz_base:
    size 36
    font QUIZ_FONT_REGULAR
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_result_info is quiz_base:
    size 28
    color QUIZ_COLOR_ACCENT
    font QUIZ_FONT_REGULAR
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]

# Экраны завершения
style quiz_game_gameover_title is quiz_base:
    size 70
    color QUIZ_COLOR_ERROR
    outlines [(3, QUIZ_OUTLINE_ERROR, 0, 0)]

style quiz_game_gameover_message is quiz_base:
    size 40
    font QUIZ_FONT_REGULAR
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_gameover_score is quiz_base:
    size 48
    color QUIZ_COLOR_ACCENT
    bold True
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_gameover_info is quiz_base:
    size 32
    font QUIZ_FONT_REGULAR
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_title is quiz_base:
    size 70
    outlines [(3, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_score is quiz_base:
    size 48
    color QUIZ_COLOR_ACCENT
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_excellent is quiz_base:
    size 40
    font QUIZ_FONT_REGULAR
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_good is quiz_base:
    size 40
    color QUIZ_COLOR_ACCENT
    font QUIZ_FONT_REGULAR
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_bad is quiz_base:
    size 40
    color QUIZ_COLOR_PALE
    font QUIZ_FONT_REGULAR
    outlines [(2, QUIZ_OUTLINE_PRIMARY, 0, 0)]

style quiz_game_completed_thanks is quiz_base:
    size 32
    font QUIZ_FONT_REGULAR
    outlines [(1, QUIZ_OUTLINE_PRIMARY, 0, 0)]
