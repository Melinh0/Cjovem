import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MOODLE_URL = os.getenv("MOODLE_URL", "https://capacitabrasil.moodlece.com.br/")
MOODLE_USERNAME = os.getenv("MOODLE_USERNAME", "")
MOODLE_PASSWORD = os.getenv("MOODLE_PASSWORD", "")

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

DATA_DIR = BASE_DIR / "data"
PLANILHAS_DIR = DATA_DIR / "planilhas"
OUTPUT_DIR = BASE_DIR / "output"
GRAFICOS_DIR = BASE_DIR / "docs" / "graficos"

DESTINATARIOS_IMERSAO = DATA_DIR / "destinatarios_imersao.txt"
ALUNOS_PENDENTES_IMERSAO = DATA_DIR / "alunos_pendentes_imersao.txt"


def require_env(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise SystemExit(
            f"A variavel '{name}' nao esta configurada. "
            f"Copie '.env.example' para '.env' e preencha com seus dados."
        )
    return value


def require_moodle_credentials() -> tuple[str, str]:
    username = require_env("MOODLE_USERNAME")
    password = require_env("MOODLE_PASSWORD")
    return username, password


def require_email_credentials() -> tuple[str, str]:
    email = require_env("EMAIL_REMETENTE")
    senha = require_env("EMAIL_SENHA_APP")
    return email, senha


def ler_lista_arquivo(caminho: Path) -> list[str]:
    if not caminho.exists():
        raise SystemExit(
            f"Arquivo nao encontrado: {caminho}\n"
            f"Crie o arquivo com um item por linha (veja o arquivo .example correspondente)."
        )
    with open(caminho, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]
