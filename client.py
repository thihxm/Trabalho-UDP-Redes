import socket
import random
import hashlib

def compute_sha256(data):
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(data)
    return hash_sha256.hexdigest()

def solicitar_reenvio(nome_arquivo, indice_pacote, server_address):
    mensagem = f"RESEND {nome_arquivo} {indice_pacote}".encode()
    client_socket.sendto(mensagem, server_address)

def requisitar_arquivo(nome_arquivo, server_address):
    mensagem = f"GET {nome_arquivo}".encode()
    client_socket.sendto(mensagem, server_address)

    pacotes_recebidos = {}
    pacotes_a_receber = set()
    finalizado = False

    while not (finalizado and not pacotes_a_receber - pacotes_recebidos.keys()):
        pacote = client_socket.recvfrom(buffer_size)[0]

        if pacote == b"TERMINO":
            finalizado = True
            continue

        if pacote.startswith(b"ERRO"):
            print(pacote.decode())
            break

        indice_pacote, checksum_recebido, dados = pacote.split(b'|', 2)
        indice_pacote = int(indice_pacote)
        pacotes_a_receber.add(indice_pacote)
        checksum_recebido = checksum_recebido.decode()

        # Simular perda de pacotes
        if random.random() < probabilidade_perda:
            print(f"Pacote {indice_pacote} perdido (simulado)")
            solicitar_reenvio(nome_arquivo, indice_pacote, server_address)
            continue

        # Processamento do pacote
        checksum_calculado = compute_sha256(dados)
        if checksum_recebido == checksum_calculado:
            print(f"Recebido pacote {indice_pacote}")
            pacotes_recebidos[indice_pacote] = dados
        else:
            print(f"Erro de checksum no pacote {indice_pacote}. "
                  f"Solicitando reenvio...")
            solicitar_reenvio(nome_arquivo, indice_pacote, server_address)

    if finalizado and not pacotes_a_receber - pacotes_recebidos.keys():
        print("Arquivo recebido com sucesso!")
        # Escrever os pacotes em ordem
        with open(f"recebido_{nome_arquivo}", "wb") as arquivo:
            for i in sorted(pacotes_recebidos.keys()):
                arquivo.write(pacotes_recebidos[i])

# Configurações do cliente
server_ip = '127.0.0.1'
server_port = 12345
buffer_size = 1024 + 72  # 1024 bytes de dados + 72 bytes de cabeçalho
probabilidade_perda = 0.1  # 10% de chance de perder um pacote

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    nome_arquivo = input("Digite o nome do arquivo para requisitar: ")
    if nome_arquivo.lower() == "sair":
        break
    probabilidade_perda = float(input("Digite a probabilidade de perda de pacotes (%): ")) / 100
    print(f"Probabilidade de perda de pacotes: {probabilidade_perda * 100}%")
    requisitar_arquivo(nome_arquivo, (server_ip, server_port))

client_socket.close()
