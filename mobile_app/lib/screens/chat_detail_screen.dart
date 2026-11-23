import 'dart:async';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/moderation_dialogs.dart';

class ChatDetailScreen extends StatefulWidget {
  final int otherUserId;
  final String otherUserName;
  final int? elanId;
  final String? elanTitle;

  const ChatDetailScreen({
    super.key,
    required this.otherUserId,
    required this.otherUserName,
    this.elanId,
    this.elanTitle,
  });

  @override
  State<ChatDetailScreen> createState() => _ChatDetailScreenState();
}

class _ChatDetailScreenState extends State<ChatDetailScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  final _messageCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();

  final List<ChatMessageModel> _messages = [];
  bool _isLoading = true;
  bool _isSending = false;
  bool _fetching = false;
  bool _hasOlder = true;
  bool _loadingOlder = false;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _loadMessages();
    _pollTimer = Timer.periodic(const Duration(seconds: 6), (_) {
      _loadMessages(silent: true);
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _messageCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadMessages({bool silent = false}) async {
    if (_fetching || !mounted || !ApiService.isAuthenticated) return;
    _fetching = true;
    final sessionToken = ApiService.token;
    if (!silent) setState(() => _isLoading = true);
    try {
      final list = await ApiService.getChatMessages(
        widget.otherUserId,
        afterId: _messages.isNotEmpty ? _messages.last.id : null,
      );
      if (!mounted || ApiService.token != sessionToken) return;
      setState(() {
        if (_messages.isEmpty) _hasOlder = list.length == 100;
        final ids = _messages.map((message) => message.id).toSet();
        _messages.addAll(list.where((message) => !ids.contains(message.id)));
        _messages.sort((a, b) => a.id.compareTo(b.id));
        _isLoading = false;
      });
      if (list.isNotEmpty) _scrollToBottom();
    } catch (e) {
      if (mounted && !silent) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Mesajlar yüklənmədi. Yenidən cəhd edin.'),
          ),
        );
      }
    } finally {
      _fetching = false;
    }
  }

  Future<void> _loadOlder() async {
    if (_loadingOlder || _messages.isEmpty) return;
    setState(() => _loadingOlder = true);
    final sessionToken = ApiService.token;
    try {
      final list = await ApiService.getChatMessages(
        widget.otherUserId,
        beforeId: _messages.first.id,
      );
      if (!mounted || ApiService.token != sessionToken) return;
      setState(() {
        final ids = _messages.map((message) => message.id).toSet();
        _messages.insertAll(
          0,
          list.where((message) => !ids.contains(message.id)),
        );
        _hasOlder = list.length == 100;
      });
    } finally {
      if (mounted) setState(() => _loadingOlder = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  String _formatMsgTime(String raw) {
    final dt = DateTime.tryParse(raw)?.toLocal();
    if (dt == null) return raw;
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(dt.hour)}:${two(dt.minute)}';
  }

  Future<void> _sendMessage() async {
    final text = _messageCtrl.text.trim();
    if (text.isEmpty || _isSending) return;

    setState(() => _isSending = true);
    try {
      final msg = await ApiService.sendMessage(
        otherUserId: widget.otherUserId,
        metn: text,
        elanId: widget.elanId,
      );
      if (!mounted) return;
      _messageCtrl.clear();
      setState(() {
        _messages.add(msg);
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  void _showReportDialog() {
    showReportContentDialog(
      context: context,
      title: 'İstifadəçidən şikayət',
      initialReason: 'uygunsuz',
      userId: widget.otherUserId,
      elanId: widget.elanId,
      reasons: const [
        {'key': 'uygunsuz', 'label': 'Uyğunsuz / təhqiramiz mesajlar'},
        {'key': 'spam', 'label': 'Spam və ya reklam'},
        {'key': 'saxta', 'label': 'Fırıldaqçılıq cəhdi'},
        {'key': 'tehdid', 'label': 'Təhdid və ya təqib'},
        {'key': 'diger', 'label': 'Digər'},
      ],
    );
  }

  void _showBlockConfirmation() {
    showBlockUserDialog(
      context: context,
      userId: widget.otherUserId,
      userName: widget.otherUserName,
      onBlocked: () {
        if (mounted) Navigator.pop(context);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentUser = context.watch<AuthProvider>().user;
    final isSystem = widget.otherUserName.toLowerCase().contains('sistem');
    final myInitial = (currentUser != null && currentUser.fullName.isNotEmpty)
        ? currentUser.fullName[0].toUpperCase()
        : 'M';

    return Scaffold(
      backgroundColor: const Color(0xFFF4F8F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 19,
              backgroundColor: _brandLight,
              child: isSystem
                  ? const Icon(
                      Icons.campaign_rounded,
                      color: _brandPrimary,
                      size: 20,
                    )
                  : Text(
                      widget.otherUserName.isNotEmpty
                          ? widget.otherUserName[0].toUpperCase()
                          : 'U',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        color: _brandPrimary,
                        fontSize: 15,
                      ),
                    ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.otherUserName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 15.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    isSystem
                        ? 'Rəsmi Bildiriş'
                        : (widget.elanTitle != null &&
                                widget.elanTitle!.isNotEmpty)
                            ? 'Online • ${widget.elanTitle!}'
                            : 'Online',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 11.5,
                      color: isSystem
                          ? const Color(0xFF007B52)
                          : const Color(0xFF0FA968),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => _loadMessages(),
            icon: const Icon(
              Icons.refresh_rounded,
              color: Color(0xFF0F172A),
              size: 21,
            ),
          ),
          if (!isSystem)
            PopupMenuButton<String>(
              icon: const Icon(
                Icons.more_vert_rounded,
                color: Color(0xFF0F172A),
                size: 21,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              onSelected: (val) {
                if (val == 'report') {
                  _showReportDialog();
                } else if (val == 'block') {
                  _showBlockConfirmation();
                }
              },
              itemBuilder: (ctx) => [
                const PopupMenuItem(
                  value: 'report',
                  child: Row(
                    children: [
                      Icon(
                        Icons.flag_outlined,
                        size: 20,
                        color: Color(0xFFEF4444),
                      ),
                      SizedBox(width: 10),
                      Text('Şikayət et'),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'block',
                  child: Row(
                    children: [
                      Icon(
                        Icons.block_rounded,
                        size: 20,
                        color: Color(0xFF64748B),
                      ),
                      SizedBox(width: 10),
                      Text('İstifadəçini blokla'),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            children: [
              if (_hasOlder && _messages.isNotEmpty)
                TextButton(
                  onPressed: _loadingOlder ? null : _loadOlder,
                  child: Text(
                    _loadingOlder ? 'Yüklənir…' : 'Əvvəlki mesajları yüklə',
                  ),
                ),
              const Divider(height: 1, color: Color(0xFFE2E8F0)),
              Expanded(
                child: _isLoading
                    ? const Center(
                        child: CircularProgressIndicator(color: _brandPrimary),
                      )
                    : _messages.isEmpty
                    ? const Center(
                        child: Text(
                          'Mesaj yazaraq söhbətə başlayın',
                          style: TextStyle(
                            color: Color(0xFF64748B),
                            fontSize: 13.5,
                          ),
                        ),
                      )
                    : ListView.separated(
                        controller: _scrollCtrl,
                        physics: const BouncingScrollPhysics(),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 16,
                        ),
                        itemCount: _messages.length,
                        separatorBuilder: (_, _) =>
                            const SizedBox(height: 14.0),
                        itemBuilder: (context, index) {
                          final msg = _messages[index];
                          final isMine = msg.isMine;
                          return _buildChatTwoMessageRow(
                            msg: msg,
                            isMine: isMine,
                            myInitial: myInitial,
                            myAvatarUrl: currentUser?.profil.avatar,
                          );
                        },
                      ),
              ),
              SafeArea(
                top: false,
                child: Container(
                  margin: const EdgeInsets.symmetric(
                    vertical: 10.0,
                    horizontal: 14.0,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(30.0),
                    border: Border.all(color: const Color(0xFFDCECE5)),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.06),
                        blurRadius: 14,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.symmetric(
                    vertical: 4.0,
                    horizontal: 16.0,
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageCtrl,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => _sendMessage(),
                          style: const TextStyle(
                            fontSize: 14.5,
                            color: Color(0xFF0F172A),
                            fontWeight: FontWeight.w500,
                          ),
                          decoration: const InputDecoration(
                            hintText: 'Mesaj yazın...',
                            hintStyle: TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 14,
                            ),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(
                              vertical: 10.0,
                              horizontal: 4.0,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        width: 40,
                        height: 40,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Color(0xFF0FA968), Color(0xFF007B52)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          padding: EdgeInsets.zero,
                          color: Colors.white,
                          onPressed: _isSending ? null : _sendMessage,
                          icon: _isSending
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.send_rounded, size: 19),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChatTwoMessageRow({
    required ChatMessageModel msg,
    required bool isMine,
    required String myInitial,
    String? myAvatarUrl,
  }) {
    const double radius = 20.0;
    return Row(
      mainAxisAlignment: isMine
          ? MainAxisAlignment.end
          : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: <Widget>[
        if (!isMine) ...[
          CircleAvatar(
            radius: 16.0,
            backgroundColor: _brandLight,
            child: Text(
              widget.otherUserName.isNotEmpty
                  ? widget.otherUserName[0].toUpperCase()
                  : 'U',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w800,
                color: _brandPrimary,
              ),
            ),
          ),
          const SizedBox(width: 6.0),
        ],
        Flexible(
          child: Column(
            crossAxisAlignment: isMine
                ? CrossAxisAlignment.end
                : CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  vertical: 10.0,
                  horizontal: 15.0,
                ),
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.70,
                ),
                decoration: BoxDecoration(
                  color: isMine ? const Color(0xFF007B52) : Colors.white,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(radius),
                    topRight: const Radius.circular(radius),
                    bottomLeft: isMine
                        ? const Radius.circular(radius)
                        : Radius.zero,
                    bottomRight: isMine
                        ? Radius.zero
                        : const Radius.circular(radius),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF0F172A).withValues(alpha: 0.05),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      msg.metn,
                      style: TextStyle(
                        color: isMine ? Colors.white : const Color(0xFF0F172A),
                        fontSize: 14.0,
                        height: 1.38,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 3.0),
                    Icon(
                      Icons.done_all_rounded,
                      size: 13.0,
                      color: isMine
                          ? Colors.white.withValues(alpha: 0.85)
                          : const Color(0xFF0FA968),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 3.0),
              Text(
                _formatMsgTime(msg.yaradildi),
                style: const TextStyle(
                  fontSize: 11.0,
                  color: Color(0xFF64748B),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
        if (isMine) ...[
          const SizedBox(width: 6.0),
          CircleAvatar(
            radius: 16.0,
            backgroundColor: const Color(0xFF0FA968),
            backgroundImage:
                (myAvatarUrl != null && myAvatarUrl.trim().isNotEmpty)
                ? CachedNetworkImageProvider(myAvatarUrl)
                : null,
            child: (myAvatarUrl == null || myAvatarUrl.trim().isEmpty)
                ? Text(
                    myInitial,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  )
                : null,
          ),
        ],
      ],
    );
  }
}
