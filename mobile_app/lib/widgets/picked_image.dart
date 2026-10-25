import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

/// Bytes-based previews work on web as well as Android and iOS.
class PickedImage extends StatelessWidget {
  final XFile file;
  final double? width;
  final double? height;
  final BoxFit fit;
  const PickedImage(
    this.file, {
    super.key,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) => FutureBuilder<Uint8List>(
    future: file.readAsBytes(),
    builder: (context, snapshot) => snapshot.hasData
        ? Image.memory(snapshot.data!, width: width, height: height, fit: fit)
        : SizedBox(
            width: width,
            height: height,
            child: snapshot.hasError
                ? const Icon(Icons.broken_image)
                : const Center(child: CircularProgressIndicator()),
          ),
  );
}
