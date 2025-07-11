import serial
import time
import sys
import requests
import openai
import base64

# ESP32-CAM의 스트리밍 주소
capture_url = "http://192.168.219.186/capture"

# GPT Vision API 요청
openai.api_key = ""


# 아두이노 블루투스 모듈의 시리얼 포트 이름 (실제 환경에 맞게 변경)
bluetooth_port = 'COM7' # 예시: 'COM3' 또는 '/dev/rfcomm0' 또는 '/dev/tty.Bluetooth-Incoming-Port'
baud_rate = 9600
reconnect_interval = 5 # 재연결 시도 간격 (초)

ser = None # 시리얼 객체를 전역으로 선언

def set_image():
    response = requests.get(capture_url)
    image_data = response.content
    b64_image = base64.b64encode(image_data).decode('utf-8')
    return b64_image


def classify_trash(image):
  response = openai.chat.completions.create(
      model="gpt-4o",
      messages=[
          {
              "role": "system",
              "content": "You are a trash classification system. "
                "Only respond with one of the following: plastic, can, glass, other. "
                "Plastic includes PET bottles and hard plastic items. "
                "Vinyl, plastic bags, or film should be classified as 'other'. "
                "Straws should be classified as 'other'. "
                "respond only in lowercase. "
          },
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "Classify the trash in this image"},
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": f"data:image/jpeg;base64,{image}",
                          "detail": "low"
                      }
                  }
              ]
          }
      ],
      max_tokens=5
  )

  return response.choices[0].message.content.strip()


try:
    while True:
        try:
            # 시리얼 포트가 연결되어 있지 않거나 닫혀 있으면 새로 연결 시도
            if ser is None or not ser.is_open:
                print(f"'{bluetooth_port}'에 연결 시도 중...")
                ser = serial.Serial(bluetooth_port, baud_rate, timeout=1)
                print(f"'{bluetooth_port}'에 성공적으로 연결되었습니다.")
                print("아두이노 통신 대기 중...")

                # 초기 수신 버퍼 비우기 (연결 직후 발생할 수 있는 이전 데이터 제거)
                if ser.in_waiting > 0:
                    ser.read(ser.in_waiting)
                    print("초기 수신 버퍼 비움.")

            # 연결이 성공적으로 이루어졌을 때만 통신 로직 실행
            # 이 내부 while 루프는 연결이 유지되는 동안 계속 실행됩니다.
            while ser.is_open:
                # 아두이노로부터 데이터 수신 (최대 1초 대기)
                if ser.in_waiting > 0:
                    try:
                        # readline()은 개행 문자를 만날 때까지 읽고, timeout이 설정되어 있으면 해당 시간 동안만 기다립니다.
                        received_data = ser.readline().decode('utf-8').strip()

                        if received_data: # 빈 문자열이 아닌 경우에만 처리
                            print(f"아두이노로부터 수신: {received_data}")

                            # 아두이노에서 보낸 신호가 'TRIGGER'인지 확인
                            if received_data == "TRIGGER":
                                print("아두이노로부터 'TRIGGER' 신호를 받았습니다!")

                                image=set_image()
                                trash=classify_trash(image)

                                if(trash=="plastic"):
                                    response_message="1"
                                elif(trash=="glass"):
                                    response_message="2"
                                elif(trash=="can"):
                                    response_message="3"
                                elif(trash=="other"):
                                    response_message="4"
                                else:
                                    response_message="0"
                                print(trash)
                                print(response_message)

                                # 데이터를 보내기 전에 혹시 남아있을 수 있는 수신 버퍼를 비웁니다.
                                if ser.in_waiting > 0:
                                    ser.read(ser.in_waiting)
                                    print("전송 전 수신 버퍼 비움.")

                                # 아두이노에게 문자열 전송 (개행 문자 '\n' 포함)
                                ser.write((response_message + '\n').encode('utf-8'))
                                print(f"아두이노로 '{response_message}' 전송했습니다.")
                                time.sleep(0.5) # 아두이노가 처리할 시간을 주기 위한 지연
                    except UnicodeDecodeError:
                        print("수신된 데이터를 디코딩하는 중 오류가 발생했습니다. 유효하지 않은 UTF-8 문자일 수 있습니다.")
                        # 이 경우, 버퍼를 비우고 다음 데이터를 기다립니다.
                        if ser.in_waiting > 0:
                            ser.read(ser.in_waiting)
                    except serial.SerialException as e:
                        # 통신 중 시리얼 오류 발생 (예: 아두이노 연결 끊김)
                        print(f"**통신 중 시리얼 오류 발생: {e}**")
                        print("연결이 끊어졌을 수 있습니다. 재연결을 시도합니다.")
                        if ser.is_open: # 현재 열려있는 포트가 있다면 닫아줍니다.
                            ser.close()
                        ser = None # 시리얼 객체를 None으로 설정하여 외부 루프에서 재연결 시도
                        break # 내부 while 루프를 빠져나와 외부 루프에서 재연결 시도
                
                time.sleep(0.1) # 짧은 지연으로 CPU 사용률 관리 및 다음 데이터 대기

        except serial.SerialException as e:
            # 연결 시도 중 시리얼 포트 오류 발생
            print(f"**오류: 시리얼 포트 연결에 실패했습니다.**")
            print(f"  - 오류 메시지: {e}")
            print(f"  - '{bluetooth_port}' 포트가 올바른지 확인하세요.")
            print(f"  - 아두이노 IDE의 시리얼 모니터가 열려있지 않은지 확인하세요 (동시에 사용할 수 없습니다).")
            print(f"  - 블루투스 모듈이 페어링되어 있고 올바른 COM 포트에 연결되었는지 확인하세요.")
            if ser and ser.is_open: # 연결 실패 시 ser가 None이 아닐 수 있으므로 확인 후 닫기
                ser.close()
            ser = None # 시리얼 객체를 None으로 설정하여 다음 루프에서 재연결 시도
        except Exception as e:
            # 예상치 못한 다른 오류 발생
            print(f"**예상치 못한 오류가 발생했습니다.**")
            print(f"  - 오류 메시지: {e}")
            if ser and ser.is_open:
                ser.close()
            ser = None # 시리얼 객체를 None으로 설정하여 다음 루프에서 재연결 시도
        
        # 연결이 끊어졌거나 실패했을 경우, 일정 시간 대기 후 재연결 시도
        if ser is None or not ser.is_open:
            print(f"{reconnect_interval}초 후 재연결 시도...")
            time.sleep(reconnect_interval)

except KeyboardInterrupt:
    # 사용자가 Ctrl+C를 눌러 프로그램을 종료할 때
    print("\n프로그램을 종료합니다. 시리얼 포트를 닫습니다.")
finally:
    # 프로그램이 완전히 종료되기 전에 시리얼 포트 닫기 (Ctrl+C 외의 다른 방식으로 종료될 경우 대비)
    if ser is not None and ser.is_open:
        ser.close()
        print("시리얼 포트가 닫혔습니다.")

