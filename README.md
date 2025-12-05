# EduPlatform – Platform Web Pembelajaran Online

Proyek ini adalah platform web pembelajaran online berbasis **Django** yang dirancang modular, mudah dikembangkan, dan memiliki antarmuka yang ramah pengguna (mirip CMS seperti WordPress).

## Fitur Utama

### Untuk Admin / Instruktur

- Dashboard instruktur untuk mengelola kursus.
- Membuat, mengedit, dan menghapus kursus.
- Upload materi (video URL + file materi seperti PDF/dokumen).
- Editor konten WYSIWYG (TinyMCE) untuk materi & deskripsi kursus.
- Manajemen materi (lesson) per kursus.
- Membuat quiz dan ujian (melalui admin Django – soal pilihan ganda).
- Melihat jumlah siswa per kursus (statistik di dashboard).
- Manajemen user, kategori, tag, kursus, quiz, komentar, review via **Django Admin**.

### Untuk Siswa

- Registrasi dan login.
- Browse dan cari kursus.
- Enroll ke kursus.
- Akses materi pembelajaran (konten teks, video URL, file lampiran).
- Mengerjakan quiz (pilihan ganda).
- Tracking progres belajar (persentase penyelesaian materi).
- Sertifikat setelah menyelesaikan kursus (halaman sertifikat + tombol print/PDF).
- Profil pengguna berisi daftar kursus yang diikuti & progres.

### Fitur Tambahan

- Sistem komentar dan diskusi per kursus.
- Rating dan review kursus.
- Notifikasi email (console backend) ketika siswa enroll kursus.
- Desain responsif (Bootstrap 5, mobile-friendly).
- Landing page yang menarik dengan highlight fitur dan kursus terbaru.

## Arsitektur & Struktur Folder

- `manage.py` – entry point Django.
- `online_learning/` – konfigurasi proyek Django (settings, urls, wsgi, asgi).
- `learning/` – aplikasi utama yang memuat:
  - `models.py` – model untuk User, Course, Lesson, Quiz, Enrollment, Comment, Review, Certificate, dll.
  - `views.py` – logika tampilan untuk:
    - landing page
    - daftar kursus
    - detail kursus
    - halaman belajar kursus
    - quiz
    - sertifikat
    - dashboard instruktur
    - CRUD kursus & materi
    - profil pengguna, registrasi
  - `forms.py` – form untuk registrasi, kursus, materi, komentar, review.
  - `urls.py` – routing khusus aplikasi `learning`.
  - `templates/learning/` – template HTML (berbasis Bootstrap).
  - `templates/registration/` – template login/register/logout.
  - `static/learning/` – file CSS tambahan.

Database default menggunakan **SQLite** untuk kemudahan pengembangan, dan bisa diganti ke PostgreSQL/MySQL sesuai kebutuhan.

## Cara Menjalankan Secara Lokal

1. **Clone repo & masuk ke folder proyek**

   ```bash
   git clone <url-repo-anda>
   cd <folder-proyek>
   ```

2. **Buat dan aktifkan virtual environment (disarankan)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # di Linux / macOS
   venv\Scripts\activate     # di Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Buat migrasi dan migrasikan database**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Buat superuser (akun admin)**

   ```bash
   python manage.py createsuperuser
   ```

   Akun ini digunakan untuk mengakses `/admin/` (Django Admin) untuk mengelola semua data (user, kursus, quiz, dll).

6. **Jalankan server pengembangan**

   ```bash
   python manage.py runserver
   ```

7. **Akses aplikasi**

   - Landing page / website utama: `http://127.0.0.1:8000/`
   - Login / logout:
     - Login: `/accounts/login/`
     - Logout: `/accounts/logout/`
   - Registrasi (siswa / instruktur): `/register/`
   - Dashboard instruktur: `/instructor/dashboard/`
   - Admin (full manajemen konten & user): `/admin/`

## Alur Penggunaan

### Sebagai Admin / Instruktur

1. Login ke `/admin/` dengan akun superuser.
2. Tambahkan kategori (`Category`) dan tag (`Tag`) bila diperlukan.
3. Tambahkan user instruktur atau ubah peran user menjadi `Instruktur`.
4. Buat kursus (`Course`), materi (`Lesson`), dan quiz (`Quiz`, `Question`, `Choice`) di admin atau melalui dashboard instruktur:
   - Dashboard instruktur: kelola kursus dan materi.
   - Form deskripsi/materi mendukung editor WYSIWYG (TinyMCE).
5. Publish kursus (`is_published = True`) agar muncul di listing.

### Sebagai Siswa

1. Registrasi di `/register/`, pilih peran **Siswa**.
2. Login dan jelajahi kursus di `/courses/` atau dari beranda.
3. Enroll ke kursus dan mulai belajar:
   - Materi berupa konten teks + video URL + file (PDF/dokumen).
   - Tandai materi sebagai selesai untuk meningkatkan progres.
4. Kerjakan quiz yang tersedia di halaman belajar kursus.
5. Setelah menyelesaikan semua materi dan lulus ujian akhir (quiz dengan `is_final=True`), sertifikat akan terbit dan dapat diakses di halaman kursus (`Lihat Sertifikat`).

## Kustomisasi & Pengembangan Lanjutan

Karena ini berbasis Django dan terstruktur modular, Anda dapat dengan mudah:

- Menambahkan jenis materi baru (misalnya tugas / assignment).
- Mengintegrasikan payment gateway (untuk kursus berbayar).
- Mengganti backend email dari console ke SMTP / layanan email pihak ketiga.
- Menambahkan API (REST) dengan Django REST Framework.
- Mengganti tampilan front-end menjadi SPA (React/Vue) bila dibutuhkan.

Jika Anda ingin, saya bisa membantu menambahkan:
- API mobile (REST/GraphQL),
- Modul pembayaran,
- Atau tema UI tambahan agar tampilan lebih mirip WordPress premium.