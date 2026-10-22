(() => {
  const search = document.querySelector('#research-search');
  if (!search) return;
  const cards = [...document.querySelectorAll('.research-card')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-results');
  let domain = 'all';
  const update = () => {
    const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const match = (domain === 'all' || card.dataset.domain === domain) && terms.every(term => card.dataset.search.includes(term));
      card.hidden = !match;
      if (match) visible++;
    }
    count.textContent = `${visible} ${visible === 1 ? 'article' : 'articles'}`;
    empty.hidden = visible > 0;
  };
  search.addEventListener('input', update);
  for (const button of buttons) button.addEventListener('click', () => {
    domain = button.dataset.filter;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    update();
  });
})();
