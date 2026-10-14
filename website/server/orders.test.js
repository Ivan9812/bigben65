import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { validateOrder } from '../shared/orders.js';

const order = () => ({ requestId: randomUUID(), items: [{ id: 'tissot-prx', quantity: 2, price: 1 }], customer: { name: 'Тестовый покупатель', email: 'test@example.com', phone: '+79990000000', consent: true }, delivery: 'pickup' });
test('uses catalog price, never the client price', () => { const result = validateOrder(order()); assert.equal(result.total, 159800); assert.equal(result.items[0].price, 79900); });
test('rejects missing, unknown, duplicate and excessive items', () => {
  for (const items of [[], [{ id: 'unknown', quantity: 1 }], [{ id: 'tissot-prx', quantity: 0 }], [{ id: 'tissot-prx', quantity: 11 }], [{ id: 'tissot-prx', quantity: 1.5 }], [{ id: 'tissot-prx', quantity: 1 }, { id: 'tissot-prx', quantity: 1 }]]) assert.throws(() => validateOrder({ ...order(), items }));
});
test('requires contact data and explicit consent', () => {
  for (const change of [{ consent: false }, { email: 'bad' }, { name: 'x' }, { phone: '123' }]) { const o = order(); assert.throws(() => validateOrder({ ...o, customer: { ...o.customer, ...change } })); }
});
test('requires a valid delivery address and retry identifier', () => {
  assert.throws(() => validateOrder({ ...order(), delivery: 'delivery', address: '' }));
  assert.throws(() => validateOrder({ ...order(), requestId: 'bad' }));
  assert.equal(validateOrder({ ...order(), delivery: 'delivery', address: 'Тестовый город, улица 1' }).delivery, 'delivery');
});
