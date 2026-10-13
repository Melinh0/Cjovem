import pandas as pd
import openpyxl
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from config import DATA_DIR, MOODLE_URL, require_moodle_credentials

ARQUIVO_NOTAS = DATA_DIR / 'notas_alunos.xlsx'
ARQUIVO_PRINCIPAL = DATA_DIR / 'planilha_notas.xlsx'
ARQUIVO_PRINCIPAL_ATUALIZADA = DATA_DIR / 'planilha_notas_atualizada.xlsx'

def normalizar_nome(nome):
    return unidecode(str(nome)).lower().strip()

def extrair_notas_moodle():
    print("Iniciando extração de notas do Moodle...")

    options = webdriver.ChromeOptions()
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        username, password = require_moodle_credentials()
        driver.get(MOODLE_URL)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        username_input = driver.find_element(By.NAME, "username")
        username_input.send_keys(username)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        login_button = driver.find_element(By.ID, "submit")
        login_button.click()

        wait.until(EC.url_changes(MOODLE_URL))
        time.sleep(3)

        driver.get("https://capacitabrasil.moodlece.com.br/grade/report/grader/index.php?id=249&report=grader&perpage=0")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "userfield")))
        time.sleep(3)

        alunos = []

        linhas_alunos = driver.find_elements(By.CSS_SELECTOR, "tr.userrow")

        for linha in linhas_alunos:
            try:
                nome_element = linha.find_element(By.CSS_SELECTOR, "th a.username")
                nome_aluno = nome_element.text

                nota_element = linha.find_element(By.CSS_SELECTOR, "td.course span.gradevalue")
                nota_texto = nota_element.text

                try:
                    nota = float(nota_texto.replace(',', '.'))
                except ValueError:
                    nota = 0.0

                alunos.append([nome_aluno, nota])

            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue

        df = pd.DataFrame(alunos, columns=['Nome do Aluno', 'Nota Total'])

        df = df.sort_values(by='Nome do Aluno')

        df.to_excel(ARQUIVO_NOTAS, index=False)

        print(f"Dados salvos com sucesso em '{ARQUIVO_NOTAS.name}'")
        print(f"Total de alunos encontrados: {len(alunos)}")
        print("Lista ordenada alfabeticamente")
        return True

    except Exception as e:
        print(f"Erro durante a extração: {e}")
        return False
    finally:
        driver.quit()

def atualizar_planilha_principal():
    print("\nIniciando atualização da planilha principal...")

    try:
        planilha_principal = pd.read_excel(ARQUIVO_PRINCIPAL, sheet_name='Página1')
        planilha_notas = pd.read_excel(ARQUIVO_NOTAS, sheet_name='Sheet1')

        notas_dict = {}
        for _, row in planilha_notas.iterrows():
            nome_completo = row['Nome do Aluno']

            if '\n' in str(nome_completo):
                nome_limpo = nome_completo.split('\n')[1]
            else:
                nome_limpo = nome_completo

            nome_normalizado = normalizar_nome(nome_limpo)
            nota = row['Nota Total']

            if pd.isna(nota) or nota == '':
                nota = 0.0

            notas_dict[nome_normalizado] = nota

        wb = openpyxl.load_workbook(ARQUIVO_PRINCIPAL)
        ws = wb['Página1']

        alunos_atualizados = 0
        for idx, row in planilha_principal.iterrows():
            row_num = idx + 2
            nome_aluno = str(row['Nome'])
            nome_normalizado = normalizar_nome(nome_aluno)

            if nome_normalizado in notas_dict:
                ws.cell(row=row_num, column=11).value = notas_dict[nome_normalizado]
                alunos_atualizados += 1

        wb.save(ARQUIVO_PRINCIPAL_ATUALIZADA)

        nomes_encontrados = sum(1 for nome in planilha_principal['Nome']
                               if normalizar_nome(str(nome)) in notas_dict)

        print(f"Planilha atualizada salva como '{ARQUIVO_PRINCIPAL_ATUALIZADA.name}'")
        print(f"\nEstatísticas:")
        print(f"Total de alunos na planilha principal: {len(planilha_principal)}")
        print(f"Alunos com notas encontradas: {nomes_encontrados}")
        print(f"Alunos sem correspondência: {len(planilha_principal) - nomes_encontrados}")
        print(f"Alunos atualizados: {alunos_atualizados}")

        return True

    except Exception as e:
        print(f"Erro durante a atualização da planilha: {e}")
        return False

def main():
    print("=== SISTEMA DE ATUALIZAÇÃO DE NOTAS ===\n")

    if extrair_notas_moodle():
        print("\n" + "="*50)

        if atualizar_planilha_principal():
            print("\nProcesso concluído com sucesso!")
        else:
            print("\nErro na atualização da planilha principal.")
    else:
        print("\nErro na extração de notas do Moodle.")

if __name__ == "__main__":
    main()
