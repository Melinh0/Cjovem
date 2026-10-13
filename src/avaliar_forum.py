from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import pyperclip

from config import DATA_DIR, OUTPUT_DIR, require_moodle_credentials

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 10)

login_url = "https://capacitabrasil.moodlece.com.br/login/index.php"
usuario, senha = require_moodle_credentials()

forum_links = [
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=8988",
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=8995",
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=9002",
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=9009",
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=9016",
    "https://capacitabrasil.moodlece.com.br/mod/forum/view.php?id=9023",

]

driver.get(login_url)
wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(usuario)
driver.find_element(By.ID, "password").send_keys(senha)
driver.find_element(By.ID, "loginbtn").click()

try:
    wait.until(
        EC.any_of(
            EC.presence_of_element_located((By.ID, "page-wrapper")),
            EC.presence_of_element_located((By.ID, "region-main")),
            EC.presence_of_element_located((By.CLASS_NAME, "usertext"))
        )
    )
    print("Login realizado com sucesso.")
except Exception:
    print("Erro no login: não foi possível encontrar o elemento esperado após login.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "pagina_erro.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.quit()
    exit(1)

topicos_visitados = set()

for forum_url in forum_links:
    print(f"\nAcessando fórum: {forum_url}")
    driver.get(forum_url)
    time.sleep(2)

    try:
        descricao_element = driver.find_element(By.CSS_SELECTOR, "div.activity-description")
        descricao_texto = descricao_element.text.strip()
        print("\nDescrição do Fórum:\n", descricao_texto)
        print("-" * 80)
    except Exception:
        descricao_texto = "[Não foi possível capturar a descrição do fórum]"
        print("\nDescrição do Fórum:\n", descricao_texto)
        print("-" * 80)

    while True:
        discussions = driver.find_elements(By.CSS_SELECTOR, 'tr.discussion')
        encontrou = False

        for discussion in discussions:
            try:
                replies = discussion.find_element(By.CSS_SELECTOR, 'td:nth-last-child(3) span')
                if replies.text.strip() == "0":
                    topic_link = discussion.find_element(By.CSS_SELECTOR, 'th.topic a')
                    topic_href = topic_link.get_attribute("href")

                    if topic_href not in topicos_visitados:
                        print(f"Acessando tópico: {topic_href}")
                        topicos_visitados.add(topic_href)
                        driver.execute_script("window.open(arguments[0]);", topic_href)
                        driver.switch_to.window(driver.window_handles[1])
                        time.sleep(3)

                        try:
                            author_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mb-3 a")))
                            message_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fullmessage")))

                            nome_aluno = author_element.text.strip()
                            resposta = message_element.text.strip()

                            print(f"Aluno: {nome_aluno}")
                            print("Resposta:\n", resposta)
                            print("-" * 50)

                            try:
                                rating_select_elem = wait.until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "select.ratinginput")))
                                select = Select(rating_select_elem)
                                select.select_by_value("10")
                                print("Resposta avaliada com nota 10.")
                                avaliou_com_sucesso = True
                                time.sleep(1)
                            except Exception as e:
                                print("Não foi possível avaliar automaticamente:", e)
                                avaliou_com_sucesso = False

                            with open(DATA_DIR / "respostas_forum.txt", "a", encoding="utf-8") as f:
                                f.write(f"Fórum: {forum_url}\n")
                                f.write(f"Tópico: {topic_href}\n")
                                f.write("Descrição do Fórum:\n")
                                f.write(descricao_texto + "\n\n")
                                f.write(f"Aluno: {nome_aluno}\n")
                                f.write("Resposta:\n")
                                f.write(resposta + "\n")
                                f.write("-" * 80 + "\n\n")

                            if avaliou_com_sucesso:
                                time.sleep(2)

                                texto_copiado = (
                                    f"Descrição do Fórum:\n{descricao_texto}\n\n"
                                    f"Aluno: {nome_aluno}\n"
                                    f"Resposta:\n{resposta}\n\n"
                                    "--->Escreva um feedback para a resposta do aluno na atividade. "
                                    "Quero apenas o feedback e não uma frase sua dizendo que entendeu o comando."
                                )

                                pyperclip.copy(texto_copiado)
                                print("Texto copiado para a área de transferência.")

                                time.sleep(2)

                                pyautogui.click(x=789, y=443)
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
                                    (1314, 505),
                                    (1022, 596),
                                    (731, 523),
                                    (731, 523),
                                    (731, 551),
                                    (731, 551),
                                    (731, 587),
                                    (731, 587),
                                    (711, 114),
                                    (902, 496),
                                    (935, 637),
                                    (1189, 467),
                                    (741, 157),
                                ]

                                for x, y in coordenadas:
                                    pyautogui.click(x=x, y=y)
                                    time.sleep(5)

                                try:
                                    responder_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Responder")]')))
                                    responder_btn.click()
                                    print("Botão 'Responder' clicado.")
                                except Exception as e:
                                    print("Erro ao clicar no botão 'Responder':", e)

                                try:
                                    private_checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="privatereply"]')))
                                    if not private_checkbox.is_selected():
                                        private_checkbox.click()
                                        print("Caixa 'Resposta privada' marcada.")
                                except Exception as e:
                                    print("Erro ao marcar 'Resposta privada':", e)

                                try:
                                    text_area = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Escreva sua resposta ...']"))
                                    )

                                    driver.execute_script("arguments[0].scrollIntoView(true);", text_area)
                                    time.sleep(3)

                                    pyautogui.click(x=92, y=146)

                                    pyautogui.hotkey('ctrl', 'v')
                                    time.sleep(1)

                                    print("Texto colado na área de resposta com sucesso.")
                                except Exception as e:
                                    print("Erro ao colar resposta:", e)

                                try:
                                    send_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-action="forum-inpage-submit"]')))
                                    send_btn.click()
                                    print("Mensagem enviada com sucesso.")
                                except Exception as e:
                                    print("Erro ao clicar em 'Enviar mensagem':", e)

                                time.sleep(5)

                        except Exception as e:
                            print("Erro ao coletar nome ou resposta:", e)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(2)
                        encontrou = True

            except Exception as e:
                print("Erro ao processar discussão:", e)

        if not encontrou:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Próximo"]')
                if "disabled" in next_button.get_attribute("class"):
                    print("Fim das páginas deste fórum.")
                    break
                else:
                    print("Indo para a próxima página do fórum...")
                    next_button.click()
                    time.sleep(2)
            except Exception:
                print("Não encontrou botão de próxima página. Encerrando este fórum.")
                break

driver.quit()
