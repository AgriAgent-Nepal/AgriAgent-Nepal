from __future__ import annotations

import argparse
import json

from .orchestrator import AgriAgent


def _serve(host: str, port: int) -> None:
    import uvicorn

    uvicorn.run("agriagent.api:app", host=host, port=port, reload=False)


def _chat(debug: bool) -> None:
    agent = AgriAgent()
    print("AgriAgent Nepal — type 'exit' to quit")
    while True:
        try:
            message = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not message or message.lower() in {"exit", "quit"}:
            break
        result = agent.chat(message, debug=debug)
        print(f"\nAgriAgent > {result['answer']}")
        if result.get("citations"):
            print("\nSources:")
            for src in result["citations"]:
                print(f"- {src['title']}: {src['url']}")
        if debug:
            print("\nDebug:")
            print(json.dumps(result.get("debug", {}), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="agriagent", description="AgriAgent Nepal")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Run the web chat and API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=8000, type=int)

    chat = sub.add_parser("chat", help="Run an interactive terminal chat")
    chat.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    if args.command == "serve":
        _serve(args.host, args.port)
    else:
        _chat(getattr(args, "debug", False))


if __name__ == "__main__":
    main()
