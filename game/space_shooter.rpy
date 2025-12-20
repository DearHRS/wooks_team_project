"""
Space Shooter (Galaga Style) - Mini Game
"""

# Анимация огня для корабля игрока
image playerShip:
    animation
    "images/sprites/Player1.png"
    0.1
    "images/sprites/Player2.png"
    0.1
    "images/sprites/Player3.png"
    repeat

image explosionAnim:
    animation
    "images/sprites/explosion1.png"
    0.02
    "images/sprites/explosion2.png"
    0.02
    "images/sprites/explosion3.png"
    0.02
    "images/sprites/explosion4.png"
    0.02
    "images/sprites/explosion5.png"
    0.02
    "images/sprites/explosion6.png"
    0.02
    "images/sprites/explosion7.png"
    0.02
    "images/sprites/explosion8.png"
    0.02
    "images/sprites/explosion9.png"
    0.02
    "images/sprites/explosion10.png"
    0.02
    "images/sprites/explosion11.png"
    0.02
    repeat

image gunShotAnim:
    animation
    "images/sprites/gunFire1.png"
    0.02
    "images/sprites/gunFire2.png"
    0.02
    "images/sprites/gunFire3.png"
    0.02
    repeat

image dashAnim:
    animation
    "images/sprites/dash1.png"
    0.02
    "images/sprites/dash2.png"
    0.02
    "images/sprites/dash3.png"
    0.02
    "images/sprites/dash4.png"
    0.02
    repeat

# === КОНСТАНТЫ ===
define PLAY_AREA = {"xmin": 0.25, "xmax": 0.75, "ymin": 0.05, "ymax": 0.95}
define SHIP_MUZZLE_OFFSET_X = 0.027
define SHIP_MUZZLE_FORWARD_Y = -0.03
define BULLET_STEP = 0.025
define ENEMY_SIZE = {"hw": 0.03, "hh": 0.045}
define FORMATION_SPEED = 0.002
define FORMATION_MAX_OFFSET = 0.08
define GAME_UPDATE_RATE = 0.02

# === ПЕРЕМЕННЫЕ ИГРЫ ===
default show_hitboxes = False
default show_enemy_hitboxes = False
default ship_data = {
    "x": 0.5, "y": 0.9, 
    "dx": 0.0, "dy": 0.0,
    "is_iframe_active": True, 
    "iframe_timer": 10,
    "lives": 3,
    "score": 0,
    "hitboxHeight": 0.1,
    "hitboxWidth": 0.03,
    "moveStep": 0.005,
    "isWeaponReady": False,
    "weaponCooldown": 5,
    "knockback": 0.015
}
default shipBounds = { 
    "xmin": 0.25 + (ship_data["hitboxWidth"] / 2 + 0.018), 
    "xmax": 0.75 - (ship_data["hitboxWidth"] / 2 + 0.018), 
    "ymin": 0.05 + (ship_data["hitboxHeight"] / 2 + 0.005), 
    "ymax": 0.95 - (ship_data["hitboxHeight"] / 2)
}
default longAnimations = []
default bullets = []
default enemies = []
default enemy_bullets = []
default current_wave = 1
default game_over = False
default formation_x_offset = 0.0
default formation_direction = 1

