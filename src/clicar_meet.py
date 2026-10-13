import pyautogui
import time

x = 535
y = 612
m = 441
n = 518

try:
    while True:
        pyautogui.moveTo(x, y)

        for _ in range(5):
            pyautogui.scroll(300)
            time.sleep(0.2)

        pyautogui.click(x, y)
        time.sleep(0.2)
        pyautogui.click(m, n)
        print(f"Clicou em ({x}, {y}) após rolar para cima")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nBot encerrado pelo usuário.")
