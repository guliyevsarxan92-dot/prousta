# Prousta Flutter müştərisi

Flutter 3.41.7 / Dart 3.11.5. Quraşdırma və test əmrləri əsas [README](../README.md)-dədir.

- API ünvanı: `--dart-define=API_URL=https://staging.example/api/v1`. Release-də HTTPS məcburidir.
- API token secure storage-da saxlanılır. Android auto-backup deaktivdir; iOS signing profilində Runner.entitlements yoxlanmalıdır.
- Google iOS: `ios/Flutter/GoogleSignIn.xcconfig.example` əsasında lokal konfiqurasiya yaradın. Düzgün iOS client ID və reversed ID tələb olunur.
- Android release üçün `android/key.properties` və uyğun keystore tələb olunur. Bunlar Git-ə daxil edilmir. Debug signing-ə fallback yoxdur.
- Şəkil yükləməsi XFile/bytes istifadə edir; web-də fayl sistemi yolu tələb etmir.
- İcazələr və məbləğlər serverdə yoxlanır; müştəri qiymətləri təhlükəsizlik qərarı deyil.
- Linux desktop üçün secure storage plugin-inin sistem keyring/libsecret tələblərini də təmin edin.
- Buraxılışdan əvvəl `flutter analyze --fatal-infos`, `flutter test`, web/Android build və real iOS giriş/upload sınağı aparın.
