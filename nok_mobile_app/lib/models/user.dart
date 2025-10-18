class User {
  final String _id;
  final String email;
  final String name;

  User({
    required String id,
    required this.email,
    required this.name,
  }) : _id = id;

  String get id => _id;

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['_id'] ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
    );
  }

  Map<String, String> toJson() {
    return {
      '_id': _id,
      'email': email,
      'name': name,
    };
  }
}
