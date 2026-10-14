import { products } from '../src/data.js';

export function validateOrder(body) {
  if (!body || typeof body !== 'object' || !Array.isArray(body.items) || body.items.length < 1 || body.items.length > 8) throw new Error('Выберите товары для заказа.');
  const seen = new Set();
  const items = body.items.map(({ id, quantity } = {}) => {
    const product = products.find(p => p.id === id);
    if (!product || seen.has(id) || !Number.isInteger(quantity) || quantity < 1 || quantity > 10) throw new Error('Проверьте состав заказа и количество (от 1 до 10).');
    seen.add(id);
    return { id, name: `${product.brand} ${product.name}`, price: product.price, quantity };
  });
  const customer = body.customer;
  if (!customer || typeof customer.name !== 'string' || customer.name.trim().length < 2 || customer.name.length > 100 || typeof customer.email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customer.email) || customer.email.length > 254 || typeof customer.phone !== 'string' || !/^[+\d\s()-]{10,25}$/.test(customer.phone) || customer.phone.replace(/\D/g, '').length < 10 || customer.consent !== true) throw new Error('Заполните имя, телефон, email и подтвердите согласие.');
  if (!['pickup', 'delivery'].includes(body.delivery)) throw new Error('Выберите способ получения.');
  if (body.delivery === 'delivery' && (typeof body.address !== 'string' || body.address.trim().length < 8 || body.address.length > 400)) throw new Error('Укажите полный адрес доставки.');
  if (typeof body.requestId !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(body.requestId)) throw new Error('Некорректный идентификатор запроса.');
  return { items, customer: { name: customer.name.trim(), email: customer.email.trim(), phone: customer.phone, consent: true }, delivery: body.delivery, address: body.delivery === 'delivery' ? body.address.trim() : '', total: items.reduce((sum, item) => sum + item.price * item.quantity, 0), requestId: body.requestId };
}
