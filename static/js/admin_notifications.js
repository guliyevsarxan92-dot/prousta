/**
 * Prousta.az Admin Panel — Canlı Səsli Bildiriş Sistemi
 * - Yeni Elan gəldikdə: Zərif ikiqat zəng/ding-dong səsi (Web Audio API)
 * - Yeni Ödəniş gəldikdə: Fərqli kassa/qəpik cingiltisi "Ka-Ching" səsi (Web Audio API)
 * - Masaüstü və ekran bildirişləri (Toast)
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

  // =========================================================================
  // SƏS 1: YENİ ELAN SƏSİ (Zərif Kristal İkiqat Ding-Dong Zəngi)
  // =========================================================================
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

  // =========================================================================
  // SƏS 2: YENİ ÖDƏNİŞ SƏSİ (Kassa Cingiltisi "Ka-Ching" / Qəpik səsi)
  // =========================================================================
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
  // TOAST BİLDİRİŞ DİGƏRİNİ YARAT (Ekranın yuxarı sağ küncü)
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
      ';display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:20px;">' +
      opt.icon +
      '</div>' +
      '<div style="flex:1;min-width:0;">' +
      '<div style="display:flex;align-items:center;justify-content:between;gap:8px;margin-bottom:2px;">' +
      '<strong style="font-size:12px;color:#0f172a;letter-spacing:-0.2px;">' +
      opt.title +
      '</strong>' +
      '<button type="button" class="toast-close" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:16px;line-height:1;padding:0;margin-left:auto;">✕</button>' +
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
      ' ↗</a>' +
      '</div>' +
      '</div>';

    container.appendChild(toast);

    // Animasiyalı giriş
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

    // 12 saniyədən sonra avtomatik silinmə
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
  // KONTROL WIDGET-İ (Sağ aşağı künc)
  // =========================================================================
  var widgetEl = null;

  function createControlWidget() {
    if (document.getElementById('proustaSoundWidget')) return;

    widgetEl = document.createElement('div');
    widgetEl.id = 'proustaSoundWidget';
    widgetEl.style.cssText =
      'position:fixed;bottom:18px;right:18px;z-index:99999;font-family:inherit;';

    widgetEl.innerHTML =
      '<div id="soundWidgetPill" style="cursor:pointer;display:inline-flex;align-items:center;gap:7px;background:#ffffff;border:1px solid #cbd5e1;padding:7px 12px;border-radius:25px;box-shadow:0 6px 20px rgba(0,0,0,0.1);font-size:11px;font-weight:700;color:#334155;user-select:none;transition:all .2s;">' +
      '<span id="soundWidgetIcon" style="font-size:14px;">🔊</span>' +
      '<span id="soundWidgetLabel">Səsli Bildiriş: Aktiv</span>' +
      '</div>' +
      '<div id="soundWidgetMenu" style="display:none;position:absolute;bottom:42px;right:0;width:240px;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:12px;box-shadow:0 14px 35px rgba(0,0,0,0.18);flex-direction:column;gap:8px;">' +
      '<div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding-bottom:6px;margin-bottom:2px;">' +
      '<span style="font-size:11px;font-weight:800;color:#0f172a;">🔔 SƏS PARAMETRLƏRİ</span>' +
      '<button id="toggleMuteBtn" type="button" style="background:#f1f5f9;border:none;cursor:pointer;border-radius:6px;padding:3px 8px;font-size:10px;font-weight:700;color:#334155;">Səssiz et</button>' +
      '</div>' +
      '<div style="font-size:10px;color:#64748b;line-height:1.4;">Yeni elan və ödəniş gəldikdə admin paneldə avtomatik fərqli səs çalınır.</div>' +
      '<div style="display:flex;flex-direction:column;gap:5px;margin-top:4px;">' +
      '<button id="testElanSoundBtn" type="button" style="display:flex;align-items:center;gap:6px;background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46;border-radius:8px;padding:6px 10px;font-size:11px;font-weight:700;cursor:pointer;">' +
      '<span>🔔</span><span>Yeni Elan Səsini Yoxla</span>' +
      '</button>' +
      '<button id="testOdenisSoundBtn" type="button" style="display:flex;align-items:center;gap:6px;background:#fef3c7;border:1px solid #fde68a;color:#92400e;border-radius:8px;padding:6px 10px;font-size:11px;font-weight:700;cursor:pointer;">' +
      '<span>💰</span><span>Yeni Ödəniş Səsini Yoxla</span>' +
      '</button>' +
      '<button id="enableDesktopNotifyBtn" type="button" style="display:flex;align-items:center;gap:6px;background:#f8fafc;border:1px solid #e2e8f0;color:#475569;border-radius:8px;padding:6px 10px;font-size:10px;font-weight:600;cursor:pointer;">' +
      '<span>💻</span><span>Masaüstü Bildirişi Aç</span>' +
      '</button>' +
      '</div>' +
      '</div>';

    document.body.appendChild(widgetEl);

    var pill = document.getElementById('soundWidgetPill');
    var menu = document.getElementById('soundWidgetMenu');
    var toggleBtn = document.getElementById('toggleMuteBtn');
    var testElanBtn = document.getElementById('testElanSoundBtn');
    var testOdenisBtn = document.getElementById('testOdenisSoundBtn');
    var desktopBtn = document.getElementById('enableDesktopNotifyBtn');

    pill.addEventListener('click', function (e) {
      e.stopPropagation();
      unlockAudio();
      menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    });

    document.addEventListener('click', function (e) {
      if (!widgetEl.contains(e.target)) {
        menu.style.display = 'none';
      }
    });

    toggleBtn.addEventListener('click', function () {
      var nowMuted = !isSoundMuted();
      setSoundMuted(nowMuted);
    });

    testElanBtn.addEventListener('click', function () {
      unlockAudio();
      playElanSound();
      showToast({
        title: '🔔 Test: Yeni Elan!',
        body: 'Kondisioner təmiri və quraşdırılması',
        sub: 'Usta: Əli Məmmədov · 050 123 45 67',
        url: '/admin/core/elan/?status__exact=gozlemede',
        icon: '🔔',
        iconBg: '#ecfdf5',
        iconColor: '#059669',
        borderColor: '#a7f3d0',
        textColor: '#047857',
        btnBg: '#059669',
        btnText: 'Elanlara Bax',
      });
    });

    testOdenisBtn.addEventListener('click', function () {
      unlockAudio();
      playOdenisSound();
      showToast({
        title: '💰 Test: Yeni Ödəniş!',
        body: '15.00 AZN — Super VIP Paketi',
        sub: 'İstifadəçi: usta_resul (Ödəniş qəbzi ilə)',
        url: '/admin/core/odenis/?status__exact=gozlemede',
        icon: '💳',
        iconBg: '#fef3c7',
        iconColor: '#d97706',
        borderColor: '#fde68a',
        textColor: '#b45309',
        btnBg: '#d97706',
        btnText: 'Ödənişə Bax',
      });
    });

    desktopBtn.addEventListener('click', function () {
      if ('Notification' in window) {
        Notification.requestPermission().then(function (perm) {
          if (perm === 'granted') {
            showDesktopNotification(
              'Prousta Admin Bildirişləri Aktivdir!',
              'Yeni elan və ödənişlər daxil olduqda burada xəbərdarlıq görəcəksiniz.'
            );
            desktopBtn.innerText = '✅ Masaüstü Bildiriş Aktivdir';
            desktopBtn.style.color = '#059669';
          }
        });
      }
    });

    updateSoundStatusUI();
  }

  function updateSoundStatusUI() {
    var muted = isSoundMuted();
    var pill = document.getElementById('soundWidgetPill');
    var icon = document.getElementById('soundWidgetIcon');
    var label = document.getElementById('soundWidgetLabel');
    var toggleBtn = document.getElementById('toggleMuteBtn');

    if (!pill || !icon || !label || !toggleBtn) return;

    if (muted) {
      icon.innerText = '🔇';
      label.innerText = 'Səs: Səssiz';
      pill.style.borderColor = '#fca5a5';
      pill.style.background = '#fff5f5';
      pill.style.color = '#dc2626';
      toggleBtn.innerText = 'Səsi Aç 🔊';
      toggleBtn.style.color = '#059669';
    } else {
      icon.innerText = '🔊';
      label.innerText = 'Səs: Aktiv';
      pill.style.borderColor = '#bbf7d0';
      pill.style.background = '#f0fdf4';
      pill.style.color = '#15803d';
      toggleBtn.innerText = 'Səssiz Et 🔇';
      toggleBtn.style.color = '#dc2626';
    }
  }

  // =========================================================================
  // CANLI YOXLAMA (POLLING) VƏ BİLDİRİŞ İNTELLEKTİ
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
            // YENİ ELAN GƏLDİ!
            lastElanId = curElanId;
            sessionStorage.setItem('prousta_last_elan_id', curElanId);

            playElanSound();

            showToast({
              title: '🆕 Yeni Elan Daxil Oldu!',
              body: data.elan.latest.title,
              sub: 'İstifadəçi: ' + data.elan.latest.user + (data.elan.latest.phone ? ' · ' + data.elan.latest.phone : ''),
              url: data.elan.latest.url || '/admin/core/elan/?status__exact=gozlemede',
              icon: '🆕',
              iconBg: '#ecfdf5',
              iconColor: '#059669',
              borderColor: '#6ee7b7',
              textColor: '#047857',
              btnBg: '#059669',
              btnText: 'Elanı Təsdiqlə',
            });

            showDesktopNotification(
              '🆕 Yeni Elan Daxil Oldu!',
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
            // YENİ ÖDƏNİŞ GƏLDİ!
            lastOdenisId = curOdenisId;
            sessionStorage.setItem('prousta_last_odenis_id', curOdenisId);

            playOdenisSound();

            showToast({
              title: '💰 Yeni Ödəniş Daxil Oldu!',
              body: data.odenis.latest.amount + ' — ' + data.odenis.latest.type,
              sub: 'İstifadəçi: ' + data.odenis.latest.user,
              url: data.odenis.latest.url || '/admin/core/odenis/?status__exact=gozlemede',
              icon: '💳',
              iconBg: '#fef3c7',
              iconColor: '#d97706',
              borderColor: '#fcd34d',
              textColor: '#b45309',
              btnBg: '#d97706',
              btnText: 'Ödənişi Yoxla',
            });

            showDesktopNotification(
              '💰 Yeni Ödəniş Daxil Oldu!',
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

  // DOM hazır olduqda başlat
  function init() {
    createControlWidget();
    pollNotifications();
    setInterval(pollNotifications, POLL_INTERVAL);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
