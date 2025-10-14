import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:nok_mobile_app/config.dart';
import 'package:nok_mobile_app/screens/home_screen.dart';
import 'package:nok_mobile_app/services/snackbar_service.dart';
import 'package:nok_mobile_app/services/storage.dart';
import 'package:nok_mobile_app/utils/api_handler.dart';

class ApiService {
  String baseUrl = Config().baseUrl;

  Future<bool?> signIn(String email, String password) async {
    return await apiHandler<Future<bool>>(
      () => http.post(
        Uri.parse("$baseUrl/api/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      ),
      (response) async {
        final token = response['data']?['token'];

        if (token != null) {
          await Storage.saveToken(token);
          SnackbarService.show("Login successful 🎉");
          return true;
        } else {
          SnackbarService.show("Login failed: Missing token");
          return false;
        }
      },
    );
  }

  Future<List<Person>> getAllPerson() async {
    final token = await Storage.getToken();
    List<Person> p = [];

    List<Person>? result = await apiHandler<List<Person>>(
      () => http.get(
        Uri.parse("$baseUrl/api/person/"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
      (data) {
        final persons =
            (data['data'] as List)
                .map((p) => Person(name: p["name"], image: p["picture"]))
                .toList();
        return persons;
      },
    );

    if (result != null) {
      p = result;
    }
    return p;
  }
}
