# Importando Bibliotecas
import pygame
import os
import random
from abc import ABC, abstractmethod
from assets import SNOWBALL_IMG, COOKIE_IMG, THROW_SOUND, SNOW_SOUND, SANTAHAT_GAME
from config import WIDTH, HEIGHT, GRAVITY, WALKING, SPAWN

"""

O código da classe Background foi tirado do artigo do seguinte website:
https://coderslegacy.com/python/pygame-scrolling-background/

"""

class Background:
    def __init__(self):

        #Imagem background jogo 
        self.image = pygame.image.load(os.path.join('Assets','Images','BG_02.png')).convert_alpha() # abre a imagem de fundo

    
        self.rect = self.image.get_rect() # pega algumas informações de posição da imagem

        #Posições
        self.x1 = 0 # posição X inicial da "primeira imagem"
        self.y1 = 0 # posição Y inicial da "primeira imagem"
        self.x2 = self.rect.width # posição X inicial da "segunda imagem"
        self.y2 = 0 # posição Y inicial da "segunda imagem"

        #Velocidade que o fundo move
        self.velocidade = 0.15 # define a velocidade de deslocamento das imagens

    def uptade(self, delta_time): # função que faz com que quando uma imagem sai da tela, outra entra em seguida

        self.x1 -= self.velocidade * delta_time
        self.x2 -= self.velocidade * delta_time

        if self.x1 <= - self.rect.width:
            self.x1 = self.rect.width
        if self.x2 <= - self.rect.width:
            self.x2 = self.rect.width

    def render(self, surface, score): # função que "blita" as imagens na janela (surface)

        #Colocando Score durante o jogo
        score_fnt = pygame.font.Font('Assets/Font/PressStart2P.ttf', 28)
        text_surface = score_fnt.render("{:08d}".format(score), True, (220, 20, 60))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (WIDTH / 2,  30)

        #Atualizando
        surface.blit(self.image, (self.x1, self.y1))
        surface.blit(self.image, (self.x2, self.y2))
        surface.blit(text_surface, text_rect)



#Função para sprite sheets, adaptada do handout fornecido pelos professores

def load_spritesheet(spritesheet, rows, columns):
    # Calcula a largura e altura de cada sprite.
    sprite_width = spritesheet.get_width() // columns
    sprite_height = spritesheet.get_height() // rows

    # Percorre todos os sprites adicionando em uma lista.
    sprites = []
    for row in range(rows):
        for column in range(columns):
            # Calcula posição do sprite atual
            x = column * sprite_width
            y = row * sprite_height
            # Define o retângulo que contém o sprite atual
            dest_rect = pygame.Rect(x, y, sprite_width, sprite_height)

            # Cria uma imagem vazia do tamanho do sprite
            image = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            # Copia o sprite atual (do spritesheet) na imagem
            image.blit(spritesheet, (0, 0), dest_rect)
            sprites.append(image)

    return sprites

