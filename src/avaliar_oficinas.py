from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import pyperclip
import os
from PyPDF2 import PdfReader
import docx
import glob

from config import OUTPUT_DIR, require_moodle_credentials

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 15)

login_url = "https://capacitabrasil.moodlece.com.br/login/index.php"
usuario, senha = require_moodle_credentials()

oficina_base_links = [
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8866",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8871",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8876",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8881"
]

driver.get(login_url)
try:
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)

    driver.find_element(By.ID, "loginbtn").click()

    wait.until(EC.any_of(
        EC.presence_of_element_located((By.CLASS_NAME, "userpicture")),
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Painel")),
        EC.presence_of_element_located((By.ID, "page-wrapper"))
    ))
    print("Login realizado com sucesso.")
except Exception as e:
    print(f"Falha no login: {str(e)}")
    driver.quit()
    exit(1)

def get_latest_file(download_path):
    list_of_files = glob.glob(os.path.join(download_path, '*'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def extract_file_content(file_path):
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return f"[Conteúdo não extraído - formato não suportado: {os.path.basename(file_path)}]"
    except Exception as e:
        print(f"Erro ao extrair conteúdo do arquivo: {e}")
        return f"[Erro ao extrair conteúdo do arquivo: {os.path.basename(file_path)}]"

for base_url in oficina_base_links:
    print(f"\nProcessando oficina: {base_url}")

    driver.get(base_url)
    time.sleep(3)

    try:
        descricao_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.no-overflow")))
        descricao_texto = descricao_element.text.strip()
        print("\nDescrição da Oficina:\n", descricao_texto)
    except Exception:
        descricao_texto = "[Descrição não disponível]"
        print("Não foi possível capturar a descrição da oficina")

    try:
        ver_envios_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ver todos os envios')]")))
        ver_envios_btn.click()
        print("Acessando página de avaliação...")
        time.sleep(3)
    except Exception as e:
        print(f"Erro ao acessar envios: {e}")
        continue

    page_count = 1

    while True:
        print(f"\nProcessando página {page_count}...")
        linhas_envio = driver.find_elements(By.CSS_SELECTOR, 'tr[class*="user"]')
        if not linhas_envio:
            print("Nenhum envio encontrado nesta página.")
            break

        for linha in linhas_envio:
            try:
                status_td = linha.find_element(By.CSS_SELECTOR, 'td.c4')

                avaliado_divs = status_td.find_elements(By.CSS_SELECTOR, 'div.submissiongraded')
                if avaliado_divs:
                    print("Aluno já avaliado, pulando...")
                    continue

                enviado_divs = status_td.find_elements(By.CSS_SELECTOR, 'div.submissionstatussubmitted')
                if enviado_divs:
                    print("Aluno enviado para avaliação, processando...")
                    nota_btn = linha.find_element(By.CSS_SELECTOR, 'td.c5 a.btn-primary')
                    nota_url = nota_btn.get_attribute('href')

                    print(f"Acessando avaliação: {nota_url}")
                    driver.execute_script("window.open(arguments[0]);", nota_url)
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(3)

                    try:
                        try:
                            nome_aluno = driver.find_element(By.CSS_SELECTOR, 'div.user-info h4').text.strip()
                        except:
                            try:
                                nome_aluno = driver.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            except:
                                nome_aluno = driver.find_element(By.CSS_SELECTOR, 'h2').text.strip()

                        print(f"\nAvaliando aluno: {nome_aluno}")

                        file_links = driver.find_elements(By.CSS_SELECTOR, 'div.fileuploadsubmission a[target="_blank"]')
                        if file_links:
                            file_links[0].click()
                            print("Arquivo clicado para download...")
                            time.sleep(5)

                            latest_file = get_latest_file(os.path.expanduser('~\\Downloads'))
                            if latest_file:
                                print(f"Arquivo mais recente: {latest_file}")
                                resposta = extract_file_content(latest_file)
                            else:
                                resposta = "[Arquivo não encontrado após download]"
                        else:
                            resposta = "[Nenhum arquivo encontrado]"

                        print("\nResposta extraída:\n", resposta[:500] + "..." if len(resposta) > 500 else resposta)

                        prompt = (
                            f"Descrição da Oficina:\n{descricao_texto}\n\n"
                            f"Aluno: {nome_aluno}\n"
                            f"Resposta:\n{resposta}\n\n"
                            "Escreva um feedback para a resposta do aluno na atividade. "
                            "Quero apenas o feedback e não uma frase sua dizendo que entendeu o comando. "
                            "Caso o arquivo não seja encontrado ou não tenha acesso ao texto da resposta do aluno, escreva um resposta genérica dizendo que o aluno fez um ótimo trabalho."
                        )
                        pyperclip.copy(prompt)
                        print("\nPrompt copiado para o ChatGPT. Aguardando 30 segundos para resposta...")

                        time.sleep(2)

                        pyautogui.click(x=1313, y=399)
                        time.sleep(1)
                        pyautogui.click(x=743, y=395)
                        time.sleep(1)

                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(1)
                        pyautogui.hotkey('ctrl', 'enter')
                        pyautogui.hotkey('ctrl', 'enter')
                        time.sleep(1)
                        feedback_text = " --->Escreva um feedback para a resposta do aluno na atividade. Quero apenas o feedback e não uma frase sua dizendo que entendeu o comando"
                        pyperclip.copy(feedback_text)
                        time.sleep(1)
                        pyautogui.hotkey('enter')
                        time.sleep(1)

                        print("Aguardando 20 segundos após colagem do feedback...")
                        time.sleep(20)

                        coordenadas = [
                            (1309, 448),
                            (1024, 551),
                            (731, 523),
                            (731, 523),
                            (731, 555),
                            (731, 555),
                            (731, 587),
                            (731, 587),
                            (218, 490),
                            (248, 648),
                            (858, 437),
                            (70, 156),
                        ]

                        for idx, (x, y) in enumerate(coordenadas):
                            pyautogui.click(x=x, y=y)
                            print(f"Clicado em coordenada {idx + 1}: ({x}, {y})")
                            time.sleep(5)

                            if idx == 7:
                                print("Simulando Win + seta para cima...")
                                pyautogui.keyDown('win')
                                pyautogui.press('up')
                                pyautogui.keyUp('win')
                                time.sleep(2)

                        print("Simulando Win + seta para a direita...")
                        pyautogui.keyDown('win')
                        pyautogui.press('right')
                        pyautogui.keyUp('win')
                        time.sleep(2)

                        feedback = pyperclip.paste()
                        print("\nFeedback recebido do ChatGPT:\n", feedback[:500] + "..." if len(feedback) > 500 else feedback)

                        grade_input = wait.until(EC.element_to_be_clickable((By.ID, 'id_grade')))
                        grade_input.click()
                        grade_input.clear()
                        grade_input.send_keys("10")
                        print("Nota 10 atribuída.")

                        iframe = wait.until(EC.presence_of_element_located((By.ID, 'id_assignfeedbackcomments_editor_ifr')))
                        driver.switch_to.frame(iframe)
                        editor = wait.until(EC.presence_of_element_located((By.ID, 'tinymce')))
                        editor.clear()
                        editor.send_keys(feedback)
                        driver.switch_to.default_content()
                        print("Feedback colado no editor.")

                        salvar_btn = driver.find_element(By.CSS_SELECTOR, 'button[name="savechanges"]')
                        salvar_btn.click()
                        print("Avaliação salva com sucesso.")
                        time.sleep(3)

                    except Exception as e:
                        print("Não foi possível localizar o nome do aluno. Verifique o seletor.")
                        print("Salvando trecho de página para debug...")
                        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                        with open(OUTPUT_DIR / "pagina_avaliacao_debug.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        raise e

                    finally:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(2)

            except Exception as e:
                print(f"Erro ao processar linha: {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.nextpage a:not(.disabled)')
            print("Indo para próxima página...")
            next_button.click()
            time.sleep(3)
            page_count += 1
        except:
            print("Fim das páginas desta oficina.")
            break

print("\nProcessamento concluído!")
driver.quit()
