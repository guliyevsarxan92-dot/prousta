(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Nav kölgə */
  var nav = document.querySelector('nav');
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle('is-scrolled', window.scrollY > 6);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* Mobil menyu */
  window.toggleMenu = function (el) {
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

  /* Alt nav aktiv */
  var path = window.location.pathname;
  document.querySelectorAll('.alt-nav-item').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href === path || (href === '/' && path === '/')) {
      link.classList.add('aktiv');
    }
  });

  /* Toast */
  document.querySelectorAll('.msg').forEach(function (msg, i) {
    setTimeout(function () {
      msg.classList.add('is-dismissing');
      setTimeout(function () { msg.remove(); }, 300);
    }, 4500 + i * 400);
  });

  /* Xidmət slayderi — avtomatik sürüşən bir sətir */
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
      track.style.transform = 'translateX(' + offset + 'px)';
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

  if (reduced) {
    document.querySelectorAll('[data-reveal], [data-stagger]').forEach(function (el) {
      el.classList.add('is-visible');
    });
    return;
  }

  /* Scroll reveal */
  var targets = document.querySelectorAll('[data-reveal], [data-stagger]');
  if (!targets.length || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }

  function revealEl(el) {
    if (el.classList.contains('is-visible')) return;
    if (el.hasAttribute('data-stagger') || el.querySelector('[data-stagger]')) {
      var staggers = el.hasAttribute('data-stagger') ? [el] : el.querySelectorAll('[data-stagger]');
      Array.prototype.forEach.call(staggers, function (stagger) {
        Array.prototype.forEach.call(stagger.children, function (child, i) {
          child.style.transitionDelay = (i * 0.06) + 's';
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
  }, { threshold: 0.08, rootMargin: '0px 0px 40px 0px' });

  targets.forEach(function (el) { io.observe(el); });

  /* Artıq görünən bölmələri dərhal aç (məs. qısa ekran, scrollsuz) */
  requestAnimationFrame(function () {
    targets.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) revealEl(el);
    });
  });

  /* Şəkil fade-in */
  document.querySelectorAll('.kart-img img').forEach(function (img) {
    if (img.complete) return;
    img.style.opacity = '0';
    img.style.transition = 'opacity 0.5s ease';
    img.addEventListener('load', function () { img.style.opacity = '1'; });
  });

  /* Sol və sağ yan reklamların üst menyunun altına düşməsinin qarşısını al */
  function updateSideBannersPosition() {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;
    var rect = nav.getBoundingClientRect();
    var targetTop = Math.max(Math.round(rect.bottom + 12), 84);
    document.documentElement.style.setProperty('--side-ad-top', targetTop + 'px');
  }
  window.addEventListener('scroll', updateSideBannersPosition, { passive: true });
  window.addEventListener('resize', updateSideBannersPosition);
  window.addEventListener('load', updateSideBannersPosition);
  updateSideBannersPosition();
})();