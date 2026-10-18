import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/models.dart';

class ApiService {
  static const String _envUrl = String.fromEnvironment('API_URL', defaultValue: '');
  static String _resolvedBaseUrl = _envUrl.isNotEmpty ? _envUrl : 'http://127.0.0.1:8000/api/v1';
  static bool _urlChecked = false;

  static String get baseUrl => _resolvedBaseUrl;

  static Future<void> ensureBaseUrl() async {
    if (_urlChecked || _envUrl.isNotEmpty) return;
    _urlChecked = true;
    try {
      final res = await http
          .get(Uri.parse('http://127.0.0.1:8000/api/v1/banners/'))
          .timeout(const Duration(seconds: 2));
      if (res.statusCode == 200) {
        _resolvedBaseUrl = 'http://127.0.0.1:8000/api/v1';
        return;
      }
    } catch (_) {}
    _resolvedBaseUrl = 'https://prousta.az/api/v1';
  }

  static String? _token;

  static Future<void> init() async {
    await ensureBaseUrl();
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }

  static Future<void> setToken(String? token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    if (token == null) {
      await prefs.remove('auth_token');
    } else {
      await prefs.setString('auth_token', token);
    }
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
    final h = <String, String>{
      'Accept': 'application/json',
    };
    if (_token != null && _token!.isNotEmpty) {
      h['Authorization'] = 'Token $_token';
    }
    return h;
  }

  // ---------------------------------------------------------------------------
  // AUTH
  // ---------------------------------------------------------------------------

