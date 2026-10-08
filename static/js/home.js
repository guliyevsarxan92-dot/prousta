(function () {
  'use strict';
  document.querySelectorAll('[data-demo-favorite]').forEach(function (button) {
    button.addEventListener('click', function () {
      var selected = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(selected));
      button.setAttribute('aria-label', selected ? 'Nümunə seçimini ləğv et' : 'Nümunə elanı seç');
    });
  });
  var dialog = document.getElementById('demoContact');
  if (dialog) {
    document.querySelectorAll('[data-demo-contact]').forEach(function (button) {
      button.addEventListener('click', function () { dialog.showModal(); });
    });
    dialog.querySelector('.dialog-close').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
      var bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  }
}());
