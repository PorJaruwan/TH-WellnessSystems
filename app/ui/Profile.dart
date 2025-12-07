import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: ProfileScreen(),
    );
  }
}

// วิดเจ็ตหลักสำหรับหน้าจอ UI
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // 1. ตั้งค่าสีพื้นหลังหลักเป็นสีเทาเข้ม
      backgroundColor: Colors.grey.shade600,
      body: Stack(
        children: [
          // 2. ใช้วิดเจ็ต ClipPath เพื่อตัด Container ให้เป็นรูปทรงที่ต้องการ
          ClipPath(
            // 3. เรียกใช้ CustomClipper ที่เราสร้างขึ้น
            clipper: ProfileShapeClipper(),
            child: Container(
              // 4. ตั้งค่าสีของรูปทรงโปรไฟล์เป็นสีเทาอ่อน
              color: Colors.grey.shade300,
            ),
          ),
        ],
      ),
    );
  }
}

// คลาสสำหรับสร้าง Path (เส้นทาง) ของรูปทรงโปรไฟล์
class ProfileShapeClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    // สร้าง Path เพื่อวาดรูปทรง
    // จุดต่างๆ จะอ้างอิงจากความกว้าง (size.width) และความสูง (size.height)
    // ทำให้รูปทรงสามารถปรับขนาดตามหน้าจอได้ (responsive)
    Path path = Path();

    // เริ่มวาดจากมุมซ้ายล่างของพื้นที่วาด
    path.moveTo(0, size.height * 0.7);

    // วาดเส้นโค้งส่วน "ไหล่" ขึ้นไป
    path.quadraticBezierTo(
      size.width * 0.1, // Control point X
      size.height * 0.9, // Control point Y
      size.width * 0.25, // End point X
      size.height * 0.6, // End point Y
    );

    // วาดเส้นโค้งส่วน "ศีรษะ"
    path.cubicTo(
      size.width * 0.35, // Control point 1 X
      size.height * 0.2, // Control point 1 Y
      size.width * 0.75, // Control point 2 X
      size.height * 0.2, // Control point 2 Y
      size.width * 0.6, // End point X
      size.height * 0.65, // End point Y
    );

    // วาดเส้นโค้งส่วน "คอ" กลับมายังขอบซ้าย
    path.quadraticBezierTo(
      size.width * 0.5, // Control point X
      size.height * 0.95, // Control point Y
      0, // End point X (กลับมาที่ขอบซ้าย)
      size.height, // End point Y (สุดขอบล่าง)
    );

    // ปิด Path เพื่อให้เป็นรูปทรงที่สมบูรณ์
    path.close();

    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) {
    // กำหนดเป็น false เนื่องจากรูปทรงของเราเป็นแบบคงที่ ไม่มีการเปลี่ยนแปลง
    return false;
  }
}
