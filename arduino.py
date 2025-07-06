import serial
import time
import sys

# 아두이노 블루투스 모듈의 시리얼 포트 이름 (실제 환경에 맞게 변경)
bluetooth_port = 'COM7' # 예시: 'COM3' 또는 '/dev/rfcomm0' 또는 '/dev/tty.Bluetooth-Incoming-Port'
baud_rate = 9600

try:
    ser = serial.Serial(bluetooth_port, baud_rate, timeout=1)
    print(f"{bluetooth_port}에 성공적으로 연결되었습니다.")
    print("아두이노 통신 대기 중...")

    # 초기 수신 버퍼 비우기 (연결 직후 발생할 수 있는 이전 데이터 제거)
    if ser.in_waiting > 0:
        ser.read(ser.in_waiting)
        print("초기 수신 버퍼 비움.")

    while True:
        # 아두이노로부터 데이터 수신 (최대 1초 대기)
        if ser.in_waiting > 0:
            # readline()은 개행 문자를 만날 때까지 읽고, timeout이 설정되어 있으면 해당 시간 동안만 기다립니다.
            received_data = ser.readline().decode('utf-8').strip()

            if received_data: # 빈 문자열이 아닌 경우에만 처리
                print(f"아두이노로부터 수신: {received_data}")

                # 아두이노에서 보낸 신호가 'TRIGGER'인지 확인
                if received_data == "TRIGGER":
                    print("아두이노로부터 'TRIGGER' 신호를 받았습니다!")

                    # 아두이노에게 보낼 문자열 정의
                    response_message = "Python received trigger!"

                    # 데이터를 보내기 전에 혹시 남아있을 수 있는 수신 버퍼를 비웁니다.
                    if ser.in_waiting > 0:
                        ser.read(ser.in_waiting)
                        print("전송 전 수신 버퍼 비움.")

                    # 아두이노에게 문자열 전송 (개행 문자 '\n' 포함)
                    ser.write((response_message + '\n').encode('utf-8'))
                    print(f"아두이노로 '{response_message}' 전송했습니다.")
                    time.sleep(0.5) # 아두이노가 처리할 시간을 주기 위한 지연
                # else:
                #     # 'TRIGGER' 신호가 아닌 다른 응답을 받았을 경우
                #     print(f"알 수 없는 신호 수신: {received_data}")
            # else:
            #     print("아두이노로부터 빈 데이터 수신 (아직 데이터가 도착하지 않았거나, 전송 방식 확인 필요)")

        time.sleep(0.1) # 짧은 지연으로 CPU 사용률 관리 및 다음 데이터 대기
                        # 아두이노의 delay(100)과 맞춰서 0.1초 지연
except serial.SerialException as e:
    print(f"**오류: 시리얼 포트 연결에 실패했습니다.**")
    print(f"  - 오류 메시지: {e}")
    print(f"  - '{bluetooth_port}' 포트가 올바른지 확인하세요.")
    print(f"  - 아두이노 IDE의 시리얼 모니터가 열려있지 않은지 확인하세요 (동시에 사용할 수 없습니다).")
    print(f"  - 블루투스 모듈이 페어링되어 있고 올바른 COM 포트에 연결되었는지 확인하세요.")
except Exception as e:
    print(f"**예상치 못한 오류가 발생했습니다.**")
    print(f"  - 오류 메시지: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("시리얼 포트가 닫혔습니다.")