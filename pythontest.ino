#include <SoftwareSerial.h>

// 블루투스 모듈 TX (HC-05 TX)를 아두이노 RX 핀(3)에,
// 블루투스 모듈 RX (HC-05 RX)를 아두이노 TX 핀(2)에 연결
SoftwareSerial BTSerial(3, 2); // (아두이노 RX 핀, 아두이노 TX 핀)

void setup() {
  Serial.begin(9600);    // 아두이노 시리얼 모니터와의 통신 속도
  BTSerial.begin(9600);  // 블루투스 모듈과의 통신 속도 (보통 9600)
  Serial.println("아두이노 시작됨. 블루투스 대기 중...");
}

void loop() {
  // 1. 블루투스로부터 데이터 수신 (파이썬 -> 아두이노)
  if (BTSerial.available()) {
    String receivedData = BTSerial.readStringUntil('\n'); // 개행 문자가 올 때까지 읽기
    Serial.print("블루투스 수신: ");
    Serial.println(receivedData);

    // 수신된 데이터를 파이썬으로 다시 전송 (양방향 통신 테스트)
    BTSerial.print("아두이노 응답: ");
    BTSerial.println(receivedData + " (OK)");
  }

  // 2. 시리얼 모니터로부터 데이터 수신 (시리얼 모니터 -> 아두이노)
  if (Serial.available()) {
    String serialData = Serial.readStringUntil('\n'); // 개행 문자가 올 때까지 읽기
    Serial.print("시리얼 모니터 수신: ");
    Serial.println(serialData);

    // 시리얼 모니터에서 받은 데이터를 블루투스로 전송
    BTSerial.print("시리얼로부터 받은 데이터 전송: ");
    BTSerial.println(serialData);
  }
}