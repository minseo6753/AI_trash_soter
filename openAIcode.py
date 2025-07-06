import cv2
import requests
import openai
import base64
import serial
import time

# ESP32-CAM의 스트리밍 주소
stream_url = "http://192.168.0.101:81/stream"

# GPT Vision API 요청
openai.api_key = ""

def set_image():
  # 프레임 캡처 (1장만)
  cap = cv2.VideoCapture(stream_url)
  ret, frame = cap.read()
  cap.release()

  # 이미지 인코딩 → base64 변환
  _, buffer = cv2.imencode('.jpg', frame)
  b64_image = base64.b64encode(buffer).decode('utf-8')
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


# 아두이노 연결
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

while(True):
  # 아두이노에서 쓰레기 투입 신호 받음
   arduino.read()

   if():
      
      arduino.write(classify_trash(set_image()).encode())