import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../assets/site.js', import.meta.url), 'utf8');
const oldVersion = '1111111111111111';
const newVersion = '2222222222222222';
const settle = () => new Promise(resolve => setImmediate(resolve));

async function browser({ current = oldVersion, latest = current,
  url = 'https://example.org/research.html?topic=ai#paper-test',
  hidden = false, fail = false, ok = true } = {}) {
  let now = 1_000_000;
  const requests = [], redirects = [], events = {}, timers = [];
  const location = { href: url, replace(value) { redirects.push(new URL(value)); this.href = String(value); } };
  const document = {
    visibilityState: hidden ? 'hidden' : 'visible',
    querySelector(selector) { return selector === 'meta[name="site-version"]' && current ? { content: current } : null; },
    addEventListener(name, callback) { events[name] = callback; },
  };
  const history = { state: { retained: true }, replaceState(state, _, value) { this.state = state; location.href = String(value); } };
  vm.runInNewContext(source, { URL, document, location, history,
    Date: { now: () => now },
    fetch: async (url, options) => {
      requests.push({ url: new URL(url), options });
      if (fail) throw new Error('Offline');
      return { ok, json: async () => ({ version: latest }) };
    },
    window: {
      addEventListener(name, callback) { events[name] = callback; },
      setInterval(callback, delay) { timers.push({ callback, delay }); },
    },
  });
  await settle();
  return { requests, redirects, events, timers, document, location, history,
    advance(ms) { now += ms; }, setLatest(version) { latest = version; },
  };
}

test('current pages stay on the clean URL and check an uncached manifest', async () => {
  const b = await browser();
  assert.equal(b.redirects.length, 0);
  assert.equal(b.requests[0].url.pathname, '/version.json');
  assert.ok(b.requests[0].url.searchParams.has('_check'));
  assert.equal(b.requests[0].options.cache, 'no-store');
  assert.equal(b.timers[0].delay, 60_000);
});

test('a stale page refreshes while preserving its filters and anchor', async () => {
  const b = await browser({ latest: newVersion });
  assert.equal(b.redirects.length, 1);
  const [url] = b.redirects;
  assert.equal(url.pathname, '/research.html');
  assert.equal(url.searchParams.get('topic'), 'ai');
  assert.equal(url.hash, '#paper-test');
  assert.equal(url.searchParams.get('_site'), newVersion);
  assert.ok(url.searchParams.has('_refresh'));
});

test('a successful refresh removes only the temporary update parameters', async () => {
  const b = await browser({ current: newVersion,
    url: `https://example.org/research.html?topic=ai&_site=${newVersion}&_refresh=999999#paper-test` });
  assert.equal(b.location.href, 'https://example.org/research.html?topic=ai#paper-test');
  assert.equal(b.history.state.retained, true);
  assert.equal(b.redirects.length, 0);
});

test('deployment propagation cannot cause an immediate reload loop, but is retried later', async () => {
  const b = await browser({ latest: newVersion,
    url: `https://example.org/?_site=${newVersion}&_refresh=999999` });
  assert.equal(b.redirects.length, 0);
  b.advance(60_000);
  b.timers[0].callback();
  await settle();
  assert.equal(b.redirects.length, 1);
  assert.equal(b.redirects[0].searchParams.get('_refresh'), '1060000');
});

test('offline, unavailable and malformed manifests leave the page usable', async () => {
  for (const options of [{ fail: true }, { ok: false }, { latest: 'not-a-release' }, { latest: null }]) {
    const b = await browser(options);
    assert.equal(b.redirects.length, 0);
  }
});

test('returning to a tab checks again, with duplicate events throttled', async () => {
  const b = await browser();
  b.events.pageshow();
  b.events.visibilitychange();
  await settle();
  assert.equal(b.requests.length, 1);
  b.advance(60_000);
  b.setLatest(newVersion);
  b.events.pageshow();
  await settle();
  assert.equal(b.requests.length, 2);
  assert.equal(b.redirects.length, 1);
});

test('hidden tabs make no requests and check when made visible', async () => {
  const b = await browser({ hidden: true, latest: newVersion });
  assert.equal(b.requests.length, 0);
  b.document.visibilityState = 'visible';
  b.events.visibilitychange();
  await settle();
  assert.equal(b.redirects.length, 1);
});

test('legacy pages without version metadata can upgrade when they load the new script', async () => {
  const b = await browser({ current: null, latest: newVersion });
  assert.equal(b.redirects.length, 1);
});
