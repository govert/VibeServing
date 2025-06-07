async function loadPrompt() {
  const resp = await fetch('/api/prompt');
  const data = await resp.json();
  document.getElementById('prompt').value = data.prompt;
}

async function loadExamples() {
  const resp = await fetch('/api/examples');
  const examples = await resp.json();
  const chooser = document.getElementById('prompt-chooser');
  chooser.innerHTML = '<option value="">Select example...</option>';
  examples.forEach((ex) => {
    if (ex.prompt) {
      const opt = document.createElement('option');
      opt.value = ex.prompt;
      opt.textContent = ex.name;
      chooser.appendChild(opt);
    }
  });
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
  logIndex = 0;
  const iframe = document.getElementById('browser');
  iframe.src = 'http://localhost:8000/';
  loadLogs();
}

let logIndex = 0;

async function loadLogs() {
  const resp = await fetch('/api/logs');
  const logs = await resp.json();
  const pre = document.getElementById('traffic');
  for (let i = logIndex; i < logs.length; i++) {
    const l = logs[i];
    pre.textContent += `${l.status} ${l.request} -> ${l.response}\n`;
  }
  logIndex = logs.length;
}

async function loadMetaChat() {
  const resp = await fetch('/api/meta_logs');
  const logs = await resp.json();
  const pre = document.getElementById('meta-chat');
  pre.textContent = logs.map(l => (l.direction === 'out' ? '>> ' : '<< ') + l.text).join('\n');
}

async function sendMeta() {
  const input = document.getElementById('meta-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  await fetch('/api/meta_chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  loadMetaChat();
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
  loadMetaChat();
  document.getElementById('save-prompt').addEventListener('click', savePrompt);
  document.getElementById('save-meta').addEventListener('click', saveMetaPrompt);
  document.getElementById('restart-server').addEventListener('click', restartServer);
  document.getElementById('run-tests').addEventListener('click', runTests);
  document.getElementById('send-meta').addEventListener('click', sendMeta);
  document.getElementById('prompt-chooser').addEventListener('change', (e) => {
    if (e.target.value) {
      document.getElementById('prompt').value = e.target.value;
    }
  });
  setInterval(loadLogs, 2000);
  setInterval(loadMetaChat, 2000);
});
