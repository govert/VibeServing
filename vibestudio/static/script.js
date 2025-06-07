async function loadExamples() {
  const resp = await fetch('/api/examples');
  const examples = await resp.json();
  const container = document.getElementById('examples');
  const chooser = document.getElementById('prompt-chooser');
  container.innerHTML = '';
  chooser.innerHTML = '<option value="">Select example...</option>';
  examples.forEach((ex) => {
    const div = document.createElement('div');
    div.className = 'example';
    const title = document.createElement('h2');
    title.textContent = ex.name;
    div.appendChild(title);
    if (ex.prompt) {
      const btn = document.createElement('button');
      btn.textContent = 'Use Prompt';
      btn.addEventListener('click', () => {
        document.getElementById('prompt').value = ex.prompt;
      });
      div.appendChild(btn);

      const opt = document.createElement('option');
      opt.value = ex.prompt;
      opt.textContent = ex.name;
      chooser.appendChild(opt);
    }
    const runLabel = document.createElement('div');
    runLabel.textContent = 'Run the example:';
    div.appendChild(runLabel);
    const run = document.createElement('pre');
    run.textContent = ex.run;
    div.appendChild(run);
    if (ex.test) {
      const testLabel = document.createElement('div');
      testLabel.textContent = 'Run the tests:';
      div.appendChild(testLabel);
      const test = document.createElement('pre');
      test.textContent = ex.test;
      div.appendChild(test);
    }
    container.appendChild(div);
  });
}

async function loadPrompt() {
  const resp = await fetch('/api/prompt');
  const data = await resp.json();
  document.getElementById('prompt').value = data.prompt;
}

async function loadMetaPrompt() {
  const resp = await fetch('/api/meta_prompt');
  const data = await resp.json();
  document.getElementById('meta-prompt').value = data.meta_prompt;
}

async function savePrompt() {
  const prompt = document.getElementById('prompt').value;
  await fetch('/api/prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
}

async function saveMetaPrompt() {
  const meta_prompt = document.getElementById('meta-prompt').value;
  await fetch('/api/meta_prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meta_prompt }),
  });
}

async function restartServer() {
  const prompt = document.getElementById('prompt').value;
  const meta_prompt = document.getElementById('meta-prompt').value;
  await fetch('/api/restart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, meta_prompt }),
  });
  document.getElementById('traffic').textContent = '';
  const iframe = document.getElementById('browser');
  iframe.src = 'http://localhost:8000/';
  loadLogs();
}

async function loadLogs() {
  const resp = await fetch('/api/logs');
  const logs = await resp.json();
  const pre = document.getElementById('traffic');
  pre.textContent = logs.map(l => `${l.request} -> ${l.response}`).join('\n');
}

async function runTests() {
  document.getElementById('test-output').textContent = 'Running...';
  const resp = await fetch('/api/run_tests', { method: 'POST' });
  const data = await resp.json();
  document.getElementById('test-output').textContent = data.output;
}

window.addEventListener('load', () => {
  loadExamples();
  loadPrompt();
  loadMetaPrompt();
  loadLogs();
  document.getElementById('save-prompt').addEventListener('click', savePrompt);
  document.getElementById('save-meta').addEventListener('click', saveMetaPrompt);
  document.getElementById('restart-server').addEventListener('click', restartServer);
  document.getElementById('run-tests').addEventListener('click', runTests);
  document.getElementById('prompt-chooser').addEventListener('change', (e) => {
    if (e.target.value) {
      document.getElementById('prompt').value = e.target.value;
    }
  });
  setInterval(loadLogs, 2000);
});
