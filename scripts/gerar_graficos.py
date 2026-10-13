import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PLANILHAS_DIR = DATA_DIR / "planilhas"
GRAFICOS_DIR = BASE_DIR / "docs" / "graficos"
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

COR_PRINCIPAL = "#1f6feb"
COR_SECUNDARIA = "#f0b429"
COR_ALERTA = "#d64545"
COR_OK = "#2da44e"
COR_FUNDO = "#ffffff"

plt.rcParams.update({
    "figure.facecolor": COR_FUNDO,
    "axes.facecolor": COR_FUNDO,
    "axes.edgecolor": "#cccccc",
    "axes.grid": True,
    "grid.color": "#eaeaea",
    "grid.linestyle": "-",
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

PARTICIPACAO_ENCONTROS = {
    "27/05": 34,
    "29/05": 36,
    "03/06": 40,
    "05/06": 32,
    "10/06": 37,
    "17/06": 35,
}


def salvar(fig, nome: str) -> None:
    caminho = GRAFICOS_DIR / nome
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico salvo: {caminho.relative_to(BASE_DIR)}")


def grafico_engajamento_turma() -> None:
    df = pd.read_excel(PLANILHAS_DIR / "Status_Alunos_TQ14.xlsx", header=None)
    dados = df.iloc[7:, [3, 5, 7]].dropna()
    dados.columns = ["status_curso", "status_discord", "retorno"]

    total = len(dados)
    cursando = (dados["status_curso"] == "Cursando").sum()
    nao_iniciado = (dados["status_curso"] == "Não iniciado").sum()
    no_discord = (dados["status_discord"] == "Entrou no discord").sum()
    com_retorno = (dados["retorno"] == "RETORNO").sum()

    categorias = ["Cursando\nno AVA", "Entrou\nno Discord", "Retorno\nà mentoria"]
    valores = [cursando, no_discord, com_retorno]
    cores = [COR_OK, COR_PRINCIPAL, COR_SECUNDARIA]

    fig, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(categorias, valores, color=cores, width=0.55)
    for barra, valor in zip(barras, valores):
        pct = 100 * valor / total
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.6,
            f"{int(valor)}\n({pct:.0f}%)",
            ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    ax.set_ylim(0, total + 6)
    ax.set_ylabel("Número de alunos")
    ax.set_title(f"Engajamento da turma TQ14 — acompanhamento automatizado ({total} alunos)", pad=14)
    ax.set_xticks(range(len(categorias)))
    ax.set_xticklabels(categorias)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(
        0, -0.22,
        f"Alunos não iniciados no AVA: {int(nao_iniciado)} | Fonte: relatório gerado por src/relatorio_turma.py",
        transform=ax.transAxes, fontsize=8, color="#666666",
    )
    salvar(fig, "engajamento_turma_tq14.png")


def grafico_presenca_encontros() -> None:
    datas = list(PARTICIPACAO_ENCONTROS.keys())
    participacoes = list(PARTICIPACAO_ENCONTROS.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(datas, participacoes, color=COR_PRINCIPAL, width=0.55)
    for barra, valor in zip(barras, participacoes):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.5,
            str(valor), ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    media = sum(participacoes) / len(participacoes)
    ax.axhline(
        media, color=COR_ALERTA, linestyle="--", linewidth=1.5,
        label=f"Média: {media:.0f} alunos/aula",
    )
    ax.legend(loc="upper right", framealpha=0.9, fontsize=10)

    ax.set_ylim(0, max(participacoes) + 6)
    ax.set_ylabel("Alunos presentes")
    ax.set_xlabel("Data da aula síncrona (2025)")
    ax.set_title("Presença nas aulas síncronas de recuperação — turma Ciência de Dados", pad=14)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(
        0, -0.2,
        "Fonte: CSVs de participação exportados do Google Meet, tratados por src/registrar_chamada.py",
        transform=ax.transAxes, fontsize=8, color="#666666",
    )
    salvar(fig, "presenca_aulas_sincronas.png")


def grafico_distribuicao_notas() -> None:
    df = pd.read_excel(DATA_DIR / "notas_alunos.xlsx")
    notas = pd.to_numeric(df["Nota Total"], errors="coerce").dropna()

    faixas = ["0–2", "2–4", "4–6", "6–8", "8–10"]
    contagens = [
        ((notas >= 0) & (notas < 2)).sum(),
        ((notas >= 2) & (notas < 4)).sum(),
        ((notas >= 4) & (notas < 6)).sum(),
        ((notas >= 6) & (notas < 8)).sum(),
        ((notas >= 8) & (notas <= 10)).sum(),
    ]
    cores = [COR_ALERTA, "#e8963c", COR_SECUNDARIA, "#7cb342", COR_OK]

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(faixas, contagens, color=cores, width=0.6)
    for barra, valor in zip(barras, contagens):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.4,
            str(valor), ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    media = notas.mean()
    aprovados = (notas >= 6).sum()

    ax.set_ylabel("Número de alunos")
    ax.set_xlabel("Faixa de nota total")
    ax.set_title(f"Distribuição de notas — {len(notas)} alunos avaliados no Moodle", pad=14)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(
        0, -0.2,
        f"Nota média: {media:.2f} | Alunos com nota ≥ 6: {int(aprovados)} ({100 * aprovados / len(notas):.0f}%) | "
        f"Fonte: notas extraídas por src/atualizar_notas.py",
        transform=ax.transAxes, fontsize=8, color="#666666",
    )
    salvar(fig, "distribuicao_notas.png")


def grafico_impacto() -> None:
    registros_forum = 0
    arquivo_forum = DATA_DIR / "respostas_forum.txt"
    if arquivo_forum.exists():
        with open(arquivo_forum, "r", encoding="utf-8", errors="replace") as f:
            registros_forum = len(re.findall(r"^Aluno:", f.read(), re.M))

    alunos_notas = len(pd.read_excel(DATA_DIR / "notas_alunos.xlsx"))
    encontros = len(PARTICIPACAO_ENCONTROS)
    total_participacoes = sum(PARTICIPACAO_ENCONTROS.values())

    min_por_feedback = 5
    min_chamada_manual = 15
    min_extracao_notas = 30
    horas_forum = registros_forum * min_por_feedback / 60
    horas_chamada = encontros * min_chamada_manual / 60
    horas_notas = min_extracao_notas / 60
    horas_total = horas_forum + horas_chamada + horas_notas

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.1, 1]})

    categorias = ["Feedbacks no\nfórum", "Chamada das\naulas síncronas", "Extração e\nconsolidação de notas"]
    horas = [horas_forum, horas_chamada, horas_notas]
    barras = ax1.barh(categorias, horas, color=[COR_PRINCIPAL, COR_SECUNDARIA, COR_OK], height=0.5)
    for barra, valor in zip(barras, horas):
        ax1.text(
            barra.get_width() + 0.3, barra.get_y() + barra.get_height() / 2,
            f"{valor:.1f} h", va="center", fontsize=11, fontweight="bold",
        )
    ax1.set_xlabel("Horas estimadas poupadas")
    ax1.set_title("Tempo economizado com automação", pad=14)
    ax1.set_xlim(0, horas_forum * 1.25)
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)

    kpis = [
        (f"{registros_forum}", "feedbacks automatizados\nno fórum do AVA"),
        (f"{alunos_notas}", "alunos com notas\nextraídas do Moodle"),
        (f"{encontros}", f"aulas síncronas\ncom chamada automática\n({total_participacoes} presenças registradas)"),
        (f"{horas_total:.0f} h", "de tarefas repetitivas\npoupadas no total*"),
    ]
    ax2.axis("off")
    for i, (valor, descricao) in enumerate(kpis):
        y = 0.82 - i * 0.24
        ax2.text(0.1, y, valor, fontsize=22, fontweight="bold", color=COR_PRINCIPAL, transform=ax2.transAxes)
        ax2.text(0.32, y - 0.01, descricao, fontsize=10, color="#333333", va="top", transform=ax2.transAxes)
    ax2.set_title("Resultados da experiência como mentor", pad=14)

    fig.suptitle("Impacto das ferramentas de automação — Capacita Brasil C-Jovem", fontsize=15, fontweight="bold", y=1.02)
    fig.text(
        0, -0.06,
        "*Estimativa conservadora: 5 min/feedback, 15 min/chamada manual e 30 min na consolidação manual de notas.",
        fontsize=8, color="#666666",
    )
    salvar(fig, "impacto_automacao.png")


def main() -> None:
    print("Gerando gráficos de resultados...")
    grafico_engajamento_turma()
    grafico_presenca_encontros()
    grafico_distribuicao_notas()
    grafico_impacto()
    print("Concluído!")


if __name__ == "__main__":
    main()
