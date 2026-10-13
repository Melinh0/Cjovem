from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from config import MOODLE_URL, require_moodle_credentials

options = webdriver.ChromeOptions()
service = ChromeService()
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

participantes_enviados = []

mensagem = """Atenção, alunos! O curso Ciência de Dados – Nível Básico será encerrado em 18 de maio, sem nova prorrogação. A próxima etapa é o nível Intermediário, mas só segue quem concluir o básico! Não deixe para depois o que pode te levar mais longe hoje. Finalize suas atividades e conte com a gente — mentores e professores estão aqui para ajudar. Seu futuro começa com o esforço de agora! https://capacitabrasil.moodlece.com.br/"""

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

    driver.get("https://capacitabrasil.moodlece.com.br/user/index.php?id=248&perpage=5000")
    wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
    time.sleep(3)

    linhas = driver.find_elements(By.XPATH, "//table//tr")
    nomes = []
    for linha in linhas:
        try:
            celula = linha.find_element(By.XPATH, ".//td[1]")
            nome = celula.text.strip().replace("Selecione '", "").replace("'", "")
            if nome and nome not in ["Yago Melo da Costa", "Lucas Vieira Alves"]:
                nomes.append(nome)
        except:
            continue

    nomes = sorted(set(nomes))

    print("Participantes filtrados:")
    for n in nomes:
        print(n)

    driver.get("https://capacitabrasil.moodlece.com.br/message/index.php?id=2726")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-region='send-message-txt']")))
    time.sleep(3)

    for nome in nomes:
        print(f"\nEnviando mensagem para: {nome}")

        try:
            driver.get("https://capacitabrasil.moodlece.com.br/message/index.php?id=2726")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-region='send-message-txt']")))
            time.sleep(2)

            pesquisa_input = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.form-control[placeholder='Pesquisar']")))
            pesquisa_input.clear()
            pesquisa_input.send_keys(nome)

            buscar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-action='search']")))
            buscar_btn.click()
            time.sleep(4)

            nome_normalizado = nome.lower()
            nome_xpath_compat = nome_normalizado.replace("'", "").replace('"', '')

            xpath = f"""//a[contains(@class, 'list-group-item-action')]//h6[contains(@class, 'font-weight-bold')]/span[
                contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÂÊÎÔÛÃÕÀÇ', 'abcdefghijklmnopqrstuvwxyzáéíóúâêîôûãõàç'), 
                "{nome_xpath_compat}")]"""

            resultado = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            resultado.click()
            time.sleep(3)

            mensagem_textarea = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "textarea[data-region='send-message-txt']")))
            mensagem_textarea.clear()
            mensagem_textarea.send_keys(mensagem)
            time.sleep(2)

            enviar_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-action='send-message']")))
            enviar_btn.click()
            time.sleep(2)

            participantes_enviados.append(nome)

        except Exception as e:
            print(f"[!] Não foi possível enviar mensagem para {nome}. Erro: {e}")
            continue

    print("\n✅ Mensagens enviadas com sucesso para os seguintes participantes:")
    for p in participantes_enviados:
        print(f"- {p}")

finally:
    driver.quit()
