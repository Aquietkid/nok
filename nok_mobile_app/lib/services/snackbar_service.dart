import 'package:flutter/material.dart';
import 'package:nok_mobile_app/main.dart';

class SnackbarService {
  static void show(String message, {bool isError = false}) {
    rootScaffoldMessengerKey.currentState?.showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }
}
