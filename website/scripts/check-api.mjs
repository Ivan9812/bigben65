import 'dotenv/config';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const base = 'http://127.0.0.1:3000';
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const requestId = randomUUID();
const payload = { requestId, items: [{ id: 'tissot-prx', quantity: 2, price: 1 }], customer: { name: 'API test', email: 'api-test@example.com', phone: '+79990000000', consent: true }, delivery: 'pickup' };
const post = body => fetch(`${base}/api/orders`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
try {
  const health = await (await fetch(`${base}/api/health`)).json();
  assert.equal(health.database, 'postgresql');
  const catalog = await (await fetch(`${base}/api/products`)).json();
  assert.equal(catalog.length, 8);
  for (const body of [{ ...payload, items: [] }, { ...payload, items: [{ id: 'bad', quantity: 1 }] }, { ...payload, customer: { ...payload.customer, consent: false } }]) assert.equal((await post(body)).status, 400);
  const responses = await Promise.all([post(payload), post(payload)]);
  assert.deepEqual(responses.map(r => r.status).sort(), [200, 201]);
  const orders = await Promise.all(responses.map(r => r.json()));
  assert.equal(orders[0].id, orders[1].id);
  assert.equal(orders[0].total, 159800);
  assert.equal(orders[0].customer, undefined);
  const result = await pool.query('SELECT total,items FROM demo_orders WHERE request_id=$1', [requestId]);
  assert.equal(result.rowCount, 1);
  assert.equal(result.rows[0].total, 159800);
  assert.equal(result.rows[0].items[0].quantity, 2);
  console.log('PASS: real PostgreSQL persistence, server-side pricing, validation and concurrent retry deduplication.');
} finally {
  await pool.query('DELETE FROM demo_orders WHERE request_id=$1', [requestId]);
  await pool.end();
}
