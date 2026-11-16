"""Lightweight Web Map & Telemetry Dashboard for SITL / Flight Testing."""

import http.server
import json
import socketserver
import threading
import time
import logging
from core.mavlink_bridge import MAVLinkBridge

logger = logging.getLogger("WebViewer")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>KKRTI Autonomous UAV - Live Ground Station Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html { margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121826; color: #fff; }
    #container { display: flex; flex-direction: column; height: 100vh; }
    #navbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px; background: #1e293b; border-bottom: 2px solid #334155; }
    #nav-title { font-weight: bold; font-size: 1.1rem; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .badge-online { background: #15803d; color: #fff; }
    .badge-offline { background: #b91c1c; color: #fff; }
    .badge-mode { background: #0284c7; color: #fff; }
    #metrics { display: flex; gap: 20px; font-size: 0.9rem; }
    .metric-item { display: flex; flex-direction: column; }
    .metric-label { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; }
    .metric-val { font-weight: bold; color: #f8fafc; font-size: 1.05rem; }
    #map { flex: 1; z-index: 1; }
  </style>
</head>
<body>
  <div id="container">
    <div id="navbar">
      <div id="nav-title">KKRTI UAV Ground Visualizer <span id="link-badge" class="badge badge-offline">CONNECTING</span> <span id="mode-badge" class="badge badge-mode">--</span></div>
      <div id="metrics">
        <div class="metric-item"><span class="metric-label">Alt (AGL)</span><span class="metric-val" id="val-alt">0.0 m</span></div>
        <div class="metric-item"><span class="metric-label">Speed</span><span class="metric-val" id="val-speed">0.0 m/s</span></div>
        <div class="metric-item"><span class="metric-label">Heading</span><span class="metric-val" id="val-yaw">0°</span></div>
        <div class="metric-item"><span class="metric-label">Battery</span><span class="metric-val" id="val-bat">100%</span></div>
        <div class="metric-item"><span class="metric-label">Home Dist</span><span class="metric-val" id="val-dist">0 m</span></div>
      </div>
    </div>
    <div id="map"></div>
  </div>

  <script>
    const map = L.map('map').setView([-7.925500, 110.548500], 17);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let droneMarker = null;
    let homeMarker = null;
    let flightPath = L.polyline([], { color: '#0284c7', weight: 3, opacity: 0.8 }).addTo(map);
    let initialized = false;

    // Drone Icon
    const droneIcon = L.divIcon({
      html: '<div style="width:14px;height:14px;border-radius:50%;background:#38bdf8;border:2px solid #ffffff;box-shadow:0 0 8px #38bdf8;"></div>',
      className: 'drone-div-icon',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const homeIcon = L.divIcon({
      html: '<div style="width:12px;height:12px;background:#e11d48;border:2px solid #ffffff;transform:rotate(45deg);"></div>',
      className: 'home-div-icon',
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    async function updateTelemetry() {
      try {
        const res = await fetch('/api/telemetry');
        const data = await res.json();

        // Update Nav status
        const linkBadge = document.getElementById('link-badge');
        const modeBadge = document.getElementById('mode-badge');
        if (data.link_alive) {
          linkBadge.className = 'badge badge-online';
          linkBadge.innerText = data.armed ? 'ARMED' : 'DISARMED';
        } else {
          linkBadge.className = 'badge badge-offline';
          linkBadge.innerText = 'DISCONNECTED';
        }
        modeBadge.innerText = data.mode || 'N/A';

        // Update metrics
        document.getElementById('val-alt').innerText = data.alt_rel.toFixed(1) + ' m';
        document.getElementById('val-speed').innerText = data.groundspeed.toFixed(1) + ' m/s';
        document.getElementById('val-yaw').innerText = data.yaw.toFixed(0) + '°';
        document.getElementById('val-bat').innerText = data.battery_pct.toFixed(0) + '%';
        document.getElementById('val-dist').innerText = (data.dist_home ? data.dist_home.toFixed(0) : 0) + ' m';

        if (data.lat !== 0 && data.lon !== 0) {
          const latlng = [data.lat, data.lon];
          if (!droneMarker) {
            droneMarker = L.marker(latlng, { icon: droneIcon }).addTo(map).bindPopup('UAV Drone');
          } else {
            droneMarker.setLatLng(latlng);
          }

          // Add to trail
          flightPath.addLatLng(latlng);

          if (!initialized) {
            map.panTo(latlng);
            homeMarker = L.marker(latlng, { icon: homeIcon }).addTo(map).bindPopup('Home Base');
            initialized = true;
          }
        }
      } catch (err) {
        console.error('Fetch error:', err);
      }
    }

    setInterval(updateTelemetry, 500);
  </script>
</body>
</html>
"""


class WebGCSHandler(http.server.BaseHTTPRequestHandler):
    bridge_ref: MAVLinkBridge = None

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/api/telemetry":
            snap = self.bridge_ref.get_snapshot() if self.bridge_ref else None
            dist_h = snap.distance_to_home() if snap else None
            payload = {
                "link_alive": snap.is_link_alive() if snap else False,
                "armed": snap.state.armed if snap else False,
                "mode": snap.state.mode if snap else "OFFLINE",
                "lat": snap.position.lat if snap else 0.0,
                "lon": snap.position.lon if snap else 0.0,
                "alt_rel": snap.position.alt_rel if snap else 0.0,
                "yaw": snap.attitude.yaw if snap else 0.0,
                "groundspeed": snap.velocity.groundspeed if snap else 0.0,
                "battery_pct": snap.battery.percentage if snap else 0.0,
                "dist_home": dist_h
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        # Silence default HTTP server access logs to keep terminal clean
        return


def start_web_viewer(endpoint: str = "udp:127.0.0.1:14550", http_port: int = 8080):
    bridge = MAVLinkBridge(endpoint=endpoint)
    logger.info(f"Connecting web viewer to {endpoint}...")
    bridge.connect()

    WebGCSHandler.bridge_ref = bridge

    server = socketserver.TCPServer(("127.0.0.1", http_port), WebGCSHandler)
    server.allow_reuse_address = True
    print(f"\n=======================================================")
    print(f"[OK] KKRTI Web Ground Station Live on http://127.0.0.1:{http_port}")
    print(f"=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bridge.disconnect()
        server.server_close()


if __name__ == "__main__":
    start_web_viewer()

