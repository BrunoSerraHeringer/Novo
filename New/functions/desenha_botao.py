import pygame

def desenhar_botao(tela, fonte, texto, x, y, largura, altura, cor, cor_hover, cor_texto, acao=None):
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()

    if x < mouse[0] < x + largura and y < mouse[1] < y + altura:
        pygame.draw.rect(tela, cor_hover, (x, y, largura, altura))
        if clique[0] == 1 and acao:
            acao()
    else:
        pygame.draw.rect(tela, cor, (x, y, largura, altura))

    texto_render = fonte.render(texto, True, cor_texto)
    texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
    tela.blit(texto_render, texto_rect)