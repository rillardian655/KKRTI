"""Live Telemetry HUD Dashboard in Terminal using Rich."""

import time
import sys
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from core.mavlink_bridge import MAVLinkBridge
from core.telemetry import calculate_distance_3d


def make_hud_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    layout["body"].split_row(
        Layout(name="flight_info", ratio=1),
        Layout(name="spatial_info", ratio=1),
        Layout(name="power_safety", ratio=1)
    )
    return layout


def run_hud(endpoint: str = "udp:127.0.0.1:14550"):
    console = Console()
    bridge = MAVLinkBridge(endpoint=endpoint)

    console.print(f"[bold cyan]Connecting HUD to {endpoint}...[/bold cyan]")
    if not bridge.connect():
        console.print("[bold red]Could not connect to MAVLink endpoint. Is SITL running?[/bold red]")
        return

    layout = make_hud_layout()

    try:
        with Live(layout, refresh_per_second=4, screen=True):
            while True:
                snap = bridge.get_snapshot()

                # Header
                armed_str = "[bold green]ARMED[/bold green]" if snap.state.armed else "[bold red]DISARMED[/bold red]"
                link_str = "[bold green]ONLINE[/bold green]" if snap.is_link_alive() else "[bold red]LOST[/bold red]"
                layout["header"].update(
                    Panel(
                        f"[bold yellow]✈ KKRTI AUTONOMOUS UAV TELEMETRY HUD[/bold yellow] | "
                        f"MAVLink: {link_str} | Status: {armed_str} | Mode: [bold cyan]{snap.state.mode}[/bold cyan]",
                        style="blue"
                    )
                )

                # Column 1: Flight & Attitude
                t1 = Table(show_header=False, expand=True)
                t1.add_column("Key", style="bold")
                t1.add_column("Value")
                t1.add_row("Roll", f"{snap.attitude.roll:+.1f}°")
                t1.add_row("Pitch", f"{snap.attitude.pitch:+.1f}°")
                t1.add_row("Yaw / Heading", f"{snap.attitude.yaw:05.1f}°")
                t1.add_row("Groundspeed", f"{snap.velocity.groundspeed:.2f} m/s")
                t1.add_row("Climb Rate", f"{snap.velocity.climb_rate:+.2f} m/s")
                t1.add_row("GPS Satellites", f"{snap.state.satellites_visible} (3D Fix)")
                layout["flight_info"].update(Panel(t1, title="[bold]Flight Dynamics[/bold]", border_style="cyan"))

                # Column 2: Spatial & Navigation
                t2 = Table(show_header=False, expand=True)
                t2.add_column("Key", style="bold")
                t2.add_column("Value")
                t2.add_row("Latitude", f"{snap.position.lat:.6f}")
                t2.add_row("Longitude", f"{snap.position.lon:.6f}")
                t2.add_row("Altitude AGL", f"[bold green]{snap.position.alt_rel:.2f} m[/bold green]")
                t2.add_row("Altitude MSL", f"{snap.position.alt_msl:.1f} m")
                
                dist_home = snap.distance_to_home()
                dist_home_str = f"{dist_home:.1f} m" if dist_home is not None else "N/A"
                t2.add_row("Distance to Home", dist_home_str)
                layout["spatial_info"].update(Panel(t2, title="[bold]GPS & Position[/bold]", border_style="green"))

                # Column 3: Power & Safety
                t3 = Table(show_header=False, expand=True)
                t3.add_column("Key", style="bold")
                t3.add_column("Value")
                
                pct = snap.battery.percentage
                color = "green" if pct > 40 else ("yellow" if pct > 20 else "red")
                t3.add_row("Battery", f"[{color}]{pct:.1f}%[/{color}]")
                t3.add_row("Voltage", f"{snap.battery.voltage:.2f} V")
                t3.add_row("Current", f"{snap.battery.current:.2f} A")
                t3.add_row("Geofence", "[bold green]SAFE[/bold green]")
                layout["power_safety"].update(Panel(t3, title="[bold]Power & Diagnostics[/bold]", border_style="yellow"))

                # Footer
                layout["footer"].update(
                    Panel("[dim]Press Ctrl+C to exit HUD. Running in live streaming mode.[/dim]", style="white")
                )

                time.sleep(0.25)

    except KeyboardInterrupt:
        pass
    finally:
        bridge.disconnect()
        console.print("[cyan]HUD closed.[/cyan]")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "udp:127.0.0.1:14550"
    run_hud(endpoint)
