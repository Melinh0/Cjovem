from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import os
import re
import pyautogui
import pyperclip
from PyPDF2 import PdfReader
import docx
import glob

from config import DATA_DIR, require_moodle_credentials

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 15)
actions = ActionChains(driver)

login_url = "https://capacitabrasil.moodlece.com.br/login/index.php"
usuario, senha = require_moodle_credentials()

cd_basico_links = [
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8452",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8459",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8466",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8473",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8480",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8487",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8494",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8501"
]

cd_intermediario_links = [
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8793",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8800",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8807",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8814",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8821",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8828",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8835",
    "https://capacitabrasil.moodlece.com.br/mod/assign/view.php?id=8842"
]

def fazer_login():
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
        return True
    except Exception as e:
        print(f"Falha no login: {str(e)}")
        return False

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

def extrair_descricao_oficina():
    try:
        descricao_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.activity-description div.no-overflow")))
        descricao_texto = descricao_element.text.strip()
        print("\nDescrição da Oficina:\n", descricao_texto[:200] + "..." if len(descricao_texto) > 200 else descricao_texto)
        return descricao_texto
    except Exception as e:
        print(f"Erro ao extrair descrição: {e}")
        return "[Descrição não disponível]"

def classificar_resposta_com_chatgpt(descricao, resposta_aluno, tipo):
    if tipo == "aluno":
        prompt = (
            f"Descrição da Oficina:\n{descricao}\n\n"
            f"Resposta do Aluno:\n{resposta_aluno}\n\n"
            "Classifique a resposta do aluno em uma das seguintes categorias:\n"
            "- Dentro do esperado: a resposta atende ao que foi solicitado\n"
            "- Acima do esperado: a resposta vai além do esperado\n"
            "- Abaixo do Esperado: a resposta não atende ao solicitado\n"
            "- Atividade Ausente: não há resposta do aluno\n\n"
            "Responda APENAS com uma das categorias acima, sem explicações."
        )
    else:
        prompt = (
            f"Descrição da Oficina:\n{descricao}\n\n"
            f"Resposta do Aluno:\n{resposta_aluno}\n\n"
            "Classifique o feedback do professor em uma das seguintes categorias:\n"
            "- Dentro do esperado: feedback adequado e pertinente\n"
            "- Acima do esperado: feedback excepcional e detalhado\n"
            "- Abaixo do Esperado: feedback inadequado ou insuficiente\n"
            "- Atividade Ausente: não há feedback do professor\n\n"
            "Responda APENAS com uma das categorias acima, sem explicações."
        )

    try:
        pyperclip.copy(prompt)
        print("Prompt copiado para o ChatGPT. Aguardando 20 segundos para resposta...")

        time.sleep(2)

        pyautogui.click(x=1866, y=985)
        time.sleep(1)

        pyautogui.click(x=1324, y=532)
        time.sleep(1)

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(20)

        pyautogui.click(x=1300, y=800)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)

        classificacao = pyperclip.paste().strip()

        pyautogui.click(x=1865, y=988)
        time.sleep(1)
        pyautogui.click(x=1229, y=518)
        time.sleep(1)
        pyautogui.click(x=1275, y=679)
        time.sleep(1)
        pyautogui.click(x=1638, y=623)
        time.sleep(2)

        return classificacao

    except Exception as e:
        print(f"Erro ao classificar com ChatGPT: {e}")
        return "Erro na classificação"

def analisar_pagina_aluno(driver, descricao_oficina, oficina_num):
    try:
        nome_aluno = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.page-header-headings h2"))).text.strip()

        resposta_aluno = "[Nenhum arquivo enviado]"
        try:
            file_links = driver.find_elements(By.CSS_SELECTOR, "div.fileuploadsubmission a[target='_blank']")
            if file_links:
                file_links[0].click()
                time.sleep(5)
                latest_file = get_latest_file(os.path.join(os.path.expanduser('~'), 'Downloads'))
                if latest_file:
                    resposta_aluno = extract_file_content(latest_file)[:2000]
        except:
            resposta_aluno = "[Erro na extração]"

        feedback_professor = "[Nenhum feedback encontrado]"
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe#id_assignfeedbackcomments_editor_ifr")
            driver.switch_to.frame(iframe)
            feedback_professor = driver.find_element(By.CSS_SELECTOR, "body#tinymce").text.strip()
            driver.switch_to.default_content()
        except:
            pass

        try:
            nota_input = driver.find_element(By.ID, "id_grade")
            nota_valor = nota_input.get_attribute("value").strip()
        except:
            nota_valor = ""

        if (
            resposta_aluno in ["", "[Nenhum arquivo enviado]", "[Nenhum arquivo encontrado]", "[Erro na extração]"]
            and feedback_professor in ["", "[Nenhum feedback encontrado]"]
            and (nota_valor == "" or nota_valor == "0,00")
        ):
            return nome_aluno, "Não fez", "Não fez"

        classificacao_aluno = classificar_resposta_com_chatgpt(descricao_oficina, resposta_aluno, "aluno")
        classificacao_professor = classificar_resposta_com_chatgpt(descricao_oficina, feedback_professor, "professor")

        return nome_aluno, classificacao_aluno, classificacao_professor

    except:
        return None, "Erro na análise", "Erro na análise"

