(() => {
  'use strict';
  const isRu = document.documentElement.lang === 'ru';
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
      let text;
      if (isRu) {
        text = [
          `Здравствуйте, обращаюсь по услуге «${form.dataset.service}».`,
          `Адрес / район: ${String(data.get('area')).trim()}`,
          `Оборудование / линия: ${String(data.get('equipment')).trim()}`,
        ];
        if (data.has('radiators')) text.push(`Количество радиаторов: ${data.get('radiators')}`);
        text.push(`Описание задачи: ${String(data.get('problem')).trim()}`);
        if (form.dataset.price) text.push(`Хочу уточнить итоговую стоимость по объёму работ (предложение на странице: ${form.dataset.price}).`);
        text.push('Укажите, что входит в стоимость, время выезда и условия гарантии.');
      } else {
        text = [
          `Salam, ${form.dataset.service} üçün müraciət edirəm.`,
          `Ünvan / rayon: ${String(data.get('area')).trim()}`,
          `Avadanlıq / xətt: ${String(data.get('equipment')).trim()}`,
        ];
        if (data.has('radiators')) text.push(`Radiator sayı: ${data.get('radiators')}`);
        text.push(`İşin təsviri: ${String(data.get('problem')).trim()}`);
        if (form.dataset.price) text.push(`Səhifədəki ${form.dataset.price} təklifinə əsasən iş həcmi üzrə yekun məbləği dəqiqləşdirmək istəyirəm.`);
        text.push('Qiymətə daxil olan işləri, gəliş vaxtını və zəmanətin müddəti/şərtlərini bildirin.');
      }
      output.value = text.join('\n');
      if (whatsapp) whatsapp.href = `https://wa.me/${form.dataset.phone.replace(/\D/g, '')}?text=${encodeURIComponent(output.value)}`;
      result.hidden = false;
      status.textContent = isRu ? 'Текст готов. Проверьте перед отправкой.' : 'Mətn hazırdır. Göndərməzdən əvvəl yoxlayın.';
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
        status.textContent = isRu ? 'Текст скопирован.' : 'Mətn kopyalandı.';
      } catch (_) {
        output.focus();
        output.select();
        status.textContent = isRu ? 'Выделите текст и скопируйте вручную.' : 'Mətni seçib cihazınızın kopyalama əmri ilə kopyalayın.';
      }
    });
  });
})();
