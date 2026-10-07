import json
import sqlite3
import uuid
import urllib.request

BASE_URL = 'http://localhost:8000'


def request(path, method='GET', payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        response_body = response.read().decode('utf-8')
        return response.status, json.loads(response_body) if response_body else None


company_email = f'empresa-{uuid.uuid4().hex[:8]}@teste.com'
status, company = request('/api/company/register', 'POST', {
    'name': 'Empresa Teste',
    'email': company_email,
    'phone': '(11) 90000-0000',
    'password': '123456',
    'description': 'Empresa de teste'
})
print('COMPANY', status, company)

client_email = f'cliente-{uuid.uuid4().hex[:8]}@teste.com'
status, client = request('/api/client/register', 'POST', {
    'name': 'Cliente Teste',
    'email': client_email,
    'phone': '(11) 91111-1111',
    'password': '123456'
})
print('CLIENT', status, client)

status, product = request(f"/api/company/{company['company']['id']}/products", 'POST', {
    'company_id': company['company']['id'],
    'name': 'Produto Teste',
    'category': 'pizza',
    'price': 29.9,
    'stock': 10,
    'description': 'Produto de teste',
    'image': 'https://example.com/image.jpg',
})
print('PRODUCT', status, product)

conn = sqlite3.connect('backend/database.db')
print('COUNTS', conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0], conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0], conn.execute('SELECT COUNT(*) FROM products').fetchone()[0])
conn.close()
