const cart = [];
const productList = document.getElementById('productList');
const cartItems = document.getElementById('cartItems');
const subtotalEl = document.getElementById('subtotal');
const deliveryEl = document.getElementById('delivery');
const totalEl = document.getElementById('total');
const cartCountEl = document.getElementById('cartCount');
const checkoutBtn = document.getElementById('checkoutBtn');
const pixContainer = document.getElementById('pixContainer');
const companyFilter = document.getElementById('companyFilter');
const companyProductSelect = document.getElementById('companyProductSelect');
const companyForm = document.getElementById('companyForm');
const clientForm = document.getElementById('clientForm');
const productForm = document.getElementById('productForm');

let allProducts = [];
let allCompanies = [];
let selectedCategory = 'all';

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

function getProductById(id) {
  return allProducts.find((product) => product.id === id);
}

async function loadCompanies() {
  try {
    const response = await fetch('/api/companies');
    const companies = await response.json();
    allCompanies = companies;

    companyFilter.innerHTML = `
      <option value="all">Todas as empresas</option>
      ${companies
        .map((company) => `<option value="${company.id}">${company.name}</option>`)
        .join('')}
    `;

    companyProductSelect.innerHTML = `
      <option value="">Selecione uma empresa</option>
      ${companies
        .map((company) => `<option value="${company.id}">${company.name}</option>`)
        .join('')}
    `;
  } catch (error) {
    console.error('Erro ao carregar empresas:', error);
  }
}

