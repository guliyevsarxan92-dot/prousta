import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/elan_provider.dart';
import '../widgets/prousta_wordmark.dart';

class CategoriesScreen extends StatefulWidget {
  final VoidCallback? onCategorySelected;

  const CategoriesScreen({
    super.key,
    this.onCategorySelected,
  });

  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  String _searchQuery = '';

  static const List<Map<String, String>> _fallbackServices = [
    {'ad': 'Elektrik xidmətləri', 'slug': 'elektrik'},
    {'ad': 'Santexnik xidmətləri', 'slug': 'santexnik'},
    {'ad': 'Təmir və tikinti', 'slug': 'temir-ve-tikinti'},
    {'ad': 'Mebel ustası', 'slug': 'mebel'},
    {'ad': 'Məişət texnikası təmiri', 'slug': 'meiset-texnikasi'},
    {'ad': 'Rəngsaz və divar kağızı', 'slug': 'rengsaz'},
    {'ad': 'Təmizlik xidmətləri', 'slug': 'temizlik'},
    {'ad': 'Kondisioner və kombi', 'slug': 'kondisioner'},
    {'ad': 'Avto təmir və qaraj', 'slug': 'avto'},
    {'ad': 'Yükdaşıma və köçürmə', 'slug': 'yukdasima'},
    {'ad': 'Bağban və həyət işləri', 'slug': 'bagban'},
    {'ad': 'Digər xidmətlər', 'slug': 'diger'},
  ];

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  IconData _getServiceIcon(String text) {
    final lower = text.toLowerCase();
    if (lower.contains('elektrik') || lower.contains('işıq')) {
      return Icons.electrical_services_rounded;
    }
    if (lower.contains('santexnik') ||
        lower.contains('su ') ||
        lower.contains('kanalizasiya') ||
        lower.contains('kombi')) {
      return Icons.plumbing_rounded;
    }
    if (lower.contains('təmir') ||
        lower.contains('temir') ||
        lower.contains('tikinti') ||
        lower.contains('usta')) {
      return Icons.handyman_rounded;
    }
    if (lower.contains('mebel') || lower.contains('qapı')) {
      return Icons.chair_rounded;
    }
    if (lower.contains('kondisioner') ||
        lower.contains('məişət') ||
        lower.contains('meiset') ||
        lower.contains('texnika') ||
        lower.contains('soyuducu')) {
      return Icons.ac_unit_rounded;
    }
    if (lower.contains('rəng') ||
        lower.contains('reng') ||
        lower.contains('boya') ||
        lower.contains('divar') ||
        lower.contains('oboy')) {
      return Icons.format_paint_rounded;
    }
    if (lower.contains('təmizlik') || lower.contains('temizlik')) {
      return Icons.cleaning_services_rounded;
    }
    if (lower.contains('avto') ||
        lower.contains('maşın') ||
        lower.contains('qaraj')) {
      return Icons.car_repair_rounded;
    }
    if (lower.contains('yük') ||
        lower.contains('yuk') ||
        lower.contains('köçürmə')) {
      return Icons.local_shipping_rounded;
    }
    if (lower.contains('bağ') || lower.contains('bag')) {
      return Icons.yard_rounded;
    }
    return Icons.home_repair_service_rounded;
  }

