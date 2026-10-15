// All content is available without JavaScript. Filtering is an optional aid.
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
