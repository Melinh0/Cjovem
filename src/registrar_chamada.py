from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import io
import re
import glob
import time
import shutil
from datetime import datetime

from config import MOODLE_URL, PLANILHAS_DIR, require_moodle_credentials

USERNAME, PASSWORD = require_moodle_credentials()
TRATADOS_DIR = PLANILHAS_DIR / 'tratados'
COLUNA_NOME = 'Full Name'
STATUS_PRESENTE = 'Pr'

TRATADOS_DIR.mkdir(parents=True, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def tirar_screenshot(nome="erro.png"):
    driver.save_screenshot(nome)
    print(f"📸 Screenshot salvo como {nome}")

def fazer_login():
    print("🔐 Fazendo login...")
    try:
        driver.get(MOODLE_URL)
        time.sleep(3)

        username = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[name='username']")
        ))
        username.send_keys(USERNAME)

        password = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[name='password']")
        ))
        password.send_keys(PASSWORD)

        login_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button#submit")
        ))
        login_btn.click()

        wait.until(EC.url_contains("my"))
        print("✅ Login realizado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Falha no login: {e}")
        tirar_screenshot("erro_login.png")
        return False

def extrair_lista_alunos_moodle(session_id):
    print("📋 Extraindo lista de alunos do Moodle...")
    try:
        session_url = f"https://capacitabrasil.moodlece.com.br/mod/attendance/take.php?id=8787&sessionid={session_id}&grouptype=610"
        print(f"🌐 Acessando sessão para extrair alunos: {session_url}")
        driver.get(session_url)
        time.sleep(3)

        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.CONTROL + 'a')
        time.sleep(1)

        body.send_keys(Keys.CONTROL + 'c')
        time.sleep(1)

        texto_copiado = driver.execute_script("return navigator.clipboard.readText();")

        caminho_lista = PLANILHAS_DIR / "lista_alunos_moodle.txt"
        with open(caminho_lista, 'w', encoding='utf-8') as f:
            f.write(texto_copiado)

        print(f"✅ Lista de alunos copiada e salva em: {caminho_lista}")
        return texto_copiado

    except Exception as e:
        print(f"❌ Erro ao extrair lista de alunos: {e}")
        return ""

def extrair_data_arquivo(nome_arquivo):
    padrao = r'meeting_(\d{2})-(\d{2})-(\d{4})'
    match = re.search(padrao, nome_arquivo)
    if match:
        dia, mes, ano = match.groups()
        return datetime(int(ano), int(mes), int(dia))
    return None

def listar_arquivos_csv():
    arquivos = glob.glob(str(PLANILHAS_DIR / 'meeting_*.csv'))
    arquivos_com_data = []

    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        data = extrair_data_arquivo(nome)
        if data:
            arquivos_com_data.append((arquivo, data))

    arquivos_com_data.sort(key=lambda x: x[1])
    return [arq[0] for arq in arquivos_com_data]

