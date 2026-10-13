import pyautogui
import time
import pyperclip

from config import ALUNOS_PENDENTES_IMERSAO, ler_lista_arquivo

alunos_pendentes = ler_lista_arquivo(ALUNOS_PENDENTES_IMERSAO)
lista_alunos_texto = "\n".join(alunos_pendentes)

mensagem = f"""
@everyone 
Olá, pessoal! Bom dia!

Estamos finalizando o levantamento das atividades e verificamos que alguns de vocês ainda não responderam ao formulário de atividades.

⚠️ Atenção: o preenchimento do formulário é obrigatório. Quem não responder, além de ser considerado como evadido, também não terá direito ao recebimento da bolsa.

Confira abaixo os nomes dos alunos que ainda não responderam:

{lista_alunos_texto}

**Se o seu nome estiver na lista e você já respondeu, por favor, nos avise para que possamos corrigir a informação.**

Contamos com a colaboração de todos para regularizar essa situação o quanto antes!

Atenciosamente,
Equipe Capacita Brasil/C-Jovem."""

pyperclip.copy(mensagem)

pyautogui.click(x=33, y=187)

time.sleep(2)
pyautogui.click(x=373, y=617)

time.sleep(2)
pyautogui.click(x=251, y=531)

time.sleep(2)
pyautogui.click(x=465, y=673)
time.sleep(1)

pyautogui.hotkey('ctrl', 'v')

pyautogui.press('enter')

print("Mensagem enviada no chat da Embrapa!")

time.sleep(2)
pyautogui.click(x=465, y=673)

time.sleep(2)
pyautogui.click(x=239, y=566)

time.sleep(2)
pyautogui.click(x=465, y=673)
time.sleep(1)

pyautogui.hotkey('ctrl', 'v')

pyautogui.press('enter')

print("Mensagem enviada no chat do Nutec!")
