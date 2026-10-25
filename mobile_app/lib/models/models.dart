class UserProfile {
  final String ad;
  final String soyad;
  final String telefon;
  final String sheher;
  final String? avatar;
  final double balans;

  UserProfile({
    required this.ad,
    required this.soyad,
    required this.telefon,
    required this.sheher,
    this.avatar,
    required this.balans,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      ad: json['ad'] ?? '',
      soyad: json['soyad'] ?? '',
      telefon: json['telefon'] ?? '',
      sheher: json['sheher'] ?? 'Bakı',
      avatar: json['avatar'],
      balans: double.tryParse(json['balans']?.toString() ?? '0') ?? 0.0,
    );
  }
}

class AppUser {
  final int id;
  final String username;
  final String email;
  final String firstName;
  final String lastName;
  final UserProfile profil;
  final bool hasPassword;

  AppUser({
    required this.id,
    required this.username,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.profil,
    this.hasPassword = true,
  });

  String get fullName {
    final pName = '${profil.ad} ${profil.soyad}'.trim();
    if (pName.isNotEmpty) return pName;
    final uName = '$firstName $lastName'.trim();
    if (uName.isNotEmpty) return uName;
    return username;
  }

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      profil: UserProfile.fromJson(json['profil'] ?? {}),
      hasPassword: json['has_password'] ?? true,
    );
  }
}

class CategoryModel {
  final int id;
  final String ad;
  final String slug;
  final String ikon;
  final int elanSayi;
  final List<CategoryModel> altKateqoriyalar;

  CategoryModel({
    required this.id,
    required this.ad,
    required this.slug,
    required this.ikon,
    required this.elanSayi,
    this.altKateqoriyalar = const [],
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    final subs =
        (json['alt_kateqoriyalar'] as List<dynamic>?)
            ?.map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    return CategoryModel(
      id: json['id'] ?? 0,
      ad: json['ad'] ?? '',
      slug: json['slug'] ?? '',
      ikon: json['ikon'] ?? '',
      elanSayi: json['elan_sayi'] ?? 0,
      altKateqoriyalar: subs,
    );
  }
}

class ElanShekilModel {
  final int id;
  final String? shekilUrl;
  final bool esas;

  ElanShekilModel({required this.id, this.shekilUrl, required this.esas});

  factory ElanShekilModel.fromJson(Map<String, dynamic> json) {
    return ElanShekilModel(
      id: json['id'] ?? 0,
      shekilUrl: json['shekil_url'],
      esas: json['esas'] ?? false,
    );
  }
}

class ElanModel {
  final int id;
  final String nomre;
  final String bashliq;
  final String? acaqlama;
  final double? qiymet;
  final String status;
  final String vipStatus;
  final String sheher;
  final String telefon;
  final int baxishSayi;
  final int zengSayi;
  final int wpSayi;
  final String yaradildi;
  final String? esasShekil;
  final String? kategoriAd;
  final String? kategoriSlug;
  final int? kategoriId;
  final List<ElanShekilModel> shekillar;
  final Map<String, dynamic>? istifadeciInfo;
  bool isFavorit;
  final bool isOwner;

  ElanModel({
    required this.id,
    required this.nomre,
    required this.bashliq,
    this.acaqlama,
    this.qiymet,
    required this.status,
    required this.vipStatus,
    required this.sheher,
    required this.telefon,
    required this.baxishSayi,
    this.zengSayi = 0,
    this.wpSayi = 0,
    required this.yaradildi,
    this.esasShekil,
    this.kategoriAd,
    this.kategoriSlug,
    this.kategoriId,
    this.shekillar = const [],
    this.istifadeciInfo,
    this.isFavorit = false,
    this.isOwner = false,
  });

  bool get isVip => vipStatus == 'vip' || vipStatus == 'super_vip';
  bool get isSuperVip => vipStatus == 'super_vip';

  String get formattedPrice {
    if (qiymet == null || qiymet == 0) return 'Razılaşma yolu ilə';
    if (qiymet! == qiymet!.roundToDouble()) {
      return '${qiymet!.toInt()} ₼';
    }
    return '${qiymet!.toStringAsFixed(2)} ₼';
  }

  List<String> get allImageUrls {
    final urls = shekillar
        .map((s) => s.shekilUrl)
        .whereType<String>()
        .where((u) => u.isNotEmpty)
        .toList();
    if (urls.isEmpty && esasShekil != null && esasShekil!.isNotEmpty) {
      urls.add(esasShekil!);
    }
    return urls;
  }

