import pygame
import sys
import subprocess
from functions.desenha_botao import desenhar_botao

pygame.init()

# Verifica se o modo tela cheia foi solicitado
modo_tela_cheia = "--fullscreen" in sys.argv

# Tela
largura, altura = 800, 600
if modo_tela_cheia:
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    largura, altura = tela.get_size()
else:
    tela = pygame.display.set_mode((largura, altura))

pygame.display.set_caption("Breves Falsos")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 120, 215)
AZUL_HOVER = (0, 150, 255)

# Fonte
fonte = pygame.font.SysFont(None, 60)

# Caminho da imagem de fundo
CAMINHO_FUNDO = "fotos/menu.jpg"

# Plano de fundo
fundo = pygame.image.load(CAMINHO_FUNDO)
fundo = pygame.transform.smoothscale(fundo, (largura, altura))

# Ações
def jogar():
    print("Iniciando o jogo...")

def sair():
    pygame.quit()
    sys.exit()

def alternar_tela_cheia():
    global tela, modo_tela_cheia, largura, altura, fundo
    modo_tela_cheia = not modo_tela_cheia
    if modo_tela_cheia:
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        largura, altura = tela.get_size()
    else:
        largura, altura = 800, 600
        tela = pygame.display.set_mode((largura, altura))

    fundo = pygame.image.load(CAMINHO_FUNDO)
    fundo = pygame.transform.smoothscale(fundo, (largura, altura))

def the_resistance():
    pygame.quit()
    if modo_tela_cheia:
        subprocess.run(["python", "sala_espera.py", "--fullscreen"])
    else:
        subprocess.run(["python", "sala_espera.py"])

def the_council():
    print("The Council selecionado")

# Menu
def menu():
    while True:
        tela.blit(fundo, (0, 0))  # Desenha o plano de fundo

        # Título do jogo
        titulo = fonte.render("Breves Falsos", True, BRANCO)
        titulo_rect = titulo.get_rect(center=(largura // 2, 100))
        tela.blit(titulo, titulo_rect)

        # Botões centralizados
        desenhar_botao(tela, fonte, "The Resistance", (largura - 320) // 2, 200, 320, 80, AZUL, AZUL_HOVER, BRANCO, the_resistance)
        desenhar_botao(tela, fonte, "The Council", (largura - 320) // 2, 300, 320, 80, AZUL, AZUL_HOVER, BRANCO, the_council)
        desenhar_botao(tela, fonte, "Tela Cheia", (largura - 320) // 2, 400, 320, 80, AZUL, AZUL_HOVER, BRANCO, alternar_tela_cheia)
        desenhar_botao(tela, fonte, "Sair", (largura - 320) // 2, 500, 320, 80, AZUL, AZUL_HOVER, BRANCO, sair)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sair()

        pygame.display.update()

menu()