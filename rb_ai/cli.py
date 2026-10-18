#!/usr/bin/env python3
"""
RB.AI - Command Line Interface & Assistant Daemon
Usage:
  python cli.py                     # Start interactive RB.AI terminal chat
  python cli.py --server            # Start the HTTP/WebSocket API server for Flutter
  python cli.py --voice             # Continuous voice listener with 'Hey RB' wake phrase
  python cli.py --chat "Hey RB..."  # Run single prompt through Gemini & automation
"""

import sys
import argparse
from core.assistant import RBAssistant
from core.config import load_config
from core.automation import automation
from core.server import RBServer
from core.sub_agents import sub_agents
from core.database import db

def banner():
    print("""
\033[1;36m
  ██████╗ ██████╗       █████╗ ██╗
  ██╔══██╗██╔══██╗     ██╔══██╗██║
  ██████╔╝██████╔╝     ███████║██║
  ██╔══██╗██╔══██╗     ██╔══██║██║
  ██║  ██║██████╔╝     ██║  ██║██║
\033[0m
  \033[1;32mVoice & Multimodal AI Assistant (Termux + Python + Flutter)\033[0m
  \033[1;33mWake Phrase:\033[0m "Hey RB"
    """)

def interactive_chat(assistant: RBAssistant):
    banner()
    print("Type your message (or 'exit' / 'quit' to stop).")
    print("Example: 'Hey RB, turn on the flashlight and check battery status'\n")

    while True:
        try:
            user_input = input("\033[1;34mYou > \033[0m").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            # Check Autonomous Sub-Agent Intent Router first
            routed = sub_agents.route_and_process_intent(user_input)
            if routed and routed.get("routed"):
                agent_name = routed.get("agent", "RB Agent")
                response_text = routed.get("response", "")
                db.add_chat(sender="user", message=user_input, agent_type=routed.get("tag", "general"))
                db.add_chat(sender="assistant", message=response_text, agent_type=routed.get("tag", "general"))
                print(f"\033[1;36m[{agent_name} Executed]\033[0m")
                print(f"\033[1;32mRB.AI >\033[0m {response_text}\n")
                continue

            print("\033[1;33m[RB.AI is thinking...]\033[0m")
            res = assistant.process_input(raw_text=user_input, is_voice=False)

            # Display any tools called
            for tool in res.get("tool_calls", []):
                print(f"\033[1;35m⚙️ [Action Executed]: {tool.get('tool')}\033[0m -> {tool.get('result')}")

            print(f"\033[1;32mRB.AI >\033[0m {res.get('response')}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting RB.AI.")
            break

def continuous_voice(assistant: RBAssistant):
    banner()
    print("🎙️ Starting Continuous Voice Listener with 'Hey RB' detection...")
    print("Listening for wake phrase 'Hey RB' via Termux STT...\n")

    while True:
        try:
            print("\033[1;30m[Listening for 'Hey RB'...] (Press Ctrl+C to stop)\033[0m")
            heard_text = assistant.audio.listen_termux_stt()
            if heard_text:
                print(f"Heard: '{heard_text}'")
                if assistant.audio.contains_wake_word(heard_text):
                    print("✨ Wake phrase 'Hey RB' detected!")
                    res = assistant.process_input(raw_text=heard_text, is_voice=True)
                    print(f"RB.AI > {res.get('response')}")
        except KeyboardInterrupt:
            print("\nStopped voice listener.")
            break
        except Exception as e:
            print(f"Voice loop error: {e}")
            break

def main():
    parser = argparse.ArgumentParser(description="RB.AI Assistant")
    parser.add_argument("--server", action="store_true", help="Start RB.AI API server for Flutter client")
    parser.add_argument("--voice", action="store_true", help="Start continuous 'Hey RB' voice listening loop")
    parser.add_argument("--chat", type=str, help="Process a single query and exit")
    parser.add_argument("--battery", action="store_true", help="Check battery via Termux API")
    parser.add_argument("--torch", choices=["on", "off"], help="Control flashlight")
    parser.add_argument("--port", type=int, default=8765, help="Port for server")

    args = parser.parse_args()
    config = load_config()
    if args.port:
        config.PORT = args.port

    assistant = RBAssistant(config)

    if args.battery:
        print(automation.get_battery_status())
        return

    if args.torch:
        res = automation.set_torch(args.torch == "on")
        print(f"Torch {args.torch}: {res}")
        return

    if args.chat:
        res = assistant.process_input(raw_text=args.chat)
        print(f"RB.AI: {res.get('response')}")
        return

    if args.server:
        server = RBServer(assistant, host=config.HOST, port=config.PORT)
        server.run()
        return

    if args.voice:
        continuous_voice(assistant)
        return

    # Default to interactive chat
    interactive_chat(assistant)

if __name__ == "__main__":
    main()
