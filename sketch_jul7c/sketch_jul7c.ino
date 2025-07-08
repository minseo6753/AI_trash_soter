#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <Servo.h>
#include <SoftwareSerial.h>
//스피커 확인 필요
//#include <SoftwareSerial.h>
//#include <DFRobotDFPlayerMini.h>

// 핀 정의
#define LED_RED 5
#define LED_GREEN 6
#define Trig 12
#define Echo 13
#define SERVO_PIN1 10
#define SERVO_PIN2 9

// LCD 객체 생성
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 서보모터 객체
Servo servo1;
Servo servo2;

// DFPlayer 객체(스피커 확인 필요)
//SoftwareSerial mySoftwareSerial(,); // DFPlayer TX→, RX→
//DFRobotDFPlayerMini myDFPlayer;

SoftwareSerial BTSerial(3, 2);

// 거리 측정 함수
float measureDistance() 
{
  digitalWrite(Trig, LOW);
  delayMicroseconds(2);
  digitalWrite(Trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(Trig, LOW);

  unsigned long duration = pulseIn(Echo, HIGH, 6000);  // 6ms 타임아웃
  float distance = duration * 0.0343 / 2;  // cm로 변환
  return distance;
}

// (......모터 천천히 회전하는 방식도 가능
  //for (pos = 0; pos <= 180; pos += 10) { // 10도씩 증가
    //myservo.write(pos);
    //delay(20); // 속도 조절: delay를 늘리면 더 느려짐
  //}......)



// 모터 구동 함수
void activate(char command) 
{


  switch (command) 
  {
    case '1':


      //lcd 표시
      lcd.clear();
      lcd.setCursor(2, 0);
      lcd.print("Processing 1");

     // ✅ 스피커 출력: 1번 트랙 재생 (스피커 확인 필요)
      //myDFPlayer.play(1);

      //모터 구동
      servo1.write(100);//반시계 속도
      delay(2000);//돌아가는 시간
      servo1.write(90);//멈춤
      delay(2000);//멈춤시간

      servo2.write(70); 
      delay(2000);
      servo2.write(0);
      delay(2000);

      servo1.write(80);//시계방향
      delay(2000);//돌아가는 시간
      servo1.write(90);//멈춤
      delay(2000);//멈춤시

      break;

    case '2':

     //lcd 표시
      lcd.clear();
      lcd.setCursor(2, 0);
      lcd.print("Processing 2");

      // ✅ 스피커 출력: 2번 트랙 재생 (스피커 확인 필요)
      //myDFPlayer.play(2);

      servo1.write(100);
      delay(2000);
      servo1.write(90);
      delay(2000);

      servo2.write(60);
      delay(2000);
      servo2.write(0);
      delay(2000);

      servo1.write(80);
      delay(2000);
      servo1.write(90);
      delay(2000);


      break;

    case '3':

      //lcd 표시
      lcd.clear();
      lcd.setCursor(2, 0);
      lcd.print("Processing 3");

      // ✅ 스피커 출력: 3번 트랙 재생 (스피커 확인 필요)
      //myDFPlayer.play(3);

      servo1.write(100);
      delay(2000);
      servo1.write(90);
      delay(2000);

      servo2.write(60);
      delay(2000);
      servo2.write(0);
      delay(2000);

      servo1.write(80);
      delay(2000);
      servo1.write(90);
      delay(2000);

      break;

    case '4':

      //lcd 표시
      lcd.clear();
      lcd.setCursor(2, 0);
      lcd.print("Processing 4");

       // ✅ 스피커 출력: 4번 트랙 재생 (스피커 확인 필요)
      //myDFPlayer.play(4);

      servo1.write(100);
      delay(2000);
      servo1.write(90);
      delay(2000);

      servo2.write(60);
      delay(2000);
      servo2.write(0);
      delay(2000);

      servo1.write(80);
      delay(2000);
      servo1.write(90);
      delay(2000);

      break;
  }

  // 모터 원위치
  //servo1.write(90);
  //servo2.write(0);
   //lcd wating 표시

  lcd.clear();
  lcd.setCursor(2, 0);
  lcd.print("WAITING");
   // ✅ 스피커 출력: 5번 트랙 재생 (스피커 확인 필요)
   //myDFPlayer.play(5);


}




//초기 셋업
void setup() 
{
  BTSerial.begin(9600);

  pinMode(Trig, OUTPUT);
  pinMode(Echo, INPUT);

  analogWrite(LED_RED, 0); 
  analogWrite(LED_GREEN, 255);

  lcd.init();
  lcd.clear();
  lcd.backlight();
  lcd.print("WAITING");

  //Serial.begin(9600);

  // DFPlayer 초기화(스피커 확인 필요)
  //if (!myDFPlayer.begin(mySoftwareSerial))
  //{
    //Serial.println("DFPlayer 초기화 실패!");
    //while (true);
  //}
  //myDFPlayer.volume(20); // 볼륨: 0~30
  //myDFPlayer.EQ(DFPLAYER_EQ_NORMAL);//이퀄라이저 설정

  servo1.attach(SERVO_PIN1);
  servo2.attach(SERVO_PIN2);
  servo1.write(90);
  servo2.write(0);
}



void loop() 
{


  // 2초 동안 거리 측정 (100ms 간격으로 20회)
  int inRangeCount = 0;
  int totalSamples = 0;
  unsigned long startTime = millis();

  while (millis() - startTime < 2000) 
  {
    float distance = measureDistance();

    if (distance > 0 && distance <= 15) 
    {
      inRangeCount++;
    }

    totalSamples++;
    delay(100);
  }

  float ratio = (float)inRangeCount / totalSamples;

  //비율 50% 이상 구동
  if (ratio >= 0.5) 
  {

      // 초록 LED on, 빨간 off
    analogWrite(LED_RED, 255);
    analogWrite(LED_GREEN, 0);

    BTSerial.println("TRIGGER");

    
    unsigned long btStart=millis();
    while(millis() - btStart < 10000){
    // 2. 블루투스로부터 데이터 수신 (파이썬 -> 아두이노)
      if (BTSerial.available()) {
        String receivedData = BTSerial.readStringUntil('\n');
        receivedData.trim(); // 수신된 문자열 앞뒤의 공백/개행 문자 제거

        // 수신 후 블루투스 시리얼 버퍼에 혹시 남아있을 수 있는 잔여 데이터를 강제로 비움
       
        if (receivedData.length() > 0) {
          char command = receivedData.charAt(0);
          activate(command);
        }

        break;
      }
    }
    // 초록 LED off, 빨간 on
    analogWrite(LED_RED, 0);
    analogWrite(LED_GREEN, 255);
  } 

  delay(1000);
}

