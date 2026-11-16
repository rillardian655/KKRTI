"""KKRTI - Autonomous Flight Simulation & Mission Controller (Main CLI)."""

import sys
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from simulator.sitl_runner import SITLRunner
from missions import (
    basic_takeoff_land,
    waypoint_survey,
    payload_drop,
    geofence_failsafe
)
from tools.live_hud import run_hud
from tools.web_viewer import start_web_viewer

console = Console()


def show_banner():
    banner = """[bold cyan]
  _  ______  ____ _____ ___   _   _    ___     ______ 
 | |/ /  _ \|  _ \_   _|_ _| | | | |  / \ \   / / ___|
 | ' /| |_) | |_) || |  | |  | | | | / _ \ \ / /\___ \\
 | . \|  _ <|  _ < | |  | |  | |_| |/ ___ \ V /  ___) |
 |_|\_\_| \_\_| \_\|_| |___|  \___//_/   \_\\_/  |____/ 
    [/bold cyan][bold yellow]Autonomous Flight Simulation & Mission Controller[/bold yellow]
    [dim]ArduPilot SITL / MAVLink / Autonomous Waypoint Navigation[/dim]
"""
    console.print(banner)


def run_mission_wrapper(mission_num: int, endpoint: str):
    console.print(f"[bold green]Starting Mission #{mission_num}...[/bold green]")
    if mission_num == 1:
        basic_takeoff_land.run_mission(endpoint=endpoint)
    elif mission_num == 2:
        waypoint_survey.run_mission(endpoint=endpoint)
    elif mission_num == 3:
        payload_drop.run_mission(endpoint=endpoint)
    elif mission_num == 4:
        geofence_failsafe.run_mission(endpoint=endpoint)
    else:
        console.print(f"[bold red]Unknown mission number: {mission_num}[/bold red]")


def interactive_menu(endpoint: str):
    show_banner()
    sim_runner = None

    while True:
        console.print(Panel("""[bold]Select an action:[/bold]
 [1] Launch Built-in MAVLink SITL Simulator (Background)
 [2] Run Mission 01: Basic Takeoff, Hover & Land
 [3] Run Mission 02: Autonomous Waypoint Survey & Camera Trigger
 [4] Run Mission 03: Precision Payload Drop (KRTI VTOL/TD)
 [5] Run Mission 04: Geofence Enforcement & Autonomous Failsafe
 [6] Open Live Terminal HUD (Real-time Telemetry)
 [7] Start Web Ground Station Map (http://127.0.0.1:8080)
 [0] Exit
""", title="[bold cyan]KKRTI Mission Control Menu[/bold cyan]"))

        choice = Prompt.ask("Enter option", default="1")

        if choice == "1":
            if sim_runner is None:
                sim_runner = SITLRunner(mode="mock", port=14550)
                sim_runner.start()
                console.print("[bold green][OK] SITL Simulator is running on udp:127.0.0.1:14550[/bold green]")
            else:
                console.print("[yellow]SITL Simulator is already running![/yellow]")

        elif choice == "2":
            run_mission_wrapper(1, endpoint)
        elif choice == "3":
            run_mission_wrapper(2, endpoint)
        elif choice == "4":
            run_mission_wrapper(3, endpoint)
        elif choice == "5":
            run_mission_wrapper(4, endpoint)
        elif choice == "6":
            run_hud(endpoint)
        elif choice == "7":
            start_web_viewer(endpoint)
        elif choice == "0":
            if sim_runner:
                sim_runner.stop()
            console.print("[cyan]Exiting KKRTI. Fly safe![/cyan]")
            break
        else:
            console.print("[red]Invalid choice![/red]")


def main():
    parser = argparse.ArgumentParser(description="KKRTI Drone Mission & Simulation Suite")
    parser.add_argument("command", nargs="?", choices=["sim", "run", "hud", "web"], help="Direct command to run")
    parser.add_argument("arg", nargs="?", help="Mission number (1-4) if command is 'run'")
    parser.add_argument("--endpoint", default="udp:127.0.0.1:14550", help="MAVLink connection endpoint")
    args = parser.parse_args()

    if args.command == "sim":
        show_banner()
        console.print(f"[bold green]Starting SITL simulator on {args.endpoint}... (Ctrl+C to stop)[/bold green]")
        runner = SITLRunner(mode="mock", port=14550)
        runner.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            runner.stop()
            console.print("[yellow]SITL Stopped.[/yellow]")

    elif args.command == "run":
        if not args.arg:
            console.print("[red]Error: Specify mission number (1-4). Example: python main.py run 3[/red]")
            sys.exit(1)
        run_mission_wrapper(int(args.arg), args.endpoint)

    elif args.command == "hud":
        run_hud(args.endpoint)

    elif args.command == "web":
        start_web_viewer(args.endpoint)

    else:
        interactive_menu(args.endpoint)


if __name__ == "__main__":
    main()

