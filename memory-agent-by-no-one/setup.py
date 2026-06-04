#!/usr/bin/env python3
"""
engram setup helper — verifica instalación del binario y estado del MCP.
Uso: python3 setup.py [--check | --install-instructions | --status]
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
DB_PATH = Path.home() / ".engram" / "engram.db"


def check_binary():
    path = shutil.which("engram")
    if path:
        try:
            result = subprocess.run(["engram", "version"], capture_output=True, text=True, timeout=5)
            version = result.stdout.strip() or result.stderr.strip()
            print(f"[OK] engram binary: {path}")
            print(f"     Versión: {version}")
            return True
        except Exception as e:
            print(f"[WARN] engram encontrado en {path} pero no responde: {e}")
            return False
    else:
        print("[ERROR] engram no está instalado o no está en el PATH.")
        return False


def check_database():
    if DB_PATH.exists():
        size_kb = DB_PATH.stat().st_size // 1024
        print(f"[OK] Base de datos: {DB_PATH} ({size_kb} KB)")
        return True
    else:
        print(f"[INFO] Base de datos no encontrada en {DB_PATH}")
        print("       Se crea automáticamente al usar engram por primera vez.")
        return False


def check_plugin():
    """Verifica si el plugin de Claude Code está configurado."""
    plugin_paths = [
        Path.home() / ".claude" / "plugins" / "engram",
        Path.home() / ".claude-code" / "plugins" / "engram",
    ]
    for p in plugin_paths:
        if p.exists():
            print(f"[OK] Plugin Claude Code: {p}")
            return True

    settings = {}
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)

    mcp_servers = settings.get("mcpServers", {})
    if "engram" in mcp_servers:
        print("[OK] MCP engram configurado en settings.json")
        return True

    print("[WARN] Plugin engram no detectado en Claude Code.")
    print("       Ejecuta: claude plugin marketplace add Gentleman-Programming/engram")
    print("                claude plugin install engram")
    return False


def check_all():
    print("=== Estado de engram ===\n")
    binary_ok = check_binary()
    print()
    db_ok = check_database()
    print()
    plugin_ok = check_plugin()
    print()

    if binary_ok and plugin_ok:
        print("[OK] engram listo para usar.")
    elif not binary_ok:
        print("[ACTION] Instalar engram primero (ver --install-instructions).")
    elif not plugin_ok:
        print("[ACTION] Configurar el plugin en Claude Code.")

    return binary_ok and plugin_ok


def install_instructions():
    print("=== Instrucciones de instalación de engram ===\n")
    print("1. Instalar el binario:")
    print()
    print("   macOS (Homebrew):")
    print("     brew install gentleman-programming/tap/engram")
    print()
    print("   Linux / Windows / otros métodos:")
    print("     https://github.com/Gentleman-Programming/engram/blob/main/docs/INSTALLATION.md")
    print()
    print("2. Configurar en Claude Code:")
    print("     claude plugin marketplace add Gentleman-Programming/engram")
    print("     claude plugin install engram")
    print()
    print("3. Verificar:")
    print("     python3 setup.py --check")
    print()
    print("4. (Opcional) TUI para explorar memorias:")
    print("     engram tui")
    print()
    print("Repositorio: https://github.com/Gentleman-Programming/engram")


def backup():
    if not DB_PATH.exists():
        print("[ERROR] No hay base de datos para respaldar.")
        sys.exit(1)
    import shutil as sh
    from datetime import datetime
    backup_path = DB_PATH.parent / f"engram.db.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    sh.copy2(DB_PATH, backup_path)
    size_kb = backup_path.stat().st_size // 1024
    print(f"[OK] Backup creado: {backup_path} ({size_kb} KB)")


def main():
    parser = argparse.ArgumentParser(description="engram setup helper")
    parser.add_argument("--check", action="store_true", help="Verifica instalación y estado")
    parser.add_argument("--install-instructions", action="store_true", help="Muestra cómo instalar engram")
    parser.add_argument("--backup", action="store_true", help="Crea un backup de engram.db")
    args = parser.parse_args()

    if args.check:
        ok = check_all()
        sys.exit(0 if ok else 1)
    elif args.install_instructions:
        install_instructions()
    elif args.backup:
        backup()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
