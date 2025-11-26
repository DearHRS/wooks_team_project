"""
Space Shooter (Galaga Style) - Mini Game

to do:
iframe Animtion, 
speedup animation for virus,
enemies attack while climbing up,
moving background
"""

# Анимация огня для корабля игрока
image playerShip1:
    animation
    "PlayerForward1.png"
    linear 0.1
    "PlayerForward2.png"
    linear 0.1
    "PlayerForward3.png"
    linear 0.1
    repeat

# === ПЕРЕМЕННЫЕ ИГРЫ ===
default ship_data = {
    "x": 0.5, "y": 0.9, 
    "is_iframe_active" : True, 
    "iframe_timer" : 10,
    "player_lives" : 3,
    "score" : 0
    }
default moveStep = 0.005
default shipBounds = { "xmin": 0.25, "xmax": 0.75, "ymin": 0.7, "ymax": 0.95 }
default play_area = { "xmin": 0.25, "xmax": 0.75, "ymin": 0.05, "ymax": 0.95 }
default shipMuzzleOffsetX = 0.03
default shipMuzzleForwardY = -0.03
default bullets = []
default bullet_step = 0.025
```
<summary>
enemies_dict; array of dictionaries which contains parameters for enemy
</summary>
    x position              "x"
    y position              "y"
    aliveBool               "alive"
    hitboxWidth             "hw"
    hitboxHeight            "hh"
    "hb_px_w"
    "hb_px_h"
    enemyInFormationBool    "in_formation" 
    formationInWidth        "formation_x" 
    formartionInHeight      "formation_y"
    timeBeforeDive          "dive_timer"
    enemyIsInDive           "dive_state"
```
default enemies_dict = []
default enemySize = { "hw": 0.015, "hh": 0.02 }
default show_enemy_hitboxes = False
default enemy_bullets = []
default enemy_bullet_step = 0.015
default current_wave = 1
default game_over = False
default formation_x_offset = 0.0
default formation_direction = 1
default formation_speed = 0.002

