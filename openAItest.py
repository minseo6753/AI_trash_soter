import openai

openai.api_key = ""

def classify_trash_from_url(image_url):
    response = openai.chat.completions.create(
        model="gpt-4.1",
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
                    {"type": "text", "text": "Classify the trash in this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "low"  # 비용 절감
                        }
                    }
                ]
            }
        ],
        max_tokens=5  # 최소 토큰만 사용
    )

    return response.choices[0].message.content.strip()

print(classify_trash_from_url("https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMDEwMDZfMTI3%2FMDAxNjAxOTg3NzE3MTQy.DdGSB5_Y08ZjCPNhaHrBk58nVRhyI6Hq-VhpK46sC-4g.fqSr5uWWWdU5iruSD_9atanN4fI5OJpxdCE2fioVBd0g.JPEG.wlgpdydfur12%2F1601987715715.jpg&type=a340"))