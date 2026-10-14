import { existsSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'));
if (!existsSync('.env')) {
  const password = randomBytes(24).toString('hex');
  writeFileSync('.env', `POSTGRES_PASSWORD=${password}\nDATABASE_URL=postgresql://bigben:${password}@127.0.0.1:5433/bigben\nPORT=3000\n`, { mode: 0o600, flag: 'wx' });
  console.log('Created local database configuration in ignored .env (values hidden).');
}
const result = spawnSync('docker', ['compose', 'up', '-d', '--wait'], { stdio: 'inherit' });
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
