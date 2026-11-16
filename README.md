# KKRTI Autonomous Flight Controller and SITL Simulation

Framework kendali terbang otonom dan simulasi misi berbasis protokol MAVLink, dirancang untuk keperluan riset UAV dan skenario kompetisi Kontes Robot Terbang Indonesia (KRTI).

---

## Latar Belakang

Kendala yang paling sering dihadapi saat mengembangkan sistem otonom untuk drone adalah ketergantungan pada drone fisik atau simulator resmi (ArduPilot SITL + Gazebo) yang ukurannya sangat besar, proses build yang rumit, dan kebutuhan resource laptop yang tinggi saat riset lapangan. Seringkali pengembang hanya ingin menguji logika navigasi waypoint, mekanisme pelepasan payload, atau respon sistem failsafe tanpa harus menyalakan drone sungguhan atau menunggu build simulator puluhan gigabyte selesai.

Repositori ini menyediakan solusi ringkas:
- Abstraksi kendali terbang Python yang bersih dan modular di atas `pymavlink`.
- Simulator bawaan (mock SITL) berbasis kinematis 6-DOF yang langsung bisa diajak komunikasi via paket MAVLink standar di port UDP lokal tanpa dependensi eksternal.
- Sistem keselamatan penerbangan (geofencing poligon 2D dan failsafe dinamis).
- Dukungan langsung untuk beralih dari simulasi ke flight controller fisik (Pixhawk, Cube, Pixracer) hanya dengan mengganti parameter endpoint koneksi.

---

## Arsitektur Proyek

Sistem dibangun dengan pemisahan tugas yang jelas agar mudah dimodifikasi:

```
KKRTI/
├── config/
│   ├── default_config.json          # Parameter terbang, kecepatan, dan koordinat home base
│   └── geofence_sample.json         # Definisi poligon zona terbang aman
├── core/
│   ├── drone_controller.py          # Antarmuka kendali utama (takeoff, goto, drop, land, RTL)
│   ├── mavlink_bridge.py            # Layer parsing paket MAVLink multi-threaded
│   ├── telemetry.py                 # Struktur data posisi, attitude, kalkulasi jarak Haversine
│   ├── geofence_manager.py          # Validasi poligon (Ray-Casting) dan batas elevasi
│   ├── mission_planner.py           # Generator lintasan survey (lawnmower grid)
│   └── failsafe_manager.py          # Pengecekan status baterai, sinyal, dan pelanggaran batas
├── simulator/
│   ├── sitl_mock_server.py          # Engine simulator internal (emulasi ArduCopter di UDP 14550)
│   └── sitl_runner.py               # Handler untuk menjalankan simulator internal atau sim_vehicle.py
├── missions/
│   ├── mission_01_takeoff_land.py   # Misi dasar: arming, lepas landas, hover, mendarat
│   ├── mission_02_waypoint_survey.py# Misi pemetaan: jelajah waypoint berurutan dan trigger kamera
│   ├── mission_03_payload_drop.py   # Misi KRTI VTOL/TD: navigasi titik sasaran, servo drop, dan RTL
│   └── mission_04_geofence_failsafe.py # Pengujian intersepsi failsafe saat drone keluar perimeter
├── tools/
│   ├── live_hud.py                  # Dashboard telemetri konsol real-time
│   └── web_viewer.py                # Visualisasi posisi drone pada peta Leaflet di browser
├── main.py                          # Antarmuka CLI interaktif
├── requirements.txt
└── README.md
```

---

## Fitur Teknis

### 1. Mock SITL Berbasis Protokol MAVLink Nyata
Simulator internal bukan sekadar mock data di memori. Simulator ini membuka socket UDP lokal dan bertukar paket biner MAVLink sungguhan (Heartbeat 1 Hz, Global Position 10 Hz, Attitude 10 Hz, System Status 2 Hz, Home Position, serta menangani Command ACK). Artinya, kamu juga bisa menghubungkan QGroundControl atau Mission Planner ke simulator ini secara bersamaan.

