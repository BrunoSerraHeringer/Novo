import socket
import threading
import pygame
import sys
from constants import BLACK, WHITE, GOLD, RED, GREEN, LIGHT_GRAY, DARK_GRAY, LIGHT_BLUE, BACKGROUND_DARK, TEXT_PRIMARY, ACCENT_COLOR, SUCCESS_COLOR, FAIL_COLOR

# Inicialização
pygame.init()
# Usar fullscreen por padrão
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
largura, altura = tela.get_size()
pygame.display.set_caption("The Resistance - Tabuleiro do Jogo")

# Variável para controlar fullscreen
fullscreen = True

# Cores e fontes (mantendo compatibilidade)
BRANCO = WHITE
PRETO = BLACK
AZUL = (0, 120, 215)
CINZA = LIGHT_GRAY
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

# Classe do tabuleiro do The Resistance
class ResistanceBoard:
    """
    Classe que desenha o tabuleiro visual do The Resistance
    """
    
    def __init__(self, screen, theme_system=None):
        self.screen = screen
        self.theme_system = theme_system
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Estado do jogo
        self.current_mission = 1
        self.max_missions = 5
        self.players = []
        self.current_leader = 0
        self.team_size = 0
        self.votes = {}
        self.mission_results = {}  # {mission: 'success'/'fail'}
        
        # Cores do tema
        self.bg_color = BACKGROUND_DARK
        self.text_color = TEXT_PRIMARY
        self.accent_color = ACCENT_COLOR
        self.success_color = SUCCESS_COLOR
        self.fail_color = FAIL_COLOR
        
        if theme_system:
            self.bg_color = theme_system.get_color('background')
            self.text_color = theme_system.get_color('text_primary')
            self.accent_color = theme_system.get_color('accent')
    
    def set_game_state(self, game_state):
        """Atualiza o estado do jogo"""
        self.players = game_state.get('players', [])
        self.current_mission = game_state.get('current_mission', 1)
        self.current_leader = game_state.get('current_leader', 0)
        self.team_size = game_state.get('team_size', 0)
        self.votes = game_state.get('votes', {})
        self.mission_results = game_state.get('mission_results', {})
    
    def draw(self, board_rect):
        """Desenha o tabuleiro completo"""
        # Fundo do tabuleiro
        pygame.draw.rect(self.screen, self.bg_color, board_rect)
        pygame.draw.rect(self.screen, self.accent_color, board_rect, 3)
        
        # Título
        title = self.font_title.render("THE RESISTANCE", True, self.accent_color)
        title_rect = title.get_rect(center=(board_rect.centerx, board_rect.top + 40))
        self.screen.blit(title, title_rect)
        
        # Missão atual
        mission_text = self.font_text.render(f"Missão {self.current_mission}/5", True, self.text_color)
        mission_rect = mission_text.get_rect(center=(board_rect.centerx, board_rect.top + 80))
        self.screen.blit(mission_text, mission_rect)
        
        # Desenhar seções do tabuleiro
        self._draw_leader_section(board_rect)
        self._draw_team_section(board_rect)
        self._draw_voting_section(board_rect)
        self._draw_mission_track(board_rect)
        self._draw_players_section(board_rect)
    
    def _draw_leader_section(self, board_rect):
        """Desenha seção do líder atual"""
        section_y = board_rect.top + 120
        section_height = 60
        
        # Fundo da seção
        section_rect = pygame.Rect(board_rect.left + 20, section_y, board_rect.width - 40, section_height)
        pygame.draw.rect(self.screen, DARK_GRAY, section_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, section_rect, 2, border_radius=8)
        
        # Título
        leader_title = self.font_text.render("LÍDER ATUAL", True, self.accent_color)
        self.screen.blit(leader_title, (section_rect.left + 10, section_rect.top + 10))
        
        # Nome do líder
        if self.players and 0 <= self.current_leader < len(self.players):
            leader_name = self.players[self.current_leader]
            leader_text = self.font_text.render(leader_name, True, self.text_color)
            self.screen.blit(leader_text, (section_rect.left + 10, section_rect.top + 35))
    
    def _draw_team_section(self, board_rect):
        """Desenha seção da equipe proposta"""
        section_y = board_rect.top + 200
        section_height = 80
        
        # Fundo da seção
        section_rect = pygame.Rect(board_rect.left + 20, section_y, board_rect.width - 40, section_height)
        pygame.draw.rect(self.screen, DARK_GRAY, section_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, section_rect, 2, border_radius=8)
        
        # Título
        team_title = self.font_text.render("EQUIPE PROPOSTA", True, self.accent_color)
        self.screen.blit(team_title, (section_rect.left + 10, section_rect.top + 10))
        
        # Tamanho da equipe
        team_size_text = self.font_text.render(f"Tamanho: {self.team_size} jogadores", True, self.text_color)
        self.screen.blit(team_size_text, (section_rect.left + 10, section_rect.top + 35))
        
        # Botões de ação
        button_width = 120
        button_height = 30
        button_y = section_rect.top + 45
        
        # Botão Propor Equipe
        propose_rect = pygame.Rect(section_rect.left + 10, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, GREEN, propose_rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, propose_rect, 1, border_radius=5)
        propose_text = self.font_small.render("Propor", True, WHITE)
        propose_text_rect = propose_text.get_rect(center=propose_rect.center)
        self.screen.blit(propose_text, propose_text_rect)
        
        # Botão Votar
        vote_rect = pygame.Rect(section_rect.left + 140, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, LIGHT_BLUE, vote_rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, vote_rect, 1, border_radius=5)
        vote_text = self.font_small.render("Votar", True, WHITE)
        vote_text_rect = vote_text.get_rect(center=vote_rect.center)
        self.screen.blit(vote_text, vote_text_rect)
    
    def _draw_voting_section(self, board_rect):
        """Desenha seção de votação"""
        section_y = board_rect.top + 300
        section_height = 100
        
        # Fundo da seção
        section_rect = pygame.Rect(board_rect.left + 20, section_y, board_rect.width - 40, section_height)
        pygame.draw.rect(self.screen, DARK_GRAY, section_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, section_rect, 2, border_radius=8)
        
        # Título
        vote_title = self.font_text.render("VOTAÇÃO", True, self.accent_color)
        self.screen.blit(vote_title, (section_rect.left + 10, section_rect.top + 10))
        
        # Status da votação
        if self.votes:
            approved = sum(1 for vote in self.votes.values() if vote == 'approve')
            rejected = sum(1 for vote in self.votes.values() if vote == 'reject')
            total = len(self.votes)
            
            vote_status = f"Aprovado: {approved} | Rejeitado: {rejected} | Total: {total}"
            vote_text = self.font_text.render(vote_status, True, self.text_color)
            self.screen.blit(vote_text, (section_rect.left + 10, section_rect.top + 35))
        else:
            no_votes = self.font_text.render("Aguardando votos...", True, (200, 200, 200))
            self.screen.blit(no_votes, (section_rect.left + 10, section_rect.top + 35))
    
    def _draw_mission_track(self, board_rect):
        """Desenha trilha de missões"""
        section_y = board_rect.top + 420
        section_height = 80
        
        # Fundo da seção
        section_rect = pygame.Rect(board_rect.left + 20, section_y, board_rect.width - 40, section_height)
        pygame.draw.rect(self.screen, DARK_GRAY, section_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, section_rect, 2, border_radius=8)
        
        # Título
        track_title = self.font_text.render("TRILHA DE MISSÕES", True, self.accent_color)
        self.screen.blit(track_title, (section_rect.left + 10, section_rect.top + 10))
        
        # Missões
        mission_width = 60
        mission_height = 40
        mission_spacing = 10
        start_x = section_rect.left + 10
        mission_y = section_rect.top + 35
        
        for i in range(1, 6):
            mission_x = start_x + (i - 1) * (mission_width + mission_spacing)
            mission_rect = pygame.Rect(mission_x, mission_y, mission_width, mission_height)
            
            # Cor baseada no resultado
            if i in self.mission_results:
                if self.mission_results[i] == 'success':
                    color = self.success_color
                else:
                    color = self.fail_color
            elif i == self.current_mission:
                color = self.accent_color
            else:
                color = LIGHT_GRAY
            
            pygame.draw.rect(self.screen, color, mission_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, mission_rect, 2, border_radius=5)
            
            # Número da missão
            mission_num = self.font_text.render(str(i), True, WHITE)
            mission_num_rect = mission_num.get_rect(center=mission_rect.center)
            self.screen.blit(mission_num, mission_num_rect)
    
    def _draw_players_section(self, board_rect):
        """Desenha seção dos jogadores"""
        section_y = board_rect.top + 520
        section_height = 100
        
        # Fundo da seção
        section_rect = pygame.Rect(board_rect.left + 20, section_y, board_rect.width - 40, section_height)
        pygame.draw.rect(self.screen, DARK_GRAY, section_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.accent_color, section_rect, 2, border_radius=8)
        
        # Título
        players_title = self.font_text.render("JOGADORES", True, self.accent_color)
        self.screen.blit(players_title, (section_rect.left + 10, section_rect.top + 10))
        
        # Lista de jogadores
        if self.players:
            player_y = section_rect.top + 35
            for i, player in enumerate(self.players):
                player_text = self.font_small.render(f"• {player}", True, self.text_color)
                self.screen.blit(player_text, (section_rect.left + 10, player_y))
                player_y += 20

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

