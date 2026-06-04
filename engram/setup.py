#!/usr/bin/env python3
"""
engram setup helper — verifica configuración del MCP y conectividad con Pinecone/Gemini.
Uso: python3 setup.py [--check | --configure | --test-search "query"]
"""

import argparse
import json
import os
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
MCP_NAME = "engram"


def load_settings():
    if not SETTINGS_PATH.exists():
        return {}
    with open(SETTINGS_PATH) as f:
        return json.load(f)


def save_settings(settings: dict):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)


def check_config():
    settings = load_settings()
    mcp_servers = settings.get("mcpServers", {})

    if MCP_NAME not in mcp_servers:
        print(f"[ERROR] El MCP '{MCP_NAME}' no está configurado en {SETTINGS_PATH}")
        print("Ejecuta: python3 setup.py --configure")
        return False

    engram_cfg = mcp_servers[MCP_NAME]
    env = engram_cfg.get("env", {})
    missing = []

    for key in ["PINECONE_API_KEY", "PINECONE_INDEX", "GEMINI_API_KEY"]:
        if not env.get(key):
            missing.append(key)

    if missing:
        print(f"[ERROR] Faltan variables de entorno: {', '.join(missing)}")
        return False

    print("[OK] Configuración de engram encontrada.")
    print(f"     Índice Pinecone: {env['PINECONE_INDEX']}")
    print(f"     Gemini API Key:  {'*' * 8}{env['GEMINI_API_KEY'][-4:]}")
    return True


def configure():
    print("=== Configuración de engram ===\n")
    pinecone_key = input("PINECONE_API_KEY: ").strip()
    pinecone_index = input("PINECONE_INDEX (nombre del índice): ").strip()
    gemini_key = input("GEMINI_API_KEY: ").strip()

    if not all([pinecone_key, pinecone_index, gemini_key]):
        print("[ERROR] Todos los campos son obligatorios.")
        sys.exit(1)

    settings = load_settings()
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    settings["mcpServers"][MCP_NAME] = {
        "command": "npx",
        "args": ["-y", "@openclaw/engram-mcp"],
        "env": {
            "PINECONE_API_KEY": pinecone_key,
            "PINECONE_INDEX": pinecone_index,
            "GEMINI_API_KEY": gemini_key,
        },
    }

    save_settings(settings)
    print(f"\n[OK] Configuración guardada en {SETTINGS_PATH}")
    print("[!]  Reinicia Claude Code para que los cambios surtan efecto.")
    print("\n⚠️  AVISO DE SEGURIDAD:")
    print("     Las claves se almacenan en texto plano.")
    print(f"     No compartas {SETTINGS_PATH} ni lo subas a un repositorio.")


def test_connectivity():
    """Verifica conectividad básica con los servicios externos."""
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        print("[ERROR] No se puede importar urllib.")
        return

    endpoints = {
        "Pinecone": "https://api.pinecone.io",
        "Gemini": "https://generativelanguage.googleapis.com",
    }

    for name, url in endpoints.items():
        try:
            urllib.request.urlopen(url, timeout=5)
            print(f"[OK] {name}: accesible")
        except urllib.error.HTTPError as e:
            # HTTP error = servidor respondió (conectividad OK)
            print(f"[OK] {name}: accesible (HTTP {e.code})")
        except Exception as e:
            print(f"[FAIL] {name}: no accesible — {e}")


def main():
    parser = argparse.ArgumentParser(description="engram setup helper")
    parser.add_argument("--check", action="store_true", help="Verifica la configuración actual")
    parser.add_argument("--configure", action="store_true", help="Configura el MCP interactivamente")
    parser.add_argument("--test-connectivity", action="store_true", help="Prueba conectividad con Pinecone y Gemini")
    args = parser.parse_args()

    if args.configure:
        configure()
    elif args.check:
        ok = check_config()
        if ok:
            test_connectivity()
    elif args.test_connectivity:
        test_connectivity()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
