import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:nok_mobile_app/models/person.dart';
import 'package:nok_mobile_app/services/api_service.dart';
import 'home_screen.dart';

class AddPersonScreen extends StatefulWidget {
  const AddPersonScreen({Key? key}) : super(key: key);

  @override
  State<AddPersonScreen> createState() => _AddPersonScreenState();
}

class _AddPersonScreenState extends State<AddPersonScreen> {
  final _nameController = TextEditingController();
  final List<File?> _images = List.filled(imageCountPerPerson, null);

  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;

  Future<void> _pickImage(int index) async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: ImageSource.gallery,
      );
      if (pickedFile != null) {
        setState(() {
          _images[index] = File(pickedFile.path);
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error picking image: $e")));
    }
  }

  // void _savePerson() {
  //   if (_nameController.text.isEmpty || _images.any((img) => img == null)) {
  //     ScaffoldMessenger.of(
  //       context,
  //     ).showSnackBar(const SnackBar(content: Text("Please fill all fields")));
  //     return;
  //   }

  //   final newPerson = Person(
  //     name: _nameController.text,
  //     // For now, just storing file paths. Later you’ll replace this with uploaded URLs.
  //     image: "_images.first()",
  //   );

  //   Navigator.pop(context, newPerson);
  // }

  Future<void> _savePerson() async {
    if (_nameController.text.isEmpty || _images.any((img) => img == null)) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Please fill all fields")));
      return;
    }

    final apiService = ApiService();
    setState(() {
      _isLoading = true;
    });
    final newPerson = await apiService.addPerson(_nameController.text, _images);

    if (newPerson != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Person saved successfully!")),
      );
      Navigator.pop(context, newPerson);
    }
    setState(() {
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Add Person")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: "Person Name",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            for (int i = 0; i < imageCountPerPerson; i++) ...[
              GestureDetector(
                onTap: () => _pickImage(i),
                child: Container(
                  height: 120,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                    color: Colors.grey.shade200,
                  ),
                  child:
                      _images[i] != null
                          ? Image.file(_images[i]!, fit: BoxFit.cover)
                          : const Center(child: Text("Tap to select image")),
                ),
              ),
              const SizedBox(height: 16),
            ],
            ElevatedButton(
              onPressed: _isLoading ? null : _savePerson,
              child:
                  _isLoading
                      ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                      : const Text("Save"),
            ),
          ],
        ),
      ),
    );
  }
}
