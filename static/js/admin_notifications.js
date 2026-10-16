/**
 * Prousta.az Admin Panel — Canlı Səsli Bildiriş Sistemi
 * - Yeni Elan gəldikdə: Zərif ikiqat zəng/ding-dong səsi (Web Audio API)
 * - Yeni Ödəniş gəldikdə: Kassa/qəpik cingiltisi "Ka-Ching" səsi (Web Audio API)
 * - Parametrlərdə yerləşdirilmiş səs tənzimləmələri və masaüstü bildirişləri
 */
(function () {
  'use strict';

  // Yalnız admin səhifələrində icra edilsin
  if (!window.location.pathname.startsWith('/admin/')) return;

  var POLL_INTERVAL = 12000; // 12 saniyədən bir yoxlama
  var API_URL = '/admin/api/pending-notifications/';

  // Audio Context (Web Audio API)
  var audioCtx = null;
  var isAudioUnlocked = false;

  function getAudioContext() {
    if (!audioCtx) {
      var AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) {
        audioCtx = new AudioCtxClass();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  // İlk klikdə brauzerin audio kilidini aç
  function unlockAudio() {
    if (isAudioUnlocked) return;
    try {
      var ctx = getAudioContext();
      if (ctx && ctx.state === 'suspended') {
        ctx.resume().then(function () {
          isAudioUnlocked = true;
          updateSoundStatusUI();
        });
      } else if (ctx) {
        isAudioUnlocked = true;
        updateSoundStatusUI();
      }
    } catch (e) {
      console.warn('Audio unlock xətası:', e);
    }
  }

  document.addEventListener('click', unlockAudio, { once: true });
  document.addEventListener('keydown', unlockAudio, { once: true });

  // Səs Statusu (localStorage)
  function isSoundMuted() {
    return localStorage.getItem('prousta_admin_sound_muted') === 'true';
  }

  function setSoundMuted(muted) {
    localStorage.setItem('prousta_admin_sound_muted', muted ? 'true' : 'false');
    updateSoundStatusUI();
  }

  function toggleSound() {
    unlockAudio();
    var nowMuted = !isSoundMuted();
    setSoundMuted(nowMuted);
    if (!nowMuted) {
      // Səs açıldıqda xəfif təsdiq səsi çal
      playSoftConfirmSound();
    }
  }

  // =========================================================================
  // SƏSLƏR (Web Audio API)
  // =========================================================================
  function playSoftConfirmSound() {
    try {
      var ctx = getAudioContext();
      if (!ctx) return;
      var now = ctx.currentTime;
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.2, now + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.25);
    } catch (e) {}
  }

  // SƏS 1: YENİ ELAN SƏSİ (Zərif Kristal İkiqat Ding-Dong Zəngi)
  function playElanSound() {
    if (isSoundMuted()) return;
    try {
      var ctx = getAudioContext();
      if (!ctx) return;
      var now = ctx.currentTime;

      // 1-ci ton: E5 (659.25 Hz)
      var osc1 = ctx.createOscillator();
      var gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(659.25, now);
      gain1.gain.setValueAtTime(0, now);
      gain1.gain.linearRampToValueAtTime(0.35, now + 0.02);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.55);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.55);

      // 2-ci ton: A5 (880.00 Hz) - 130ms sonra
      var osc2 = ctx.createOscillator();
      var gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(880.0, now + 0.13);
      gain2.gain.setValueAtTime(0, now + 0.13);
      gain2.gain.linearRampToValueAtTime(0.4, now + 0.15);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.13);
      osc2.stop(now + 0.9);
    } catch (err) {
      console.warn('Elan səsi ifa xətası:', err);
    }
  }

  // SƏS 2: YENİ ÖDƏNİŞ SƏSİ (Kassa Cingiltisi "Ka-Ching" / Qəpik səsi)
  function playOdenisSound() {
    if (isSoundMuted()) return;
    try {
      var ctx = getAudioContext();
      if (!ctx) return;
      var now = ctx.currentTime;

      // 1. Qəpik toqquşması (Metalik klik - 1600 Hz)
      var oscClick = ctx.createOscillator();
      var gainClick = ctx.createGain();
      oscClick.type = 'triangle';
      oscClick.frequency.setValueAtTime(1600, now);
      gainClick.gain.setValueAtTime(0.35, now);
      gainClick.gain.exponentialRampToValueAtTime(0.001, now + 0.07);
      oscClick.connect(gainClick);
      gainClick.connect(ctx.destination);
      oscClick.start(now);
      oscClick.stop(now + 0.07);

      // 2. Kassa parlaq qəpik akkordu (C6 - 1046.5 Hz)
      var osc1 = ctx.createOscillator();
      var gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(1046.5, now + 0.05);
      gain1.gain.setValueAtTime(0, now + 0.05);
      gain1.gain.linearRampToValueAtTime(0.38, now + 0.07);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now + 0.05);
      osc1.stop(now + 0.7);

      // 3. Kassa yüksək cingiltisi (C7 - 2093 Hz & G6 - 1568 Hz)
      var osc2 = ctx.createOscillator();
      var gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(2093, now + 0.11);
      gain2.gain.setValueAtTime(0, now + 0.11);
      gain2.gain.linearRampToValueAtTime(0.42, now + 0.13);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 1.15);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.11);
      osc2.stop(now + 1.15);

      // 4. Parıltı harmonikası (E6 - 1318.5 Hz)
      var osc3 = ctx.createOscillator();
      var gain3 = ctx.createGain();
      osc3.type = 'sine';
      osc3.frequency.setValueAtTime(1318.5, now + 0.09);
      gain3.gain.setValueAtTime(0, now + 0.09);
      gain3.gain.linearRampToValueAtTime(0.25, now + 0.11);
      gain3.gain.exponentialRampToValueAtTime(0.001, now + 0.85);
      osc3.connect(gain3);
      gain3.connect(ctx.destination);
      osc3.start(now + 0.09);
      osc3.stop(now + 0.85);
    } catch (err) {
      console.warn('Ödəniş səsi ifa xətası:', err);
    }
  }

  // =========================================================================
  // TOAST BİLDİRİŞ SİSTEMİ (Ekranın yuxarı sağ küncü)
  // =========================================================================
  var toastContainer = null;
  function getToastContainer() {
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'adminNotificationToasts';
      toastContainer.style.cssText =
        'position:fixed;top:20px;right:20px;z-index:999999;display:flex;flex-direction:column;gap:12px;pointer-events:none;max-width:380px;width:calc(100% - 40px);';
      document.body.appendChild(toastContainer);
    }
    return toastContainer;
  }

  function showToast(opt) {
    var container = getToastContainer();
    var toast = document.createElement('div');
    toast.style.cssText =
      'pointer-events:auto;border-radius:14px;padding:14px 16px;background:#ffffff;box-shadow:0 12px 35px rgba(0,0,0,0.18),0 3px 8px rgba(0,0,0,0.06);border:1px solid ' +
      opt.borderColor +
      ';display:flex;align-items:flex-start;gap:12px;transform:translateX(110%);transition:all .35s cubic-bezier(0.16, 1, 0.3, 1);font-family:inherit;';

    toast.innerHTML =
      '<div style="width:38px;height:38px;border-radius:10px;background:' +
      opt.iconBg +
      ';color:' +
      opt.iconColor +
      ';display:flex;align-items:center;justify-content:center;flex-shrink:0;">' +
      '<span class="material-symbols-outlined" style="font-size:20px;">' +
      opt.icon +
      '</span>' +
      '</div>' +
      '<div style="flex:1;min-width:0;">' +
      '<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:2px;">' +
      '<strong style="font-size:12px;color:#0f172a;letter-spacing:-0.2px;">' +
      opt.title +
      '</strong>' +
      '<button type="button" class="toast-close" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:16px;line-height:1;padding:0;margin-left:auto;display:flex;align-items:center;"><span class="material-symbols-outlined" style="font-size:16px;">close</span></button>' +
      '</div>' +
      '<div style="font-size:12px;font-weight:700;color:' +
      opt.textColor +
      ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' +
      opt.body +
      '</div>' +
      '<div style="font-size:11px;color:#64748b;margin-top:2px;">' +
      opt.sub +
      '</div>' +
      '<div style="margin-top:8px;">' +
      '<a href="' +
      opt.url +
      '" style="display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;color:#ffffff;background:' +
      opt.btnBg +
      ';padding:5px 12px;border-radius:7px;text-decoration:none;transition:background .2s;">' +
      opt.btnText +
      ' <span class="material-symbols-outlined" style="font-size:13px;">open_in_new</span></a>' +
      '</div>' +
      '</div>';

    container.appendChild(toast);

    setTimeout(function () {
      toast.style.transform = 'translateX(0)';
    }, 10);

    function removeToast() {
      toast.style.transform = 'translateX(115%)';
      toast.style.opacity = '0';
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 350);
    }

    var closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', removeToast);
    }

    setTimeout(removeToast, 12000);
  }

  // HTML5 Desktop Bildirişi
  function showDesktopNotification(title, body, url) {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'granted') {
      try {
        var n = new Notification(title, {
          body: body,
          icon: '/static/brand-logo.svg',
          badge: '/static/favicon.svg',
        });
        n.onclick = function () {
          window.focus();
          if (url) window.location.href = url;
          n.close();
        };
      } catch (e) {
        console.warn('Desktop bildirişi xətası:', e);
      }
    }
  }

  // =========================================================================
  // PARAMETRLƏR & İNTERFEYS İDARƏETMƏSİ (User Menu & Header)
  // =========================================================================
  function initSoundControls() {
    // 1. Header Səs Düyməsi
    var headerBtn = document.getElementById('adminHeaderSoundBtn');
    if (headerBtn && !headerBtn.dataset.bound) {
      headerBtn.dataset.bound = 'true';
      headerBtn.addEventListener('click', function (e) {
        e.preventDefault();
        toggleSound();
      });
    }

    // 2. Parametrlər Menyusu (Sidebar User Links) Səs Düyməsi
    var toggleBtn = document.getElementById('toggleSoundBtn');
    if (toggleBtn && !toggleBtn.dataset.bound) {
      toggleBtn.dataset.bound = 'true';
      toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        toggleSound();
      });
    }

    // 3. Test Elan Səsi Düyməsi
    var testElanBtn = document.getElementById('testElanSoundQuickBtn');
    if (testElanBtn && !testElanBtn.dataset.bound) {
      testElanBtn.dataset.bound = 'true';
      testElanBtn.addEventListener('click', function (e) {
        e.preventDefault();
        unlockAudio();
        playElanSound();
        showToast({
          title: 'Test: Yeni Elan',
          body: 'Kondisioner təmiri və quraşdırılması',
          sub: 'Usta: Əli Məmmədov · 050 123 45 67',
          url: '/admin/core/elan/?status__exact=gozlemede',
          icon: 'campaign',
          iconBg: '#ecfdf5',
          iconColor: '#059669',
          borderColor: '#a7f3d0',
          textColor: '#047857',
          btnBg: '#059669',
          btnText: 'Elanlara Bax',
        });
      });
    }

    // 4. Test Ödəniş Səsi Düyməsi
    var testOdenisBtn = document.getElementById('testOdenisSoundQuickBtn');
    if (testOdenisBtn && !testOdenisBtn.dataset.bound) {
      testOdenisBtn.dataset.bound = 'true';
      testOdenisBtn.addEventListener('click', function (e) {
        e.preventDefault();
        unlockAudio();
        playOdenisSound();
        showToast({
          title: 'Test: Yeni Ödəniş',
          body: '15.00 AZN — Super VIP Paketi',
          sub: 'İstifadəçi: usta_resul (Ödəniş qəbzi ilə)',
          url: '/admin/core/odenis/?status__exact=gozlemede',
          icon: 'payments',
          iconBg: '#fef3c7',
          iconColor: '#d97706',
          borderColor: '#fde68a',
          textColor: '#b45309',
          btnBg: '#d97706',
          btnText: 'Ödənişə Bax',
        });
      });
    }

    updateSoundStatusUI();
  }

  function updateSoundStatusUI() {
    var muted = isSoundMuted();

    // 1. Header Butonu
    var headerBtn = document.getElementById('adminHeaderSoundBtn');
    var headerIcon = document.getElementById('headerSoundIcon');
    if (headerBtn && headerIcon) {
      if (muted) {
        headerIcon.innerText = 'volume_off';
        headerIcon.className = 'material-symbols-outlined text-lg text-red-500';
        headerBtn.title = 'Səsli Bildiriş: Səssiz (Açmaq üçün klikləyin)';
      } else {
        headerIcon.innerText = 'volume_up';
        headerIcon.className = 'material-symbols-outlined text-lg text-emerald-600 dark:text-emerald-400';
        headerBtn.title = 'Səsli Bildiriş: Aktiv (Səssiz etmək üçün klikləyin)';
      }
    }

    // 2. Parametrlər Menyusu (Sidebar)
    var toggleBtn = document.getElementById('toggleSoundBtn');
    var soundIcon = document.getElementById('soundStatusIcon');
    if (toggleBtn) {
      if (muted) {
        toggleBtn.innerText = 'Səssiz';
        toggleBtn.className =
          'cursor-pointer font-bold px-2 py-0.5 rounded text-[11px] transition-colors bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-950/60 dark:text-red-400';
      } else {
        toggleBtn.innerText = 'Aktiv';
        toggleBtn.className =
          'cursor-pointer font-bold px-2 py-0.5 rounded text-[11px] transition-colors bg-emerald-100 text-emerald-800 hover:bg-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300';
      }
    }
    if (soundIcon) {
      if (muted) {
        soundIcon.innerText = 'volume_off';
        soundIcon.className = 'material-symbols-outlined text-[17px] text-red-500';
      } else {
        soundIcon.innerText = 'volume_up';
        soundIcon.className = 'material-symbols-outlined text-[17px] text-primary-600 dark:text-primary-500';
      }
    }
  }

  // =========================================================================
  // CANLI YOXLAMA (POLLING) VƏ BİLDİRİŞLƏR
  // =========================================================================
  var lastElanId = null;
  var lastOdenisId = null;
  var isFirstPoll = true;

  function pollNotifications() {
    fetch(API_URL, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
    })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        if (!data || data.status !== 'ok') return;

        // İlkin yüklənmədə baseline qeyd et (səhifə açılanda köhnələri təkrar çalmasın)
        if (isFirstPoll) {
          isFirstPoll = false;
          if (data.elan && data.elan.latest) {
            lastElanId = parseInt(
              sessionStorage.getItem('prousta_last_elan_id') || data.elan.latest.id,
              10
            );
            sessionStorage.setItem('prousta_last_elan_id', lastElanId);
          }
          if (data.odenis && data.odenis.latest) {
            lastOdenisId = parseInt(
              sessionStorage.getItem('prousta_last_odenis_id') || data.odenis.latest.id,
              10
            );
            sessionStorage.setItem('prousta_last_odenis_id', lastOdenisId);
          }
          return;
        }

        // 1. YENİ ELAN YOXLAMASI
        if (data.elan && data.elan.latest && data.elan.latest.id) {
          var curElanId = parseInt(data.elan.latest.id, 10);
          if (lastElanId !== null && curElanId > lastElanId) {
            lastElanId = curElanId;
            sessionStorage.setItem('prousta_last_elan_id', curElanId);

            playElanSound();

            showToast({
              title: 'Yeni Elan Daxil Oldu',
              body: data.elan.latest.title,
              sub: 'İstifadəçi: ' + data.elan.latest.user + (data.elan.latest.phone ? ' · ' + data.elan.latest.phone : ''),
              url: data.elan.latest.url || '/admin/core/elan/?status__exact=gozlemede',
              icon: 'campaign',
              iconBg: '#ecfdf5',
              iconColor: '#059669',
              borderColor: '#6ee7b7',
              textColor: '#047857',
              btnBg: '#059669',
              btnText: 'Elanı Təsdiqlə',
            });

            showDesktopNotification(
              'Yeni Elan Daxil Oldu',
              data.elan.latest.title + ' — ' + data.elan.latest.user,
              data.elan.latest.url
            );
          } else {
            lastElanId = curElanId;
            sessionStorage.setItem('prousta_last_elan_id', curElanId);
          }
        }

        // 2. YENİ ÖDƏNİŞ YOXLAMASI
        if (data.odenis && data.odenis.latest && data.odenis.latest.id) {
          var curOdenisId = parseInt(data.odenis.latest.id, 10);
          if (lastOdenisId !== null && curOdenisId > lastOdenisId) {
            lastOdenisId = curOdenisId;
            sessionStorage.setItem('prousta_last_odenis_id', curOdenisId);

            playOdenisSound();

            showToast({
              title: 'Yeni Ödəniş Daxil Oldu',
              body: data.odenis.latest.amount + ' — ' + data.odenis.latest.type,
              sub: 'İstifadəçi: ' + data.odenis.latest.user,
              url: data.odenis.latest.url || '/admin/core/odenis/?status__exact=gozlemede',
              icon: 'payments',
              iconBg: '#fef3c7',
              iconColor: '#d97706',
              borderColor: '#fcd34d',
              textColor: '#b45309',
              btnBg: '#d97706',
              btnText: 'Ödənişi Yoxla',
            });

            showDesktopNotification(
              'Yeni Ödəniş Daxil Oldu',
              data.odenis.latest.amount + ' (' + data.odenis.latest.type + ') — ' + data.odenis.latest.user,
              data.odenis.latest.url
            );
          } else {
            lastOdenisId = curOdenisId;
            sessionStorage.setItem('prousta_last_odenis_id', curOdenisId);
          }
        }
      })
      .catch(function (err) {
        // Sakit xəta jurnallaması
      });
  }

  function init() {
    initSoundControls();
    pollNotifications();
    setInterval(pollNotifications, POLL_INTERVAL);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
