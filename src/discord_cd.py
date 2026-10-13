import pyautogui
import time
import pyperclip

mensagem = """
@everyone 
Olá pessoal,

                        

lembrando do nosso encontro hoje às 20:00 pelo link:

                        

https://meet.google.com/xyk-vdns-gar"""

pyperclip.copy(mensagem)

time.sleep(2)
pyautogui.click(x=369, y=647)
time.sleep(2)
pyautogui.click(x=369, y=647)
time.sleep(2)
pyautogui.click(x=149, y=320)
time.sleep(2)
pyautogui.click(x=465, y=673)
time.sleep(2)

pyautogui.hotkey('ctrl', 'v')

pyautogui.press('enter')

print("Mensagem enviada ao chat da turma!")

pyautogui.click(x=192, y=345)
time.sleep(2)
pyautogui.click(x=465, y=673)
time.sleep(2)

pyautogui.hotkey('ctrl', 'v')

pyautogui.press('enter')

print("Mensagem enviada aos avisos da turma!")

time.sleep(2)