# === ЛОГИКА ИГРЫ ===
init python:
    import pygame
    import random
    
    config.keymap['screenshot'].remove('noshift_K_s') #removes failed screenshot attempt error message

    def FireBulletUp(side):
        if game_over:
            return

        offset_x = shipMuzzleOffsetX if side == "right" else -shipMuzzleOffsetX
        spawn_x = max(0.0, min(1.0, ship_data["x"] + offset_x))
        spawn_y = max(0.0, min(1.0, ship_data["y"] + shipMuzzleForwardY))
        bullets.append({ "x": spawn_x, "y": spawn_y, "vx": 0.0, "vy": -bullet_step })

    def _is_point_in_rect(ex, ey, hw, hh, px, py):
        return (ex - hw) <= px <= (ex + hw) and (ey - hh) <= py <= (ey + hh)

    def ResetGame():
        global current_wave, game_over, formation_x_offset, formation_direction
        ship_data["x"] = 0.5
        ship_data["y"] = 0.9
        ship_data["is_iframe_active"] = True
        ship_data["player_lives"] = 1000
        ship_data["score"] = 0
        current_wave = 1
        game_over = False
        formation_x_offset = 0.0
        formation_direction = 1
        bullets[:] = []
        enemies_dict[:] = []
        enemy_bullets[:] = []
        SpawnEnemyFormation(current_wave)
        renpy.restart_interaction()

    def SpawnEnemyFormation(wave):
        enemies_dict[:] = []
        rows = min(3 + wave // 2, 5)
        cols = 8
        start_y = 0.15
        spacing_x = 0.08
        spacing_y = 0.08
        center_x = 0.5
        
        for row in range(rows):
            for col in range(cols):
                x = center_x + (col - cols/2.0 + 0.5) * spacing_x
                y = start_y + row * spacing_y
                x = max(play_area["xmin"] + 0.02, min(play_area["xmax"] - 0.02, x))
                y = max(play_area["ymin"] + 0.02, min(play_area["ymax"] - 0.02, y))
                hw = enemySize["hw"]
                hh = enemySize["hh"]
                sw = renpy.config.screen_width
                sh = renpy.config.screen_height
                hb_px_w = int(hw * sw * 2)
                hb_px_h = int(hh * sh * 2)
                enemies_dict.append({
                    "x": x, "y": y, "hw": hw, "hh": hh,
                    "alive": True, "hb_px_w": hb_px_w, "hb_px_h": hb_px_h,
                    "in_formation": True, "formation_x": x, "formation_y": y,
                    "dive_timer": 0, "dive_state": None
                })

    def EnemyShoot(enemy):
        if not enemy["alive"]:
            return
        
        enemy_bullets.append({
            "x": enemy["x"], "y": enemy["y"],
            "vx": 0.0, "vy": enemy_bullet_step
        })

    def UpdateEnemies():
        global formation_x_offset, formation_direction
        if not enemies_dict or game_over:
            return
        
        formation_x_offset += formation_direction * formation_speed
        if formation_x_offset > 0.08 or formation_x_offset < -0.08:
            formation_direction *= -1
        
        for enemy in enemies_dict:
            if not enemy["alive"]:
                continue
            
            if enemy["in_formation"]:
                enemy["x"] = max(play_area["xmin"], min(play_area["xmax"], enemy["formation_x"] + formation_x_offset))
                enemy["dive_timer"] -= 1
                if enemy["dive_timer"] <= 0:
                    if random.random() < 0.01:
                        enemy["in_formation"] = False
                        enemy["dive_state"] = "diving"
                    else:
                        enemy["dive_timer"] = 5

                if random.random() < 0.002:
                    EnemyShoot(enemy)
            else:
                if enemy["dive_state"] == "diving":
                    if(enemy["x"] < ship_data["x"]):
                        dx = -0.002
                    else:
                        dx = 0.002
                    
                    jiterryMovement = 0.003 * random.randint(-2, 2)
                    dy = 0.015
                    if (abs(enemy["x"] - ship_data["x"]) > 0.02):
                        dy /= 10
                    
                    enemy["x"] -= dx + jiterryMovement
                    enemy["y"] += dy

                    if random.random() < 0.05:
                        EnemyShoot(enemy)

                    if enemy["y"] > play_area["ymax"]:
                        enemy["dive_state"] = "returning"

                elif enemy["dive_state"] == "returning":
                    target_x = max(play_area["xmin"], min(play_area["xmax"], enemy["formation_x"] + formation_x_offset))
                    dx = (target_x - enemy["x"]) * 0.03
                    dy = (enemy["formation_y"] - enemy["y"]) * 0.03
                    enemy["x"] = max(play_area["xmin"], min(play_area["xmax"], enemy["x"] + dx))
                    enemy["y"] = max(play_area["ymin"], min(play_area["ymax"], enemy["y"] + dy))
                    if abs(enemy["x"] - target_x) < 0.02 and abs(enemy["y"] - enemy["formation_y"]) < 0.02:
                        enemy["in_formation"] = True
                        enemy["dive_state"] = None
                        enemy["dive_timer"] = 10

    def UpdateEnemyBullets():
        global game_over

        if not enemy_bullets or game_over:
            return

        remaining = []
        for bullet in enemy_bullets:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

            if not (-0.1 <= bullet["x"] <= 1.1 and -0.1 <= bullet["y"] <= 1.1):
                continue
            
            ship_hw = 0.03
            ship_hh = 0.04
            
            if _is_point_in_rect(ship_data["x"], ship_data["y"], 
            ship_hw, ship_hh, bullet["x"], bullet["y"]):
                HitPlayer()
                continue

            remaining.append(bullet)

        enemy_bullets[:] = remaining

    def UpdateBullets():
        global current_wave

        if game_over:
            return

        for bullet in bullets:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

        remaining_bullets = []
        for bullet in bullets:
            if not (-0.1 <= bullet["x"] <= 1.1 and -0.1 <= bullet["y"] <= 1.1):
                continue

            hit = False
            for enemy in enemies_dict:
                if enemy["alive"] and _is_point_in_rect(enemy["x"], enemy["y"], enemy["hw"], enemy["hh"], bullet["x"], bullet["y"]):
                    enemy["alive"] = False
                    hit = True
                    ship_data["score"] += 100
                    break

            if not hit:
                remaining_bullets.append(bullet)

        bullets[:] = remaining_bullets
        enemies_dict[:] = [enemy for enemy in enemies_dict if enemy["alive"]]

        if not enemies_dict and not game_over:
            current_wave += 1
            SpawnEnemyFormation(current_wave)

    def ProcessInput():
        if game_over:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= moveStep
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += moveStep
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= moveStep
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += moveStep
        if dx != 0.0 or dy != 0.0:
            MoveShip(dx, dy)

    def ProcessIframes():
        if(ship_data["is_iframe_active"] == True):
            ship_data["iframe_timer"] -= 1

            if(ship_data["iframe_timer"] <= 0):
                ship_data["is_iframe_active"] = False
                ship_data["iframe_timer"] = 60
        
    def HitPlayer():
        global game_over
        if not ship_data["is_iframe_active"]:
            ship_data["player_lives"] -= 1
            ship_data["is_iframe_active"] = True;

        if ship_data["player_lives"] <= 0:
            game_over = True
    
    def MoveShip(dx, dy):
        ship_data["x"] = max(shipBounds["xmin"], min(shipBounds["xmax"], ship_data["x"] + dx))
        ship_data["y"] = max(0.0, min(1.0, ship_data["y"] + dy))

    def UpdatePlayer():
        ProcessInput()
        ProcessIframes()

    def HideGameScreens():
        renpy.hide_screen("play_area_screen")
        renpy.hide_screen("ship_screen")
        renpy.hide_screen("player_screen")
        renpy.hide_screen("bullets_screen")
        renpy.hide_screen("enemy_bullets_screen")
        renpy.hide_screen("enemies_screen")
        renpy.hide_screen("hud_screen")
        renpy.hide_screen("game_over_screen")
        renpy.restart_interaction()

# === ЭКРАНЫ ===
screen player_screen():
    #key "K_q" action Function(FireBulletUp, "left")
    #key "K_e" action Function(FireBulletUp, "right")
    key "K_SPACE" action [Function(FireBulletUp, "right"), Function(FireBulletUp, "left")]
    $ UpdatePlayer()
    timer 0.02 repeat True

screen ship_screen():
    zorder 100
    add "playerShip1" xalign ship_data["x"] yalign ship_data["y"]

screen bullets_screen():
    zorder 110
    for bullet in bullets:
        add Solid("#00ff00") xysize (3, 10) xalign bullet["x"] yalign bullet["y"]
    timer 0.02 repeat True action Function(UpdateBullets)

screen enemy_bullets_screen():
    zorder 110
    for bullet in enemy_bullets:
        add Solid("#ff0000") xysize (3, 10) xalign bullet["x"] yalign bullet["y"]
    timer 0.02 repeat True action Function(UpdateEnemyBullets)

screen enemies_screen():
    zorder 105
    for enemy in enemies_dict:
        add Transform("virus-36904.png", xysize=(enemy["hb_px_w"], enemy["hb_px_h"])) xalign enemy["x"] yalign enemy["y"]
        if show_enemy_hitboxes:
            add Solid("#00ff0080") xysize (enemy["hb_px_w"], enemy["hb_px_h"]) xalign enemy["x"] yalign enemy["y"]
    timer 0.02 repeat True action Function(UpdateEnemies)

screen hud_screen():
    zorder 200
    frame:
        xalign 0.5 yalign 0.0
        padding (20, 10)
        background "#00000080"
        hbox:
            spacing 40
            text "LIVES: [ship_data[\"player_lives\"]]" size 24 color "#ffffff"
            text "Score: [ship_data[\"score\"]]" size 24 color "#ffff00"
            text "WAVE: [current_wave]" size 24 color "#00ff00"

screen game_over_screen():
    if game_over:
        zorder 300
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
                textbutton "Restart" action Function(ResetGame) xalign 0.5
                textbutton "Return to Menu" action [Function(HideGameScreens), Jump("main_menu")] xalign 0.5

screen play_area_screen():
    zorder 50
    frame:
        xalign 0.5 yalign 0.5
        xysize (int((play_area["xmax"] - play_area["xmin"]) * config.screen_width), 
                int((play_area["ymax"] - play_area["ymin"]) * config.screen_height))
        background None
        padding (0, 0)
        add Solid("#ffffff20")
        add Solid("#00ff00") xysize (int((play_area["xmax"] - play_area["xmin"]) * config.screen_width), 2) yalign 0.0
        add Solid("#00ff00") xysize (int((play_area["xmax"] - play_area["xmin"]) * config.screen_width), 2) yalign 1.0
        add Solid("#00ff00") xysize (2, int((play_area["ymax"] - play_area["ymin"]) * config.screen_height)) xalign 0.0
        add Solid("#00ff00") xysize (2, int((play_area["ymax"] - play_area["ymin"]) * config.screen_height)) xalign 1.0

# === ТОЧКА ВХОДА В ИГРУ ===
label game_space_shooter:
    hide screen main_menu_screen
    $ ResetGame()
    scene bgBlack
    show bgSpaceBackground
    show screen play_area_screen
    show screen ship_screen
    show screen player_screen
    show screen bullets_screen
    show screen enemy_bullets_screen
    show screen enemies_screen
    show screen hud_screen
    show screen game_over_screen
    $ renpy.pause(hard=True)
