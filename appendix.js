(function () {
  'use strict';

  function copyText(value, button) {
    function done() {
      var oldText = button.textContent;
      var status = document.getElementById('copy-status');
      button.textContent = '已复制 ✓';
      button.classList.add('copied');
      if (status) status.textContent = '已复制：' + value;
      window.setTimeout(function () {
        button.textContent = oldText;
        button.classList.remove('copied');
      }, 1800);
    }

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(value).then(done, function () { fallbackCopy(value, done); });
    } else {
      fallbackCopy(value, done);
    }
  }

  function fallbackCopy(value, done) {
    var field = document.createElement('textarea');
    field.value = value;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    try { document.execCommand('copy'); done(); } catch (error) {
      var status = document.getElementById('copy-status');
      if (status) status.textContent = '复制失败，请手动复制：' + value;
    }
    field.remove();
  }

  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', function () { copyText(button.dataset.copy, button); });
  });

  var dialog = document.getElementById('image-dialog');
  if (!dialog) return;
  var dialogImage = dialog.querySelector('img');
  var dialogCaption = dialog.querySelector('figcaption');

  document.querySelectorAll('.gallery-open').forEach(function (button) {
    button.addEventListener('click', function () {
      dialogImage.src = button.dataset.image;
      dialogImage.alt = button.dataset.caption || '';
      dialogCaption.textContent = button.dataset.caption || '';
      dialog.showModal();
    });
  });

  dialog.querySelector('.dialog-close').addEventListener('click', function () { dialog.close(); });
  dialog.addEventListener('click', function (event) { if (event.target === dialog) dialog.close(); });
}());
