const express = require('express');
const client = require('prom-client');

const app = express();
const port = Number(process.env.PORT || 3000);
const register = new client.Registry();
client.collectDefaultMetrics({ register, prefix: 'releasepilot_' });
const requests = new client.Counter({ name: 'releasepilot_http_requests_total', help: 'Total HTTP requests handled by ReleasePilot', labelNames: ['method', 'route', 'status'], registers: [register] });
const duration = new client.Histogram({ name: 'releasepilot_http_request_duration_seconds', help: 'HTTP request duration in seconds', labelNames: ['method', 'route', 'status'], registers: [register] });

app.use(express.json());
app.use((req, res, next) => {
  const end = duration.startTimer({ method: req.method, route: req.path });
  res.on('finish', () => { requests.inc({ method: req.method, route: req.path, status: res.statusCode }); end({ status: res.statusCode }); });
  next();
});
app.get('/', (_req, res) => res.json({ service: 'releasepilot', status: 'running', version: process.env.APP_VERSION || 'local' }));
app.get('/health', (_req, res) => res.status(200).json({ status: 'healthy' }));
app.get('/ready', (req, res) => req.query.fail === 'true' ? res.status(503).json({ status: 'not ready', reason: 'demo failure' }) : res.status(200).json({ status: 'ready' }));
app.get('/api/v1/status', (_req, res) => res.json({ environment: process.env.NODE_ENV || 'development', timestamp: new Date().toISOString() }));
app.get('/metrics', async (_req, res) => { res.set('Content-Type', register.contentType); res.end(await register.metrics()); });

if (require.main === module) app.listen(port, () => console.log(`ReleasePilot listening on ${port}`));
module.exports = app;
