import socket
import os
import hashlib

def compute_sha256(data):
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(data)
    return hash_sha256.hexdigest()

def reenviar_pacote(nome_arquivo, endereco_cliente, indice_pacote):
    caminho_arquivo = f'./server_files/{nome_arquivo}'
    try:
        with open(caminho_arquivo, "rb") as arquivo:
            # Pular para a posição do pacote especificado
            posicao_pacote = indice_pacote * (buffer_size)
            arquivo.seek(posicao_pacote)

            # Ler e enviar apenas o pacote especificado
            dados = arquivo.read(buffer_size)
            if dados:
                checksum = compute_sha256(dados)
                pacote = (str(indice_pacote) + '|' + checksum + '|').encode() + dados
                server_socket.sendto(pacote, endereco_cliente)
    except FileNotFoundError:
        server_socket.sendto(b"ERRO: Arquivo nao encontrado", endereco_cliente)
        return    

def enviar_arquivo(nome_arquivo, endereco_cliente):
    caminho_arquivo = f'./server_files/{nome_arquivo}'
    try:    
        with open(caminho_arquivo, "rb") as arquivo:
            indice_pacote = 0
            while True:
                dados = arquivo.read(buffer_size)
                if not dados:
                    server_socket.sendto(b"TERMINO", endereco_cliente)
                    break  # Arquivo terminou
                checksum = compute_sha256(dados)
                pacote = (str(indice_pacote) + '|' + checksum + '|').encode() + dados
                print(f"Enviando pacote {indice_pacote}")
                server_socket.sendto(pacote, endereco_cliente)
                indice_pacote += 1

    except FileNotFoundError:
        server_socket.sendto(b"ERRO: Arquivo nao encontrado", endereco_cliente)
        return

# Configurações do servidor
server_ip = '127.0.0.1'
server_port = 12345
buffer_size = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

print(f"Servidor UDP esperando conexões na porta {server_port}")

while True:
    mensagem, endereco_cliente = server_socket.recvfrom(buffer_size)
    mensagem = mensagem.decode()

    if mensagem.startswith("GET"):
        _, nome_arquivo = mensagem.split()
        enviar_arquivo(nome_arquivo, endereco_cliente)
    elif mensagem.startswith("RESEND"):
        _, nome_arquivo, indice_pacote = mensagem.split()
        print(f"Reenviando pacote {indice_pacote}")
        reenviar_pacote(nome_arquivo, endereco_cliente, int(indice_pacote))

