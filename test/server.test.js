const test = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const app = require('../src/server');

test('health endpoint confirms the service is healthy', async () => {
  const response = await request(app).get('/health');
  assert.equal(response.status, 200);
  assert.equal(response.body.status, 'healthy');
});
test('readiness endpoint exposes a controlled failure for probe demonstrations', async () => {
  const response = await request(app).get('/ready?fail=true');
  assert.equal(response.status, 503);
});
