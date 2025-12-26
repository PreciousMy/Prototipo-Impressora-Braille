import serial
import time

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
CMD_NO_PUNCH = 0
CMD_PUNCH = 1
CMD_SPACE = 2
CMD_LINE_BREAK = 3
CMD_NEW_TEXT_LINE = 4 
CMD_EJECT_PAPER = 5   


def texto_para_celulas_braille(texto):
    celulas = []
    for char in texto.lower():
        if char in BRAILLE_MAP:
            celulas.append(BRAILLE_MAP[char])
    return celulas


def preparar_dados_impressao(celulas_braille):

    if not celulas_braille:
        return []

    comandos_finais = []
    num_celulas = len(celulas_braille)


    for i in range(2):

        for idx, celula in enumerate(celulas_braille):
            
            if i == 0:
                ponto_1_val = celula[2] 
                ponto_2_val = celula[1] 
                ponto_3_val = celula[0] 
            else:
                ponto_1_val = celula[5]
                ponto_2_val = celula[4] 
                ponto_3_val = celula[3] 

            if celula == BRAILLE_MAP[' ']:
              
                comandos_finais.append(CMD_NO_PUNCH) 
                comandos_finais.append(CMD_NO_PUNCH) 
                comandos_finais.append(CMD_NO_PUNCH) 
            else:
   
                comandos_finais.append(ponto_1_val) 
                comandos_finais.append(ponto_2_val)
                comandos_finais.append(ponto_3_val) 

            if idx < num_celulas - 1:
                comandos_finais.append(CMD_SPACE)
        

        if i < 1: 
            comandos_finais.append(CMD_LINE_BREAK) 

    return comandos_finais


def enviar_comandos(ser, comandos):
    try:
        total_comandos = len(comandos)
        for i, cmd in enumerate(comandos):
            print(f"Enviando comando {i+1}/{total_comandos}: {cmd}")
            ser.write(bytes([cmd]))
            if(cmd==1):
                time.sleep(0.2) # Mantendo o seu delay de 3s após puncionar
            ack = ser.readline().decode('utf-8').strip()
            if ack == "OK":
                print("Arduino confirmou. OK.")
            else:
                print(f"Erro: Arduino respondeu '{ack}', esperaba 'OK'. Abortando.")
                return False
        return True
    except Exception as e:
        print(f"Ocorreu um erro durante o envio: {e}")
        return False


if __name__ == "__main__":
 
    PORTA_ARDUINO = "COM3" 
    
    TEXTO_PARA_IMPRIMIR = "ola mundo"

    print(f"Texto original a ser impresso: '{TEXTO_PARA_IMPRIMIR}'")
    
    caracteres_para_imprimir = list(TEXTO_PARA_IMPRIMIR)
    
    print("\nO texto será impresso verticalmente (um caractere por linha):")
    for char in caracteres_para_imprimir:
        if char == ' ':
            print("- (Linha em Branco)")
        else:
            print(f"- '{char}'")
    
    input("\nPressione Enter para iniciar a impressão...")

    comecoTudo = time.time()

    ser = None
    try:
        print(f"Tentando conectar na porta {PORTA_ARDUINO}...")
        ser = serial.Serial(PORTA_ARDUINO, 9600, timeout=2)
        time.sleep(2)
        print("Conectado com sucesso!")
        ser.read_all() # Limpa qualquer mensagem de inicialização do Arduino

        for i, char in enumerate(caracteres_para_imprimir):
            
            if char == ' ':
                print("\n==========================================")
                print("DETECTADO ESPAÇO: Inserindo linha em branco.")
                print("==========================================")
                
                comandos_de_avanco = [CMD_NEW_TEXT_LINE]
                enviar_comandos(ser, comandos_de_avanco)
                
                continue 
            
            print(f"\n==========================================")
            print(f"IMPRIMINDO CARACTERE: '{char}'")
            print(f"==========================================")


            celulas = texto_para_celulas_braille(char)

            comandos = preparar_dados_impressao(celulas)
            print(f"Comandos para '{char}': {comandos}")

            if not comandos:
                print("Caractere não reconhecido. Pulando.")
                continue

            sucesso = enviar_comandos(ser, comandos)

            if not sucesso:
                print("Erro ao imprimir o caractere. Abortando.")
                break

            if i < len(caracteres_para_imprimir) - 1:
                print("\n--- Avançando papel para o próximo caractere ---")
                comandos_de_avanco = [CMD_NEW_TEXT_LINE]
                enviar_comandos(ser, comandos_de_avanco)

        print("\n\nIMPRESSÃO COMPLETA DO TEXTO.")

        fimTudo = time.time()
        print("\n\nImpressão Completa")
        print(f"Tempo total =  {fimTudo-comecoTudo}")
        
        print("Ejetando o papel...")
        enviar_comandos(ser, [CMD_EJECT_PAPER])
        print("Processo finalizado.")

    except serial.SerialException as e:
        print(f"Erro ao conectar: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Conexão serial fechada.")