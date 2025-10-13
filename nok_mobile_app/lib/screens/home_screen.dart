import 'package:flutter/material.dart';
import 'package:nok_mobile_app/services/api_service.dart';
import 'person_detail_screen.dart';
import 'add_person_screen.dart';

const int imageCountPerPerson = 3;

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class Person {
  final String name;
  final String image;

  Person({required this.name, required this.image});
}

class _HomeScreenState extends State<HomeScreen> {
  List<Person> persons = [];

  void _addPerson(Person person) {
    setState(() {
      // persons.add(person);
    });
  }

  void fetchData() async {
    final fetchedPersons = await ApiService().getAllPerson();
    setState(() {
      persons = fetchedPersons;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Persons")),
      body: GridView.builder(
        padding: const EdgeInsets.all(12),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2, // 2 items per row
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: persons.length,
        itemBuilder: (context, index) {
          final person = persons[index];
          return GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => PersonDetailScreen(person: person),
                ),
              );
            },
            child: Card(
              clipBehavior: Clip.antiAlias,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Stack(
                children: [
                  Image.network(
                    person.image,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                  ),
                  Container(
                    alignment: Alignment.bottomCenter,
                    padding: const EdgeInsets.all(6),
                    color: Colors.black54,
                    child: Text(
                      person.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final newPerson = await Navigator.push<Person?>(
            context,
            MaterialPageRoute(builder: (_) => const AddPersonScreen()),
          );
          if (newPerson != null) {
            _addPerson(newPerson);
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
