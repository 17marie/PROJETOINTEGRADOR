from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Base de dados em memória (custo zero, sem necessidade de banco configurado)
estoque = [
    {
        "id": 1,
        "nome": "Carne Bovina (KG)",
        "quantidade": 12.0,
        "minimo": 20.0,
        "maximo": 60.0,
        "custo_unitario": 38.00,
        "validade": "2026-10-15",
        "lote": "L-20261001",
    },
    {
        "id": 2,
        "nome": "Arroz Parboilizado (KG)",
        "quantidade": 45.0,
        "minimo": 15.0,
        "maximo": 80.0,
        "custo_unitario": 5.50,
        "validade": "2026-12-20",
        "lote": "L-20260915",
    },
    {
        "id": 3,
        "nome": "Azeite Extra Virgem (L)",
        "quantidade": 3.0,
        "minimo": 8.0,
        "maximo": 20.0,
        "custo_unitario": 45.00,
        "validade": "2027-01-10",
        "lote": "L-20260820",
    },
]

fichas_tecnicas = [
    {
        "prato": "Executivo Bife com Arroz",
        "preco_venda": 32.00,
        "ingredientes": [
            {"nome": "Carne Bovina (KG)", "qtd": 0.220, "custo_unit": 38.00},
            {"nome": "Arroz Parboilizado (KG)", "qtd": 0.150, "custo_unit": 5.50},
            {"nome": "Azeite Extra Virgem (L)", "qtd": 0.015, "custo_unit": 45.00},
        ],
    }
]

def processar_curva_abc(itens):
    """Calcula o valor acumulado e classifica os itens em A (80%), B (15%) e C (5%)."""
    itens_calculados = []
    total_geral = 0.0

    for item in itens:
        valor_total = item["quantidade"] * item["custo_unitario"]
        total_geral += valor_total
        itens_calculados.append({**item, "valor_total": valor_total})

    itens_ordenados = sorted(itens_calculados, key=lambda x: x["valor_total"], reverse=True)

    acumulado = 0.0
    for item in itens_ordenados:
        if total_geral > 0:
            acumulado += item["valor_total"]
            porcentagem = (acumulado / total_geral) * 100
        else:
            porcentagem = 0

        if porcentagem <= 80:
            item["categoria_abc"] = "A (Crítico)"
        elif porcentagem <= 95:
            item["categoria_abc"] = "B (Moderado)"
        else:
            item["categoria_abc"] = "C (Baixo)"

    return itens_ordenados, total_geral

@app.route("/")
def dashboard():
    itens_abc, total_estoque = processar_curva_abc(estoque)

    # Lógica de Gestão Visual Kanban (Ponto de Pedido)
    kanban = {
        "comprar": [item for item in estoque if item["quantidade"] <= item["minimo"]],
        "atencao": [
            item for item in estoque 
            if item["minimo"] < item["quantidade"] <= item["minimo"] * 1.25
        ],
        "normal": [item for item in estoque if item["quantidade"] > item["minimo"] * 1.25],
    }

    # Cálculo do CMV de cada preparação (Ficha Técnica)
    for ficha in fichas_tecnicas:
        custo_preparacao = sum(ing["qtd"] * ing["custo_unit"] for ing in ficha["ingredientes"])
        ficha["custo_total"] = custo_preparacao
        ficha["cmv_percentual"] = round((custo_preparacao / ficha["preco_venda"]) * 100, 2) if ficha["preco_venda"] > 0 else 0

    return render_template(
        "index.html",
        estoque=itens_abc,
        kanban=kanban,
        fichas=fichas_tecnicas,
        total_estoque=total_estoque,
    )

@app.route("/adicionar_item", methods=["POST"])
def adicionar_item():
    novo_id = len(estoque) + 1
    estoque.append({
        "id": novo_id,
        "nome": request.form["nome"],
        "quantidade": float(request.form["quantidade"]),
        "minimo": float(request.form["minimo"]),
        "maximo": float(request.form["maximo"]),
        "custo_unitario": float(request.form["custo_unitario"]),
        "validade": request.form["validade"],
        "lote": request.form["lote"],
    })
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)