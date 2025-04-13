from pygame import *
from random import randint, choice
import threading

init()
mixer.init(frequency=22050, size=-16, channels=2)
window = display.set_mode((700, 500))
display.set_caption('Шутер')

clock = time.Clock()
background = transform.scale(image.load('galaxy.jpg'), (700, 500))
mixer.music.load('space.ogg')
mixer.music.play(-1)
mixer.music.set_volume(-1)
fire = mixer.Sound('fire.ogg')

bullets = sprite.Group()
ufos = sprite.Group()
boosters = sprite.Group()

class GameSprite(sprite.Sprite):
    def __init__(self, image_path, speed, x, y):
        super().__init__()
        self.image = transform.scale(image.load(image_path), (65, 65))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image_path, speed, x, y):
        super().__init__(image_path, speed, x, y)
        self.last_shot_time = 0
        self.shoot_delay = 200

    def update(self):
        keys = key.get_pressed()
        if (keys[K_a] or keys[K_LEFT]) and self.rect.x > self.speed + 5:
            self.rect.x -= self.speed
        if (keys[K_d] or keys[K_RIGHT]) and self.rect.x < 640 - self.speed - 5:
            self.rect.x += self.speed
    
    def fire(self):
        current_time = time.get_ticks()
        keys_pressed = key.get_pressed()
        if keys_pressed[K_SPACE] and current_time - self.last_shot_time > self.shoot_delay:
            bullet = Bullet('bullet.png', 10, self.rect.x + 20, self.rect.y)
            bullets.add(bullet)
            fire.play()
            self.last_shot_time = current_time

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= 500:
            global missed_ufos
            missed_ufos += 1
            self.reset_position()

    def reset_position(self):
        self.rect.x = randint(0, 640)
        self.rect.y = randint(-100, -50)

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        self.image = transform.scale(self.image, (20, 20))
        if self.rect.y <= 10:
            self.kill()

class Booster(GameSprite):
    def __init__(self, image_path, speed, x, y):
        super().__init__(image_path, speed, x, y)
        self.active = False
        self.start_time = 0
        self.duration = 15

    def activate(self):
        self.active = True
        self.start_time = time.get_ticks()

    def update(self):
        self.rect.y += 3
        if self.active:
            elapsed_time = (time.get_ticks() - self.start_time) / 1000
            if elapsed_time >= self.duration:
                self.active = False
                return False  
            else:
                return self.duration - elapsed_time 
        if self.rect.y > 500: 
            self.kill()
        return None

label_font = font.SysFont('Arial', 70)

destroyed_ufos = 0
missed_ufos = 0
victory_condition = 500
defeat_condition = 150

for i in range(10):
    ufos.add(Enemy('ufo.png', randint(3, 5), randint(0, 640), randint(-100, -50)))

player = Player('rocket.png', 5, 200, 430)

booster = Booster('surprise1.jpg', 0, randint(0, 640), randint(-100, -50))
booster_spawned = False
booster_active = False

booster_spawn_time = 25000
last_booster_spawn_time = time.get_ticks()

game = True
game_over = False
victory = False

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False

    if not game_over:
        window.blit(background, (0, 0))
        bullets.update()
        bullets.draw(window)
        ufos.update()
        ufos.draw(window)
        player.update()
        player.reset()

        collided = sprite.groupcollide(bullets, ufos, True, False)
        for bullet, ufo_list in collided.items():
            destroyed_ufos += 1
            for ufo in ufo_list:
                ufo.reset_position()

       
        current_time = time.get_ticks()
        if not booster_active and current_time - last_booster_spawn_time > booster_spawn_time:
            booster_spawned = True
            booster.rect.x = randint(0, 640)
            booster.rect.y = -50  
            last_booster_spawn_time = current_time 

        if booster_spawned:
            booster.update()
            booster.reset()
            if player.rect.colliderect(booster.rect):
                booster.activate()
                booster_active = True
                booster_spawned = False 

    
        if booster_active:
            for ufo in ufos:
                ufo.speed = 1  
            remaining_time = booster.update()
            if remaining_time is Arial:
                booster_active = False
                for ufo in ufos:
                    ufo.speed = randint(3, 5) 

        window.blit(label_font.render(f'Уничтожено: {destroyed_ufos}', 1, (255, 255, 255)), (10, 5))
        window.blit(label_font.render(f'Пропущено: {missed_ufos}', 1, (255, 255, 255)), (20, 60))

        if booster_active:
            window.blit(label_font.render(f'Замедление: {remaining_time:.1f} сек', 1, (255, 255, 255)), (10, 15))

        player.fire()
        
        if destroyed_ufos >= victory_condition:
            victory = True
            game_over = True
        elif missed_ufos >= defeat_condition:
            game_over = True

    else:
        window.fill((0, 0, 0))
        if victory:
            window.blit(label_font.render('Ты победил!', 1, (0, 255, 0)), (200, 200))
        else:
            window.blit(label_font.render('Ты проиграл!', 1, (255, 0, 0)), (200, 200))
        
        window.blit(label_font.render('Нажмите R для перезапуска', 1, (255, 255, 255)), (9, 300))
        display.update()

        keys = key.get_pressed()
        if keys[K_r]:
            destroyed_ufos = 0
            missed_ufos = 0
            victory = False
            game_over = False
            bullets.empty()
            ufos.empty()
            for i in range(10):
                ufos.add(Enemy('ufo.png', randint(3, 5), randint(0, 640), randint(-100, -50)))
            booster_active = False
            booster_spawned = False
            last_booster_spawn_time = time.get_ticks() 

    display.update()
    clock.tick(60)

quit()