async function loadProducts() {
  const companyId = companyFilter.value;
  const url = companyId === 'all' ? '/api/products' : `/api/products?company_id=${companyId}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    allProducts = data;
    renderProducts();
  } catch (error) {
    console.error('Erro ao carregar produtos:', error);
  }
}

function renderProducts() {
  const filteredProducts = allProducts.filter((product) => {
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesCategory;
  });

  if (!filteredProducts.length) {
    productList.innerHTML = '<div class="empty-cart">Nenhum produto cadastrado para essa seleção.</div>';
    return;
  }

  productList.innerHTML = filteredProducts
    .map(
      (product) => `
        <article class="product-card">
          <div class="product-media">
            <span class="badge">${product.company_name || 'Empresa'}</span>
            <img src="${product.image}" alt="${product.name}" />
          </div>
          <div class="product-info">
            <div class="product-header">
              <h3>${product.name}</h3>
              <span class="product-price">${formatCurrency(product.price)}</span>
            </div>
            <p class="product-description">${product.description}</p>
            <div class="product-meta">
              <span class="stock">${product.stock} disponíveis</span>
              <button class="add-btn" type="button" data-id="${product.id}">Adicionar</button>
            </div>
          </div>
        </article>
      `
    )
    .join('');

  document.querySelectorAll('.add-btn').forEach((button) => {
    button.addEventListener('click', () => addToCart(Number(button.dataset.id)));
  });
}

function addToCart(productId) {
  const product = getProductById(productId);
  if (!product) return;

  const existingItem = cart.find((item) => item.id === productId);

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  renderCart();
}

function updateQuantity(productId, change) {
  const item = cart.find((entry) => entry.id === productId);

  if (!item) return;

  item.quantity += change;

  if (item.quantity <= 0) {
    const index = cart.findIndex((entry) => entry.id === productId);
    cart.splice(index, 1);
  }

  renderCart();
}

function renderCart() {
  if (cart.length === 0) {
    cartItems.innerHTML = '<li class="empty-cart">Seu carrinho está vazio.</li>';
  } else {
    cartItems.innerHTML = cart
      .map(
        (item) => `
          <li class="cart-item">
            <div>
              <h4>${item.name}</h4>
              <small>${formatCurrency(item.price)} cada</small>
              <div class="item-controls">
                <div class="qty-controls">
                  <button class="qty-btn" type="button" data-action="minus" data-id="${item.id}">−</button>
                  <span class="qty-value">${item.quantity}</span>
                  <button class="qty-btn" type="button" data-action="plus" data-id="${item.id}">+</button>
                </div>
              </div>
            </div>
            <div class="cart-price">${formatCurrency(item.price * item.quantity)}</div>
          </li>
        `
      )
      .join('');
  }

  document.querySelectorAll('.qty-btn').forEach((button) => {
    button.addEventListener('click', () => {
      const id = Number(button.dataset.id);
      const action = button.dataset.action;
      updateQuantity(id, action === 'plus' ? 1 : -1);
    });
  });

  const subtotal = cart.reduce((total, item) => total + item.price * item.quantity, 0);
  const delivery = cart.length > 0 ? 7.5 : 0;
  const total = subtotal + delivery;

  subtotalEl.textContent = formatCurrency(subtotal);
  deliveryEl.textContent = formatCurrency(delivery);
  totalEl.textContent = formatCurrency(total);
  cartCountEl.textContent = `${cart.reduce((sum, item) => sum + item.quantity, 0)} itens`;
}

async function handleCheckout() {
  if (cart.length === 0) {
    alert('Adicione pelo menos um item ao carrinho.');
    return;
  }

  const payload = {
    user_id: 1,
    user_email: 'cliente@email.com',
    items: cart.map(({ id, quantity }) => ({ id, quantity })),
  };

  checkoutBtn.disabled = true;
  checkoutBtn.textContent = 'Gerando QR Code...';

  try {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('Não foi possível gerar o pagamento PIX.');
    }

    const data = await response.json();

    pixContainer.hidden = false;
    pixContainer.innerHTML = `
      <p><strong>Pagamento via PIX</strong></p>
      <p>Escaneie o QR Code abaixo:</p>
      <img src="data:image/jpeg;base64,${data.pix_qr}" alt="QR Code do PIX" />
    `;
  } catch (error) {
    alert(error.message || 'Erro ao processar o pagamento.');
  } finally {
    checkoutBtn.disabled = false;
    checkoutBtn.textContent = 'Pagar com PIX';
  }
}

async function registerCompany(event) {
  event.preventDefault();

  const formData = new FormData(companyForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/company/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Erro ao cadastrar empresa');

    alert('Empresa cadastrada com sucesso!');
    companyForm.reset();
    await loadCompanies();
  } catch (error) {
    alert(error.message);
  }
}

async function registerClient(event) {
  event.preventDefault();

  const formData = new FormData(clientForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/client/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Erro ao cadastrar cliente');

    alert('Cliente cadastrado com sucesso!');
    clientForm.reset();
  } catch (error) {
    alert(error.message);
  }
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Não foi possível ler a imagem selecionada.'));
    reader.readAsDataURL(file);
  });
}

async function registerProduct(event) {
  event.preventDefault();

  const formData = new FormData(productForm);
  const payload = Object.fromEntries(formData.entries());
  const companyId = Number(payload.company_id);

  if (!companyId) {
    alert('Selecione uma empresa antes de cadastrar o produto.');
    return;
  }

  try {
    const imageFile = formData.get('image');
    const imageValue = imageFile && imageFile instanceof File && imageFile.size > 0
      ? await fileToDataUrl(imageFile)
      : 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80';

    const response = await fetch(`/api/company/${companyId}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId,
        name: payload.name,
        category: payload.category,
        price: Number(payload.price),
        stock: Number(payload.stock),
        description: payload.description || 'Produto da empresa',
        image: imageValue,
      }),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Erro ao cadastrar produto');

    alert('Produto cadastrado com sucesso!');
    productForm.reset();
    await loadProducts();
  } catch (error) {
    alert(error.message);
  }
}

document.getElementById('filters').addEventListener('click', (event) => {
  const button = event.target.closest('.filter-btn');
  if (!button) return;

  document.querySelectorAll('.filter-btn').forEach((btn) => btn.classList.remove('active'));
  button.classList.add('active');
  selectedCategory = button.dataset.category;
  renderProducts();
});

const tabButtons = document.querySelectorAll('.tab-button, .tab-trigger');
const tabPanels = document.querySelectorAll('.tab-panel');

function changeTab(target) {
  tabButtons.forEach((button) => {
    const isActive = button.dataset.target === target;
    button.classList.toggle('active', isActive);
  });

  tabPanels.forEach((panel) => {
    panel.classList.toggle('active', panel.dataset.panel === target);
  });
}

tabButtons.forEach((button) => {
  button.addEventListener('click', () => changeTab(button.dataset.target));
});

companyFilter.addEventListener('change', () => {
  loadProducts();
});

companyForm.addEventListener('submit', registerCompany);
clientForm.addEventListener('submit', registerClient);
productForm.addEventListener('submit', registerProduct);
checkoutBtn.addEventListener('click', handleCheckout);

loadCompanies();
loadProducts();
renderCart();
