import pyautogui
import time

print("Posicione o mouse onde deseja pegar a coordenada.")
print("Clique para capturar as coordenadas.")

while True:
    x, y = pyautogui.position()
    print(f"Coordenada X: {x}, Coordenada Y: {y}")

    time.sleep(5)
