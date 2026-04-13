import mss
import ollama
from PIL import Image


def capture_screen():

    with mss.mss() as sct:

        monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        path = "screen.png"

        img.save(path)

        return path


def analyze_screen(question):

    path = capture_screen()

    response = ollama.chat(
        model="llava",
        messages=[
            {
                "role": "user",
                "content": question,
                "images": [path]
            }
        ]
    )

    return response["message"]["content"]
