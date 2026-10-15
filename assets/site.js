// All content is available without JavaScript. Refresh stale pages when online.
(() => {
  const currentVersion = document.querySelector('meta[name="site-version"]')?.content;
  const parameter = '_site';
  const retryParameter = '_refresh';
  const interval = 60_000;
  const pageUrl = new URL(location.href);
  if (currentVersion && pageUrl.searchParams.get(parameter) === currentVersion) {
    pageUrl.searchParams.delete(parameter);
    pageUrl.searchParams.delete(retryParameter);
    history.replaceState(history.state, '', pageUrl);
  }

  let checking = false;
  let lastCheck = -Infinity;
  async function checkVersion() {
    const now = Date.now();
    if (document.visibilityState === 'hidden' || checking || now - lastCheck < interval) return;
    checking = true;
    lastCheck = now;
    try {
      // Both browser and shared caches must be bypassed for this small manifest.
      const manifest = new URL('version.json', location.href);
      manifest.searchParams.set('_check', String(now));
      const response = await fetch(manifest, { cache: 'no-store' });
      if (!response.ok) return;
      const { version } = await response.json();
      if (typeof version !== 'string' || !/^[a-f0-9]{16}$/.test(version) || version === currentVersion) return;

      const freshUrl = new URL(location.href);
      // If an edge server briefly returns an older page, retry at most once a minute.
      const previousAttempt = Number(freshUrl.searchParams.get(retryParameter));
      if (freshUrl.searchParams.get(parameter) === version && now - previousAttempt < interval) return;
      freshUrl.searchParams.set(parameter, version);
      freshUrl.searchParams.set(retryParameter, String(now));
      location.replace(freshUrl);
    } catch {
      // Offline visitors can continue reading; the next visible check will retry.
    } finally {
      checking = false;
    }
  }

  checkVersion();
  window.addEventListener('pageshow', checkVersion);
  document.addEventListener('visibilitychange', checkVersion);
  window.setInterval(checkVersion, interval);
})();

// Publication filtering is an optional aid.
const filterBar = document.querySelector('[data-filters]');
if (filterBar) {
  filterBar.hidden = false;
  const papers = [...document.querySelectorAll('[data-topics]')];
  const groups = [...document.querySelectorAll('[data-paper-group]')];
  const status = document.querySelector('[data-results]');
  const params = new URLSearchParams(location.search);
  const buttons = [...filterBar.querySelectorAll('button')];
  function filter(topic) {
    let count = 0;
    papers.forEach(paper => {
      const show = topic === 'all' || paper.dataset.topics.split(' ').includes(topic);
      paper.hidden = !show;
      if (show) count++;
    });
    groups.forEach(group => { group.hidden = ![...group.querySelectorAll('[data-topics]')].some(p => !p.hidden); });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === topic)));
    status.textContent = `${count} papers`;
    const url = new URL(location.href);
    if (topic === 'all') url.searchParams.delete('topic');
    else url.searchParams.set('topic', topic);
    history.replaceState(null, '', url);
  }
  buttons.forEach(button => button.addEventListener('click', () => filter(button.dataset.filter)));
  const initial = params.get('topic');
  filter(buttons.some(b => b.dataset.filter === initial) ? initial : 'all');
}
