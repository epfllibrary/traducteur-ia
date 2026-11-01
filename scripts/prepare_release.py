"""Prépare localement les notes et le JSON d'une release GitLab, sans publier."""

import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_URL = "https://gitlab.epfl.ch/sisb-public/id/traducteur"


def main():
    module = ast.parse((ROOT / "translate.py").read_text(encoding="utf-8"))
    version = next(
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "APP_VERSION" for target in node.targets)
    )
    installer_source = (ROOT / "installer/traducteur.iss").read_text(encoding="utf-8")
    if f'#define MyAppVersion "{version}"' not in installer_source or \
            f"VersionInfoVersion={version}.0" not in installer_source:
        raise SystemExit("Versions de l'application et de l'installateur incohérentes.")
    if f"# Traducteur IA ({version})" not in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("La version du README doit correspondre à celle de l'application.")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(rf"^## {re.escape(version)} \([^\n]+\)\n(.*?)(?=^## |\Z)",
                        changelog, re.MULTILINE | re.DOTALL)
    if section is None:
        raise SystemExit(f"Notes de version {version} introuvables dans CHANGELOG.md.")
    installer = ROOT / "bin/traducteur-setup.exe"
    if not installer.is_file():
        raise SystemExit("Reconstruire bin/traducteur-setup.exe avant de préparer la release.")
    with installer.open("rb") as stream:
        checksum = hashlib.file_digest(stream, "sha256").hexdigest()
    tag = f"v{version}"
    asset_url = f"{PROJECT_URL}/-/raw/{tag}/bin/traducteur-setup.exe?inline=false"
    notes = (
        f"## Traducteur {version}\n\n{section.group(1).strip()}\n\n"
        f"## Installation Windows\n\n"
        f"[Télécharger traducteur-setup.exe]({asset_url})\n\n"
        "Windows 10/11 x64. Python n'est pas nécessaire sur le poste utilisateur. "
        "Le modèle doit être accessible via Ollama ou une API compatible OpenAI.\n\n"
        f"SHA-256 de `traducteur-setup.exe` : `{checksum}`\n"
    )
    payload = {
        "name": f"Traducteur {version}", "tag_name": tag, "description": notes,
        "assets": {"links": [{
            "name": f"Installateur Windows — Traducteur {version}",
            "url": asset_url, "direct_asset_path": "/traducteur-setup.exe", "link_type": "package",
        }]},
    }
    output = ROOT / "build/release" / tag
    output.mkdir(parents=True, exist_ok=True)
    (output / "release.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "release-notes.md").write_text(notes, encoding="utf-8")
    print(f"Préparation locale : {output.relative_to(ROOT)}")
    print(f"Setup : {installer.stat().st_size} octets ; SHA-256 : {checksum}")
    print("Publication séparée après validation du commit et du tag.")


if __name__ == "__main__":
    main()