  factory ElanModel.fromJson(Map<String, dynamic> json) {
    final imgs =
        (json['shekillar'] as List<dynamic>?)
            ?.map((e) => ElanShekilModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    String? mainImg = json['esas_shekil'];
    if (mainImg == null && imgs.isNotEmpty) {
      final primary = imgs.where((i) => i.esas).firstOrNull ?? imgs.first;
      mainImg = primary.shekilUrl;
    }

    return ElanModel(
      id: json['id'] ?? 0,
      nomre: json['nomre'] ?? '',
      bashliq: json['bashliq'] ?? '',
      acaqlama: json['acaqlama'],
      qiymet: json['qiymet'] != null
          ? double.tryParse(json['qiymet'].toString())
          : null,
      status: json['status'] ?? 'aktiv',
      vipStatus: json['vip_status'] ?? 'normal',
      sheher: json['sheher'] ?? 'Bakı',
      telefon: json['telefon'] ?? '',
      baxishSayi: json['baxish_sayi'] ?? 0,
      zengSayi: json['zeng_sayi'] ?? 0,
      wpSayi: json['wp_sayi'] ?? 0,
      yaradildi: json['yaradildi'] ?? '',
      esasShekil: mainImg,
      kategoriAd: json['kategori_ad'],
      kategoriSlug: json['kategori_slug'],
      kategoriId: json['kategori'] is int ? json['kategori'] : null,
      shekillar: imgs,
      istifadeciInfo: json['istifadeci_info'] as Map<String, dynamic>?,
      isFavorit: json['is_favorit'] ?? false,
      isOwner: json['is_owner'] ?? false,
    );
  }
}

class ConversationModel {
  final int lastMessageId;
  final int userId;
  final String username;
  final String adSoyad;
  final String? avatar;
  final String lastMessage;
  final String lastMessageTime;
  final int unreadCount;
  final int? elanId;

  ConversationModel({
    this.lastMessageId = 0,
    required this.userId,
    required this.username,
    required this.adSoyad,
    this.avatar,
    required this.lastMessage,
    required this.lastMessageTime,
    required this.unreadCount,
    this.elanId,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      lastMessageId: json['last_message_id'] ?? 0,
      userId: json['user_id'] ?? 0,
      username: json['username'] ?? '',
      adSoyad: json['ad_soyad'] ?? '',
      avatar: json['avatar'],
      lastMessage: json['last_message'] ?? '',
      lastMessageTime: json['last_message_time'] ?? '',
      unreadCount: json['unread_count'] ?? 0,
      elanId: json['elan_id'],
    );
  }
}

class ChatMessageModel {
  final int id;
  final int gonderici;
  final String gondericiUsername;
  final String gondericiAd;
  final int alici;
  final int? elanId;
  final String metn;
  final bool oxundu;
  final String yaradildi;
  final bool isMine;

  ChatMessageModel({
    required this.id,
    required this.gonderici,
    required this.gondericiUsername,
    required this.gondericiAd,
    required this.alici,
    this.elanId,
    required this.metn,
    required this.oxundu,
    required this.yaradildi,
    required this.isMine,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    return ChatMessageModel(
      id: json['id'] ?? 0,
      gonderici: json['gonderici'] ?? 0,
      gondericiUsername: json['gonderici_username'] ?? '',
      gondericiAd: json['gonderici_ad'] ?? '',
      alici: json['alici'] ?? 0,
      elanId: json['elan'],
      metn: json['metn'] ?? '',
      oxundu: json['oxundu'] ?? false,
      yaradildi: json['yaradildi'] ?? '',
      isMine: json['is_mine'] ?? false,
    );
  }
}

class VipPaketModel {
  final int id;
  final String nov;
  final String ad;
  final double qiymet;
  final int muddetGun;
  final List<String> ustunlukler;

  VipPaketModel({
    required this.id,
    required this.nov,
    required this.ad,
    required this.qiymet,
    required this.muddetGun,
    required this.ustunlukler,
  });

  factory VipPaketModel.fromJson(Map<String, dynamic> json) {
    return VipPaketModel(
      id: json['id'] ?? 0,
      nov: json['nov'] ?? 'vip',
      ad: json['ad'] ?? '',
      qiymet: double.tryParse(json['qiymet']?.toString() ?? '0') ?? 0.0,
      muddetGun: json['muddet_gun'] ?? 10,
      ustunlukler:
          (json['ustunlukler'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class BankMelumatModel {
  final int id;
  final String bankAdi;
  final String kartNomresi;
  final String kartSahibi;

  BankMelumatModel({
    required this.id,
    required this.bankAdi,
    required this.kartNomresi,
    required this.kartSahibi,
  });

  factory BankMelumatModel.fromJson(Map<String, dynamic> json) {
    return BankMelumatModel(
      id: json['id'] ?? 0,
      bankAdi: json['bank_adi'] ?? 'ABB Bank',
      kartNomresi: json['kart_nomresi'] ?? '',
      kartSahibi: json['kart_sahibi'] ?? 'Prousta MMC',
    );
  }
}

class BannerModel {
  final int id;
  final String movqe;
  final String bashliq;
  final String link;
  final String? shekilUrl;

  BannerModel({
    required this.id,
    required this.movqe,
    required this.bashliq,
    required this.link,
    this.shekilUrl,
  });

  factory BannerModel.fromJson(Map<String, dynamic> json) {
    return BannerModel(
      id: json['id'] ?? 0,
      movqe: json['movqe'] ?? 'ust',
      bashliq: json['bashliq'] ?? '',
      link: json['link'] ?? '',
      shekilUrl: json['shekil_url'],
    );
  }
}
