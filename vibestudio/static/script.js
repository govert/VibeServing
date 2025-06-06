async function loadExamples() {
  const resp = await fetch('/api/examples');
  const examples = await resp.json();
  const container = document.getElementById('examples');
  container.innerHTML = '';
  examples.forEach((ex) => {
    const div = document.createElement('div');
    div.className = 'example';
    const title = document.createElement('h2');
    title.textContent = ex.name;
    div.appendChild(title);
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

window.addEventListener('load', loadExamples);
