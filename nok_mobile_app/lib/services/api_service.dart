import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:nok_mobile_app/config.dart';
import 'package:nok_mobile_app/services/snackbar_service.dart';
import 'package:nok_mobile_app/utils/api_handler.dart';

class ApiService {
  Future<bool> signIn(String email, String password) async {
    String baseUrl = Config().baseUrl;
    return await apiHandler(
      () => http.post(
        Uri.parse("$baseUrl/api/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      ),
      (data) {
        SnackbarService.show("Login successful");
      },
    );
  }
}
