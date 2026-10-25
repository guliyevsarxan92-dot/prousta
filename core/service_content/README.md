# Fərdi xidmət məzmunu

`data/*.json` fayllarında hər xidmət üçün ayrıca yazılmış seçim bələdçisi saxlanılır. Sahələr: `name`, `heading`, `description`, `intro`, `scope`, `pricing`, `prepare`, iki `questions`, `queries`, `related`, `sources`.

`queries` axtarış niyyəti planıdır; ölçülmüş həcm deyil və keyword siyahısı kimi səhifədə gizli yerləşdirilmir. `sources` əsas anlayışların mənbə identifikatorlarını verir. Heç bir mətn avtomatik ekspert təsdiqi, usta sertifikatı, nəticə və ya qiymət zəmanəti sayılmır.

Admin-də fərdi SEO title/description saxlanılır. Köhnə seed şablonunun yalnız məlum blokları fingerprint əsasında təqdimatdan çıxarılır; əlavə edilmiş və redaktə edilmiş HTML saxlanılır. Baza qeydləri yenidən yazılmır. `legacy_fingerprints.json` tarixdəki seed variantlarından yaradılıb; canlı məxfi məlumat ehtiva etmir.
