/* Progressive enhancement only; all 57 records and sources are in the HTML. */
(() => {
  const $ = selector => document.querySelector(selector);
  const entries = [...document.querySelectorAll('.entry')];
  const groups = [...document.querySelectorAll('.reference-group')];
  const indexItems = [...document.querySelectorAll('[data-for]')];
  const search = $('#reader-search');
  const filter = $('#group-filter');
  const toggle = $('#toggle-entries');
  const directory = $('.directory');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const corpus = new Map(entries.map(entry => [entry, normalize(entry.textContent)]));
  let searching = false;
  let beforeSearch = new Map();
  let printing = false;
  let printState = [];
  let visible = entries;

  $('.reader-tools').hidden = false;
  $('[data-print]').hidden = false;
  const narrow = window.matchMedia('(max-width: 900px)');
  directory.open = !narrow.matches;
  narrow.addEventListener('change', event => { directory.open = !event.matches; });

  function updateToggle() {
    if (printing) return;
    const allOpen = visible.length > 0 && visible.every(entry => entry.open);
    toggle.textContent = allOpen ? '收起全部' : '展开全部';
    toggle.setAttribute('aria-expanded', String(allOpen));
    toggle.disabled = visible.length === 0;
  }

  function applyFilters() {
    const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    if (words.length && !searching) beforeSearch = new Map(entries.map(entry => [entry, entry.open]));
    if (!words.length && searching) beforeSearch.forEach((open, entry) => { entry.open = open; });
    searching = words.length > 0;
    visible = [];
    for (const entry of entries) {
      entry.hidden = !(words.every(word => corpus.get(entry).includes(word)) && (filter.value === 'all' || entry.dataset.group === filter.value));
      if (!entry.hidden) {
        visible.push(entry);
        if (searching) entry.open = true;
      }
    }
    for (const group of groups) group.hidden = !visible.some(entry => entry.dataset.group === group.dataset.group);
    for (const item of indexItems) item.hidden = document.getElementById(item.dataset.for).hidden;
    for (const group of document.querySelectorAll('.index-group')) group.hidden = !group.querySelector('li:not([hidden])');
    $('#result-count').textContent = visible.length === 57 ? '显示全部 57 条' : `显示 ${visible.length} / 57 条`;
    $('#empty-state').hidden = visible.length > 0;
    $('#clear-search').hidden = !search.value;
    updateToggle();
  }

  function revealHash() {
    const id = location.hash.slice(1);
    const entry = entries.find(item => item.id === id);
    if (!entry) return;
    if (entry.hidden) {
      search.value = '';
      filter.value = 'all';
      applyFilters();
    }
    entry.open = true;
    for (const item of indexItems) {
      const selected = item.dataset.for === id;
      const anchor = item.querySelector('a');
      if (selected) {
        anchor.setAttribute('aria-current', 'location');
        item.closest('.index-group').open = true;
      } else anchor.removeAttribute('aria-current');
    }
    if (narrow.matches) directory.open = false;
    requestAnimationFrame(() => {
      entry.querySelector('summary').focus({preventScroll:true});
      entry.scrollIntoView({block:'start', behavior:'instant'});
    });
  }

  search.addEventListener('input', applyFilters);
  filter.addEventListener('change', applyFilters);
  $('#clear-search').addEventListener('click', () => {search.value = ''; applyFilters(); search.focus();});
  $('#reset-filters').addEventListener('click', () => {search.value = ''; filter.value = 'all'; applyFilters(); search.focus();});
  toggle.addEventListener('click', () => {const open = !visible.every(entry => entry.open); visible.forEach(entry => {entry.open = open;}); updateToggle();});
  entries.forEach(entry => entry.addEventListener('toggle', updateToggle));
  window.addEventListener('hashchange', revealHash);
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#ref-"]');
    if (anchor && anchor.hash === location.hash) revealHash();
  });
  $('[data-print]').addEventListener('click', () => window.print());
  window.addEventListener('beforeprint', () => {
    if (printing) return;
    printing = true;
    printState = [...groups, ...entries].map(el => [el, el.hidden, el.open]);
    for (const el of [...groups, ...entries]) {el.hidden = false; if (el.matches('details')) el.open = true;}
  });
  window.addEventListener('afterprint', () => {
    for (const [el, hidden, open] of printState) {el.hidden = hidden; if (el.matches('details')) el.open = open;}
    printing = false;
    updateToggle();
  });
  applyFilters();
  revealHash();
})();
