from __future__ import annotations

import base64
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DB_PATH = ROOT / "backend" / "database.db"

DEFAULT_COMPANIES = [
    {
        "id": 1,
        "name": "Buraco da Pizza",
        "email": "buraco@empresa.com",
        "phone": "(11) 98888-1111",
        "description": "Pizzaria artesanal com receitas caseiras.",
        "password": "123456",
    },
    {
        "id": 2,
        "name": "Burger House",
        "email": "burger@empresa.com",
        "phone": "(11) 97777-2222",
        "description": "Hambúrgueres gourmet e refeições rápidas.",
        "password": "123456",
    },
]

DEFAULT_PRODUCTS = [
    {
        "id": 1,
        "company_id": 1,
        "company_name": "Buraco da Pizza",
        "name": "Pizza Margherita",
        "category": "pizza",
        "price": 39.9,
        "description": "Molho de tomate, mussarela, manjericão e azeite.",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
        "stock": 12,
    },
    {
        "id": 2,
        "company_id": 1,
        "company_name": "Buraco da Pizza",
        "name": "Pizza Pepperoni",
        "category": "pizza",
        "price": 46.9,
        "description": "Pepperoni, queijo e molho artesanal com toque defumado.",
        "image": "https://images.unsplash.com/photo-1548365328-9f547fb9587c?auto=format&fit=crop&w=900&q=80",
        "stock": 8,
    },
    {
        "id": 3,
        "company_id": 2,
        "company_name": "Burger House",
        "name": "Burger Clássico",
        "category": "burger",
        "price": 34.9,
        "description": "Hambúrguer 180g, queijo, alface, tomate e molho especial.",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
        "stock": 15,
    },
    {
        "id": 4,
        "company_id": 2,
        "company_name": "Burger House",
        "name": "Burger Duplo",
        "category": "burger",
        "price": 44.9,
        "description": "Dois hambúrgueres, queijo cheddar e cebola caramelizada.",
        "image": "https://images.unsplash.com/photo-1550317138-10000687a72b?auto=format&fit=crop&w=900&q=80",
        "stock": 7,
    },
    {
        "id": 5,
        "company_id": 1,
        "company_name": "Buraco da Pizza",
        "name": "Refrigerante 600ml",
        "category": "drink",
        "price": 9.9,
        "description": "Escolha sua bebida favorita para acompanhar o pedido.",
        "image": "https://images.unsplash.com/photo-1622483767028-3f66f2b0d1d6?auto=format&fit=crop&w=900&q=80",
        "stock": 20,
    },
    {
        "id": 6,
        "company_id": 2,
        "company_name": "Burger House",
        "name": "Milkshake",
        "category": "drink",
        "price": 15.9,
        "description": "Milkshake cremoso de baunilha com cobertura crocante.",
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=900&q=80",
        "stock": 10,
    },
    {
        "id": 7,
        "company_id": 1,
        "company_name": "Buraco da Pizza",
        "name": "Brownie",
        "category": "dessert",
        "price": 12.9,
        "description": "Brownie de chocolate com nozes e sorvete de creme.",
        "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=80",
        "stock": 18,
    },
    {
        "id": 8,
        "company_id": 2,
        "company_name": "Burger House",
        "name": "Pudim",
        "category": "dessert",
        "price": 11.9,
        "description": "Pudim caseiro com calda de caramelo e canela.",
        "image": "https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=900&q=80",
        "stock": 14,
    },
]

