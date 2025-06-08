async function fetchJson(url, options) {
  try {
    const resp = await fetch(url, options);
    if (!resp.ok) {
      console.error('Request failed', url, resp.status);
      return null;
    }
    return await resp.json();
  } catch (err) {
    console.error('Request error', url, err);
    return null;
  }
}

async function loadPrompt() {
  const data = await fetchJson('/api/prompt');
  if (data) {
    document.getElementById('prompt').value = data.prompt;
  }
}

async function loadExamples() {
  const examples = await fetchJson('/api/examples');
  const chooser = document.getElementById('prompt-chooser');
  chooser.innerHTML = '<option value="">Select example...</option>';
  if (examples) {
    examples.forEach((ex) => {
      if (ex.prompt) {
        const opt = document.createElement('option');
        opt.value = ex.prompt;
        opt.textContent = ex.name;
        chooser.appendChild(opt);
      }
    });
  }
}

async function loadMetaPrompt() {
  const data = await fetchJson('/api/meta_prompt');
  if (data) {
    document.getElementById('meta-prompt').value = data.meta_prompt;
  }
}

async function loadSettings() {
  const data = await fetchJson('/api/settings');
  if (data) {
    document.getElementById('model').value = data.model || '';
    document.getElementById('temperature').value = data.temperature || '';
    document.getElementById('thinking-time').value = data.thinking_time || '';
  }
}

async function savePrompt() {
  const prompt = document.getElementById('prompt').value;
  await fetchJson('/api/prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
}

async function saveMetaPrompt() {
  const meta_prompt = document.getElementById('meta-prompt').value;
  await fetchJson('/api/meta_prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meta_prompt }),
  });
}

async function saveSettings() {
  const model = document.getElementById('model').value;
  const temperature = document.getElementById('temperature').value;
  const thinking_time = document.getElementById('thinking-time').value;
  await fetchJson('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, temperature, thinking_time }),
  });
}

async function restartServer() {
  const prompt = document.getElementById('prompt').value;
  const meta_prompt = document.getElementById('meta-prompt').value;
  await fetchJson('/api/restart', {
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
  const logs = await fetchJson('/api/logs');
  if (!logs) return;
  const pre = document.getElementById('traffic');
  for (let i = logIndex; i < logs.length; i++) {
    const l = logs[i];
    if (l.type === 'http') {
      pre.textContent += `${l.status} ${l.request} -> ${l.response}\n`;
    } else if (l.type === 'meta_out') {
      pre.textContent += `>> ${l.text}\n`;
    } else if (l.type === 'meta_in') {
      pre.textContent += `<< ${l.text}\n`;
    }
  }
  logIndex = logs.length;
}

async function loadMetaChat() {
  const logs = await fetchJson('/api/meta_logs');
  if (!logs) return;
  const pre = document.getElementById('meta-chat');
  pre.textContent = logs.map(l => (l.direction === 'out' ? '>> ' : '<< ') + l.text).join('\n');
}

async function sendMeta() {
  const input = document.getElementById('meta-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  await fetchJson('/api/meta_chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  loadMetaChat();
}

async function runTests() {
  document.getElementById('test-output').textContent = 'Running...';
  const data = await fetchJson('/api/run_tests', { method: 'POST' });
  if (data) {
    document.getElementById('test-output').textContent = data.output;
  }
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
  loadSettings();
  loadLogs();
  loadMetaChat();
  document.getElementById('save-prompt').addEventListener('click', savePrompt);
  document.getElementById('save-meta').addEventListener('click', saveMetaPrompt);
  document.getElementById('restart-server').addEventListener('click', restartServer);
  document.getElementById('run-tests').addEventListener('click', runTests);
  document.getElementById('send-meta').addEventListener('click', sendMeta);
  document.getElementById('save-settings').addEventListener('click', saveSettings);
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