def criar_dataframe_modelo(nome_curso):
    colunas_base = ['Turma', 'Nome', 'Professores']

    for i in range(1, 9):
        if nome_curso == "CD Básico":
            colunas_base.extend([f'Oficina {i:02d}', f'Resposta Aluno'])
        else:
            colunas_base.extend([f'Oficina {i}', f'Resposta Aluno'])

    if nome_curso == "CD Básico":
        colunas_base.append('Obsevarções')
    else:
        colunas_base.append('Observações')

    return pd.DataFrame(columns=colunas_base)

def processar_curso(links_oficinas, nome_curso):
    df_curso = criar_dataframe_modelo(nome_curso)
    dados_alunos = {}

    for idx, base_url in enumerate(links_oficinas):
        oficina_num = idx + 1
        driver.get(base_url)
        time.sleep(3)
        descricao = extrair_descricao_oficina()

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ver todos os envios')]"))).click()
            time.sleep(3)
        except:
            continue

        while True:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[class*="user"]')))
            linhas = driver.find_elements(By.CSS_SELECTOR, 'tr[class*="user"]')

            for linha in linhas:
                try:
                    nome_completo = linha.find_element(By.CSS_SELECTOR, 'td.c2 a').text.strip()
                    nota_btn = linha.find_element(By.CSS_SELECTOR, 'td.c5 a.btn.btn-primary')
                    nota_url = nota_btn.get_attribute('href')

                    driver.execute_script("window.open(arguments[0]);", nota_url)
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(3)

                    nome_aluno, class_aluno, class_prof = analisar_pagina_aluno(driver, descricao, oficina_num)

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    if nome_aluno:
                        if nome_aluno not in dados_alunos:
                            dados_alunos[nome_aluno] = {'Turma': nome_curso, 'Nome': nome_aluno, 'Professores': ''}
                            for j in range(1, 9):
                                dados_alunos[nome_aluno][f'Oficina {j:02d}' if nome_curso == "CD Básico" else f'Oficina {j}'] = 'Atividade Ausente'
                                dados_alunos[nome_aluno]['Resposta Aluno'] = 'Atividade Ausente'
                            dados_alunos[nome_aluno]['Obsevarções' if nome_curso == "CD Básico" else 'Observações'] = ''

                        if nome_curso == "CD Básico":
                            dados_alunos[nome_aluno][f'Oficina {oficina_num:02d}'] = class_prof
                        else:
                            dados_alunos[nome_aluno][f'Oficina {oficina_num}'] = class_prof
                        dados_alunos[nome_aluno]['Resposta Aluno'] = class_aluno

                except:
                    continue

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'li.nextpage a:not(.disabled)')
                next_button.click()
                time.sleep(3)
            except:
                break

    if dados_alunos:
        df_curso = pd.DataFrame.from_dict(dados_alunos, orient='index').reset_index(drop=True)
    return df_curso

def main():
    if not fazer_login():
        print("Erro no login. Encerrando...")
        driver.quit()
        return

    df_basico = processar_curso(cd_basico_links, "CD Básico")

    if not df_basico.empty:
        nome_arquivo_basico = DATA_DIR / 'CD_Basico_Qualidade_das_respostas.csv'
        df_basico.to_csv(nome_arquivo_basico, index=False, encoding='utf-8')
        print(f"\nPlanilha CD Básico salva: {nome_arquivo_basico}")
        print(f"Total de alunos processados: {len(df_basico)}")
    else:
        print("Nenhum dado processado para CD Básico")

    df_intermediario = processar_curso(cd_intermediario_links, "CD Intermediário")

    if not df_intermediario.empty:
        nome_arquivo_intermediario = DATA_DIR / 'CD_Intermediario_Qualidade_das_respostas.csv'
        df_intermediario.to_csv(nome_arquivo_intermediario, index=False, encoding='utf-8')
        print(f"\nPlanilha CD Intermediário salva: {nome_arquivo_intermediario}")
        print(f"Total de alunos processados: {len(df_intermediario)}")
    else:
        print("Nenhum dado processado para CD Intermediário")

    driver.quit()
    print("\nProcessamento concluído!")

if __name__ == "__main__":
    main()
