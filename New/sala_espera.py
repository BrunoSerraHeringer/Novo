import pygame
import sys
import subprocess
from functions.desenha_botao import desenhar_botao

pygame.init()

largura, altura = 800, 600
modo_tela_cheia = "--fullscreen" in sys.argv

if modo_tela_cheia:
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    largura, altura = tela.get_size()
else:
    tela = pygame.display.set_mode((largura, altura))

pygame.display.set_caption("Sala de Espera - Breves Falsos")

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 120, 215)
AZUL_HOVER = (0, 150, 255)

fonte = pygame.font.SysFont(None, 60)

def voltar_ao_menu():
    pygame.quit()
    if modo_tela_cheia:
        subprocess.run(["python", "main.py", "--fullscreen"])
    else:
        subprocess.run(["python", "main.py"])

def criar_sala():
    print("Criar Sala selecionado")
    subprocess.Popen(["python", "servidor.py"])  # Inicia o servidor

    # Fecha a janela atual e inicia o pré-jogo
    pygame.display.quit()  # Apenas fecha a janela, sem encerrar o pygame completamente
    if modo_tela_cheia:
        subprocess.run(["python", "pre_jogo.py", "--fullscreen"])
    else:
        subprocess.run(["python", "pre_jogo.py"])
    sys.exit()  # Encerra o script atual corretamente

def entrar_sala():
    print("Entrar na Sala selecionado")

def sala_espera():
    while True:
        tela.fill(PRETO)

        mensagem = fonte.render("Aguardando jogadores...", True, BRANCO)
        mensagem_rect = mensagem.get_rect(center=(largura // 2, 100))
        tela.blit(mensagem, mensagem_rect)

        desenhar_botao(tela, fonte, "Criar Sala", (largura - 320) // 2, 200, 320, 80, AZUL, AZUL_HOVER, BRANCO, criar_sala)
        desenhar_botao(tela, fonte, "Entrar na Sala", (largura - 320) // 2, 300, 320, 80, AZUL, AZUL_HOVER, BRANCO, entrar_sala)
        desenhar_botao(tela, fonte, "Voltar ao Menu", (largura - 320) // 2, 400, 320, 80, AZUL, AZUL_HOVER, BRANCO, voltar_ao_menu)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                voltar_ao_menu()

        pygame.display.update()

sala_espera()