# === ЛОГИКА ИГРЫ ===
init python:
    import pygame
    import random

    """удаление горячей клавиши"""
    config.keymap['screenshot'].remove('noshift_K_s')
    config.keymap['director'].remove('noshift_K_d')

    """звуковые каналы, работающие параллельно"""
    renpy.music.register_channel("player", "sfx", False)
    renpy.music.register_channel("playerHit", "sfx", False)
    renpy.music.register_channel("enemy", "sfx", False)
    renpy.music.register_channel("dash", "sfx", False)
    renpy.music.register_channel("explosions", "sfx", False)

    def clamp(value, min_val, max_val):
        """Ограничивает значение между min и max"""
        return max(min_val, min(max_val, value))
    
    def MoveShip(dx, dy):
        """Перемещает корабль в пределах границ"""
        ship_data["x"] = clamp(ship_data["x"] + dx, shipBounds["xmin"], shipBounds["xmax"])
        ship_data["y"] = clamp(ship_data["y"] + dy, shipBounds["ymin"], shipBounds["ymax"])

    def FireBulletUp():
        """Создает пулю из указанного орудия корабля"""
        if game_over:
            return
        
        if ship_data["isWeaponReady"]:
            ship_data["weaponCooldown"] = 20
            ship_data["isWeaponReady"] = False
            spawn_y = ship_data["y"] + SHIP_MUZZLE_FORWARD_Y + ship_data["knockback"] + ship_data["dy"]

            for i in range(1, 3):
                flip = pow(-1, i)
                spawn_x = ship_data["x"] + ship_data["dx"] + SHIP_MUZZLE_OFFSET_X * flip
                bullets.append({
                    "x": spawn_x, "y": spawn_y, "vy": -BULLET_STEP
                })
                DoLongAnimation(
                    "gunShotAnim", spawn_x, spawn_y, 0.02, 0.052, 
                    flip, 1, 3, "audio/playerShootPass.wav", "player"
                )

            MoveShip(0, ship_data["knockback"])

    def _rect_contains_point(ex, ey, hw, hh, px, py):
        """Проверяет, находится ли точка внутри прямоугольника"""
        return (ex - hw / 2) <= px <= (ex + hw / 2) and (ey - hh / 2) <= py <= (ey + hh / 2)

    def ResetGame():
        """Сбрасывает игру к начальному состоянию"""
        global current_wave, game_over, formation_x_offset, formation_direction
        
        ship_data["x"] = 0.5
        ship_data["y"] = 0.8
        ship_data["lives"] = 5
        ship_data["score"] = 0
        ship_data["weaponCooldown"] : 5
        current_wave = 1
        game_over = False
        formation_x_offset = 0.0
        formation_direction = 1
        
        bullets[:] = []
        enemies[:] = []
        longAnimations[:] = []
        enemy_bullets[:] = []
        
        SpawnEnemyFormation(current_wave)
        renpy.restart_interaction()

    def _create_enemy(x, y):
        """Создает врага с заданными координатами"""        
        return {
            "x": x, "y": y, "alive": True, "in_formation": True, "formation_x": x, 
            "formation_y": y, "dive_timer": 0, "dive_state": None, "dive_dash": False
        }
    
    def SpawnEnemyFormation(wave):
        """Создает формацию врагов для текущей волны"""
        enemies[:] = []
        
        rows = min(3 + wave // 2, 5)
        cols = 8
        start_y = 0.15
        spacing_x = 0.08
        spacing_y = 0.08
        center_x = 0.5
        
        for row in range(rows):
            for col in range(cols):
                x = center_x + (col - cols / 2.0 + 0.5) * spacing_x
                y = start_y + row * spacing_y
                x = clamp(x, PLAY_AREA["xmin"] + 0.02, PLAY_AREA["xmax"] - 0.02)
                y = clamp(y, PLAY_AREA["ymin"] + 0.02, PLAY_AREA["ymax"] - 0.02)
                enemies.append(_create_enemy(x, y))

    def EnemyShoot(enemy):
        """Враг выпускает пулю"""
        if not enemy["alive"]:
            return

        renpy.sound.play("audio/enemyShootEffect.wav", channel = "enemy", relative_volume = 0.3)
        enemy_bullets.append({"x": enemy["x"], "y": enemy["y"], "vy": 0.015})

    def _update_formation_position():
        """Обновляет позицию формации врагов"""
        global formation_x_offset, formation_direction
        
        formation_x_offset += formation_direction * FORMATION_SPEED
        if formation_x_offset > FORMATION_MAX_OFFSET or formation_x_offset < -FORMATION_MAX_OFFSET:
            formation_direction *= -1
    
    def _update_enemy_in_formation(enemy):
        """Обновляет врага, находящегося в формации"""
        enemy["x"] = clamp(
            enemy["formation_x"] + formation_x_offset,
            PLAY_AREA["xmin"] + ENEMY_SIZE["hw"] / 2,
            PLAY_AREA["xmax"] - ENEMY_SIZE["hw"] / 2
        )
        
        enemy["dive_timer"] -= 1
        if enemy["dive_timer"] <= 0:
            if random.random() < 0.001 * current_wave:
                enemy["in_formation"] = False
                enemy["dive_state"] = "diving"
                enemy["dive_target_x"] = ship_data["x"]
            else:
                enemy["dive_timer"] = 60
        
        if random.random() < 0.002:
            EnemyShoot(enemy)
    
    def _update_enemy_diving(enemy):
        """Обновляет врага в состоянии пикирования"""
        if(enemy["x"] < ship_data["x"]):
            dx = -0.002
        else:
            dx = 0.002
        
        jiterryMovement = 0.003 * random.randint(-2, 2)
        dy = 0.015
        if (abs(enemy["x"] - ship_data["x"]) > 0.02):
            dy /= 5
            enemy["dive_dash"] = True

        if(dy == 0.015 and enemy["dive_dash"]):
            enemy["dive_dash"] = False
            DoLongAnimation(
                "dashAnim", enemy["x"], enemy["y"] + 0.03, ENEMY_SIZE["hw"], ENEMY_SIZE["hw"], 
                3, 3, 4, "enemyWoosh.wav", "dash", 3.0
            )
        
        enemy["x"] -= dx + jiterryMovement
        enemy["y"] += dy
        
        if random.random() < 0.01:
            EnemyShoot(enemy)
        
        if enemy["y"] > PLAY_AREA["ymax"]:
            enemy["dive_state"] = "returning"
    
    def _update_enemy_returning(enemy):
        """Обновляет врага, возвращающегося в формацию"""
        target_x = clamp(
            enemy["formation_x"] + formation_x_offset,
            PLAY_AREA["xmin"],
            PLAY_AREA["xmax"]
        )
        
        dx = (target_x - enemy["x"]) * 0.03
        dy = (enemy["formation_y"] - enemy["y"]) * 0.03
        
        enemy["x"] = clamp(enemy["x"] + dx, PLAY_AREA["xmin"], PLAY_AREA["xmax"])
        enemy["y"] = clamp(enemy["y"] + dy, PLAY_AREA["ymin"], PLAY_AREA["ymax"])
        
        if abs(enemy["x"] - target_x) < 0.02 and abs(enemy["y"] - enemy["formation_y"]) < 0.02:
            enemy["in_formation"] = True
            enemy["dive_state"] = None
            enemy["dive_timer"] = 120
    
    def UpdateEnemies():
        """Обновляет состояние всех врагов"""
        if not enemies or game_over:
            return
        
        _update_formation_position()
        
        for enemy in enemies:
            if not enemy["alive"]:
                continue

            if _rect_contains_point(
                ship_data["x"], ship_data["y"], ship_data["hitboxWidth"], 
                ship_data["hitboxHeight"], enemy["x"], enemy["y"]
            ):
                HitPlayer()
                HitEnemy(enemy)
            
            if enemy["in_formation"]:
                _update_enemy_in_formation(enemy)
            elif enemy["dive_state"] == "diving":
                _update_enemy_diving(enemy)
            elif enemy["dive_state"] == "returning":
                _update_enemy_returning(enemy)

    def UpdateEnemyBullets():
        """Обновляет вражеские пули и проверяет попадания по игроку"""
        global game_over
        
        if not enemy_bullets or game_over:
            return
        
        remaining = []
        for bullet in enemy_bullets:
            bullet["y"] += bullet["vy"]
            
            if not (PLAY_AREA["ymin"] <= bullet["y"] <= PLAY_AREA["ymax"]):
                continue
            
            if _rect_contains_point(
                ship_data["x"], ship_data["y"], ship_data["hitboxWidth"], 
                ship_data["hitboxHeight"], bullet["x"], bullet["y"]
            ):
                HitPlayer()
                continue
            
            remaining.append(bullet)
        
        enemy_bullets[:] = remaining

    def _check_bullet_hit(bullet):
        """Проверяет попадание пули по врагам. Возвращает True если попал"""
        for enemy in enemies:
            if enemy["alive"] and _rect_contains_point(
                enemy["x"], enemy["y"], ENEMY_SIZE["hw"], ENEMY_SIZE["hh"],
                bullet["x"], bullet["y"]
            ):
                HitEnemy(enemy)
                return True
        return False
    
    def UpdateBullets():
        """Обновляет пули игрока и проверяет попадания"""
        global current_wave
        
        if game_over:
            return
        
        # Обновляем позиции пуль
        for bullet in bullets:
            bullet["y"] += bullet["vy"]
        
        # Проверяем попадания и границы
        remaining_bullets = []
        for bullet in bullets:
            if not (PLAY_AREA["ymin"] <= bullet["y"] <= PLAY_AREA["ymax"]):
                continue
            
            if not _check_bullet_hit(bullet):
                remaining_bullets.append(bullet)
        
        bullets[:] = remaining_bullets
        enemies[:] = [e for e in enemies if e["alive"]]
        
        # Проверяем окончание волны
        if not enemies and not game_over:
            current_wave += 1
            SpawnEnemyFormation(current_wave)

    def ProcessInput():
        """Обрабатывает ввод с клавиатуры для управления кораблем"""
        if game_over:
            return
        
        keys = pygame.key.get_pressed()
        ship_data["dx"] = ship_data["dy"] = 0.0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            ship_data["dy"] -= ship_data["moveStep"]
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            ship_data["dy"] += ship_data["moveStep"]
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ship_data["dx"] -= ship_data["moveStep"]
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ship_data["dx"] += ship_data["moveStep"]
        
        if ship_data["dx"] != 0.0 or ship_data["dy"]!= 0.0:
            MoveShip(ship_data["dx"], ship_data["dy"])
        
    def ProcessIframes():
        """Обрабатывает фреймы непобедимости"""
        if(ship_data["is_iframe_active"]):
            ship_data["iframe_timer"] -= 1

            if(ship_data["iframe_timer"] <= 0):
                ship_data["is_iframe_active"] = False
                ship_data["iframe_timer"] = 60
      
    def HitPlayer():
        """Обрабатывает удар по игроку"""
        global game_over
        if not ship_data["is_iframe_active"]:
            ship_data["lives"] -= 1
            ship_data["is_iframe_active"] = True
            DoLongAnimation(
                "explosionAnim", ship_data["x"], ship_data["y"], ship_data["hitboxWidth"] * 4, 
                ship_data["hitboxHeight"] * 2, 1, 1, 11, "playerExplodes.wav", "playerHit"
            )
            MoveShip(0, 0.04)

        if ship_data["lives"] <= 0:
            game_over = True

    def HitEnemy(enemy):
        """Обрабатывает удар по вирусам"""
        enemy["alive"] = False
        ship_data["score"] += 100
        DoLongAnimation(
            "explosionAnim", enemy["x"], enemy["y"], ENEMY_SIZE["hw"] * 4, ENEMY_SIZE["hh"] * 4, 
            1, 1, 11, "enemyExplodes.wav", "explosions"
        )

    def UpdatePlayer():
        """вызывает отработок по игроку"""
        ProcessInput()
        ProcessIframes()
        
        if ship_data["weaponCooldown"] <= 0 and not ship_data["isWeaponReady"]:
            ship_data["isWeaponReady"] = True
            renpy.sound.play("audio/weaponReady.wav", channel = "player", relative_volume = 0.5)
        else:
            ship_data["weaponCooldown"] -= 1

    def DoLongAnimation(
        animationName, posX, posY, sizeX = 1, sizeY = 1, zoomX = 1, zoomY = 1,
        duration = 20, soundEffectPath = "", channelName = "default", volume = 0.4
    ):
        """Вызывает длинная анимация"""
        longAnimations.append({
            "name": animationName, "x": posX, "y": posY, "zoomX": zoomX, "zoomY": zoomY,
            "sizeX": sizeX, "sizeY": sizeY, "duration": duration
        })
        renpy.sound.play(soundEffectPath, channel = channelName, relative_volume = volume)

    def ProcessLongAnimations():
        """Обрабатывает длинных анимации"""
        pendingAnimations = []

        for longAnim in longAnimations:
            longAnim["duration"] -= 1

            if longAnim["duration"] > 0:
                pendingAnimations.append(longAnim)

        longAnimations[:] = pendingAnimations

    def HideGameScreens():
        """Скрывает все игровые экраны"""
        screens_to_hide = [
            "play_area_screen",
            "ship_screen",
            "keymap_screen",
            "bullets_screen",
            "enemy_bullets_screen",
            "enemies_screen",
            "hud_screen",
            "game_over_screen",
            "longAnimation_screen"
        ]
        
        for screen_name in screens_to_hide:
            renpy.hide_screen(screen_name)
        
        renpy.restart_interaction()

# === ЭКРАНЫ ===
screen keymap_screen():
    key "K_SPACE" action Function(FireBulletUp)
    timer GAME_UPDATE_RATE repeat True action Function(UpdatePlayer)

screen ship_screen():
    default alpha_values = [0.25, 0.50, 0.75, 1]
    default i = 0
    if(ship_data["is_iframe_active"]) and (ship_data["lives"] > 0):
        add "playerShip":
            alpha alpha_values[i]
            xysize (ship_data["hitboxWidth"] * 2, ship_data["hitboxHeight"])
            xycenter (ship_data["x"], ship_data["y"])
        $i += 1
        if (i > (len(alpha_values) - 1)):
            $i = 0
    elif ship_data["lives"] > 0:
        add "playerShip":
            xysize (ship_data["hitboxWidth"] * 2, ship_data["hitboxHeight"])
            xycenter (ship_data["x"], ship_data["y"])

    if(show_hitboxes):
        add Solid("#00ff0080") xysize (ship_data["hitboxWidth"], ship_data["hitboxHeight"]) xycenter (ship_data["x"], ship_data["y"])

screen bullets_screen():
    for b in bullets:
        add Solid("#00ff00") xysize (3, 10) xycenter (b["x"], b["y"])
    timer GAME_UPDATE_RATE repeat True action Function(UpdateBullets)

screen enemy_bullets_screen():
    for b in enemy_bullets:
        add Solid("#ff0000") xysize (3, 10) xycenter (b["x"], b["y"])
    timer GAME_UPDATE_RATE repeat True action Function(UpdateEnemyBullets)

screen longAnimation_screen():
    for longAnim in longAnimations:
        add ImageReference(longAnim["name"]):
            xzoom longAnim["zoomX"]
            yzoom longAnim["zoomY"]
            xysize (longAnim["sizeX"], longAnim["sizeY"])
            xycenter (longAnim["x"], longAnim["y"])
        
    timer GAME_UPDATE_RATE repeat True action Function(ProcessLongAnimations)

screen enemies_screen():
    for e in enemies:
        add Transform("virus-36904.png", xysize = (ENEMY_SIZE["hw"], ENEMY_SIZE["hh"])) xycenter (e["x"], e["y"])
        if show_enemy_hitboxes:
            add Solid("#00ff0080") xysize (ENEMY_SIZE["hw"], ENEMY_SIZE["hh"]) xycenter (e["x"], e["y"])
    timer GAME_UPDATE_RATE repeat True action Function(UpdateEnemies)

screen hud_screen():
    frame:
        xalign 0.5 yalign 0.0
        padding (20, 10)
        background "#00000080"
        hbox:
            spacing 40
            text "LIVES: [ship_data[\"lives\"]]" size 24 color "#ffffff"
            text "SCORE: [ship_data[\"score\"]]" size 24 color "#ffff00"
            text "WAVE: [current_wave]" size 24 color "#00ff00"

default space_shooter_return_to_caller = False

screen game_over_screen():
    if game_over:
        modal True
        frame:
            xalign 0.5 yalign 0.5
            padding (40, 30)
            background "#000000e0"
            vbox:
                spacing 20
                text "GAME OVER" size 48 color "#ff0000" xalign 0.5
                text "Final Score: [ship_data[\"score\"]]" size 32 color "#ffff00" xalign 0.5
                text "Wave Reached: [current_wave]" size 24 color "#00ff00" xalign 0.5
                if space_shooter_return_to_caller:
                    textbutton "Продолжить" action Return() xalign 0.5

screen play_area_screen():
    python:
        area_width = int((PLAY_AREA["xmax"] - PLAY_AREA["xmin"]) * config.screen_width)
        area_height = int((PLAY_AREA["ymax"] - PLAY_AREA["ymin"]) * config.screen_height)
    
    frame:
        xalign 0.5 yalign 0.5
        xysize (area_width, area_height)
        background None
        padding (0, 0)
        
        add Solid("#ffffff20")
        add Solid("#00ff00") xysize (area_width, 2) yalign 0.0
        add Solid("#00ff00") xysize (area_width, 2) yalign 1.0
        add Solid("#00ff00") xysize (2, area_height) xalign 0.0
        add Solid("#00ff00") xysize (2, area_height) xalign 1.0

# === ТОЧКА ВХОДА В ИГРУ ===
label game_space_shooter(return_to_caller=False):
    hide screen main_menu_screen
    $ space_shooter_return_to_caller = return_to_caller
    $ ResetGame()
    
    scene bgBlack
    show bgSpaceBackground
    
    show screen play_area_screen zorder 4
    show screen ship_screen zorder 3
    show screen keymap_screen
    show screen bullets_screen zorder 1
    show screen enemy_bullets_screen zorder 1
    show screen enemies_screen zorder 2
    show screen hud_screen zorder 5
    show screen game_over_screen zorder 5 
    show screen longAnimation_screen zorder 4
    
    $ renpy.pause(hard=True)
    
    # После завершения игры скрываем все игровые экраны перед возвратом
    $ HideGameScreens()
    $ space_shooter_return_to_caller = False
    return
