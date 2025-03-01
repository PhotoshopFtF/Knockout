import pygame
from pygame import MOUSEBUTTONDOWN, USEREVENT

pygame.mixer.init()
all = pygame.sprite.Group()
clock = pygame.time.Clock()

pygame.mixer.music.load("data/music1.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

hit_sound = pygame.mixer.Sound("data/sword.wav")
hit_sound.set_volume(0.7)

hp = 50
hp_boss = 50
on_ground = True
end_round = False
moving_left = False
moving_right = False

dash = pygame.image.load('data/dash.png')
dragon_im = pygame.image.load('data/dragon.png')
goblin_im = pygame.image.load('data/goblin.png')

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, *group):
        super().__init__(*group)
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_text(screen, text, font_size, color, x, y):
    font = pygame.font.SysFont('Arial', font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

class Counter(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        counter_im = pygame.image.load('data/counter.png')
        self.image = counter_im
        self.rect = counter_im.get_rect()
        self.mask = pygame.mask.from_surface(counter_im)

class Hero(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        mc = pygame.image.load('data/MC_project.png')
        self.image = mc
        self.rect = mc.get_rect()
        self.mask = pygame.mask.from_surface(mc)
        self.rect.x, self.rect.y = 50, 200
        self.a = 2500
        self.v = -1000
        self.speed = 350

    def counter(self):
        global hp_boss
        counter = Counter()
        counter.rect.x = self.rect.x + 70
        counter.rect.y = self.rect.y + 20

        if pygame.sprite.collide_mask(counter, Boss()):
            hp_boss -= 5
            all.add(counter)
        pygame.time.set_timer(pygame.USEREVENT + 1, 125, loops=1)

    def jump(self):
        global on_ground
        if on_ground:
            self.v = -1000
            on_ground = False

    def update_jump(self):
        global on_ground
        dt = clock.tick(60) / 1000
        if not on_ground:
            self.v += self.a * dt
            self.rect.y += self.v * dt
            if self.rect.y >= 200:
                self.v = 0
                self.rect.y = 200
                on_ground = True

    def update(self):
        dt = clock.get_time() / 1000
        if moving_left:
            self.rect.x -= self.speed * dt
        if moving_right:
            self.rect.x += self.speed * dt

hero = Hero()

class Bullets(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def attack(self):
        global hp
        if pygame.sprite.collide_mask(self, hero):
            hp -= 5
            hit_sound.play()

class Hit(Bullets):
    def __init__(self, x, y, *group):
        hit_im = pygame.image.load('data/hit.png')
        super().__init__(*group)
        self.image = hit_im
        self.rect = hit_im.get_rect()
        self.rect.x = x
        self.rect.y = y

class Fireball(Bullets):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        fireball_im = pygame.image.load('data/fireball.png')
        self.image = fireball_im
        self.rect = fireball_im.get_rect()
        self.rect.x = x
        self.rect.y = y

    def fly(self):
        if not end_round:
            self.rect.x -= 200 * clock.get_time() / 1000
            if self.rect.x <= -128:
                self.kill()
                dragon.reset_fire()
            self.attack()

    def update(self):
        if not end_round:
            if pygame.sprite.collide_rect(self, hero) and not end_round:
                global hp
                hp -= 5
                self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.rect = goblin_im.get_rect()
        self.image = goblin_im
        self.own = self.image
        self.speed = 1500
        self.moving_left = True
        self.mask = pygame.mask.from_surface(self.image)
        self.hit_start_time = 0
        self.start_hit = False
        self.rect.x = 400
        self.rect.y = 200

    def hit(self):
        current_time = pygame.time.get_ticks()

        if on_ground and current_time - self.hit_start_time > 2000 and not end_round:
            self.start_hit = True

        if self.start_hit:
            if self.moving_left:
                self.image = dash
                self.rect.x -= self.speed * clock.get_time() / 1000
                if self.rect.x <= hero.rect.x + 60:
                    self.moving_left = False
                    self.image = self.own
                    hit = Hit(self.rect.x - 10, self.rect.y + 60, all)
                    all.add(hit)
                    pygame.time.set_timer(pygame.USEREVENT, 125, loops=1)
                    hit.attack()
                    pygame.time.wait(50)
            else:
                self.rect.x += self.speed * clock.get_time() / 1000
                self.image = dash
                if self.rect.x >= 400:
                    self.moving_left = True
                    self.image = self.own
                    self.hit_start_time = current_time
                    self.start_hit = False

goblin = Boss()

class Dragon(Boss):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = dragon_im
        self.rect = dragon_im.get_rect()
        self.rect.x = 400
        self.rect.y = 180
        self.own = self.image
        self.start_fire_time = 0
        self.fired = False
        self.start_pos = True

    def fire(self):
        current_time = pygame.time.get_ticks()

        if self.rect.x == 400:
            self.start_pos = True
        else:
            self.start_pos = False

        if not self.fired and current_time - self.start_fire_time > 1000 and self.start_pos:
            self.fired = True
            self.start_fire_time = current_time
            fireball1 = Fireball(self.rect.x - 125, self.rect.y)
            fireball2 = Fireball(self.rect.x - 200, self.rect.y - 250)
            all.add(fireball1, fireball2)
            pygame.time.set_timer(pygame.USEREVENT + 2, 2000, loops=1)

    def reset_fire(self):
        self.fired = False

dragon = Dragon()

gameover = pygame.image.load('data/gameover.png')
gameover_sprite = pygame.sprite.Sprite()
gameover_sprite.image = gameover
gameover_sprite.rect = gameover.get_rect()
gameover_sprite.rect.x = -600
gameover_sprite.rect.y = 0

victory = pygame.image.load('data/victory.jpg')
victory_sprite = pygame.sprite.Sprite()
victory_sprite.image = victory
victory_sprite.rect = victory.get_rect()
victory_sprite.rect.x = -600
victory_sprite.rect.y = 0

background = pygame.image.load('data/background.jpg')
background_sprite = pygame.sprite.Sprite()
background_sprite.image = background
background_sprite.rect = background.get_rect()

play_button = pygame.image.load('data/Play_button-1.png.png')
play_button_sprite = pygame.sprite.Sprite()
play_button_sprite.image = play_button
play_button_sprite.rect = play_button.get_rect()
play_button_sprite.rect.x = 257
play_button_sprite.rect.y = 125
all.add(play_button_sprite)

exit_button = pygame.image.load('data/exit_button.png')
exit_button_sprite = pygame.sprite.Sprite()
exit_button_sprite.image = exit_button
exit_button_sprite.rect = exit_button.get_rect()
exit_button_sprite.rect.x = 257
exit_button_sprite.rect.y = 200
all.add(exit_button_sprite)

one = pygame.image.load('data/one.png')
one_sprite = pygame.sprite.Sprite()
one_sprite.image = one
one_sprite.rect = one.get_rect()
one_sprite.rect.x = 50
one_sprite.rect.y = 50

two = pygame.image.load('data/two.png')
two_sprite = pygame.sprite.Sprite()
two_sprite.image = two
two_sprite.rect = two.get_rect()
two_sprite.rect.x = 445
two_sprite.rect.y = 50

arrow = pygame.image.load('data/arrow.png')
arrow_sprite = pygame.sprite.Sprite()
arrow_sprite.image = arrow
arrow_sprite.rect = arrow.get_rect()
all.add(arrow_sprite)

a, b  = 600, 350

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    size = int(a), int(b)
    pygame.display.set_caption('ОАтака')
    screen = pygame.display.set_mode(size)

    easy_button_im = pygame.Surface((200, 50))
    easy_button_im.fill((0, 255, 0))
    easy_text = pygame.font.SysFont('Arial', 24).render('Легкий', True, (0, 0, 0))
    easy_button_im.blit(easy_text, (60, 10))
    easy_button = pygame.sprite.Sprite()
    easy_button.image = easy_button_im
    easy_button.rect = easy_button_im.get_rect()
    easy_button.rect.x = 100
    easy_button.rect.y = 150

    medium_button_im = pygame.Surface((200, 50))
    medium_button_im.fill((255, 255, 0))
    medium_text = pygame.font.SysFont('Arial', 24).render('Средний', True, (0, 0, 0))
    medium_button_im.blit(medium_text, (60, 10))
    medium_button = pygame.sprite.Sprite()
    medium_button.image = medium_button_im
    medium_button.rect = medium_button_im.get_rect()
    medium_button.rect.x = 350
    medium_button.rect.y = 150

    hard_button_im = pygame.Surface((200, 50))
    hard_button_im.fill((255, 0, 0))
    hard_text = pygame.font.SysFont('Arial', 24).render('Сложный', True, (0, 0, 0))
    hard_button_im.blit(hard_text, (60, 10))
    hard_button = pygame.sprite.Sprite()
    hard_button.image = hard_button_im
    hard_button.rect = hard_button_im.get_rect()
    hard_button.rect.x = 100
    hard_button.rect.y = 250

    difficulty = None

    screen_state = 'main_menu'

    running = True

    while running:
        screen.fill((0, 0, 0))

        if screen_state == 'main_menu':
            screen.blit(background, (0, 0))
            screen.blit(play_button_sprite.image, play_button_sprite.rect)
            screen.blit(exit_button_sprite.image, exit_button_sprite.rect)
            screen.blit(arrow_sprite.image, arrow_sprite.rect)

            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                arrow_sprite.rect.x = x
                arrow_sprite.rect.y = y
                pygame.mouse.set_visible(False)
            else:
                pygame.mouse.set_visible(True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_sprite.rect.collidepoint(event.pos):
                        screen_state = 'difficulty_menu'
                    elif exit_button_sprite.rect.collidepoint(event.pos):
                        running = False

        elif screen_state == 'difficulty_menu':
            hp = 50
            hp_boss = 50
            end_round = False
            dragon = None
            goblin = None
            screen.blit(background, (0, 0))
            screen.blit(one_sprite.image, one_sprite.rect)
            screen.blit(two_sprite.image, two_sprite.rect)
            screen.blit(easy_button.image, easy_button.rect)
            screen.blit(medium_button.image, medium_button.rect)
            screen.blit(hard_button.image, hard_button.rect)
            screen.blit(arrow_sprite.image, arrow_sprite.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_button.rect.collidepoint(event.pos):
                        hp_boss = 30
                    elif medium_button.rect.collidepoint(event.pos):
                        hp_boss = 50
                    elif hard_button.rect.collidepoint(event.pos):
                        hp_boss = 70
                    elif two_sprite.rect.collidepoint(event.pos):
                        screen_state = 'dragon'
                        dragon = Dragon()
                    elif one_sprite.rect.collidepoint(event.pos):
                        screen_state = 'goblin'
                        goblin = Boss()

            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                arrow_sprite.rect.x = x
                arrow_sprite.rect.y = y
                pygame.mouse.set_visible(False)
            else:
                pygame.mouse.set_visible(True)

        elif screen_state == 'dragon':
            all.add(background_sprite)
            all.add(hero)
            all.add(dragon)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        hero.jump()
                    if event.key == pygame.K_a:
                        moving_left = True
                    if event.key == pygame.K_d:
                        moving_right = True
                    if event.key == pygame.K_e and not end_round:
                        hero.counter()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        moving_left = False
                    if event.key == pygame.K_d:
                        moving_right = False

                if event.type == pygame.USEREVENT:
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()

                if event.type == pygame.USEREVENT + 1:
                    for sprite in all:
                        if isinstance(sprite, Counter):
                            sprite.kill()

                for event in pygame.event.get():
                    if event.type == pygame.USEREVENT + 2:
                        dragon.reset_fire()

            if hp == 0:
                all.add(gameover_sprite)
                permission = False
                end_round = True
                if gameover_sprite.rect.x >= 0:
                    gameover_sprite.rect.x = 0
                    permission = True
                else:
                    gameover_sprite.rect.x += 400 * clock.get_time() / 1000
                if permission:
                    pygame.time.wait(1500)
                    screen_state = 'difficulty_menu'
                    dragon.kill()
                    gameover_sprite.kill()
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()
                        if isinstance(sprite, Fireball):
                            sprite.kill()

            if hp_boss == 0:
                all.add(victory_sprite)
                permission = False
                end_round = True
                if victory_sprite.rect.x >= 0:
                    victory_sprite.rect.x = 0
                    permission = True
                else:
                    victory_sprite.rect.x += 400 * clock.get_time() / 1000
                if permission:
                    pygame.time.wait(1500)
                    screen_state = 'difficulty_menu'
                    dragon.kill()
                    victory_sprite.kill()
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()
                        if isinstance(sprite, Fireball):
                            sprite.kill()
            print(hp_boss)
            all.draw(screen)
            dragon.hit()
            dragon.fire()
            hero.update()
            hero.update_jump()
            for sprite in all:
                if isinstance(sprite, Fireball):
                    sprite.fly()
                    sprite.update()
            pygame.display.flip()
            clock.tick(60)

        elif screen_state == 'goblin':
            all.add(background_sprite)
            all.add(hero)
            all.add(goblin)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        hero.jump()
                    if event.key == pygame.K_a:
                        moving_left = True
                    if event.key == pygame.K_d:
                        moving_right = True
                    if event.key == pygame.K_e and not end_round:
                        hero.counter()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        moving_left = False
                    if event.key == pygame.K_d:
                        moving_right = False

                if event.type == pygame.USEREVENT:
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()

                if event.type == pygame.USEREVENT + 1:
                    for sprite in all:
                        if isinstance(sprite, Counter):
                            sprite.kill()

            if hp == 0:
                all.add(gameover_sprite)
                permission = False
                end_round = True
                if gameover_sprite.rect.x >= 0:
                    gameover_sprite.rect.x = 0
                    permission = True
                else:
                    gameover_sprite.rect.x += 400 * clock.get_time() / 1000
                if permission:
                    pygame.time.wait(1500)
                    screen_state = 'difficulty_menu'
                    goblin.kill()
                    gameover_sprite.kill()
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()
                        if isinstance(sprite, Fireball):
                            sprite.kill()

            if hp_boss == 0:
                all.add(victory_sprite)
                permission = False
                end_round = True
                if victory_sprite.rect.x >= 0:
                    victory_sprite.rect.x = 0
                    permission = True
                else:
                    victory_sprite.rect.x += 400 * clock.get_time() / 1000
                if permission:
                    pygame.time.wait(1500)
                    screen_state = 'difficulty_menu'
                    goblin.kill()
                    victory_sprite.kill()
                    for sprite in all:
                        if isinstance(sprite, Hit):
                            sprite.kill()
                        if isinstance(sprite, Fireball):
                            sprite.kill()
            print(hp)
            all.draw(screen)
            goblin.hit()
            hero.update()
            hero.update_jump()
            pygame.display.flip()
            clock.tick(60)
        pygame.display.flip()
    pygame.quit()