import socket
import threading
import pygame
import sys

# Inicialização
pygame.init()
largura, altura = 1000, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Tabuleiro do Jogo")

# Cores e fontes
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 120, 215)
CINZA = (200, 200, 200)
fonte = pygame.font.SysFont(None, 32)

# Rede
HOST = 'localhost'
PORTA = 5001
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    cliente.connect((HOST, PORTA))
except:
    print("Não foi possível conectar ao servidor.")

# Variáveis do chat
nome_jogador = ""
mensagem_atual = ""
mensagens_chat = []
scroll_offset = 0
chat_x = largura - 300
chat_y = 0
chat_largura = 280
chat_input_altura = 40
chat_altura = altura - chat_input_altura
nome_definido = False

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

# Função para desenhar o chat
def desenhar_chat():
    pygame.draw.rect(tela, CINZA, (chat_x, chat_y, chat_largura, chat_altura))
    y_offset = chat_y + 10
    todas_linhas = []
    for msg in mensagens_chat:
        todas_linhas.extend(quebrar_texto(msg, fonte, chat_largura - 20))
    linhas_visiveis = todas_linhas[-(chat_altura // 25) - scroll_offset:len(todas_linhas) - scroll_offset]
    for linha in linhas_visiveis:
        texto = fonte.render(linha, True, PRETO)
        tela.blit(texto, (chat_x + 10, y_offset))
        y_offset += 25
    pygame.draw.rect(tela, BRANCO, (chat_x, altura - chat_input_altura, chat_largura, chat_input_altura))
    texto_input = fonte.render(mensagem_atual, True, PRETO)
    tela.blit(texto_input, (chat_x + 5, altura - chat_input_altura + 5))

# Receber mensagens do servidor e definir nome do jogador
def receber_mensagens():
    global nome_jogador, nome_definido
    while True:
        try:
            msg = cliente.recv(1024).decode()
            if msg.startswith("[SYSTEM]"):
                continue
            mensagens_chat.append(msg)
            if not nome_definido and ":" in msg:
                nome = msg.split(":")[0].strip()
                if nome:
                    nome_jogador = nome
                    nome_definido = True
        except:
            mensagens_chat.append("Erro ao receber mensagem do servidor.")
            break

threading.Thread(target=receber_mensagens, daemon=True).start()

# Loop principal
executando = True
while executando:
    tela.fill(PRETO)
    desenhar_chat()
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.MOUSEWHEEL:
            if evento.y > 0 and scroll_offset < len(mensagens_chat) - 1:
                scroll_offset += 1
            elif evento.y < 0 and scroll_offset > 0:
                scroll_offset -= 1
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if mensagem_atual.strip() and nome_jogador:
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

pygame.quit()
cliente.close()
sys.exit()