# Criar instância do tabuleiro
tabuleiro = ResistanceBoard(tela)

# Estado de exemplo do jogo (pode ser atualizado via servidor)
game_state = {
    'players': ['Jogador1', 'Jogador2', 'Jogador3', 'Jogador4', 'Jogador5'],
    'current_mission': 1,
    'current_leader': 0,
    'team_size': 3,
    'votes': {},
    'mission_results': {}
}

# Atualizar estado do tabuleiro
tabuleiro.set_game_state(game_state)

# Loop principal
executando = True
while executando:
    tela.fill(PRETO)
    
    # Desenhar tabuleiro na área principal (esquerda)
    board_rect = pygame.Rect(0, 0, largura - chat_largura, altura)
    tabuleiro.draw(board_rect)
    
    # Desenhar chat na área direita
    desenhar_chat()
    
    # Desenhar instruções de fullscreen
    if fullscreen:
        instrucao_texto = fonte.render("Pressione F11 ou ESC para sair do fullscreen", True, (200, 200, 200))
        tela.blit(instrucao_texto, (10, altura - 30))
    else:
        instrucao_texto = fonte.render("Pressione F11 para entrar em fullscreen", True, (200, 200, 200))
        tela.blit(instrucao_texto, (10, altura - 30))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.KEYDOWN:
            # Alternar fullscreen com F11 ou ESC
            if evento.key == pygame.K_F11 or evento.key == pygame.K_ESCAPE:
                fullscreen = not fullscreen
                if fullscreen:
                    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    tela = pygame.display.set_mode((1000, 600))
                largura, altura = tela.get_size()
                # Recalcular posições do chat
                chat_x = largura - 300
                chat_altura = altura - chat_input_altura
            elif evento.key == pygame.K_RETURN:
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
        elif evento.type == pygame.MOUSEWHEEL:
            if evento.y > 0 and scroll_offset < len(mensagens_chat) - 1:
                scroll_offset += 1
            elif evento.y < 0 and scroll_offset > 0:
                scroll_offset -= 1
    pygame.display.update()

pygame.quit()
cliente.close()
sys.exit()