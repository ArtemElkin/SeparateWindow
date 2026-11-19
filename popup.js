let selectShortcut;

function renderShortcut() {
  const keys = document.querySelector('#shortcut-keys');
  keys.replaceChildren();
  if (!selectShortcut) {
    keys.textContent = selectShortcut === '' ? SWI18n.t('shortcutUnassigned') : selectShortcut === null ? '—' : '…';
    return;
  }
  for (const key of selectShortcut.split('+')) {
    if (keys.children.length) keys.append('+');
    const cap = document.createElement('kbd');
    cap.textContent = key;
    keys.append(cap);
  }
}

function render() {
  document.documentElement.lang = SWI18n.language;
  for (const element of document.querySelectorAll('[data-i18n]')) element.textContent = SWI18n.t(element.dataset.i18n);
  for (const element of document.querySelectorAll('[data-i18n-label]')) element.setAttribute('aria-label', SWI18n.t(element.dataset.i18nLabel));
  for (const button of document.querySelectorAll('[data-language]')) button.setAttribute('aria-pressed', String(button.dataset.language === SWI18n.language));
  const version = chrome.runtime.getManifest().version;
  document.querySelector('#version').textContent = version;
  renderShortcut();
  for (const [id, title, body] of [['report-bug','bugTitle','bugBody'], ['suggest-feature','featureTitle','featureBody']]) {
    const url = new URL('https://github.com/MerlinRus/SeparateWindow/issues/new');
    url.searchParams.set('title', SWI18n.t(title));
    url.searchParams.set('body', SWI18n.t(body, version));
    document.getElementById(id).href = url.href;
  }
}
SWI18n.onChange(old => {
  render(); const status = document.querySelector('#status'); status.textContent = SWI18n.translate(status.textContent, old);
});
SWI18n.ready.then(render).catch(error => {document.querySelector('#status').textContent = error.message;});
chrome.commands.getAll().then(commands => {
  selectShortcut = commands.find(command => command.name === 'select')?.shortcut || '';
  renderShortcut();
}).catch(() => {selectShortcut = null; renderShortcut();});
for (const language of document.querySelectorAll('[data-language]')) language.addEventListener('click', async () => {
  const buttons = document.querySelectorAll('[data-language]');
  for (const button of buttons) button.disabled = true;
  try {await chrome.storage.local.set({language:language.dataset.language}); await SWI18n.reload(); render();}
  catch (error) {document.querySelector('#status').textContent = error.message;}
  finally {for (const button of buttons) button.disabled = false;}
});

for (const button of document.querySelectorAll('#select,#restore,#forget')) {
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      await SWI18n.ready;
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      if (!tab) throw new Error(SWI18n.t('noActiveTab'));
      const result = await chrome.runtime.sendMessage({type: button.id, tabId: tab.id});
      if (!result?.ok) throw new Error(result?.error || SWI18n.t('commandFailed'));
      window.close();
    } catch (error) {
      document.querySelector('#status').textContent = error.message;
      button.disabled = false;
    }
  });
}