DEFAULT_CLIENTS = [
    {
        "id": 1,
        "name": "Cliente Teste",
        "email": "cliente@email.com",
        "phone": "(11) 99999-9999",
        "password": "123456",
    }
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    try:
        with conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    description TEXT,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    company_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    image TEXT,
                    stock INTEGER NOT NULL,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                );
                """
            )

            if conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO companies (name, email, phone, description, password) VALUES (?, ?, ?, ?, ?)",
                    [(company["name"], company["email"], company["phone"], company["description"], company["password"]) for company in DEFAULT_COMPANIES],
                )

            if conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO clients (name, email, phone, password) VALUES (?, ?, ?, ?)",
                    [(client["name"], client["email"], client["phone"], client["password"]) for client in DEFAULT_CLIENTS],
                )

            if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
                company_map = {row["name"]: row["id"] for row in conn.execute("SELECT id, name FROM companies").fetchall()}
                products = []
                for product in DEFAULT_PRODUCTS:
                    company_id: Any | None = company_map.get(product["company_name"])
                    if company_id is None:
                        continue
                    products.append(
                        (
                            company_id,
                            product["company_name"],
                            product["name"],
                            product["category"],
                            product["price"],
                            product["description"],
                            product["image"],
                            product["stock"],
                        )
                    )
                conn.executemany(
                    "INSERT INTO products (company_id, company_name, name, category, price, description, image, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    products,
                )
    finally:
        conn.close()


def get_companies():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_products(company_id=None):
    conn = get_connection()
    try:
        if company_id is not None:
            rows = conn.execute(
                "SELECT * FROM products WHERE company_id = ? ORDER BY id",
                (company_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


class CardapioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/companies":
            self._send_json(get_companies())
            return

        if path == "/api/products":
            company_id = query.get("company_id", [None])[0]
            try:
                filtered_company_id = int(company_id) if company_id else None
            except ValueError:
                filtered_company_id = None
            self._send_json(get_products(filtered_company_id))
            return

        if path in ("/", "/index.html"):
            self._serve_file(FRONTEND / "index.html")
            return

        if path.startswith("/"):
            file_path = FRONTEND / path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                self._serve_file(file_path)
                return

        self._send_error(404, "Página não encontrada")

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_error(400, "JSON inválido")
            return

        if parsed.path == "/api/company/register":
            name = str(payload.get("name", "")).strip()
            email = str(payload.get("email", "")).strip()
            phone = str(payload.get("phone", "")).strip()
            password = str(payload.get("password", "")).strip()

            if not all([name, email, phone, password]):
                self._send_error(400, "Todos os campos da empresa são obrigatórios")
                return

            conn = get_connection()
            try:
                try:
                    cursor = conn.execute(
                        "INSERT INTO companies (name, email, phone, description, password) VALUES (?, ?, ?, ?, ?)",
                        (name, email, phone, str(payload.get("description", "")).strip(), password),
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    self._send_error(409, "Já existe uma empresa cadastrada com esse email")
                    return

                company = {
                    "id": cursor.lastrowid,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "description": str(payload.get("description", "")).strip(),
                    "password": password,
                }
                self._send_json({"message": "Empresa cadastrada com sucesso", "company": company})
            finally:
                conn.close()
            return

        if parsed.path == "/api/client/register":
            name = str(payload.get("name", "")).strip()
            email = str(payload.get("email", "")).strip()
            phone = str(payload.get("phone", "")).strip()
            password = str(payload.get("password", "")).strip()

            if not all([name, email, phone, password]):
                self._send_error(400, "Todos os campos do cliente são obrigatórios")
                return

            conn = get_connection()
            try:
                try:
                    cursor = conn.execute(
                        "INSERT INTO clients (name, email, phone, password) VALUES (?, ?, ?, ?)",
                        (name, email, phone, password),
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    self._send_error(409, "Já existe um cliente cadastrado com esse email")
                    return

                client = {
                    "id": cursor.lastrowid,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password,
                }
                self._send_json({"message": "Cliente cadastrado com sucesso", "client": client})
            finally:
                conn.close()
            return

        if parsed.path.startswith("/api/company/") and parsed.path.endswith("/products"):
            path_parts = parsed.path.strip("/").split("/")
            try:
                company_id = int(path_parts[2])
            except (IndexError, ValueError):
                self._send_error(400, "ID da empresa inválido")
                return

            conn = get_connection()
            try:
                company = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
                if company is None:
                    self._send_error(404, "Empresa não encontrada")
                    return

                try:
                    price = float(payload.get("price", 0))
                    stock = int(payload.get("stock", 0))
                except (TypeError, ValueError):
                    self._send_error(400, "Preço e estoque devem ser valores válidos")
                    return

                if stock < 0:
                    self._send_error(400, "Estoque não pode ser negativo")
                    return

                name = str(payload.get("name", "")).strip()
                if not name:
                    self._send_error(400, "Nome do produto é obrigatório")
                    return

                image = payload.get("image") or "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80"
                image_url = str(image).strip()
                if not image_url or image_url.lower() == "null":
                    image_url = "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80"

                cursor = conn.execute(
                    """
                    INSERT INTO products (company_id, company_name, name, category, price, description, image, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company_id,
                        company["name"],
                        name,
                        str(payload.get("category", "pizza")).strip() or "pizza",
                        price,
                        str(payload.get("description", "Produto da empresa")).strip() or "Produto da empresa",
                        image_url,
                        stock,
                    ),
                )
                conn.commit()

                new_product = {
                    "id": cursor.lastrowid,
                    "company_id": company_id,
                    "company_name": company["name"],
                    "name": name,
                    "category": str(payload.get("category", "pizza")).strip() or "pizza",
                    "price": price,
                    "description": str(payload.get("description", "Produto da empresa")).strip() or "Produto da empresa",
                    "image": image_url,
                    "stock": stock,
                }
                self._send_json({"message": "Produto cadastrado com sucesso", "product": new_product})
            finally:
                conn.close()
            return

        if parsed.path == "/api/checkout":
            items = payload.get("items", [])
            if not items:
                self._send_error(400, "Carrinho vazio")
                return

            ids = tuple(sorted({int(item.get("id")) for item in items if item.get("id") is not None}))
            if not ids:
                self._send_error(400, "Itens inválidos")
                return

            conn = get_connection()
            try:
                rows = conn.execute(
                    "SELECT * FROM products WHERE id IN ({})".format(", ".join("?" for _ in ids)),
                    ids,
                ).fetchall()
                product_map = {row["id"]: row for row in rows}

                total = 0.0
                for item in items:
                    product = product_map.get(item.get("id"))
                    if product is None:
                        self._send_error(400, f"Produto não encontrado: {item.get('id')}")
                        return
                    quantity = int(item.get("quantity", 0))
                    if quantity <= 0:
                        self._send_error(400, f"Quantidade inválida para {product['name']}")
                        return
                    if quantity > int(product["stock"]):
                        self._send_error(400, f"Estoque insuficiente para {product['name']}")
                        return
                    total += float(product["price"]) * quantity

                for item in items:
                    product = product_map.get(item.get("id"))
                    if product is not None:
                        new_stock = int(product["stock"]) - int(item.get("quantity", 0))
                        conn.execute(
                            "UPDATE products SET stock = ? WHERE id = ?",
                            (new_stock, product["id"]),
                        )
                conn.commit()
            finally:
                conn.close()

            qr_data = base64.b64encode(b"PIX-TEST-ORDER-123456789").decode("utf-8")
            response = {"pix_qr": qr_data, "total": round(total, 2)}
            self._send_json(response)
            return

        self._send_error(404, "Endpoint não encontrado")

    def _serve_file(self, file_path: Path):
        try:
            content = file_path.read_bytes()
        except FileNotFoundError:
            self._send_error(404, "Arquivo não encontrado")
            return

        mime_type = "text/html"
        if file_path.suffix == ".css":
            mime_type = "text/css"
        elif file_path.suffix == ".js":
            mime_type = "application/javascript"
        elif file_path.suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            mime_type = "image/" + file_path.suffix.lstrip(".")

        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status_code: int, message: str):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", 8000), CardapioHandler)
    print("Servidor rodando em http://localhost:8000")
    server.serve_forever()
