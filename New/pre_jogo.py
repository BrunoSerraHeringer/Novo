import socket
import threading
import pygame
import sys

# Inicialização
pygame.init()
modo_tela_cheia = "--fullscreen" in sys.argv
largura, altura = 1000, 600
if modo_tela_cheia:
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    largura, altura = tela.get_size()
else:
    tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pré-Jogo - Breves Falsos")

# Cores e fontes
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 120, 215)
CINZA = (200, 200, 200)
fonte = pygame.font.SysFont(None, 32)
fonte_titulo = pygame.font.SysFont(None, 48)

# Carregar imagem de fundo
board_x = 50
board_y = 80
chat_x = largura - 300
board_width = chat_x - board_x - 20
board_height = altura - board_y - 60
board_img = pygame.image.load("fotos/board.png")
board_img = pygame.transform.scale(board_img, (board_width, board_height))

# Rede
HOST = 'localhost'
PORTA = 5001
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    cliente.connect((HOST, PORTA))
except:
    print("Não foi possível conectar ao servidor.")

# Variáveis
nome_jogador = ""
input_ativo = True
mensagem_atual = ""
mensagens_chat = []
nomes_presentes = set()
scroll_offset = 0
chat_y = 100
chat_largura = 280
chat_altura = altura - 150

# Função para quebrar texto em múltiplas linhas
def quebrar_texto(texto, fonte, largura_max):
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ''

    for palavra in palavras:
        teste_linha = linha_atual + (' ' if linha_atual else '') + palavra
        if fonte.size(teste_linha)[0] <= largura_max:
            linha_atual = teste_linha
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas

# Funções de interface
def desenhar_input_box():
    pygame.draw.rect(tela, CINZA, (50, 30, 400, 40))
    texto = fonte.render(nome_jogador, True, PRETO)
    tela.blit(texto, (55, 35))
    titulo = fonte_titulo.render("Digite seu nome:", True, BRANCO)
    tela.blit(titulo, (50, 0))

    # Mostrar nomes presentes abaixo da caixa
    y_offset = 80
    tela.blit(fonte.render("Presentes:", True, BRANCO), (50, y_offset))
    y_offset += 30
    for nome in sorted(nomes_presentes):
        tela.blit(fonte.render(nome, True, BRANCO), (50, y_offset))
        y_offset += 25

def desenhar_chat():
    pygame.draw.rect(tela, CINZA, (chat_x, chat_y, chat_largura, chat_altura))
    y_offset = chat_y + 10

    # Calcula todas as linhas quebradas para mensagens visíveis
    todas_linhas = []
    for msg in mensagens_chat:
        todas_linhas.extend(quebrar_texto(msg, fonte, chat_largura - 20))

    # Aplica scroll e limita pelo espaço disponível
    linhas_visiveis = todas_linhas[-(chat_altura // 25) - scroll_offset:len(todas_linhas) - scroll_offset]

    for linha in linhas_visiveis:
        texto = fonte.render(linha, True, PRETO)
        tela.blit(texto, (chat_x + 10, y_offset))
        y_offset += 25

    # Caixa de entrada
    pygame.draw.rect(tela, BRANCO, (chat_x, altura - 40, chat_largura, 30))
    texto_input = fonte.render(mensagem_atual, True, PRETO)
    tela.blit(texto_input, (chat_x + 5, altura - 35))

def desenhar_botao(texto, x, y, largura, altura, acao):
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()
    cor = AZUL
    cor_hover = (0, 150, 255)
    if x < mouse[0] < x + largura and y < mouse[1] < y + altura:
        pygame.draw.rect(tela, cor_hover, (x, y, largura, altura))
        if clique[0] == 1:
            acao()
    else:
        pygame.draw.rect(tela, cor, (x, y, largura, altura))
    texto_render = fonte.render(texto, True, BRANCO)
    texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
    tela.blit(texto_render, texto_rect)

# Receber mensagens do servidor
def receber_mensagens():
    while True:
        try:
            msg = cliente.recv(1024).decode()
            if msg.startswith("[SYSTEM]"):
                continue
            mensagens_chat.append(msg)
            if ":" in msg:
                nome = msg.split(":")[0].strip()
                if nome:
                    nomes_presentes.add(nome)
        except:
            mensagens_chat.append("Erro ao receber mensagem do servidor.")
            break

threading.Thread(target=receber_mensagens, daemon=True).start()

# Botão iniciar jogo
import subprocess

def iniciar_jogo():
    pygame.quit()
    cliente.close()
    subprocess.Popen(["python", "tabuleiro.py"])
    sys.exit()

# Loop principal
executando = True
while executando:
    try:
        tela.fill(PRETO)
        tela.blit(board_img, (board_x, board_y))
        desenhar_input_box()
        desenhar_chat()
        desenhar_botao("Iniciar Jogo", 50, altura - 80, 200, 40, iniciar_jogo)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if 50 <= evento.pos[0] <= 450 and 30 <= evento.pos[1] <= 70:
                    input_ativo = True
            elif evento.type == pygame.MOUSEWHEEL:
                if evento.y > 0 and scroll_offset < len(mensagens_chat) - 1:
                    scroll_offset += 1
                elif evento.y < 0 and scroll_offset > 0:
                    scroll_offset -= 1
            elif evento.type == pygame.KEYDOWN:
                if input_ativo:
                    if evento.key == pygame.K_RETURN:
                        input_ativo = False
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    else:
                        nome_jogador += evento.unicode
                else:
                    if evento.key == pygame.K_RETURN:
                        if mensagem_atual.strip():
                            try:
                                cliente.send(f"{nome_jogador}: {mensagem_atual}".encode())
                            except:
                                mensagens_chat.append("Erro ao enviar mensagem.")
                            mensagem_atual = ""
                    elif evento.key == pygame.K_BACKSPACE:
                        mensagem_atual = mensagem_atual[:-1]
                    else:
                        mensagem_atual += evento.unicode
        pygame.display.update()
    except Exception as e:
        mensagens_chat.append("Erro no loop principal: " + str(e))
        executando = False

if pygame.get_init():
    pygame.quit()
cliente.close()