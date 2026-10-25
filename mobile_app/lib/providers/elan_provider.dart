import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class ElanProvider extends ChangeNotifier {
  List<ElanModel> _elanlar = [];
  List<CategoryModel> _categories = [];
  List<BannerModel> _banners = [];
  List<ElanModel> _favorites = [];

  bool _isLoading = false;
  bool _isLoadingMore = false;
  bool _hasNext = false;
  int _currentPage = 1;

  int _requestGeneration = 0;
  int? _userId;

  void bindUser(int? userId) {
    if (_userId == userId) return;
    _userId = userId;
    _requestGeneration++;
    _favorites = [];
    _elanlar = [];
    _isLoadingMore = false;
    _hasNext = false;
    Future.microtask(() => fetchElanlar());
  }

  String _searchQuery = '';
  String? _selectedCategorySlug;
  String? _selectedCategoryName;
  String _selectedCity = 'Bütün Azərbaycan';

  List<ElanModel> get elanlar => _elanlar;
  List<CategoryModel> get categories => _categories;
  List<BannerModel> get banners => _banners;
  List<ElanModel> get favorites => _favorites;
  bool get isLoading => _isLoading;
  bool get isLoadingMore => _isLoadingMore;
  bool get hasNext => _hasNext;

  String get searchQuery => _searchQuery;
  String? get selectedCategorySlug => _selectedCategorySlug;
  String? get selectedCategoryName => _selectedCategoryName;
  String get selectedCity => _selectedCity;

  Future<void> loadInitialData() async {
    await Future.wait([
      fetchElanlar(),
      ApiService.getCategories()
          .then((value) {
            _categories = value;
          })
          .catchError((Object e) {
            debugPrint('$e');
          }),
      ApiService.getBanners()
          .then((value) {
            _banners = value;
          })
          .catchError((Object e) {
            debugPrint('$e');
          }),
    ]);
    notifyListeners();
  }

  Future<void> fetchElanlar({bool reset = true}) async {
    final generation = reset ? ++_requestGeneration : _requestGeneration;
    if (reset) {
      _isLoadingMore = false;
      _isLoading = true;
      _currentPage = 1;
      notifyListeners();
    } else {
      if (_isLoading || _isLoadingMore || !_hasNext) return;
      _isLoadingMore = true;
      notifyListeners();
    }

    try {
      final pageToFetch = reset ? 1 : _currentPage + 1;
      final data = await ApiService.getElanlar(
        page: pageToFetch,
        query: _searchQuery,
        kategoriSlug: _selectedCategorySlug,
        seher: _selectedCity,
      );
      if (generation != _requestGeneration) return;
      final newItems = data['results'] as List<ElanModel>;
      if (reset) {
        _elanlar = newItems;
      } else {
        _elanlar.addAll(newItems);
      }
      _hasNext = data['hasNext'] as bool;
      _currentPage = pageToFetch;
    } catch (e) {
      debugPrint('Error fetching elanlar: $e');
    } finally {
      if (generation == _requestGeneration) {
        _isLoading = false;
        _isLoadingMore = false;
        notifyListeners();
      }
    }
  }

  void setFilters({
    String? query,
    String? categorySlug,
    String? categoryName,
    String? city,
    bool clearCategory = false,
  }) {
    if (query != null) _searchQuery = query;
    if (clearCategory) {
      _selectedCategorySlug = null;
      _selectedCategoryName = null;
    } else if (categorySlug != null) {
      _selectedCategorySlug = categorySlug;
      _selectedCategoryName = categoryName;
    }
    if (city != null) _selectedCity = city;
    fetchElanlar(reset: true);
  }

  void resetFilters() {
    _searchQuery = '';
    _selectedCategorySlug = null;
    _selectedCategoryName = null;
    _selectedCity = 'Bütün Azərbaycan';
    fetchElanlar(reset: true);
  }

  Future<void> loadFavorites() async {
    if (!ApiService.isAuthenticated) return;
    final userId = _userId;
    try {
      final result = await ApiService.getFavorites();
      if (_userId != userId) return;
      _favorites = result;
      notifyListeners();
    } catch (_) {}
  }

  Future<bool> toggleFavorite(int elanId) async {
    final isFav = await ApiService.toggleFavorite(elanId);
    for (final e in _elanlar) {
      if (e.id == elanId) e.isFavorit = isFav;
    }
    await loadFavorites();
    notifyListeners();
    return isFav;
  }
}
