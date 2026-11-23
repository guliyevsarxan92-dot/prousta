(() => {
  'use strict';
  document.querySelectorAll('[data-service-request]').forEach(form => {
    const build = form.querySelector('[data-request-build]');
    const result = form.querySelector('[data-request-result]');
    const output = form.querySelector('[data-request-text]');
    const status = form.querySelector('[data-request-status]');
    const whatsapp = form.querySelector('[data-request-whatsapp]');
    const copy = form.querySelector('[data-request-copy]');
    build.disabled = false;
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const text = [
        `Salam, ${form.dataset.service} üçün müraciət edirəm.`,
        `Ünvan / rayon: ${String(data.get('area')).trim()}`,
        `Avadanlıq / xətt: ${String(data.get('equipment')).trim()}`,
      ];
      if (data.has('radiators')) text.push(`Radiator sayı: ${data.get('radiators')}`);
      text.push(`İşin təsviri: ${String(data.get('problem')).trim()}`);
      if (form.dataset.price) text.push(`Səhifədəki ${form.dataset.price} təklifinə əsasən iş həcmi üzrə yekun məbləği dəqiqləşdirmək istəyirəm.`);
      text.push('Qiymətə daxil olan işləri, gəliş vaxtını və zəmanətin müddəti/şərtlərini bildirin.');
      output.value = text.join('\n');
      if (whatsapp) whatsapp.href = `https://wa.me/${form.dataset.phone.replace(/\D/g, '')}?text=${encodeURIComponent(output.value)}`;
      result.hidden = false;
      status.textContent = 'Mətn hazırdır. Göndərməzdən əvvəl yoxlayın.';
      output.focus();
    });
    form.addEventListener('input', () => {
      if (!result.hidden) {
        result.hidden = true;
        if (whatsapp) whatsapp.removeAttribute('href');
      }
    });
    copy.addEventListener('click', async () => {
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('clipboard');
        await navigator.clipboard.writeText(output.value);
        status.textContent = 'Mətn kopyalandı.';
      } catch (_) {
        output.focus();
        output.select();
        status.textContent = 'Mətni seçib cihazınızın kopyalama əmri ilə kopyalayın.';
      }
    });
  });
})();
