import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  AppUser? _user;
  bool _isLoading = false;
  bool _initialized = false;

  AppUser? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _user != null && ApiService.isAuthenticated;
  bool get initialized => _initialized;

  Future<void> initialize() async {
    if (_initialized) return;
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.init();
      if (ApiService.isAuthenticated) {
        _user = await ApiService.getProfile();
      }
    } catch (_) {
      await ApiService.setToken(null);
      _user = null;
    } finally {
      _isLoading = false;
      _initialized = true;
      notifyListeners();
    }
  }

  Future<void> login(String usernameOrEmail, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      final data = await ApiService.login(usernameOrEmail, password);
      _user = AppUser.fromJson(data['user']);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> register({
    required String username,
    required String email,
    required String password,
    required String ad,
    required String soyad,
    required String telefon,
    String sheher = 'Bakı',
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      final data = await ApiService.register(
        username: username,
        email: email,
        password: password,
        ad: ad,
        soyad: soyad,
        telefon: telefon,
        sheher: sheher,
      );
      _user = AppUser.fromJson(data['user']);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signInWithGoogle() async {
    _isLoading = true;
    notifyListeners();
    try {
      final googleSignIn = GoogleSignIn(
        scopes: ['email', 'profile'],
        serverClientId:
            '811460264298-gge8uv2mfv7rro7fsi6jhkgfs7i1krht.apps.googleusercontent.com',
      );
      final account = await googleSignIn.signIn();
      if (account == null) {
        throw Exception('Google girişi ləğv edildi');
      }
      final auth = await account.authentication;
      final idToken = auth.idToken;
      if (idToken == null) {
        throw Exception('Google ID Token alına bilmədi');
      }
      final data = await ApiService.googleLogin(idToken);
      _user = AppUser.fromJson(data['user']);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshProfile() async {
    if (!ApiService.isAuthenticated) return;
    try {
      _user = await ApiService.getProfile();
      notifyListeners();
    } catch (_) {}
  }

  Future<void> updateProfile({
    String? ad,
    String? soyad,
    String? telefon,
    String? sheher,
    File? avatarFile,
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      _user = await ApiService.updateProfile(
        ad: ad,
        soyad: soyad,
        telefon: telefon,
        sheher: sheher,
        avatarFile: avatarFile,
      );
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await ApiService.logout();
    _user = null;
    notifyListeners();
  }

  Future<void> deleteAccount({String? password, String? confirm}) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.deleteAccount(password: password, confirm: confirm);
      _user = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
