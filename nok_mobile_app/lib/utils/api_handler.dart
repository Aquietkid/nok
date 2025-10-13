import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:nok_mobile_app/services/snackbar_service.dart';

/// Generic API handler
Future<bool> apiHandler<T>(
  Future<http.Response> Function() apiCall,
  T Function(dynamic data)? onSuccess,
) async {
  try {
    final response = await apiCall();

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final body = jsonDecode(response.body);
      if (onSuccess != null) {
        onSuccess(body);
      }
      return true;
    } else {
      final body = jsonDecode(response.body);
      final message = body['message'] ?? "Something went wrong";
      print("Error: $body");
      SnackbarService.show(message, isError: true);
    }
  } catch (e) {
    SnackbarService.show("Error: $e", isError: true);
  }
  return false;
}
