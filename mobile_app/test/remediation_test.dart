import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prousta_mobile/providers/auth_provider.dart';
import 'package:prousta_mobile/providers/elan_provider.dart';
import 'package:prousta_mobile/services/api_service.dart';
import 'package:image_picker/image_picker.dart';

http.Response page(int id) => http.Response(
  jsonEncode({
    'results': [
      {'id': id, 'bashliq': 'Service'},
    ],
    'count': 1,
    'next': null,
  }),
  200,
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    FlutterSecureStorage.setMockInitialValues({});
    SharedPreferences.setMockInitialValues({});
    await ApiService.setToken(null);
  });

  test(
    'plaintext legacy token migrates to secure storage before removal',
    () async {
      SharedPreferences.setMockInitialValues({'auth_token': 'legacy-token'});
      await ApiService.init();
      expect(ApiService.token, 'legacy-token');
      expect(
        await const FlutterSecureStorage().read(key: 'auth_token'),
        'legacy-token',
      );
      expect(
        (await SharedPreferences.getInstance()).containsKey('auth_token'),
        isFalse,
      );
    },
  );

  test('an older listing response cannot overwrite a newer request', () async {
    final first = Completer<http.Response>();
    final second = Completer<http.Response>();
    var calls = 0;
    ApiService.setClient(
      MockClient((request) => calls++ == 0 ? first.future : second.future),
    );
    final provider = ElanProvider();
    final oldRequest = provider.fetchElanlar();
    await Future<void>.delayed(Duration.zero);
    final newRequest = provider.fetchElanlar();
    second.complete(page(2));
    await newRequest;
    first.complete(page(1));
    await oldRequest;
    expect(provider.elanlar.single.id, 2);
    expect(provider.isLoading, isFalse);
    provider.dispose();
  });

  test('temporary startup failure preserves the saved credential', () async {
    await ApiService.setToken('offline-credential');
    ApiService.setClient(
      MockClient((request) async => throw Exception('Offline')),
    );
    final provider = AuthProvider();
    await provider.initialize();
    expect(ApiService.token, 'offline-credential');
    expect(provider.initialized, isTrue);
    provider.dispose();
  });

  test('401 clears the saved credential', () async {
    await ApiService.setToken('expired-credential');
    ApiService.setClient(
      MockClient((request) async => http.Response('{}', 401)),
    );
    final provider = AuthProvider();
    await provider.initialize();
    expect(ApiService.token, isNull);
    provider.dispose();
  });

  test('a late profile response cannot restore a logged out account', () async {
    await ApiService.setToken('old-session');
    final pending = Completer<http.Response>();
    ApiService.setClient(MockClient((request) => pending.future));
    final provider = AuthProvider();
    final refresh = provider.refreshProfile();
    await Future<void>.delayed(Duration.zero);
    await ApiService.setToken(null);
    pending.complete(http.Response('{"id":42,"profil":{}}', 200));
    await refresh;
    expect(provider.user, isNull);
    provider.dispose();
  });

  test(
    'multiple image deletions are serialized as a complete JSON list',
    () async {
      String? body;
      ApiService.setClient(
        MockClient((request) async {
          body = request.body;
          return http.Response('{"elan":{"id":1,"bashliq":"Service"}}', 200);
        }),
      );
      await ApiService.updateElan(
        id: 1,
        bashliq: 'Service',
        acaqlama: 'Description',
        qiymet: '3',
        sheher: 'Bakı',
        telefon: '+994501234567',
        deleteImageIds: [4, 5],
      );
      expect(body, contains('[4,5]'));
    },
  );

  test(
    'paginated favorites are read without silently losing later pages',
    () async {
      ApiService.setClient(
        MockClient((request) async {
          final first = request.url.queryParameters['page'] == '1';
          return http.Response(
            jsonEncode({
              'results': [
                {'id': first ? 1 : 2},
              ],
              'next': first ? 'next-page' : null,
            }),
            200,
          );
        }),
      );
      expect((await ApiService.getFavorites()).map((e) => e.id), [1, 2]);
    },
  );

  test(
    'multipart uploads use bytes and work without filesystem paths',
    () async {
      ApiService.setClient(
        MockClient(
          (request) async =>
              http.Response('{"user":{"id":1,"profil":{}}}', 200),
        ),
      );
      final user = await ApiService.updateProfile(
        avatarFile: XFile.fromData(
          utf8.encode('test-bytes'),
          name: 'photo.jpg',
        ),
      );
      expect(user.id, 1);
    },
  );

  test(
    'active session 401 automatically clears token and logs out AuthProvider',
    () async {
      await ApiService.setToken('live-token');
      ApiService.setClient(
        MockClient((request) async => http.Response('{"id":7,"profil":{}}', 200)),
      );
      final provider = AuthProvider();
      await provider.initialize();
      expect(provider.isAuthenticated, isTrue);

      ApiService.setClient(
        MockClient((request) async => http.Response('{"detail":"Invalid token."}', 401)),
      );
      await expectLater(ApiService.getFavorites(), throwsA(isA<ApiAuthException>()));
      await Future<void>.delayed(Duration.zero);
      expect(ApiService.token, isNull);
      expect(provider.user, isNull);
      expect(provider.isAuthenticated, isFalse);
      provider.dispose();
    },
  );

  test('createElan rejects images larger than 5 MB before uploading', () async {
    final oversized = XFile.fromData(
      Uint8List(5 * 1024 * 1024 + 1),
      name: 'huge.jpg',
    );
    await expectLater(
      ApiService.createElan(
        bashliq: 'Kombi təmiri',
        acaqlama: 'Peşəkar kombi təmiri və texniki xidmət.',
        kategoriId: 1,
        sheher: 'Bakı',
        telefon: '501234567',
        images: [oversized],
      ),
      throwsA(
        predicate<Object>((e) => e.toString().contains('5 MB')),
      ),
    );
  });

  test('ElanProvider surfaces errorMessage when initial fetch fails', () async {
    ApiService.setClient(
      MockClient((request) async => throw Exception('No network')),
    );
    final provider = ElanProvider();
    await provider.fetchElanlar(reset: true);
    expect(provider.errorMessage, isNotNull);
    expect(provider.elanlar, isEmpty);
    provider.dispose();
  });
}
