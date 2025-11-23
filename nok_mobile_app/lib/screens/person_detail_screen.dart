import 'package:flutter/material.dart';
import 'package:nok_mobile_app/models/person.dart';

class PersonDetailScreen extends StatelessWidget {
  final Person person;

  const PersonDetailScreen({Key? key, required this.person}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(person.name)),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: 1,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.network(
                person.image,
                fit: BoxFit.cover,
              ),
            ),
          );
        },
      ),
    );
  }
}
