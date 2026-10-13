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

    driver.get("https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=8786")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navitem")))
    time.sleep(3)

    adicionar_topico_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".navitem a.btn-primary")))
    adicionar_topico_btn.click()
    time.sleep(3)

    assunto_input = wait.until(EC.element_to_be_clickable((By.ID, "id_subject")))
    assunto_input.clear()
    assunto_input.send_keys("LEMBRETE IMPORTANTE")

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "id_message_ifr")))
    corpo_msg = driver.find_element(By.ID, "tinymce")
    corpo_msg.click()
    corpo_msg.send_keys("""
@everyone 
🚀 Atenção, alunos! Vamos juntos avançar!

Iniciaremos nossas aulas de recuperação dos cursos de Ciência de Dados Básico e Lógica de Programação, a partir do dia 02 de junho, em formato síncrono, ou seja, com encontros ao vivo.
Essa é uma oportunidade valiosa para reforçar seu aprendizado, tirar dúvidas em tempo real e garantir que você esteja preparado para seguir em frente na sua jornada.

🧠💻 Nosso compromisso é te apoiar! Sua participação e dedicação agora farão toda a diferença no seu desenvolvimento.

Confira os cronogramas das aulas síncronas de recuperação:

🔹 Ciência de Dados Básico
📅 Terças e Quintas
⏰ 17h às 18h30 (Aluno: Ivo)

📅 Segundas e Quartas
⏰ 14h às 15h30 (Aluno: Normando)

🔸 Lógica de Programação
📅 Segundas e Quartas
⏰ 17h às 18h30 (Aluna: Letícia)

📅 Terças e Quintas
⏰ 17h às 18h30 (Aluno: Alexandre Nery)

💡 Aproveite essa chance para revisar, praticar, aprender e superar desafios. Sua participação nas aulas síncronas é fundamental!

👊✨ Vamos juntos rumo ao sucesso!

Atenciosamente,
Equipe Capacita Brasil/Uece.
""")
    driver.switch_to.default_content()
    time.sleep(2)

    enviar_btn = wait.until(EC.element_to_be_clickable((By.ID, "id_submitbutton")))
    enviar_btn.click()

    print("✅ Tópico criado com sucesso!")

except Exception as e:
    print(f"❌ Erro ao criar o tópico: {e}")

finally:
    time.sleep(5)
    driver.quit()
