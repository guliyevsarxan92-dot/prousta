import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:prousta_mobile/main.dart';
import 'package:prousta_mobile/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  testWidgets('ProustaApp renders navigation bar', (WidgetTester tester) async {
    FlutterSecureStorage.setMockInitialValues({});
    SharedPreferences.setMockInitialValues({});
    await ApiService.setToken(null);
    ApiService.setClient(
      MockClient(
        (request) async => http.Response(
          request.url.path.contains('elanlar')
              ? '{"results":[],"count":0,"next":null}'
              : '[]',
          200,
        ),
      ),
    );
    await tester.pumpWidget(const ProustaApp());
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.text('Ana səhifə'), findsOneWidget);
    expect(find.text('Favorilər'), findsOneWidget);
    expect(find.text('Mesajlar'), findsOneWidget);
    expect(find.text('Profil'), findsOneWidget);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
