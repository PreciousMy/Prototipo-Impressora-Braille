import serial
import time

# Dicionário
BRAILLE_MAP = {
    'a': (1, 0, 0, 0, 0, 0), 'b': (1, 1, 0, 0, 0, 0), 'c': (1, 0, 0, 1, 0, 0),
    'd': (1, 0, 0, 1, 1, 0), 'e': (1, 0, 0, 0, 1, 0), 'f': (1, 1, 0, 1, 0, 0),
    'g': (1, 1, 0, 1, 1, 0), 'h': (1, 1, 0, 0, 1, 0), 'i': (0, 1, 0, 1, 0, 0),
    'j': (0, 1, 0, 1, 1, 0), 'k': (1, 0, 1, 0, 0, 0), 'l': (1, 1, 1, 0, 0, 0),
    'm': (1, 0, 1, 1, 0, 0), 'n': (1, 0, 1, 1, 1, 0), 'o': (1, 0, 1, 0, 1, 0),
    'p': (1, 1, 1, 1, 0, 0), 'q': (1, 1, 1, 1, 1, 0), 'r': (1, 1, 1, 0, 1, 0),
    's': (0, 1, 1, 1, 0, 0), 't': (0, 1, 1, 1, 1, 0), 'u': (1, 0, 1, 0, 0, 1),
    'v': (1, 1, 1, 0, 0, 1), 'w': (0, 1, 0, 1, 1, 1), 'x': (1, 0, 1, 1, 0, 1),
    'y': (1, 0, 1, 1, 1, 1), 'z': (1, 0, 1, 0, 1, 1),
    ' ': (0, 0, 0, 0, 0, 0),
}

semPuncao = 0
puncao = 1
espacoCelula = 2
linhaPonto = 3
linhaCelula = 4 
ejetarPapel = 5   

def texto_para_celulas_braille(texto):
    celulas = []
    for char in texto.lower():
        if char in BRAILLE_MAP:
            celulas.append(BRAILLE_MAP[char])
    return celulas

# Gera a lista de comandos final para o Arduino

def preparar_dados_impressao(celulas_braille):
    if not celulas_braille:
        return []

    comandos_finais = []
    # Recebe as celulas, ou seja tuplas
    num_celulas = len(celulas_braille)
    
    for i in range(3):
        # Linha 1 de pontos - ponto 1 e 4 -> indices 0 e 3
        # Linha 2 de pontos - ponto 2 e 5 -> indices 1 e 4
        # Linha 3 de pontos - ponto 3 e 6 -> indices 2 e 5
        ponto_col_1 = i
        ponto_col_2 = i + 3

        # Para cada celula na frase (letra ou um espaço)
        for idx, celula in enumerate(celulas_braille):

            # Verifica se a celula atual é um caractere de espaço
            if celula == BRAILLE_MAP[' ']:
                # Se for um espaço trata como uma celula normal mas que não perfura.
                comandos_finais.append(semPuncao) # 0
                comandos_finais.append(semPuncao) # 0 
            else:
                # Se for uma letra, envie seus comandos de ponto normais
                comandos_finais.append(celula[ponto_col_1])
                comandos_finais.append(celula[ponto_col_2]) 

            # Após processar os pontos de cada celula (letra e espaço) adiciona um comando o espacoCelula para mover 
            # o cabeçote para a proxima celula.
            if idx < num_celulas - 1:
                comandos_finais.append(espacoCelula)
        
        # Ao final de cada linha de pontos, adiciona o comando de quebra de linha
        # para o Arduino avançar o papel e retornar o carro.
        if i < 2:
            comandos_finais.append(linhaPonto) # (3)

    return comandos_finais

def enviar_comandos(ser, comandos):
    try:
        total_comandos = len(comandos)
        for i, cmd in enumerate(comandos):
            print(f"Enviando comando {i+1}/{total_comandos}: {cmd}")
            ser.write(bytes([cmd]))
            if(cmd==1):
                time.sleep(0.2) # Tempo para marcação
            ack = ser.readline().decode('utf-8').strip()
            if ack == "OK":
                print("Arduino confirmou. OK.")
            else:
                print(f"Erro: Arduino respondeu '{ack}'")
                return False
        return True
    except Exception as e:
        print(f"Ocorreu um erro durante o envio: {e}")
        return False

def dividir_texto_em_linhas(texto, max_comprimento):
    # Cria uma lista de palavras com o texto atual.
    palavras = texto.split()

    linhas_finais = []
    
    # Auxiliar
    linha_atual = ""

    for palavra in palavras:
        
        # Palavra muito longa
        if len(palavra) > max_comprimento:
            
            if linha_atual:
                linhas_finais.append(linha_atual)
            
            # Força a quebra da palavra longa e adiciona a primeira parte dela
            linhas_finais.append(palavra[:max_comprimento])
            
            # O que sobrou da palavra agora é inicio da proxima linha_atual
            linha_atual = palavra[max_comprimento:]
            
            continue
        
        # Linha_atual vazia? 
        if not linha_atual:
            # linha_atual se torna a palavra.
            linha_atual = palavra
        
        # Verifica se cabe
        elif len(linha_atual) + len(palavra) + 1 <= max_comprimento:
            linha_atual += " " + palavra
            
        # Não cabe
        else:
            linhas_finais.append(linha_atual)

            linha_atual = palavra

    if linha_atual:
        linhas_finais.append(linha_atual)
        
    return linhas_finais

# Configuração
porta = "COM3"
# Quantidade de celulas por linha para melhorar em textos maiores
celulaPorLinha = 25

#"Ola Mundo"
#"Texto longo o suficiente para quebrar linha no texto"
textoImpressao = "Ola Mundo"

print(f"Texto original a ser impresso: '{textoImpressao}'")

linhas_do_texto = dividir_texto_em_linhas(textoImpressao, celulaPorLinha)

print("\nO texto foi dividido nas seguintes linhas para impressão:")
for linha in linhas_do_texto:
    print(f"- '{linha}'")

input("\nPressione Enter para iniciar a impressão...")

comecoTudo = time.time()

ser = None
try:
    print(f"Tentando conectar na porta {porta}...")
    ser = serial.Serial(porta, 9600, timeout=2)
    time.sleep(2)
    print("Conectado")
    ser.read_all()

    for i, linha in enumerate(linhas_do_texto):
        print(f"\n==========================================")
        print(f"Immprimindo Linha {i+1}/{len(linhas_do_texto)}: '{linha}'")
        print(f"==========================================")

        celulas = texto_para_celulas_braille(linha)
        comandos = preparar_dados_impressao(celulas)
        print(comandos)

        if not comandos:
            print("Linha vazia, pulando.")
            continue

        sucesso = enviar_comandos(ser, comandos)

        if not sucesso:
            print("Erro ao imprimir a linha. Abortando.")
            break

        # Avança o papel para criar espaço entre as linhas de texto
        if i < len(linhas_do_texto) - 1:
            print("\n--- Avançando papel para a próxima linha de texto ---")
            comandos_de_avanco = [linhaCelula]
            enviar_comandos(ser, comandos_de_avanco)

    fimTudo = time.time()
    print("\n\nImpressão Completa")
    print(f"Tempo total =  {fimTudo-comecoTudo}")


    print("Ejetando o papel...")
    enviar_comandos(ser, [ejetarPapel])
    print("Ejetado")

except serial.SerialException as e:
    print(f"Erro ao conectar: {e}")
finally:
    if ser and ser.is_open:
        ser.close()
        print("Conexão serial fechada.")