### 2. Controller Siap Pakai
Tidak perlu menulis byte packet MAVLink manual setiap kali ingin menggerakkan drone. Class `DroneController` menyediakan method tingkat tinggi:
```python
from core.drone_controller import DroneController

drone = DroneController(endpoint="udp:127.0.0.1:14550")
if drone.connect():
    drone.takeoff(altitude=15.0)
    drone.goto_location(lat=-7.924900, lon=110.549000, alt_rel=15.0, speed=8.0)
    drone.wait_for_waypoint(target_lat=-7.924900, target_lon=110.549000, target_alt=15.0)
    drone.return_to_launch()
```

### 3. Logika Safety dan Failsafe Berlapis
Keselamatan adalah prioritas utama dalam penerbangan otonom. Modul `FailsafeManager` terus mengevaluasi:
- Heartbeat Timeout: Jika link komunikasi terputus lebih dari batas toleransi (default 4 detik), mode langsung dipaksa Return-To-Launch (RTL).
- Threshold Baterai: Menangani peringatan level rendah (memicu RTL) dan level kritis (memicu autonomous land darurat di posisi saat itu).
- Geofence Breach: Menggunakan algoritma ray-casting untuk memastikan koordinat drone selalu berada di dalam poligon yang ditentukan. Jika batas terlewati, sistem langsung mengambil alih kendali dan membatalkan misi keluar.

### 4. Skenario Misi Spesifik KRTI
- Payload Drop: Mengarahkan drone ke zona sasaran, menurunkan ketinggian ke elevasi pelepasan, melakukan penahanan posisi (loiter), memicu aktuasi servo mekanik (PWM command pada channel output yang ditentukan), lalu kembali naik dan pulang ke pangkalan.
- Grid Survey: Membangun jalur sapuan (*lawnmower pattern*) untuk pemetaan area luas secara otomatis lengkap dengan event trigger kamera di tiap titik belok.

---

## Cara Penggunaan

### Persiapan Lingkungan

Pastikan Python 3 sudah terpasang di sistem kamu. Disarankan menggunakan virtual environment:

```bash
git clone https://github.com/rillardian655/KKRTI.git
cd KKRTI

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Menjalankan Lewat Menu Interaktif

Jalankan perintah berikut:
```bash
python main.py
```

Kamu akan melihat tampilan menu di terminal:
```
Select an action:
 [1] Launch Built-in MAVLink SITL Simulator (Background)
 [2] Run Mission 01: Basic Takeoff, Hover & Land
 [3] Run Mission 02: Autonomous Waypoint Survey & Camera Trigger
 [4] Run Mission 03: Precision Payload Drop (KRTI VTOL/TD)
 [5] Run Mission 04: Geofence Enforcement & Autonomous Failsafe
 [6] Open Live Terminal HUD (Real-time Telemetry)
 [7] Start Web Ground Station Map (http://127.0.0.1:8080)
 [0] Exit
```

Pilih opsi 1 terlebih dahulu untuk menyalakan simulator, lalu jalankan salah satu misi (misal opsi 4 untuk payload drop).

### Menjalankan Langsung via Parameter CLI

Bisa juga dijalankan per proses di terminal terpisah:

1. Jalankan simulator:
   ```bash
   python main.py sim
   ```

2. Jalankan misi tertentu (contoh misi 3 untuk payload drop):
   ```bash
   python main.py run 3
   ```

3. Buka dashboard monitor konsol:
   ```bash
   python main.py hud
   ```

4. Buka ground station peta di browser:
   ```bash
   python main.py web
   # Akses http://127.0.0.1:8080 melalui web browser
   ```

---

## Penerapan ke Drone Fisik di Lapangan

Kode ini tidak terkunci hanya untuk simulasi. Ketika siap uji terbang sungguhan dengan wahana:

1. Sambungkan modul telemetri radio darat (misalnya SiK Radio 433/915 MHz, RFD900, atau koneksi USB langsung ke Pixhawk) ke laptop.
2. Periksa port serial yang terdeteksi di Linux:
   ```bash
   ls /dev/ttyUSB*
   ```
3. Arahkan endpoint controller ke port tersebut dengan menyertakan baud rate:
   ```bash
   python main.py run 3 --endpoint /dev/ttyUSB0
   ```

Sistem akan otomatis mendeteksi autopilot asli, membaca koordinat GPS dari sensor onboard, dan mengeksekusi misi sesuai parameter yang ditentukan.
