(function () {
  'use strict';

  var statusBox = document.getElementById('infiniteScrollStatus');
  var grid = document.getElementById('elanlar-grid');
  var loadMoreBtn = document.getElementById('loadMoreBtn');
  var spinner = document.getElementById('scrollSpinner');
  var pager = document.getElementById('elanlar-pager');

  if (statusBox && grid) {
    var rawNext = statusBox.getAttribute('data-next-page');
    var nextPage = rawNext ? parseInt(rawNext, 10) : null;
    var totalPages = parseInt(statusBox.getAttribute('data-total-pages'), 10) || 1;
    var ajaxUrl = statusBox.getAttribute('data-ajax-url') || window.location.pathname;
    var isLoading = false;

    function loadNext() {
      if (isLoading || !nextPage || nextPage > totalPages) return;
      isLoading = true;
      if (loadMoreBtn) loadMoreBtn.style.display = 'none';
      if (spinner) spinner.style.display = 'inline-flex';

      var sep = ajaxUrl.indexOf('?') === -1 ? '?' : '&';
      var url = ajaxUrl + sep + 'page=' + nextPage + '&ajax=1';

      fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data && data.html) {
            var temp = document.createElement('div');
            temp.innerHTML = data.html;
            while (temp.firstChild) {
              grid.appendChild(temp.firstChild);
            }
          }
          if (data && data.has_next && data.next_page) {
            nextPage = data.next_page;
            statusBox.setAttribute('data-next-page', String(nextPage));
            if (loadMoreBtn) loadMoreBtn.style.display = 'inline-flex';
            if (spinner) spinner.style.display = 'none';
          } else {
            nextPage = null;
            statusBox.innerHTML = '<span class="all-loaded-note">Bütün elanlar göstərildi</span>';
            if (pager) pager.style.display = 'none';
          }
          isLoading = false;
        })
        .catch(function () {
          isLoading = false;
          if (loadMoreBtn) loadMoreBtn.style.display = 'inline-flex';
          if (spinner) spinner.style.display = 'none';
        });
    }

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', loadNext);
    }

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting && nextPage && !isLoading) {
          loadNext();
        }
      }, { rootMargin: '300px' });
      observer.observe(statusBox);
    } else {
      window.addEventListener('scroll', function () {
        if (!nextPage || isLoading) return;
        var rect = statusBox.getBoundingClientRect();
        if (rect.top <= window.innerHeight + 300) {
          loadNext();
        }
      }, { passive: true });
    }
  }

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
    var closeBtn = dialog.querySelector('.dialog-close');
    if (closeBtn) closeBtn.addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
      var bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  }
}());
