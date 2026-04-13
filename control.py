import pyautogui


def click():
    pyautogui.click()


def double_click():
    pyautogui.doubleClick()


def scroll_down():
    pyautogui.scroll(-500)


def scroll_up():
    pyautogui.scroll(500)


def type_text(text):
    pyautogui.write(text)


def press_enter():
    pyautogui.press("enter")