#Classe Santa
class Santa(pygame.sprite.Sprite):

    # Construtor da classe. O argumento player_sheet é uma imagem contendo um spritesheet.
    def __init__(self, player_sheet,groups, assets):

        # Construtor da classe pai (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Aumenta o tamanho do spritesheet para ficar mais fácil de ver
        player_sheet = pygame.transform.scale(player_sheet, (300, 300))

        # Define sequências de sprites de cada animação
        spritesheet = load_spritesheet(player_sheet, 4, 3)
        self.animations = {
            WALKING: spritesheet[3:6],
        }

        # Define estado atual (que define qual animação deve ser mostrada)
        self.state = WALKING
        # Define animação atual
        self.animation = self.animations[self.state]
        # Inicializa o primeiro quadro da animação
        self.frame = 0
        self.image = self.animation[self.frame]
        self.mask = pygame.mask.from_surface(self.image)
        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()
        self.speedx = 0
        self.speedy = 0

        # Centraliza na tela.
        self.rect.centerx = 80
        self.rect.centery = 600

        #Grupos e assets da classe
        self.groups = groups
        self.assets = assets

        # Guarda o tick da primeira imagem
        self.last_update = pygame.time.get_ticks()
        self.last_throw = pygame.time.get_ticks()

        # Tempo entre os lançamentos de gorro
        self.throw_ticks = 1750

        # Controle de ticks de animação: troca de imagem a cada self.frame_ticks milissegundos.
        self.frame_ticks = 100

    #Função que verifica e garante que o Santa se mantenha na tela
    def verify_position(self):
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0

    #Função que puxa o Santa para o chão
    def gravity(self):
        if self.rect.centery < 600:
            self.speedy += GRAVITY

        if self.rect.centery >= 600:
            self.speedy = 0
            self.rect.centery = 600

    #Função de animação
    def change_animation(self, now):
        # Marca o tick da nova imagem.
            self.last_update = now

            # Avança um quadro.
            self.frame += 1

            # Atualiza animação atual
            self.animation = self.animations[self.state]

            # Reinicia a animação caso o índice da imagem atual seja inválido
            if self.frame >= len(self.animation):
                self.frame = 0

            # Armazena a posição do centro da imagem
            center = self.rect.center

            # Atualiza imagem atual
            self.image = self.animation[self.frame]

            # Atualiza os detalhes de posicionamento
            self.rect = self.image.get_rect()
            self.rect.center = center

    # Metodo que atualiza a posição do personagem
    def update(self):

        #Atualização da posição
        self.rect.x += self.speedx
        self.rect.y += self.speedy


        self.verify_position()

        #Atualiza a posição em y, fazendo com que o santa volte para o chao depois de um pulo
        self.gravity()

        # Verifica o tick atual.
        now = pygame.time.get_ticks()

        # Verifica quantos ticks se passaram desde a ultima mudança de frame.
        elapsed_ticks = now - self.last_update

        # Se já está na hora de mudar de imagem...
        if elapsed_ticks > self.frame_ticks:
            self.change_animation(now)


    # Método de arremesso do gorro
    def throw(self):
        # Verifica se pode lançar
        now = pygame.time.get_ticks()

        # Verifica quantos ticks se passaram desde o último gorro.
        elapsed_ticks = now - self.last_throw

        # Se já pode lançar novamente...
        if elapsed_ticks > self.throw_ticks:

            # Marca o tick da nova imagem.
            self.last_throw = now

            # O novo gorro vai ser criada no centro do santa
            new_hat = Hat(self.assets, self.rect.centerx, self.rect.centery)
            self.groups['all_sprites'].add(new_hat)
            self.groups['all_hats'].add(new_hat)
            self.assets[THROW_SOUND].play()


class Element(ABC, pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, assets):
        
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        #Imagem do gorro
        self.image = assets
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.speedy = 0

    @abstractmethod
    def update(self):
        self.rect.x += self.speedx
            

class Hat(Element):

    # Construtor da classe.
    def __init__(self, assets, centerx, centery):
        # Construtor da classe mãe Element
        super().__init__(assets[SANTAHAT_GAME])

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.speedx = 15  # Velocidade fixa para direita

    def update(self):

        super().update()

        # Se o lançamento passar do inicio da tela, morre.
        if self.rect.centerx > WIDTH:
            self.kill()



#Classe das bolas de neve
class Snowball(Element):

    def __init__(self,assets):

        # Construtor da classe mãe Element
        super().__init__(assets[SNOWBALL_IMG])

        self.rect.centerx = random.randint(WIDTH, SPAWN)
        self.rect.centery = 600
        self.speedx = random.randint(-12, -5)
        

    def update(self):
        #Chama o metodo da classe mãe
        super().update()

        if self.rect.centerx <= 0:
            self.rect.centerx = random.randint(WIDTH, SPAWN)

#Classe dos cookies
class Cookie(Element):

    def __init__(self,assets):

        # Construtor da classe mãe Element
        super().__init__(assets[COOKIE_IMG])

        self.rect.centerx = random.randint(WIDTH, SPAWN)
        self.rect.centery = random.randint(430, 550)
        self.speedx = random.randint(-7,-5)


    def update(self):

        #Chama o metodo da classe mãe
        super().update()
        
        if self.rect.centerx <= 0:
            self.rect.centerx = random.randint(WIDTH, SPAWN)
            self.rect.centery = random.randint(430, 550)
            self.speedx = random.randint(-7,-5)