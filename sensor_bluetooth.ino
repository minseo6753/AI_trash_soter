#include <SoftwareSerial.h>

// 블루투스 모듈 연결 핀 설정 (이전과 동일하게 유지)
// 블루투스 모듈 TX (HC-05 TX)를 아두이노 RX 핀(3)에,
// 블루투스 모듈 RX (HC-05 RX)를 아두이노 TX 핀(2)에 연결
SoftwareSerial BTSerial(3, 2); // (아두이노 RX 핀, 아두이노 TX 핀)

// 초음파 센서 핀 설정 (HC-SR04 기준)
const int trigPin = 9; // 초음파 발생(Trig) 핀
const int echoPin = 8; // 초음파 수신(Echo) 핀

// 거리 측정 관련 변수
long duration; // 초음파 왕복 시간
int distance;  // 거리 (cm)

// 통신 관련 변수
bool triggeredByPython = false; // 파이썬으로부터 응답을 기다리는 중인지 여부

void setup() {
  Serial.begin(9600);   // PC 시리얼 모니터 통신
  BTSerial.begin(9600); // 블루투스 모듈 통신

  pinMode(trigPin, OUTPUT); // Trig 핀 출력 설정
  pinMode(echoPin, INPUT);  // Echo 핀 입력 설정

  Serial.println("아두이노 시작됨. 초음파 센서 및 블루투스 대기 중...");
}

void loop() {
  // 1. 초음파 센서 거리 측정 및 파이썬으로 신호 보내기
  // Trig 핀을 LOW로 설정하여 초음파를 초기화
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Trig 핀을 HIGH로 10us 유지하여 초음파 발생
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Echo 핀에서 초음파가 돌아오는 시간을 측정
  duration = pulseIn(echoPin, HIGH);

  // 시간을 거리(cm)로 변환 (음속: 340m/s = 0.034cm/us, 왕복 거리이므로 /2)
  distance = duration * 0.034 / 2;

  Serial.print("거리: ");
  Serial.print(distance);
  Serial.println(" cm");

  // 거리가 10cm 미만이고, 아직 파이썬으로부터 응답을 기다리지 않는 상태일 때만 신호 전송
  if (distance < 10 ) {
    BTSerial.println("TRIGGER"); // 파이썬에게 'TRIGGER' 신호 전송
    Serial.println("거리 10cm 미만! 파이썬에게 'TRIGGER' 신호 전송.");
    
    while(true){
      // 2. 블루투스로부터 데이터 수신 (파이썬 -> 아두이노)
      if (BTSerial.available()) {
        String receivedData = BTSerial.readStringUntil('\n');
        receivedData.trim(); // 수신된 문자열 앞뒤의 공백/개행 문자 제거

        // 수신 후 블루투스 시리얼 버퍼에 혹시 남아있을 수 있는 잔여 데이터를 강제로 비움
        while (BTSerial.available()) {
          BTSerial.read();
        }

        if (receivedData.length() > 0) { // 빈 문자열이 아닌 경우에만 처리
          Serial.print("파이썬으로부터 수신: ");
          Serial.println(receivedData);
          break;
        }
      }      
    }
  }



  // 너무 빠르게 측정하면 통신이나 센서에 문제가 생길 수 있으므로 적절한 지연
  delay(1000); // 0.1초마다 거리 측정 및 통신 시도
}