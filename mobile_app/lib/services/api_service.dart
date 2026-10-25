import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/models.dart';

class ApiAuthException implements Exception {
  @override
  String toString() => 'Sessiyanın müddəti bitib. Yenidən daxil olun.';
}

class BoundedClient extends http.BaseClient {
  final http.Client inner;
  BoundedClient(this.inner);

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final response = await inner
        .send(request)
        .timeout(const Duration(seconds: 30));
    if (response.statusCode == 401) {
      await response.stream.drain<void>().timeout(const Duration(seconds: 5));
      throw ApiAuthException();
    }
    return http.StreamedResponse(
      response.stream.timeout(const Duration(seconds: 30)),
      response.statusCode,
      headers: response.headers,
      request: response.request,
      reasonPhrase: response.reasonPhrase,
      isRedirect: response.isRedirect,
      persistentConnection: response.persistentConnection,
      contentLength: response.contentLength,
    );
  }

  @override
  void close() => inner.close();
}

class ApiService {
  static const String _envUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: '',
  );
  static final String _resolvedBaseUrl = _envUrl.isNotEmpty
      ? _envUrl
      : (kReleaseMode
            ? 'https://prousta.az/api/v1'
            : 'http://127.0.0.1:8000/api/v1');
  static http.Client _client = BoundedClient(http.Client());
  static String get baseUrl => _resolvedBaseUrl;

  @visibleForTesting
  static void setClient(http.Client client) {
    _client.close();
    _client = BoundedClient(client);
  }

  static Future<void> ensureBaseUrl() async {
    final uri = Uri.tryParse(_resolvedBaseUrl);
    if (uri == null ||
        uri.host.isEmpty ||
        (kReleaseMode && uri.scheme != 'https')) {
      throw StateError('API_URL düzgün HTTPS ünvanı olmalıdır.');
    }
  }

  static dynamic decodeResponse(http.Response response) {
    try {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      throw Exception('Server cavabı düzgün deyil. Yenidən cəhd edin.');
    }
  }

  static const _credentialStore = FlutterSecureStorage();
  static String? _token;

  static Future<void> init() async {
    await ensureBaseUrl();
    final prefs = await SharedPreferences.getInstance();
    var credential = await _credentialStore.read(key: 'auth_token');
    final legacy = prefs.getString('auth_token');
    if (credential == null && legacy != null) {
      await _credentialStore.write(key: 'auth_token', value: legacy);
      credential = legacy;
    }
    // Remove plaintext only after a successful secure read/write.
    await prefs.remove('auth_token');
    _token = credential;
  }

  static Future<void> setToken(String? token) async {
    if (token == null) {
      await _credentialStore.delete(key: 'auth_token');
    } else {
      await _credentialStore.write(key: 'auth_token', value: token);
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    _token = token;
  }

  static String? get token => _token;
  static bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  static Map<String, String> get _headers {
    final h = <String, String>{
      'Accept': 'application/json',
      'Content-Type': 'application/json; charset=UTF-8',
    };
    if (_token != null && _token!.isNotEmpty) {
      h['Authorization'] = 'Token $_token';
    }
    return h;
  }

  static Map<String, String> get _multipartHeaders {
    final h = <String, String>{'Accept': 'application/json'};
    if (_token != null && _token!.isNotEmpty) {
      h['Authorization'] = 'Token $_token';
    }
    return h;
  }

  // ---------------------------------------------------------------------------
  // AUTH
  // ---------------------------------------------------------------------------

  static Future<http.MultipartFile> _imagePart(String field, XFile file) async {
    final bytes = await file.readAsBytes();
    if (bytes.length > 5 * 1024 * 1024) {
      throw Exception('Şəkil 5 MB-dan böyükdür.');
    }
    return http.MultipartFile.fromBytes(field, bytes, filename: file.name);
  }

  static Future<List<dynamic>> _privateList(
    String path, {
    Map<String, String>? params,
  }) async {
    final sessionToken = _token;
    final result = <dynamic>[];
    final parameters = <String, String>{...?params, 'page_size': '50'};
    // Existing profile sheets show a full list; fetch each bounded page explicitly.
    for (var page = 1; page <= 100; page++) {
      parameters['page'] = '$page';
      final uri = Uri.parse(
        '$baseUrl/$path',
      ).replace(queryParameters: parameters);
      final response = await _client.get(uri, headers: _headers);
      if (response.statusCode != 200) {
        throw Exception('Məlumatlar yüklənə bilmədi.');
      }
      if (_token != sessionToken) throw ApiAuthException();
      final data = decodeResponse(response);
      if (data is List) return data;
      result.addAll(data['results'] as List<dynamic>);
      if (data['next'] == null) return result;
    }
    throw Exception('Siyahı çox böyükdür. Filtr tətbiq edin.');
  }

  static Future<Map<String, dynamic>> login(
    String usernameOrEmail,
    String password,
  ) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: _headers,
      body: jsonEncode({'username': usernameOrEmail, 'password': password}),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      await setToken(data['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Giriş zamanı xəta baş verdi');
  }

  static Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String ad,
    required String soyad,
    required String telefon,
    String sheher = 'Bakı',
  }) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/auth/register/'),
      headers: _headers,
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
        'ad': ad,
        'soyad': soyad,
        'telefon': telefon,
        'sheher': sheher,
      }),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 201 || res.statusCode == 200) {
      await setToken(data['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Qeydiyyat zamanı xəta baş verdi');
  }

  static Future<Map<String, dynamic>> googleLogin(String idToken) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/auth/google/'),
      headers: _headers,
      body: jsonEncode({'id_token': idToken}),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      await setToken(data['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Google ilə giriş uğursuz oldu');
  }

  static Future<void> logout() async {
    try {
      await _client.post(Uri.parse('$baseUrl/auth/logout/'), headers: _headers);
    } catch (_) {}
    await setToken(null);
  }

  static Future<AppUser> getProfile() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/auth/me/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = decodeResponse(res);
      return AppUser.fromJson(data);
    }
    throw Exception('Profil məlumatları yüklənə bilmədi');
  }

  static Future<AppUser> updateProfile({
    String? ad,
    String? soyad,
    String? telefon,
    String? sheher,
    XFile? avatarFile,
  }) async {
    final req = http.MultipartRequest('PATCH', Uri.parse('$baseUrl/auth/me/'));
    req.headers.addAll(_multipartHeaders);
    if (ad != null) req.fields['ad'] = ad;
    if (soyad != null) req.fields['soyad'] = soyad;
    if (telefon != null) req.fields['telefon'] = telefon;
    if (sheher != null) req.fields['sheher'] = sheher;
    if (avatarFile != null) {
      req.files.add(await _imagePart('avatar', avatarFile));
    }

    final streamed = await _client.send(req);
    final res = await http.Response.fromStream(streamed);
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      return AppUser.fromJson(data['user']);
    }
    throw Exception(data['error'] ?? 'Profil yenilənə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // CATEGORIES & BANNERS
  // ---------------------------------------------------------------------------

  static Future<List<CategoryModel>> getCategories() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/categories/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Kateqoriyalar yüklənə bilmədi');
  }

  static Future<List<BannerModel>> getBanners() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/banners/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => BannerModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  // ---------------------------------------------------------------------------
  // ELANLAR
  // ---------------------------------------------------------------------------

  static Future<Map<String, dynamic>> getElanlar({
    int page = 1,
    String? query,
    String? kategoriSlug,
    String? seher,
    bool vipOnly = false,
    int? userId,
  }) async {
    final params = <String, String>{'page': page.toString()};
    if (query != null && query.isNotEmpty) params['q'] = query;
    if (kategoriSlug != null && kategoriSlug.isNotEmpty) {
      params['kategori'] = kategoriSlug;
    }
    if (seher != null && seher.isNotEmpty && seher != 'Bütün Azərbaycan') {
      params['seher'] = seher;
    }
    if (vipOnly) params['vip_only'] = 'true';
    if (userId != null) params['user_id'] = userId.toString();

    final uri = Uri.parse('$baseUrl/elanlar/').replace(queryParameters: params);
    final res = await _client.get(uri, headers: _headers);
    if (res.statusCode == 200) {
      final data = decodeResponse(res);
      final results =
          (data['results'] as List<dynamic>?)
              ?.map((e) => ElanModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];
      return {
        'results': results,
        'count': data['count'] ?? results.length,
        'hasNext': data['next'] != null,
      };
    }
    throw Exception('Elanlar yüklənərkən xəta baş verdi');
  }

  static Future<ElanModel> getElanDetail(int id) async {
    final res = await _client.get(
      Uri.parse('$baseUrl/elanlar/$id/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = decodeResponse(res);
      return ElanModel.fromJson(data);
    }
    throw Exception('Elan tapılmadı');
  }

  static Future<ElanModel> createElan({
    required String bashliq,
    required String acaqlama,
    String? qiymet,
    required int kategoriId,
    required String sheher,
    required String telefon,
    required List<XFile> images,
  }) async {
    final req = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/elanlar/create/'),
    );
    req.headers.addAll(_multipartHeaders);
    req.fields['bashliq'] = bashliq;
    req.fields['acaqlama'] = acaqlama;
    if (qiymet != null && qiymet.isNotEmpty) req.fields['qiymet'] = qiymet;
    req.fields['kategori'] = kategoriId.toString();
    req.fields['sheher'] = sheher;
    req.fields['telefon'] = telefon;

    for (final xfile in images) {
      final bytes = await xfile.readAsBytes();
      final name = xfile.name.isNotEmpty ? xfile.name : 'elan_photo.jpg';
      final ext = name.split('.').last.toLowerCase();
      final subtype = ext == 'png'
          ? 'png'
          : ext == 'webp'
          ? 'webp'
          : 'jpeg';
      req.files.add(
        http.MultipartFile.fromBytes(
          'shekillar',
          bytes,
          filename: name,
          contentType: http.MediaType('image', subtype),
        ),
      );
    }

    final streamed = await _client.send(req);
    final res = await http.Response.fromStream(streamed);
    final data = decodeResponse(res);
    if (res.statusCode == 201 || res.statusCode == 200) {
      return ElanModel.fromJson(data['elan']);
    }
    throw Exception(data['error'] ?? 'Elan yaradılarkən xəta baş verdi');
  }

  static Future<ElanModel> updateElan({
    required int id,
    required String bashliq,
    required String acaqlama,
    required String qiymet,
    required String sheher,
    required String telefon,
    int? kategoriId,
    List<XFile>? newImages,
    List<int>? deleteImageIds,
  }) async {
    final req = http.MultipartRequest(
      'PATCH',
      Uri.parse('$baseUrl/elanlar/$id/update/'),
    );
    req.headers.addAll(_multipartHeaders);
    req.fields['bashliq'] = bashliq;
    req.fields['acaqlama'] = acaqlama;
    req.fields['qiymet'] = qiymet;
    req.fields['sheher'] = sheher;
    req.fields['telefon'] = telefon;
    if (kategoriId != null) req.fields['kategori_id'] = kategoriId.toString();

    if (deleteImageIds != null && deleteImageIds.isNotEmpty) {
      req.fields['silinecek_shekiller'] = jsonEncode(deleteImageIds);
    }

    if (newImages != null && newImages.isNotEmpty) {
      for (final f in newImages) {
        req.files.add(await _imagePart('shekillar', f));
      }
    }

    final streamed = await _client.send(req);
    final res = await http.Response.fromStream(streamed);
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      return ElanModel.fromJson(data['elan']);
    }
    throw Exception(data['error'] ?? 'Elan yenilənərkən xəta baş verdi');
  }

  static Future<void> deleteElan(int id) async {
    final res = await _client.delete(
      Uri.parse('$baseUrl/elanlar/$id/delete/'),
      headers: _headers,
    );
    if (res.statusCode != 200 && res.statusCode != 204) {
      throw Exception('Elan silinə bilmədi');
    }
  }

  static Future<void> registerElanClick(int id, String nov) async {
    try {
      await _client.post(
        Uri.parse('$baseUrl/elanlar/$id/click/$nov/'),
        headers: _headers,
      );
    } catch (_) {}
  }

  static Future<List<ElanModel>> getMyElanlar({String? status}) async {
    final params = <String, String>{};
    if (status != null && status.isNotEmpty) params['status'] = status;
    final list = await _privateList('my-elanlar/', params: params);
    return list
        .map((e) => ElanModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ---------------------------------------------------------------------------
  // FAVORITES
  // ---------------------------------------------------------------------------

  static Future<List<ElanModel>> getFavorites() async {
    final list = await _privateList('favorites/');
    return list
        .map((e) => ElanModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  static Future<bool> toggleFavorite(int elanId) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/favorites/toggle/$elanId/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = decodeResponse(res);
      return data['is_favorit'] ?? false;
    }
    throw Exception('Əməliyyat uğursuz oldu');
  }

  // ---------------------------------------------------------------------------
  // MESSAGES
  // ---------------------------------------------------------------------------

  static Future<List<ConversationModel>> getConversations({
    int? beforeId,
  }) async {
    final res = await _client.get(
      Uri.parse('$baseUrl/messages/conversations/').replace(
        queryParameters: {if (beforeId != null) 'before_id': '$beforeId'},
      ),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => ConversationModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Mesajlar yüklənə bilmədi');
  }

  static Future<List<ChatMessageModel>> getChatMessages(
    int otherUserId, {
    int? afterId,
    int? beforeId,
  }) async {
    final res = await _client.get(
      Uri.parse('$baseUrl/messages/$otherUserId/').replace(
        queryParameters: {
          if (afterId != null) 'after_id': '$afterId',
          if (beforeId != null) 'before_id': '$beforeId',
        },
      ),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => ChatMessageModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Söhbət yüklənə bilmədi');
  }

  static Future<ChatMessageModel> sendMessage({
    required int otherUserId,
    required String metn,
    int? elanId,
  }) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/messages/$otherUserId/'),
      headers: _headers,
      body: jsonEncode({'metn': metn, 'elan_id': ?elanId}),
    );
    if (res.statusCode == 201 || res.statusCode == 200) {
      final data = decodeResponse(res);
      return ChatMessageModel.fromJson(data);
    }
    throw Exception('Mesaj göndərilə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // VIP & PAYMENTS
  // ---------------------------------------------------------------------------

  static Future<List<VipPaketModel>> getVipPackages() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/vip-packages/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => VipPaketModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  static Future<List<BankMelumatModel>> getBankInfo() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/bank-info/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list
          .map((e) => BankMelumatModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  static Future<String> submitPayment({
    required String nov,
    required String mebleg,
    int? elanId,
    required XFile qebzFile,
    String qeyd = '',
  }) async {
    final req = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/payments/create/'),
    );
    req.headers.addAll(_multipartHeaders);
    req.fields['nov'] = nov;
    req.fields['mebleg'] = mebleg;
    if (elanId != null) req.fields['elan_id'] = elanId.toString();
    if (qeyd.isNotEmpty) req.fields['qeyd'] = qeyd;
    req.files.add(await _imagePart('qebz', qebzFile));

    final streamed = await _client.send(req);
    final res = await http.Response.fromStream(streamed);
    final data = decodeResponse(res);
    if (res.statusCode == 201 || res.statusCode == 200) {
      return data['message'] ?? 'Ödəniş qəbzi göndərildi!';
    }
    throw Exception(data['error'] ?? 'Ödəniş göndərilə bilmədi');
  }

  static Future<String> activateVipFromBalance({
    required int elanId,
    required String nov,
  }) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/elanlar/$elanId/vip/'),
      headers: _headers,
      body: jsonEncode({'nov': nov}),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 200 || res.statusCode == 201) {
      return data['message'] ?? 'Elanınız VİP edildi!';
    }
    throw Exception(data['error'] ?? 'VİP aktivləşdirilə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // ACCOUNT DELETION (Google Play Policy)
  // ---------------------------------------------------------------------------

  static Future<void> deleteAccount({String? password, String? confirm}) async {
    final body = <String, dynamic>{};
    if (password != null && password.isNotEmpty) {
      body['password'] = password;
    }
    if (confirm != null && confirm.isNotEmpty) {
      body['confirm'] = confirm;
    }

    final res = await _client.post(
      Uri.parse('$baseUrl/auth/delete-account/'),
      headers: _headers,
      body: jsonEncode(body),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      await setToken(null);
      return;
    }
    throw Exception(data['error'] ?? 'Hesab silinərkən xəta baş verdi');
  }

  // ---------------------------------------------------------------------------
  // UGC: REPORT & BLOCK (Google Play Policy)
  // ---------------------------------------------------------------------------

  static Future<String> reportContent({
    int? elanId,
    int? userId,
    required String sebeb,
    String? qeyd,
  }) async {
    final payload = <String, dynamic>{'sebeb': sebeb};
    if (elanId != null) payload['elan_id'] = elanId;
    if (userId != null) payload['user_id'] = userId;
    if (qeyd != null && qeyd.isNotEmpty) payload['qeyd'] = qeyd;

    final res = await _client.post(
      Uri.parse('$baseUrl/report/'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    final data = decodeResponse(res);
    if (res.statusCode == 201 || res.statusCode == 200) {
      return data['message'] ?? 'Şikayətiniz qəbul edildi';
    }
    throw Exception(data['error'] ?? 'Şikayət göndərilə bilmədi');
  }

  static Future<bool> toggleBlockUser(int userId) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/users/$userId/block/'),
      headers: _headers,
    );
    final data = decodeResponse(res);
    if (res.statusCode == 200) {
      return data['blocked'] == true;
    }
    throw Exception(data['error'] ?? 'İstifadəçi bloklanarkən xəta baş verdi');
  }

  static Future<List<Map<String, dynamic>>> getBlockedUsers() async {
    final res = await _client.get(
      Uri.parse('$baseUrl/users/blocked/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = decodeResponse(res) as List<dynamic>;
      return list.cast<Map<String, dynamic>>();
    }
    return [];
  }
}
