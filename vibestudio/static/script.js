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
  const url = 'http://localhost:8000/';
  iframe.src = url;
  document.getElementById('browser-url').value = url;
  browserHistory = [];
  loadLogs();
}

let logIndex = 0;
let browserHistory = [];

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

function navigateBrowser() {
  const input = document.getElementById('browser-url');
  const url = input.value.trim();
  if (!url) return;
  const iframe = document.getElementById('browser');
  if (iframe.src) {
    browserHistory.push(iframe.src);
  }
  iframe.src = url;
}

function backBrowser() {
  if (browserHistory.length === 0) return;
  const url = browserHistory.pop();
  const iframe = document.getElementById('browser');
  iframe.src = url;
  document.getElementById('browser-url').value = url;
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
  document.getElementById('browser-go').addEventListener('click', navigateBrowser);
  document.getElementById('browser-back').addEventListener('click', backBrowser);
  document.getElementById('browser-url').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      navigateBrowser();
    }
  });
  setInterval(loadLogs, 2000);
  setInterval(loadMetaChat, 2000);
});
