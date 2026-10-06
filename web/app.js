const form = document.querySelector('#research-form');
const question = document.querySelector('#question');
const mode = document.querySelector('#mode');
const results = document.querySelector('#results');
const submit = document.querySelector('#submit');
const note = document.querySelector('#mode-note');
let configured = false;
fetch('/api/config').then(r => r.json()).then(config => { configured = config.exaConfigured; }).catch(() => {});
mode.addEventListener('change', () => {
  note.textContent = mode.value === 'exa'
    ? (configured ? 'Exa searches your published corpus and synthesizes cited findings. Requests use API credits.' : 'Live mode needs EXA_API_KEY and a published, Exa-indexed CORPUS_BASE_URL. See README for setup.')
    : 'Local preview uses keyword matching and verbatim excerpts. Switch to Exa for AI retrieval and synthesis.';
});
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  submit.disabled = true;
  results.setAttribute('aria-busy', 'true');
  results.replaceChildren(element('p', mode.value === 'exa' ? 'Searching the Exa index and gathering cited evidence…' : 'Searching the local corpus…', 'notice'));
  try {
    const response = await fetch('/api/research', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: question.value, mode: mode.value}) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Research request failed.');
    const heading = element('div', '', 'result-heading');
    heading.append(element('h2', data.mode === 'exa' ? 'Research findings' : 'Evidence preview'), element('span', `${data.sources.length} sources · ${(data.elapsedMs / 1000).toFixed(1)}s`));
    results.replaceChildren(heading, element('p', data.notice, 'notice'));
    if (!data.findings.length) results.append(element('p', data.emptyMessage, 'notice'));
    const sources = new Map(data.sources.map(source => [source.id, source]));
    for (const finding of data.findings) {
      const source = sources.get(finding.sourceId);
      const row = element('article', '', 'finding');
      const citation = element('a', `${source.kind} · ${source.title} ↗`, 'citation');
      citation.href = `/sources/${source.id}`;
      citation.target = '_blank';
      citation.rel = 'noopener';
      const evidence = element('details');
      evidence.append(element('summary', `View evidence · ${source.location} · ${source.updated}`), element('blockquote', finding.quote));
      row.append(element('p', finding.text), citation, evidence);
      results.append(row);
    }
    if (data.requestId) results.append(element('p', `Exa request: ${data.requestId}`, 'notice'));
  } catch (error) {
    results.replaceChildren(element('p', error.message, 'error'));
  } finally {
    submit.disabled = false;
    results.setAttribute('aria-busy', 'false');
  }
});
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => {
  question.value = button.dataset.question;
  form.requestSubmit();
}));