def tratar_csv(arquivo_origem, lista_alunos_moodle):
    try:
        with open(arquivo_origem, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        linhas = conteudo.split('\n')

        inicio_dados = 0
        for i, linha in enumerate(linhas):
            if COLUNA_NOME in linha:
                inicio_dados = i
                break

        dados = '\n'.join(linhas[inicio_dados:])

        df = pd.read_csv(io.StringIO(dados))

        if COLUNA_NOME not in df.columns:
            print(f"⚠️ Coluna '{COLUNA_NOME}' não encontrada no arquivo. Colunas disponíveis: {df.columns.tolist()}")
            return None

        nomes_completos = []
        for nome in df[COLUNA_NOME]:
            nome_correspondente = ""
            melhor_pontuacao = 0

            for aluno_moodle in lista_alunos_moodle.split('\n'):
                palavras_nome = nome.lower().split()
                palavras_moodle = aluno_moodle.lower().split()

                pontuacao = sum(1 for palavra in palavras_nome if palavra in palavras_moodle)
                if pontuacao > melhor_pontuacao:
                    melhor_pontuacao = pontuacao
                    nome_correspondente = aluno_moodle

            if nome_correspondente:
                nomes_completos.append(nome_correspondente)
            else:
                print(f"⚠️ Nome não encontrado no Moodle: {nome}")
                nomes_completos.append(nome)

        df_tratado = pd.DataFrame({
            'nome_completo': nomes_completos,
            'status': STATUS_PRESENTE
        })

        nome_arquivo = os.path.basename(arquivo_origem)
        caminho_tratado = TRATADOS_DIR / f"tratado_{nome_arquivo}"
        df_tratado.to_csv(caminho_tratado, index=False, encoding='utf-8')

        print(f"🔄 Arquivo tratado salvo em: {caminho_tratado}")
        return caminho_tratado

    except Exception as e:
        print(f"❌ Erro ao processar CSV: {e}")
        return None

def processar_sessao(session_id, caminho_csv_tratado):
    try:
        session_url = f"https://capacitabrasil.moodlece.com.br/mod/attendance/take.php?id=8787&sessionid={session_id}&grouptype=610"
        print(f"🌐 Acessando sessão: {session_url}")
        driver.get(session_url)
        time.sleep(3)

        btn_importacao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Enviar frequência por CSV')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView();", btn_importacao)
        btn_importacao.click()
        print("➡️ Acessando página de importação...")

        wait.until(EC.presence_of_element_located((By.ID, "filepicker-button")))
        time.sleep(2)

        btn_escolher = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='button' and contains(@value, 'Escolha um arquivo')]")
        ))
        btn_escolher.click()
        time.sleep(1)

        input_upload = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='file']")
        ))

        input_upload.send_keys(caminho_csv_tratado)
        print(f"📤 Enviando arquivo: {os.path.basename(caminho_csv_tratado)}")
        time.sleep(1)

        btn_enviar_arquivo = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Enviar este arquivo')]")
        ))
        btn_enviar_arquivo.click()

        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "fp-file")))
        print("✅ Upload do arquivo realizado com sucesso!")
        time.sleep(2)

        btn_enviar_final = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='submit' and contains(@value, 'Enviar frequência por CSV')]")
        ))
        btn_enviar_final.click()

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class, 'alert-success')]")
        ))
        print("✅ Frequência registrada com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao processar sessão: {e}")
        tirar_screenshot(f"erro_sessao_{session_id}.png")
        return False

def main():
    try:
        arquivos_csv = listar_arquivos_csv()
        if not arquivos_csv:
            print("❌ Nenhum arquivo CSV encontrado para processar")
            return

        print(f"📂 {len(arquivos_csv)} arquivos CSV encontrados (ordenados do mais antigo)")

        if not fazer_login():
            print("❌ Não foi possível fazer login. Abortando.")
            return

        session_ids = [6253, 6252, 6251, 6250, 6249, 6248, 6247, 6246, 6245, 6244, 6243, 6242, 6241]

        if arquivos_csv:
            primeira_sessao_id = session_ids[0] if session_ids else None
            if primeira_sessao_id:
                lista_alunos_moodle = extrair_lista_alunos_moodle(primeira_sessao_id)
            else:
                print("❌ Nenhuma sessão disponível")
                return
        else:
            print("❌ Nenhum arquivo CSV para processar")
            return

        for i, caminho_csv in enumerate(arquivos_csv):
            if i >= len(session_ids):
                print(f"⚠️ Não há sessão correspondente para o arquivo {i+1}")
                continue

            print(f"\n🔁 Processando arquivo {i+1}/{len(arquivos_csv)}: {os.path.basename(caminho_csv)}")

            csv_tratado = tratar_csv(caminho_csv, lista_alunos_moodle)
            if not csv_tratado:
                print("⚠️ Pulando arquivo devido a erro no tratamento")
                continue

            session_id = session_ids[i]
            sucesso = processar_sessao(session_id, csv_tratado)

            if sucesso:
                backup_dir = PLANILHAS_DIR / 'processados'
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(caminho_csv, backup_dir / os.path.basename(caminho_csv))
                print(f"🗃️ Arquivo original movido para backup")

        print("\n✅ Todos os arquivos processados com sucesso!")

    except Exception as e:
        print(f"❌ Erro no processo principal: {e}")
        tirar_screenshot("erro_principal.png")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
