import cv2
import requests
import openai
import base64
import serial
import time

# ESP32-CAM의 스트리밍 주소
capture_url = "http://192.168.219.186/capture"

# GPT Vision API 요청
openai.api_key = ""


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


while(True):
  command=input("시작하려면 1")
  if(command=='1'):
    image=set_image()
    output=classify_trash(image)
    print(output)
