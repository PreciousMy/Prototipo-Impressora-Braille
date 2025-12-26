#include <Servo.h>

// Eixo X
const int relay1 = 6;
const int relay2 = 7;

// Eixo Y
const int pinoRelePapel = 9; 

// Punção e Paradas
const int pinoServo = 8;        
const int pinoFimDeCursoInicio = 2; // Botão que marca a posição inicial
const int pinoFimDeCursoFim = 3;    // Botão que marca a posição final 
Servo motorPuncao; 


const int puncaoRecua = 60; 
const int puncaoAciona = 130; 

// Tempo para espaços
const int tempo_Entre_Pontos = 22; // 2.5mm;
const int tempo_Entre_Celulas = 30; // 6mm (3mm);

const int tempo_Puncao = 250;      
const int tempo_Recolhimento = 200; 

const int tempo_Avanco_Papel_PONTO = 22; // 2.5mm;
const int tempo_Avanco_Papel_LINHA_TEXTO = 42; // 6mm;
const int tempo_Ejetar_Papel = 2000;


// Comandos python 
const int semPuncao = 0;
const int puncao = 1;
const int espacoCelula = 2;
const int linhaPonto = 3; // avanço de linha de ponto
const int linhaCelula = 4; // avanço de linha de texto
const int ejetarPapel = 5;

void setup() {
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(pinoRelePapel, OUTPUT);

  pinMode(pinoFimDeCursoInicio, INPUT);
  pinMode(pinoFimDeCursoFim, INPUT);

  motorPuncao.attach(pinoServo);
  motorPuncao.write(puncaoRecua);

  Serial.begin(9600);
  delay(1000);

  retornarCarroAoInicio();
}

void loop() {
  if (Serial.available() > 0) {
    int comando = Serial.read();

    switch (comando) {
      case semPuncao:
        moverParaProximoPonto();
        break;
      case puncao:
        acionarPuncao();
        // Para testes de marcarção no papel
        delay(200);
        moverParaProximoPonto();
        break;
      case espacoCelula:
        moverParaProximaCelula();
        break;
      case linhaPonto:
        avancarLinhaDePonto(); 
        retornarCarroAoInicio(); 
        break;
      
      case linhaCelula:
        avancarLinhaDeTexto(); 
        retornarCarroAoInicio();
        break;
      case ejetarPapel:
        ejetarPapelFuncao();
        break;
        
    }
    Serial.println("OK");
  }
}


// Funções Eixo X 

void motorCarroFrente() {
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, LOW);
}

void motorCarroVoltar() {
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, HIGH);
}

void motorCarroParar() {
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
}

void moverFrenteComFimCurso(int tempo) {
  motorCarroFrente();
  unsigned long startTime = millis();
  while (millis() - startTime < tempo) {
    if (digitalRead(pinoFimDeCursoFim) == HIGH) {
      break; 
    }
    delay(1);
  }
  motorCarroParar();
  delay(100);
}

void moverParaProximoPonto() {
  moverFrenteComFimCurso(tempo_Entre_Pontos);
}

void moverParaProximaCelula() {
  moverFrenteComFimCurso(tempo_Entre_Celulas);
}


// Função de retorno 

void retornarCarroAoInicio() {
  motorCarroVoltar();
  while (true) {
    
    // verificando o pino do fim de curso
    if (digitalRead(pinoFimDeCursoInicio) == HIGH) {
      delay(50);

      // Garantir que chegou realmente no final maximo
      if (digitalRead(pinoFimDeCursoInicio) == HIGH) {
        break;
      }
      
    }
  }
  motorCarroParar(); 
  delay(100);
}


// Função de punção 

void acionarPuncao() {
  motorPuncao.write(puncaoAciona);
  delay(tempo_Puncao);
  motorPuncao.write(puncaoRecua);
  delay(tempo_Recolhimento);
}


// Funções Eixo Y

void motorPapelFrente() {
  digitalWrite(pinoRelePapel, HIGH);
}

void motorPapelParar() {
  digitalWrite(pinoRelePapel, LOW);
}

void avancarLinhaDePonto() {
  motorPapelFrente();
  delay(tempo_Avanco_Papel_PONTO); 
  motorPapelParar();
  delay(200);
}

void avancarLinhaDeTexto() {
  motorPapelFrente();
  delay(tempo_Avanco_Papel_LINHA_TEXTO);
  motorPapelParar();
  delay(200);
}

void ejetarPapelFuncao() {
  motorPapelFrente();
  delay(tempo_Ejetar_Papel);
  motorPapelParar();
  delay(200);
}