  static Future<Map<String, dynamic>> login(
      String usernameOrEmail, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: _headers,
      body: jsonEncode({
        'username': usernameOrEmail,
        'password': password,
      }),
    );
    final data = jsonDecode(utf8.decode(res.bodyBytes));
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
    final res = await http.post(
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
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 201 || res.statusCode == 200) {
      await setToken(data['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Qeydiyyat zamanı xəta baş verdi');
  }

  static Future<Map<String, dynamic>> googleLogin(String idToken) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/google/'),
      headers: _headers,
      body: jsonEncode({'id_token': idToken}),
    );
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 200) {
      await setToken(data['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Google ilə giriş uğursuz oldu');
  }

  static Future<void> logout() async {
    try {
      await http.post(
        Uri.parse('$baseUrl/auth/logout/'),
        headers: _headers,
      );
    } catch (_) {}
    await setToken(null);
  }

  static Future<AppUser> getProfile() async {
    final res = await http.get(
      Uri.parse('$baseUrl/auth/me/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(utf8.decode(res.bodyBytes));
      return AppUser.fromJson(data);
    }
    throw Exception('Profil məlumatları yüklənə bilmədi');
  }

  static Future<AppUser> updateProfile({
    String? ad,
    String? soyad,
    String? telefon,
    String? sheher,
    File? avatarFile,
  }) async {
    final req = http.MultipartRequest('PATCH', Uri.parse('$baseUrl/auth/me/'));
    req.headers.addAll(_multipartHeaders);
    if (ad != null) req.fields['ad'] = ad;
    if (soyad != null) req.fields['soyad'] = soyad;
    if (telefon != null) req.fields['telefon'] = telefon;
    if (sheher != null) req.fields['sheher'] = sheher;
    if (avatarFile != null) {
      req.files.add(await http.MultipartFile.fromPath('avatar', avatarFile.path));
    }

    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 200) {
      return AppUser.fromJson(data['user']);
    }
    throw Exception(data['error'] ?? 'Profil yenilənə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // CATEGORIES & BANNERS
  // ---------------------------------------------------------------------------

  static Future<List<CategoryModel>> getCategories() async {
    final res = await http.get(
      Uri.parse('$baseUrl/categories/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
      return list
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Kateqoriyalar yüklənə bilmədi');
  }

  static Future<List<BannerModel>> getBanners() async {
    final res = await http.get(
      Uri.parse('$baseUrl/banners/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
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
    final params = <String, String>{
      'page': page.toString(),
    };
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
    final res = await http.get(uri, headers: _headers);
    if (res.statusCode == 200) {
      final data = jsonDecode(utf8.decode(res.bodyBytes));
      final results = (data['results'] as List<dynamic>?)
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
    final res = await http.get(
      Uri.parse('$baseUrl/elanlar/$id/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(utf8.decode(res.bodyBytes));
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
    final req =
        http.MultipartRequest('POST', Uri.parse('$baseUrl/elanlar/create/'));
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

    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    final data = jsonDecode(utf8.decode(res.bodyBytes));
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
  }) async {
    final res = await http.patch(
      Uri.parse('$baseUrl/elanlar/$id/update/'),
      headers: _headers,
      body: jsonEncode({
        'bashliq': bashliq,
        'acaqlama': acaqlama,
        'qiymet': qiymet,
        'sheher': sheher,
        'telefon': telefon,
      }),
    );
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 200) {
      return ElanModel.fromJson(data['elan']);
    }
    throw Exception(data['error'] ?? 'Elan yenilənərkən xəta baş verdi');
  }

  static Future<void> deleteElan(int id) async {
    final res = await http.delete(
      Uri.parse('$baseUrl/elanlar/$id/delete/'),
      headers: _headers,
    );
    if (res.statusCode != 200 && res.statusCode != 204) {
      throw Exception('Elan silinə bilmədi');
    }
  }

  static Future<void> registerElanClick(int id, String nov) async {
    try {
      await http.post(
        Uri.parse('$baseUrl/elanlar/$id/click/$nov/'),
        headers: _headers,
      );
    } catch (_) {}
  }

  static Future<List<ElanModel>> getMyElanlar({String? status}) async {
    final params = <String, String>{};
    if (status != null && status.isNotEmpty) params['status'] = status;
    final uri =
        Uri.parse('$baseUrl/my-elanlar/').replace(queryParameters: params);
    final res = await http.get(uri, headers: _headers);
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
      return list
          .map((e) => ElanModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Elanlarınız yüklənə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // FAVORITES
  // ---------------------------------------------------------------------------

  static Future<List<ElanModel>> getFavorites() async {
    final res = await http.get(
      Uri.parse('$baseUrl/favorites/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
      return list
          .map((e) => ElanModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Seçilmişlər yüklənə bilmədi');
  }

  static Future<bool> toggleFavorite(int elanId) async {
    final res = await http.post(
      Uri.parse('$baseUrl/favorites/toggle/$elanId/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(utf8.decode(res.bodyBytes));
      return data['is_favorit'] ?? false;
    }
    throw Exception('Əməliyyat uğursuz oldu');
  }

  // ---------------------------------------------------------------------------
  // MESSAGES
  // ---------------------------------------------------------------------------

  static Future<List<ConversationModel>> getConversations() async {
    final res = await http.get(
      Uri.parse('$baseUrl/messages/conversations/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
      return list
          .map((e) => ConversationModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Mesajlar yüklənə bilmədi');
  }

  static Future<List<ChatMessageModel>> getChatMessages(int otherUserId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/messages/$otherUserId/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
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
    final res = await http.post(
      Uri.parse('$baseUrl/messages/$otherUserId/'),
      headers: _headers,
      body: jsonEncode({
        'metn': metn,
        'elan_id': ?elanId,
      }),
    );
    if (res.statusCode == 201 || res.statusCode == 200) {
      final data = jsonDecode(utf8.decode(res.bodyBytes));
      return ChatMessageModel.fromJson(data);
    }
    throw Exception('Mesaj göndərilə bilmədi');
  }

  // ---------------------------------------------------------------------------
  // VIP & PAYMENTS
  // ---------------------------------------------------------------------------

  static Future<List<VipPaketModel>> getVipPackages() async {
    final res = await http.get(
      Uri.parse('$baseUrl/vip-packages/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
      return list
          .map((e) => VipPaketModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  static Future<List<BankMelumatModel>> getBankInfo() async {
    final res = await http.get(
      Uri.parse('$baseUrl/bank-info/'),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(utf8.decode(res.bodyBytes)) as List<dynamic>;
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
    required File qebzFile,
    String qeyd = '',
  }) async {
    final req =
        http.MultipartRequest('POST', Uri.parse('$baseUrl/payments/create/'));
    req.headers.addAll(_multipartHeaders);
    req.fields['nov'] = nov;
    req.fields['mebleg'] = mebleg;
    if (elanId != null) req.fields['elan_id'] = elanId.toString();
    if (qeyd.isNotEmpty) req.fields['qeyd'] = qeyd;
    req.files.add(await http.MultipartFile.fromPath('qebz', qebzFile.path));

    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 201 || res.statusCode == 200) {
      return data['message'] ?? 'Ödəniş qəbzi göndərildi!';
    }
    throw Exception(data['error'] ?? 'Ödəniş göndərilə bilmədi');
  }

  static Future<String> activateVipFromBalance({
    required int elanId,
    required String nov,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/elanlar/$elanId/vip/'),
      headers: _headers,
      body: jsonEncode({'nov': nov}),
    );
    final data = jsonDecode(utf8.decode(res.bodyBytes));
    if (res.statusCode == 200 || res.statusCode == 201) {
      return data['message'] ?? 'Elanınız VİP edildi!';
    }
    throw Exception(data['error'] ?? 'VİP aktivləşdirilə bilmədi');
  }
}
