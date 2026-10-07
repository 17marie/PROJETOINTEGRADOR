# main.py
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
import mercadopago # Biblioteca para Pix

app = FastAPI()

# Gerenciador de conexões WebSocket para o Painel Admin
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast_order(self, order_data: dict):
        for connection in self.active_connections:
            await connection.send_json(order_data)

manager = ConnectionManager()

# Rota para o Painel Admin escutar novos pedidos
@app.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.active_connections.remove(websocket)

# Rota de Checkout e Geração de PIX
@app.post("/api/checkout")
async def create_order(order_request: dict, db: Session = Depends(get_db)):
    # 1. Verifica estoque e deduz itens
    total = 0
    for item in order_request['items']:
        product = db.query(Product).filter(Product.id == item['id']).first()
        if product.stock < item['quantity']:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {product.name}")
        product.stock -= item['quantity']
        total += product.price * item['quantity']

    # 2. Gera a cobrança Pix no Mercado Pago
    sdk = mercadopago.SDK("SEU_ACCESS_TOKEN_AQUI")
    payment_data = {
        "transaction_amount": total,
        "description": "Pedido App",
        "payment_method_id": "pix",
        "payer": {"email": order_request['user_email']}
    }
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]

    # 3. Salva o pedido no banco
    new_order = Order(
        user_id=order_request['user_id'],
        total_price=total,
        pix_qr_code=payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
        pix_txid=payment["id"]
    )
    db.add(new_order)
    db.commit()

    # 4. Avisa o painel admin em TEMPO REAL
    await manager.broadcast_order({
        "order_id": new_order.id,
        "total": total,
        "status": "Aguardando Pagamento"
    })

    return {"pix_qr": new_order.pix_qr_code, "order_id": new_order.id}