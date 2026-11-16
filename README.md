# ✈️ KKRTI - Autonomous UAV Flight Controller & SITL Simulation Suite

> **Sistem Kontrol Terbang Otonom, Navigasi Misi Waypoint, dan Simulator MAVLink SITL untuk Kontes Robot Terbang Indonesia (KRTI) & Riset Drone.**

Proyek ini dibangun untuk mengendalikan drone/UAV secara otonom melalui protokol MAVLink (kompatibel penuh dengan **ArduPilot / PX4 / Pixhawk**), dilengkapi simulator fisika kinematis built-in (SITL), sistem *failsafe* & *geofence enforcement*, dashboard terminal HUD, serta Web Ground Station Map berbasis Leaflet.

---

## 🌟 Fitur Utama

1. **High-Level Autonomous Flight Controller (`core/drone_controller.py`)**:
   - `arm()` / `disarm()`, `set_mode()`, `takeoff(altitude)`, `goto_location(lat, lon, alt, speed)`.
   - `trigger_payload_servo(ch, pwm)` untuk mekanisme pelepasan payload KRTI.
   - `return_to_launch()` dan `land()` otomatis.
2. **Built-in Lightweight MAVLink SITL Server (`simulator/sitl_mock_server.py`)**:
   - Simulator 6-DOF kinematis mandiri tanpa perlu instalasi ArduPilot/Gazebo 20GB.
   - Emulasi streaming telemetri riil: `HEARTBEAT`, `ATTITUDE`, `GLOBAL_POSITION_INT`, `SYS_STATUS`, `GPS_RAW_INT`, dan `HOME_POSITION`.
   - Mendukung koneksi dari Mission Planner, QGroundControl, atau script Python pada port UDP `14550`.
3. **Geofencing & Safety Failsafe (`core/geofence_manager.py` & `failsafe_manager.py`)**:
   - Validasi batas poligon 2D (Ray-Casting Algorithm), batas elevasi relatif (min/max), serta radius silinder dari Home.
   - Deteksi otomatis pelanggaran batas wilayah, baterai kritis, dan kehilangan sinyal telemetri (*heartbeat timeout*) dengan intervensi langsung memicu *Emergency RTL*.
4. **Misi Terbang Siap Pakai (`missions/`)**:
   - `mission_01_takeoff_land.py`: Lepas landas otonom, *hover hold*, dan pendaratan halus.
   - `mission_02_waypoint_survey.py`: Misi pemetaan udara (*grid survey*) dengan simulasi *camera shutter trigger*.
   - `mission_03_payload_drop.py`: Skenario KRTI VTOL / TD — terbang ke koordinat sasaran, stabilisasi di atas target, buka servo payload drop, lalu kembali ke home (RTL).
   - `mission_04_geofence_failsafe.py`: Demonstrasi intersepsi otomatis saat drone diperintahkan keluar dari zona aman.
5. **Real-time Monitoring Tools (`tools/`)**:
   - **Terminal HUD (`tools/live_hud.py`)**: Dashboard konsol interaktif berbasis `rich` menampilkan dinamika terbang, koordinat GPS, kompas yaw, dan status daya.
   - **Web Ground Station (`tools/web_viewer.py`)**: Peta satelit real-time berbasis Leaflet.js di browser (`http://127.0.0.1:8080`).

---

## 📁 Struktur Direktori

```
KKRTI/
├── config/
│   ├── default_config.json      # Parameter default koneksi, kecepatan, dan koordinat arena KRTI (Lanud Gading)
│   └── geofence_sample.json     # Titik poligon batas arena penerbangan
├── core/
│   ├── drone_controller.py      # Abstraksi kendali terbang tingkat tinggi
│   ├── mavlink_bridge.py        # Adapter komunikasi MAVLink (UDP / TCP / Serial)
│   ├── telemetry.py             # Struktur data telemetri dan fungsi kalkulasi geospatial (Haversine)
│   ├── geofence_manager.py      # Engine deteksi poligon dan radius batas terbang
│   ├── mission_planner.py       # Generator jalur pencarian (*lawnmower grid*) & sequencer waypoint
│   └── failsafe_manager.py      # Pengawas keselamatan baterai, link, dan batas wilayah
├── simulator/
│   ├── sitl_mock_server.py      # MAVLink SITL physics simulator (UDP 14550)
│   └── sitl_runner.py           # Launcher simulator (mock maupun ardupilot sim_vehicle)
├── missions/
│   ├── mission_01_takeoff_land.py
│   ├── mission_02_waypoint_survey.py
│   ├── mission_03_payload_drop.py
│   └── mission_04_geofence_failsafe.py
├── tools/
│   ├── live_hud.py              # Dashboard terminal telemetri
│   └── web_viewer.py            # Peta visualizer web Leaflet
├── main.py                      # Interactive CLI entrypoint
├── requirements.txt
└── README.md
```

---

## 🚀 Panduan Memulai Cepat

### 1. Prasyarat & Instalasi
Clone repository dan aktifkan virtual environment:

```bash
git clone https://github.com/rillardian655/KKRTI.git
cd KKRTI

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Menjalankan Menu Interaktif
Cukup jalankan satu perintah:

```bash
python main.py
```

Menu interaktif akan muncul:
```
 [1] 🛸 Launch Built-in MAVLink SITL Simulator
 [2] 🛫 Run Mission 01: Basic Takeoff, Hover & Land
 [3] 🗺️  Run Mission 02: Autonomous Waypoint Survey & Camera Trigger
 [4] 🎯 Run Mission 03: Precision Payload Drop (KRTI VTOL/TD)
 [5] 🛡️  Run Mission 04: Geofence Enforcement & Autonomous Failsafe
 [6] 📊 Open Live Terminal HUD (Real-time Telemetry)
 [7] 🌐 Start Web Ground Station Map (http://127.0.0.1:8080)
 [0] ❌ Exit
```

### 3. Menjalankan Langsung via Command Line

* **Jalankan SITL Simulator di Terminal 1:**
  ```bash
  python main.py sim
  ```

* **Jalankan Misi Payload Drop (KRTI) di Terminal 2:**
  ```bash
  python main.py run 3
  ```

* **Buka Terminal HUD Telemetri di Terminal 3:**
  ```bash
  python main.py hud
  ```

* **Buka Peta Web Visualizer di Browser:**
  ```bash
  python main.py web
  # Buka http://127.0.0.1:8080 di browser
  ```

---

## 📡 Menghubungkan ke Drone Fisik / Pixhawk

Untuk mengontrol drone nyata di lapangan:
1. Hubungkan telemetri radio (SiK Radio / RFD900 / ESP32 WiFi / USB Pixhawk) ke laptop.
2. Cek port serial device (misal `/dev/ttyUSB0` pada baud rate 57600).
3. Jalankan misi dengan flag endpoint:
   ```bash
   python main.py run 3 --endpoint /dev/ttyUSB0
   ```

---

## 🛡️ Lisensi & Kontribusi
Dikembangkan untuk riset otonom UAV dan tim robotika KRTI. Kontribusi dan pengembangan algoritma baru sangat terbuka!
