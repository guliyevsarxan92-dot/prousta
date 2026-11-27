(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. Nav kölgə və Sol/Sağ yan vitrinlərin rAF ilə axıcı mövqelənməsi */
  var nav = document.querySelector('.site-nav') || document.querySelector('nav');
  var footer = document.querySelector('.site-footer') || document.querySelector('footer');
  var scrollTicking = false;

  function updateScrollLayout() {
    scrollTicking = false;
    var scrollY = window.scrollY || window.pageYOffset || 0;
    if (nav) {
      nav.classList.toggle('is-scrolled', scrollY > 6);
    }

    var topVal = 84;
    if (nav) {
      var navBottom = nav.getBoundingClientRect().bottom;
      topVal = Math.max(Math.round(navBottom + 12), 84);
    }
    var docStyle = document.documentElement.style;
    docStyle.setProperty('--side-ad-top', topVal + 'px');

    var winH = window.innerHeight || document.documentElement.clientHeight || 800;
    var maxAvail = winH - topVal - 24;
    var targetH = Math.min(Math.max(maxAvail, 280), 760);

    if (footer) {
      var ft = footer.getBoundingClientRect().top;
      var availH = ft - topVal - 20;
      if (availH < 180) {
        docStyle.setProperty('--side-ad-opacity', '0');
        docStyle.setProperty('--side-ad-pointer', 'none');
      } else {
        docStyle.setProperty('--side-ad-opacity', '1');
        docStyle.setProperty('--side-ad-pointer', 'auto');
        docStyle.setProperty('--side-ad-max-h', Math.min(availH, targetH) + 'px');
      }
    } else {
      docStyle.setProperty('--side-ad-opacity', '1');
      docStyle.setProperty('--side-ad-pointer', 'auto');
      docStyle.setProperty('--side-ad-max-h', targetH + 'px');
    }
  }

  function requestScrollLayout() {
    if (!scrollTicking) {
      scrollTicking = true;
      requestAnimationFrame(updateScrollLayout);
    }
  }

  updateScrollLayout();
  window.addEventListener('scroll', requestScrollLayout, { passive: true });
  window.addEventListener('resize', requestScrollLayout, { passive: true });
  window.addEventListener('load', requestScrollLayout);

  /* 2. Video bannerlərin səssiz avtomatik oxunmasını təmin et */
  document.querySelectorAll('.pu-top-video, .pu-wing-video, .pu-mid-video, .top-ad-video, .side-ad-custom-video, .in-grid-ad-video').forEach(function (vid) {
    vid.muted = true;
    vid.playsInline = true;
    var playPromise = vid.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(function () { /* Brauzer enerjiyə qənaət rejimindədirsə səssiz keç */ });
    }
  });

  /* 3. Mobil menyu */
  window.toggleMenu = function (el) {
    if (!el) return;
    el.classList.toggle('aktiv');
    var menu = document.getElementById('mobilMenu');
    var overlay = document.getElementById('mobilMenuOverlay');
    var open = menu && menu.classList.toggle('aktiv');
    if (overlay) overlay.classList.toggle('aktiv', open);
    document.body.style.overflow = open ? 'hidden' : '';
    el.setAttribute('aria-expanded', String(Boolean(open)));
    el.setAttribute('aria-label', open ? 'Menyunu bağla' : 'Menyunu aç');
  };

  document.addEventListener('click', function (e) {
    var menu = document.getElementById('mobilMenu');
    var hamburger = document.getElementById('hamburger');
    var overlay = document.getElementById('mobilMenuOverlay');
    if (!menu || !menu.classList.contains('aktiv')) return;
    if (menu.contains(e.target) || (hamburger && hamburger.contains(e.target))) return;
    menu.classList.remove('aktiv');
    if (hamburger) { hamburger.classList.remove('aktiv'); hamburger.setAttribute('aria-expanded', 'false'); }
    if (overlay) overlay.classList.remove('aktiv');
    document.body.style.overflow = '';
  });

  document.addEventListener('keydown', function (event) {
    var button = document.getElementById('hamburger');
    if (event.key === 'Escape' && button && button.classList.contains('aktiv')) {
      window.toggleMenu(button);
      button.focus();
    }
  });

  /* 4. Alt nav aktiv */
  var path = window.location.pathname;
  document.querySelectorAll('.alt-nav-item').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href === path || (href === '/' && path === '/')) {
      link.classList.add('aktiv');
    }
  });

  /* 5. Toast */
  document.querySelectorAll('.msg').forEach(function (msg, i) {
    setTimeout(function () {
      msg.classList.add('is-dismissing');
      setTimeout(function () { msg.remove(); }, 300);
    }, 4500 + i * 400);
  });

  /* 6. Naviqasiya açılan menyuların (details.nav-dropdown) kənara kliklədikdə bağlanması */
  document.addEventListener('click', function (e) {
    document.querySelectorAll('details.nav-dropdown[open]').forEach(function (dropdown) {
      if (!dropdown.contains(e.target)) {
        dropdown.removeAttribute('open');
      }
    });
  });

  /* 7. Xidmət slayderi — avtomatik sürüşən bir sətir */
  var slider = document.getElementById('xidmetSlider');
  if (slider) {
    var viewport = slider.querySelector('.xidmet-viewport');
    var track = slider.querySelector('.xidmet-track');
    var prevBtn = slider.querySelector('.xidmet-arrow-prev');
    var nextBtn = slider.querySelector('.xidmet-arrow-next');
    var offset = 0;
    var loopWidth = 0;
    var dragging = false;
    var autoPaused = false;
    var hoverPaused = false;
    var dragStartX = 0;
    var dragStartOffset = 0;
    var dragMoved = false;
    var resumeTimer = null;
    var lastFrame = 0;
    var autoSpeed = 38;

    function cloneTrack() {
      var chips = track.querySelectorAll('.xidmet-chip:not([data-clone])');
      chips.forEach(function (chip) {
        var clone = chip.cloneNode(true);
        clone.setAttribute('data-clone', '1');
        clone.setAttribute('aria-hidden', 'true');
        clone.setAttribute('tabindex', '-1');
        track.appendChild(clone);
      });
    }

    function measure() {
      if (!track) return;
      loopWidth = track.scrollWidth / 2;
    }

    function wrapOffset(px) {
      if (!loopWidth) return px;
      while (px <= -loopWidth) px += loopWidth;
      while (px > 0) px -= loopWidth;
      return px;
    }

    function applyOffset(px, animate) {
      offset = wrapOffset(px);
      if (animate === false || reduced) {
        viewport.classList.add('is-snapping');
      } else {
        viewport.classList.remove('is-snapping');
      }
      track.style.transform = 'translate3d(' + offset + 'px, 0, 0)';
    }

    function scrollBy(dx, animate) {
      applyOffset(offset + dx, animate !== false);
    }

    function pauseAuto(reason) {
      if (reason === 'hover') hoverPaused = true;
      else autoPaused = true;
      viewport.classList.add('is-paused');
    }

    function scheduleResume(delay) {
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(function () {
        if (!hoverPaused && !dragging) {
          autoPaused = false;
          viewport.classList.remove('is-paused');
        }
      }, delay || 1800);
    }

    function onPointerDown(e) {
      if (e.button !== undefined && e.button !== 0) return;
      dragging = true;
      dragMoved = false;
      dragStartX = e.clientX;
      dragStartOffset = offset;
      pauseAuto('drag');
      viewport.classList.add('is-dragging');
      viewport.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
      if (!dragging) return;
      var delta = e.clientX - dragStartX;
      if (Math.abs(delta) > 4) dragMoved = true;
      applyOffset(dragStartOffset + delta, false);
    }

    function onPointerUp(e) {
      if (!dragging) return;
      dragging = false;
      viewport.classList.remove('is-dragging');
      viewport.classList.remove('is-snapping');
      try { viewport.releasePointerCapture(e.pointerId); } catch (err) { /* noop */ }
      scheduleResume(1200);
    }

    function tick(now) {
      if (!lastFrame) lastFrame = now;
      var elapsed = now - lastFrame;
      lastFrame = now;

      if (!reduced && !autoPaused && !hoverPaused && !dragging && !document.hidden && loopWidth) {
        applyOffset(offset - (autoSpeed * elapsed) / 1000, false);
      }

      requestAnimationFrame(tick);
    }

    if (viewport && track) {
      cloneTrack();
      measure();
      applyOffset(0, false);

      if (prevBtn) prevBtn.disabled = false;
      if (nextBtn) nextBtn.disabled = false;

      viewport.addEventListener('pointerdown', onPointerDown);
      viewport.addEventListener('pointermove', onPointerMove);
      viewport.addEventListener('pointerup', onPointerUp);
      viewport.addEventListener('pointercancel', onPointerUp);

      slider.addEventListener('mouseenter', function () {
        pauseAuto('hover');
      });

      slider.addEventListener('mouseleave', function () {
        hoverPaused = false;
        if (!dragging) scheduleResume(400);
      });

      slider.addEventListener('focusin', function () { pauseAuto('hover'); });
      slider.addEventListener('focusout', function () {
        hoverPaused = false;
        if (!dragging) scheduleResume(600);
      });

      document.addEventListener('visibilitychange', function () {
        if (document.hidden) pauseAuto('drag');
        else scheduleResume(300);
      });

      track.addEventListener('click', function (e) {
        if (dragMoved) {
          e.preventDefault();
          e.stopPropagation();
          dragMoved = false;
        }
      }, true);

      viewport.addEventListener('keydown', function (e) {
        pauseAuto('drag');
        var step = viewport.clientWidth * 0.7;
        if (e.key === 'ArrowLeft') { e.preventDefault(); scrollBy(step); }
        if (e.key === 'ArrowRight') { e.preventDefault(); scrollBy(-step); }
        scheduleResume(2000);
      });

      if (prevBtn) prevBtn.addEventListener('click', function () {
        pauseAuto('drag');
        scrollBy(viewport.clientWidth * 0.75);
        scheduleResume(2000);
      });
      if (nextBtn) nextBtn.addEventListener('click', function () {
        pauseAuto('drag');
        scrollBy(-viewport.clientWidth * 0.75);
        scheduleResume(2000);
      });

      var resizeTimer;
      window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          measure();
          applyOffset(offset, false);
        }, 120);
      });

      if ('ResizeObserver' in window) {
        var ro = new ResizeObserver(function () {
          measure();
          applyOffset(offset, false);
        });
        ro.observe(viewport);
        ro.observe(track);
      }

      if (!reduced) requestAnimationFrame(tick);
    }
  }

  /* 8. Apple-style Scroll Reveal & Staggered Section Entrances */
  if (!reduced) {
    // Avtomatik olaraq əsas bölmələrə zərif scroll-reveal əlavə et (ilk ekranda olmayanlara)
    var autoSections = document.querySelectorAll(
      '.home-section, .pg-section, .join-banner, .home-stats, .panel'
    );
    var winHeight = window.innerHeight || 800;
    autoSections.forEach(function (sec) {
      if (sec.hasAttribute('data-reveal') || sec.closest('[data-reveal]')) return;
      var rect = sec.getBoundingClientRect();
      // İlk ekranda dərhal görünən elementləri gizlətmə (LCP və CLS qorunur)
      if (rect.top > winHeight * 0.92) {
        sec.setAttribute('data-reveal', '');
      }
    });

    var autoGrids = document.querySelectorAll(
      '.category-grid, .professional-grid, .steps-grid, .review-grid, .cat-grid'
    );
    autoGrids.forEach(function (grid) {
      if (grid.hasAttribute('data-stagger')) return;
      var rect = grid.getBoundingClientRect();
      if (rect.top > winHeight * 0.88) {
        grid.setAttribute('data-stagger', '');
      }
    });
  }

  var targets = document.querySelectorAll('[data-reveal], [data-stagger]');
  if (reduced || !targets.length || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    function revealEl(el) {
      if (el.classList.contains('is-visible')) return;
      if (el.hasAttribute('data-stagger') || el.querySelector('[data-stagger]')) {
        var staggers = el.hasAttribute('data-stagger') ? [el] : el.querySelectorAll('[data-stagger]');
        Array.prototype.forEach.call(staggers, function (stagger) {
          Array.prototype.forEach.call(stagger.children, function (child, i) {
            child.style.transitionDelay = Math.min(i * 0.045, 0.36) + 's';
          });
          stagger.classList.add('is-visible');
        });
      }
      el.classList.add('is-visible');
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        revealEl(entry.target);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.06, rootMargin: '0px 0px 48px 0px' });

    targets.forEach(function (el) { io.observe(el); });

    requestAnimationFrame(function () {
      targets.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) revealEl(el);
      });
    });
  }

  /* 9. Şəkil zərif fade-in */
  function attachSmoothImageLoad(root) {
    (root || document).querySelectorAll('.kart-img img, .service-photo img').forEach(function (img) {
      if (img.complete || img.dataset.puImgReady) return;
      img.dataset.puImgReady = '1';
      if (!reduced) {
        img.style.opacity = '0';
        img.addEventListener('load', function () {
          img.style.opacity = '1';
        }, { once: true });
        img.addEventListener('error', function () {
          img.style.opacity = '1';
        }, { once: true });
      }
    });
  }
  attachSmoothImageLoad(document);
  window.__puAttachSmoothImages = attachSmoothImageLoad;
})();

// Keyboard access for the site's custom payment dialogs.
(function () {
  'use strict';
  document.querySelectorAll('[role="dialog"][aria-modal="true"]').forEach(function (dialog) {
    var opener = null;
    var wasOpen = false;
    function isOpen() { return dialog.getClientRects().length > 0; }
    new MutationObserver(function () {
      var open = isOpen();
      if (open && !wasOpen) {
        opener = document.activeElement;
        dialog.focus();
      } else if (!open && wasOpen && opener && opener.isConnected) {
        opener.focus();
      }
      wasOpen = open;
    }).observe(dialog, {attributes: true, attributeFilter: ['style', 'class', 'hidden']});
    dialog.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        var close = dialog.querySelector('button[onclick*="close"]');
        if (close) close.click();
        event.stopPropagation();
      }
      if (event.key !== 'Tab') return;
      var items = Array.from(dialog.querySelectorAll('button:not([disabled]),a[href],input,select,textarea,[tabindex="0"]'))
        .filter(function (item) { return item.getClientRects().length > 0; });
      if (!items.length) { event.preventDefault(); dialog.focus(); return; }
      var first = items[0], last = items[items.length - 1];
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog)) {
        event.preventDefault(); first.focus();
      }
    });
  });
}());