  void _selectCategory(
    ElanProvider elanProvider, {
    String? slug,
    String? name,
    bool clear = false,
  }) {
    if (clear) {
      elanProvider.setFilters(clearCategory: true);
    } else {
      elanProvider.setFilters(
        categorySlug: slug,
        categoryName: name,
      );
    }
    widget.onCategorySelected?.call();
    if (Navigator.canPop(context)) {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final elanProvider = context.watch<ElanProvider>();
    final rawCategories = elanProvider.categories;
    final categories = rawCategories.isNotEmpty
        ? rawCategories
        : _fallbackServices
            .asMap()
            .entries
            .map(
              (entry) => CategoryModel(
                id: entry.key + 1,
                ad: entry.value['ad']!,
                slug: entry.value['slug']!,
                ikon: '',
                elanSayi: 0,
              ),
            )
            .toList();

    final query = _searchQuery.trim().toLowerCase();
    final filteredCategories = query.isEmpty
        ? categories
        : categories.where((cat) {
            final matchMain = cat.ad.toLowerCase().contains(query);
            final matchSub = cat.altKateqoriyalar.any(
              (sub) => sub.ad.toLowerCase().contains(query),
            );
            return matchMain || matchSub;
          }).toList();

    final selectedSlug = elanProvider.selectedCategorySlug;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F8F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 2,
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            color: Color(0xFF0F172A),
            size: 19,
          ),
        ),
        titleSpacing: 0,
        title: const Row(
          children: [
            ProustaWordmark(fontSize: 20),
            SizedBox(width: 10),
            Text(
              '•  Ümumi Xidmətlər',
              style: TextStyle(
                fontSize: 15.5,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
          ],
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            children: [
              // Top Search Bar for Services
              Container(
                color: Colors.white,
                padding: const EdgeInsets.fromLTRB(16, 6, 16, 14),
                child: Container(
                  height: 46,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF4F8F6),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFFDCECE5)),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 14),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.search_rounded,
                        color: Color(0xFF007B52),
                        size: 20,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _searchCtrl,
                          onChanged: (val) {
                            setState(() => _searchQuery = val);
                          },
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF0F172A),
                          ),
                          decoration: const InputDecoration(
                            hintText: 'Xidmət və ya kateqoriya axtar...',
                            border: InputBorder.none,
                            isDense: true,
                            hintStyle: TextStyle(
                              fontSize: 13.5,
                              color: Color(0xFF94A3B8),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                      if (_searchQuery.isNotEmpty)
                        GestureDetector(
                          onTap: () {
                            _searchCtrl.clear();
                            setState(() => _searchQuery = '');
                          },
                          child: const Icon(
                            Icons.close_rounded,
                            size: 18,
                            color: Color(0xFF94A3B8),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const Divider(height: 1, color: Color(0xFFE2E8F0)),

              // All Services List & Grid
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 32),
                  children: [
                    // "Bütün xidmətlər" (Show all listings) Card
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF0A4D34),
                            Color(0xFF007B52),
                            Color(0xFF0FA968),
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color:
                                const Color(0xFF007B52).withValues(alpha: 0.24),
                            blurRadius: 12,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(16),
                          onTap: () =>
                              _selectCategory(elanProvider, clear: true),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 14,
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    color: Colors.white.withValues(alpha: 0.18),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: const Icon(
                                    Icons.grid_view_rounded,
                                    color: Colors.white,
                                    size: 22,
                                  ),
                                ),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Bütün Xidmətlər',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 16,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        'Bütün usta elanlarını və xidmət sahələrini göstər',
                                        style: TextStyle(
                                          color: Colors.white
                                              .withValues(alpha: 0.85),
                                          fontSize: 12,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(
                                  Icons.arrow_forward_ios_rounded,
                                  color: Colors.white,
                                  size: 16,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),

                    const Padding(
                      padding: EdgeInsets.only(left: 4, bottom: 10),
                      child: Text(
                        'Xidmət sahələri',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ),

                    if (filteredCategories.isEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 40),
                        child: Center(
                          child: Text(
                            'Uyğun xidmət tapılmadı',
                            style: TextStyle(
                              color: Color(0xFF64748B),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      )
                    else
                      ...filteredCategories.map((cat) {
                        final isSelected = selectedSlug == cat.slug;
                        final icon = _getServiceIcon('${cat.ad} ${cat.slug}');
                        final hasSubs = cat.altKateqoriyalar.isNotEmpty;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(
                              color: isSelected
                                  ? const Color(0xFF007B52)
                                  : const Color(0xFFE2E8F0),
                              width: isSelected ? 1.5 : 1.0,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF0F172A)
                                    .withValues(alpha: 0.06),
                                blurRadius: 10,
                                offset: const Offset(0, 3),
                              ),
                            ],
                          ),
                          child: Column(
                            children: [
                              ListTile(
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                onTap: () => _selectCategory(
                                  elanProvider,
                                  slug: cat.slug,
                                  name: cat.ad,
                                ),
                                contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 14,
                                  vertical: 4,
                                ),
                                leading: Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? const Color(0xFF007B52)
                                        : const Color(0xFFEAF6F1),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Icon(
                                    icon,
                                    color: isSelected
                                        ? Colors.white
                                        : const Color(0xFF007B52),
                                    size: 22,
                                  ),
                                ),
                                title: Text(
                                  cat.ad,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: isSelected
                                        ? FontWeight.w800
                                        : FontWeight.w700,
                                    color: const Color(0xFF0F172A),
                                  ),
                                ),
                                subtitle: hasSubs
                                    ? Text(
                                        '${cat.altKateqoriyalar.length} alt xidmət sahəsi',
                                        style: const TextStyle(
                                          fontSize: 12,
                                          color: Color(0xFF64748B),
                                          fontWeight: FontWeight.w500,
                                        ),
                                      )
                                    : null,
                                trailing: const Icon(
                                  Icons.chevron_right_rounded,
                                  color: Color(0xFF94A3B8),
                                ),
                              ),
                              if (hasSubs) ...[
                                const Divider(
                                  height: 1,
                                  indent: 14,
                                  endIndent: 14,
                                  color: Color(0xFFF1F5F9),
                                ),
                                Padding(
                                  padding:
                                      const EdgeInsets.fromLTRB(12, 8, 12, 10),
                                  child: Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: cat.altKateqoriyalar.map((sub) {
                                      final isSubSelected =
                                          selectedSlug == sub.slug;
                                      return InkWell(
                                        borderRadius: BorderRadius.circular(10),
                                        onTap: () => _selectCategory(
                                          elanProvider,
                                          slug: sub.slug,
                                          name: sub.ad,
                                        ),
                                        child: Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 6,
                                          ),
                                          decoration: BoxDecoration(
                                            color: isSubSelected
                                                ? const Color(0xFF007B52)
                                                : const Color(0xFFF4FAF7),
                                            borderRadius:
                                                BorderRadius.circular(10),
                                            border: Border.all(
                                              color: isSubSelected
                                                  ? const Color(0xFF007B52)
                                                  : const Color(0xFFDCECE5),
                                            ),
                                          ),
                                          child: Text(
                                            sub.ad,
                                            style: TextStyle(
                                              fontSize: 12,
                                              fontWeight: FontWeight.w700,
                                              color: isSubSelected
                                                  ? Colors.white
                                                  : const Color(0xFF0F172A),
                                            ),
                                          ),
                                        ),
                                      );
                                    }).toList(),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        );
                      }),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
