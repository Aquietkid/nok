import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:nok_mobile_app/config.dart';
import 'package:nok_mobile_app/models/person.dart';
import 'package:nok_mobile_app/models/user.dart';
import 'package:nok_mobile_app/services/snackbar_service.dart';
import 'package:nok_mobile_app/services/storage.dart';
import 'package:nok_mobile_app/utils/api_handler.dart';

class ApiService {
  String baseUrl = Config().baseUrl;

  Future<bool?> signIn(String email, String password) async {
    final response = await apiHandler<Future<bool>>(
      () => http.post(
        Uri.parse("$baseUrl/api/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      ),
      (response) async {
        final token = response['data']?['token'];
        final user = response['data']?['user'];
        // also save response.data.user

        if (token != null) {
          await Storage.saveToken(token);
          final _user = User.fromJson(user);
          await Storage.saveUser(_user);
          SnackbarService.show("Login successful 🎉");
          return true;
        } else {
          SnackbarService.show("Login failed: Missing token");
          return false;
        }
      },
    );
    return response.success;
  }

  Future<List<Person>> getAllPerson() async {
    final token = await Storage.getToken();
    List<Person> p = [];

    final response = await apiHandler<List<Person>>(
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

    List<Person>? result = response.data;
    if (result != null) {
      p = result;
    }
    return p;
  }

  Future<bool?> authenticate() async {
    final token = await Storage.getToken();

    final response = await apiHandler<Future<bool>>(
      () => http.get(
        Uri.parse("$baseUrl/api/auth/authenticate"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
      (_data) async {
        final userJson = _data['data']?['user'];
        print(userJson);

        final _user = User.fromJson(userJson);
        await Storage.saveUser(_user);

        return true;
      },
    );
    return response.data;
  }
}
