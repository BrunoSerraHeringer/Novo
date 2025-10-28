import socket
import threading

def iniciar_servidor():
    host = 'localhost'
    porta = 5001
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen()
    print(f"Servidor iniciado em {host}:{porta}")
    print("Aguardando conexão de jogadores...")

    conexoes = []
    nomes_jogadores = set()

    def tratar_cliente(conexao):
        try:
            while True:
                dados = conexao.recv(1024)
                if not dados:
                    break
                mensagem = dados.decode()
                print(f"Mensagem recebida: {mensagem}")

                # Extrai nome do jogador
                if ":" in mensagem:
                    nome = mensagem.split(":")[0].strip()
                    if nome and nome not in nomes_jogadores:
                        nomes_jogadores.add(nome)
                        print(f"Nomes conectados: {list(nomes_jogadores)}")

                # Reenvia a mensagem original para todos os clientes conectados
                for c in conexoes:
                    try:
                        c.send(mensagem.encode())
                    except:
                        pass
        except:
            print("Erro na comunicação com o cliente.")
        finally:
            conexao.close()
            if conexao in conexoes:
                conexoes.remove(conexao)

    while True:
        conexao, endereco = servidor.accept()
        print(f"Jogador conectado: {endereco}")
        conexoes.append(conexao)
        # Envia mensagem do sistema com prefixo especial
        conexao.send("[SYSTEM] Bem-vindo à sala!".encode())
        threading.Thread(target=tratar_cliente, args=(conexao,), daemon=True).start()

iniciar_servidor()