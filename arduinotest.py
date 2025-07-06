import serial
import time
import sys

bluetooth_port = 'COM7' # 실제 포트로 변경 필수
baud_rate = 9600

try:
    ser = serial.Serial(bluetooth_port, baud_rate, timeout=1)
    print(f"{bluetooth_port}에 성공적으로 연결되었습니다.")
    print("아두이노와 통신 시작...")

    # 초기 버퍼 비우기 (연결 직후 발생할 수 있는 이전 데이터 제거)
    if ser.in_waiting > 0:
        ser.read(ser.in_waiting) # 버퍼의 모든 데이터를 읽어 비웁니다.
        print("초기 수신 버퍼 비움.")

    while True:
        send_data = input("아두이노로 보낼 값을 입력하세요 ('quit' 입력 시 종료): ")
        if send_data.lower() == 'quit':
            break

        # 데이터를 보내기 전에 혹시 남아있을 수 있는 수신 버퍼를 비웁니다.
        # 이렇게 하면 이전에 받은 응답이 현재 응답처럼 착각되는 것을 방지합니다.
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            print("전송 전 수신 버퍼 비움.")

        ser.write((send_data + '\n').encode('utf-8'))
        print(f"'{send_data}'를 아두이노로 전송했습니다.")

        # 아두이노가 처리하고 응답을 보낼 충분한 시간을 줍니다.
        # 통신 속도와 아두이노 처리 시간에 따라 이 값을 조정할 수 있습니다.
        # 너무 짧으면 문제가 다시 발생하고, 너무 길면 비효율적입니다.
        time.sleep(0.5) # 0.1초에서 0.2초로 약간 늘려보세요.

        # 아두이노로부터 데이터 수신 (최대 1초 대기)
        if ser.in_waiting > 0:
            # readline()은 개행 문자를 만날 때까지 읽고,
            # timeout이 설정되어 있으면 해당 시간 동안만 기다립니다.
            received_data = ser.readline().decode('utf-8').strip()
            if received_data:
                print(f"아두이노로부터 수신: {received_data}")
            else:
                print("아두이노로부터 빈 데이터 수신 (아직 데이터가 도착하지 않았거나, 전송 방식 확인 필요)")
        else:
            print("아두이노로부터 응답이 없습니다.")

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