import 'package:flutter_test/flutter_test.dart';
import 'package:prousta_mobile/main.dart';

void main() {
  testWidgets('ProustaApp renders navigation bar', (WidgetTester tester) async {
    await tester.pumpWidget(const ProustaApp());
    expect(find.text('Ana səhifə'), findsOneWidget);
    expect(find.text('Favorilər'), findsOneWidget);
    expect(find.text('Mesajlar'), findsOneWidget);
    expect(find.text('Profil'), findsOneWidget);
  });
}
