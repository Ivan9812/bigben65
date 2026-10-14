import 'dotenv/config';
import express from 'express';
import pg from 'pg';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { products } from '../src/data.js';
import { validateOrder } from '../shared/orders.js';

if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is missing. Run npm run db:up or configure .env.');
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 5, connectionTimeoutMillis: 5000 });
await pool.query(`CREATE TABLE IF NOT EXISTS demo_orders (
  id UUID PRIMARY KEY, request_id UUID UNIQUE NOT NULL, number BIGSERIAL UNIQUE,
  customer JSONB NOT NULL, items JSONB NOT NULL, delivery TEXT NOT NULL,
  address TEXT NOT NULL, total INTEGER NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS demo_requests (
  id UUID PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL,
  email TEXT NOT NULL, message TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW()
);`);
const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '32kb' }));
app.use('/api', (_req, res, next) => { res.set('Cache-Control', 'no-store'); next(); });
app.get('/api/health', async (_req, res, next) => {
  try { await pool.query('SELECT 1'); res.json({ status: 'ok', database: 'postgresql', mode: 'demo' }); } catch (error) { next(error); }
});
app.get('/api/products', (_req, res) => res.json(products));
app.post('/api/orders', async (req, res, next) => {
  let order;
  try { order = validateOrder(req.body); } catch (error) { return res.status(400).json({ error: error.message }); }
  try {
    const inserted = await pool.query(`INSERT INTO demo_orders (id,request_id,customer,items,delivery,address,total)
      VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT (request_id) DO NOTHING
      RETURNING id,number,items,total,delivery,created_at`,
    [randomUUID(), order.requestId, order.customer, JSON.stringify(order.items), order.delivery, order.address, order.total]);
    const row = inserted.rows[0] || (await pool.query('SELECT id,number,items,total,delivery,created_at FROM demo_orders WHERE request_id=$1', [order.requestId])).rows[0];
    res.status(inserted.rowCount ? 201 : 200).json({ ...row, number: `BB-${String(row.number).padStart(5, '0')}`, status: 'Демозаказ создан' });
  } catch (error) { next(error); }
});
app.post('/api/requests', async (req, res, next) => {
  const { kind, name, email, message, consent } = req.body || {};
  if (!['service', 'contact', 'appointment'].includes(kind) || typeof name !== 'string' || name.trim().length < 2 || name.length > 100 || typeof email !== 'string' || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || typeof message !== 'string' || message.trim().length < 10 || message.length > 2000 || consent !== true) return res.status(400).json({ error: 'Проверьте имя, email, сообщение и согласие.' });
  try {
    const id = randomUUID();
    await pool.query('INSERT INTO demo_requests(id,kind,name,email,message) VALUES ($1,$2,$3,$4,$5)', [id, kind, name.trim(), email, message.trim()]);
    res.status(201).json({ id, status: 'Демозаявка сохранена' });
  } catch (error) { next(error); }
});
app.use('/api', (_req, res) => res.status(404).json({ error: 'API route not found' }));
const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../dist');
app.use(express.static(dist));
app.get('/{*path}', (_req, res) => res.sendFile(path.join(dist, 'index.html')));
app.use((error, _req, res, _next) => {
  if (error.type === 'entity.parse.failed') return res.status(400).json({ error: 'Некорректный JSON.' });
  if (error.type === 'entity.too.large') return res.status(413).json({ error: 'Слишком большой запрос.' });
  console.error('Request failed:', error.code || error.name);
  res.status(503).json({ error: 'Не удалось сохранить данные. Попробуйте ещё раз.' });
});
const server = app.listen(Number(process.env.PORT || 3000), '0.0.0.0', () => console.log(`BIG BEN demo server listening on port ${process.env.PORT || 3000}; PostgreSQL connected.`));
async function stop() { server.close(async () => { await pool.end(); process.exit(0); }); }
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
