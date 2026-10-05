"""Validate canonical Explore sources. No network, install, submission or publication."""

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import yaml

NAME = "covercount-explore"
ENDPOINT = "https://mcp.covercount.io/explore/mcp"
TOOLS = {"search_available_reservations", "search_public_events", "search_places", "get_reservation_opening", "get_public_venue"}
SKILLS = {
    "covercount-find-reservations": {"search_available_reservations", "get_reservation_opening", "get_public_venue"},
    "covercount-find-events": {"search_public_events", "get_public_venue"},
    "covercount-find-places": {"search_places", "search_available_reservations", "get_public_venue"},
}
COMMON_FILES = {"README.md", "LICENSE.txt", "assets/icon.png", "assets/logo.svg", "assets/logo-dark.svg",
                "docs/installation.md", "docs/submission.md", "docs/evaluations.md"}
OPENAI_FILES = {"plugin.json", "mcp.json", ".codex-plugin/plugin.json", ".mcp.json"}
CLAUDE_FILES = {".claude-plugin/plugin.json", ".mcp.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_file(root, name):
    path = root / name
    require(not Path(name).is_absolute() and ".." not in Path(name).parts, f"Unsafe path: {name}")
    for part in [path, *path.parents]:
        require(not part.is_symlink() and not getattr(part, "is_junction", lambda: False)(), f"Linked path: {name}")
        if part == root:
            break
    require(path.resolve().is_relative_to(root.resolve()), f"Escaping path: {name}")
    require(path.is_file(), f"Missing file: {name}")
    return path.read_bytes()


def json_file(root, name):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key in {name}: {key}")
            result[key] = value
        return result
    return json.loads(read_file(root, name), object_pairs_hook=unique)


def validate(root, server_source=None):
    root = Path(root).absolute()
    portable = json_file(root, "plugin.json")
    codex = json_file(root, ".codex-plugin/plugin.json")
    claude = json_file(root, ".claude-plugin/plugin.json")
    version = portable.get("version", "")
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "Invalid plugin version")
    shared = {"name", "version", "description", "author", "homepage", "repository", "license", "keywords"}
    require(set(portable) == shared | {"$schema", "extensions"}, "Unexpected portable manifest fields")
    require(portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "Wrong portable schema")
    require(portable["name"] == NAME, "Wrong Explore identity")
    require(portable["homepage"] == "https://explore.covercount.io/", "Wrong Explore homepage")
    require(portable["repository"] == "https://github.com/chriswill/CoverCount_Public_Mcp", "Wrong Explore repository")
    require(set(portable["extensions"]) == {"com.openai"}, "Unexpected extension")
    require(set(portable["extensions"]["com.openai"]) == {"interface"}, "Unexpected OpenAI extension fields")
    require(set(codex) == shared | {"skills", "mcpServers", "interface"}, "Unexpected Codex fields")
    require(set(claude) == shared | {"skills", "mcpServers", "privacyPolicyUrl", "documentationUrl", "displayName", "icon"}, "Unexpected Claude fields")
    require(claude["icon"] == "./assets/icon.png", "Wrong Claude listing icon")
    require(claude["displayName"] == "CoverCount Explore", "Wrong Claude display name")
    require(claude["privacyPolicyUrl"] == "https://www.covercount.io/privacy", "Wrong Claude privacy policy")
    require(claude["documentationUrl"] == "https://www.covercount.io/learn/connected-apps/covercount-explore", "Wrong Explore documentation")
    for manifest in (codex, claude):
        require(all(manifest.get(key) == portable[key] for key in shared), "Manifest metadata/version mismatch")
        require(manifest["skills"] == "./skills/" and manifest["mcpServers"] == "./.mcp.json", "Wrong component paths")
    interface = portable["extensions"]["com.openai"]["interface"]
    require(interface == codex["interface"], "OpenAI presentation differs between layouts")
    require(interface["displayName"] == "CoverCount Explore", "Wrong display identity")
    require(1 <= len(interface["shortDescription"]) <= 30, "OpenAI subtitle exceeds submission limit")
    require(interface.get("supportURL") == "https://support.cloudscope.io/", "Missing/wrong OpenAI support URL")
    require(interface["capabilities"] == ["Interactive"], "Unexpected capability claim")
    for key, path in {"composerIcon": "./assets/icon.png", "logo": "./assets/icon.png", "logoDark": "./assets/icon.png"}.items():
        require(interface.get(key) == path, f"Wrong asset path: {key}")
    icon = read_file(root, "assets/icon.png")
    require(len(icon) >= 33 and icon[:16] == b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", "Submission icon must be PNG")
    width = int.from_bytes(icon[16:20], "big")
    height = int.from_bytes(icon[20:24], "big")
    require(48 <= width == height <= 4096, "Submission PNG must be square and between 48 and 4096 pixels")
    require(len(icon) <= 5 * 1024 * 1024, "Submission PNG exceeds 5 MiB")
    for path in ("./assets/logo.svg", "./assets/logo-dark.svg"):
        svg = ET.fromstring(read_file(root, path[2:]))
        require(svg.tag == "{http://www.w3.org/2000/svg}svg", f"Not SVG: {path}")
        require(not any(node.tag.rsplit("}", 1)[-1].lower() in
                        {"script", "foreignobject", "style", "animate", "animatemotion", "animatetransform", "set", "discard"}
                        for node in svg.iter()), f"Active/styled SVG: {path}")
        require(not any(key.rsplit("}", 1)[-1].lower().startswith("on") or
                        key.rsplit("}", 1)[-1].lower() == "style" or
                        (key.rsplit("}", 1)[-1] == "href" and not value.startswith("#"))
                        for node in svg.iter() for key, value in node.attrib.items()), f"External/active SVG: {path}")
        require(not any(not re.fullmatch(r"\s*['\"]?#[A-Za-z_][\w:.-]*['\"]?\s*", target)
                        for node in svg.iter() for value in node.attrib.values()
                        for target in re.findall(r"url\((.*?)\)", value, re.IGNORECASE)), f"External SVG reference: {path}")

    expected_mcp = {"mcpServers": {NAME: {"type": "http", "url": ENDPOINT}}}
    require(json_file(root, ".mcp.json") == expected_mcp, "Wrong anonymous connection or unexpected credentials/settings")
    require(json_file(root, "mcp.json") == {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {NAME: {"type": "streamable-http", "url": ENDPOINT}}}, "Wrong portable connection")

    skill_files = set()
    versions = {}
    references = set()
    descriptions = []
    require({path.name for path in (root / "skills").iterdir()} == set(SKILLS), "Unexpected/missing skill folders")
    for name, expected_tools in SKILLS.items():
        relative = f"skills/{name}/SKILL.md"
        text = read_file(root, relative).decode("utf-8").replace("\r\n", "\n")
        require(text.startswith("---\n"), f"Missing frontmatter: {name}")
        parts = text.split("---", 2)
        require(len(parts) == 3, f"Unclosed frontmatter: {name}")
        front = yaml.safe_load(parts[1])
        require(set(front) == {"name", "description", "metadata"} and front["name"] == name, f"Invalid skill identity: {name}")
        require(isinstance(front["description"], str) and 25 <= len(front["description"]) <= 300, f"Unfocused description: {name}")
        require(isinstance(front["metadata"], dict) and set(front["metadata"]) == {"version"}
                and isinstance(front["metadata"]["version"], str)
                and bool(re.fullmatch(r"\d+\.\d+\.\d+", front["metadata"]["version"])), f"Invalid skill version: {name}")
        descriptions.append(front["description"])
        versions[name] = front["metadata"]["version"]
        tools = set(re.findall(r"`((?:get|search|list|create|cancel|modify|send|prepare|commit|summarize)_[a-z0-9_]+)`", parts[2]))
        require(tools == expected_tools, f"Unexpected/missing skill tools in {name}: {sorted(tools)}")
        references |= tools
        dependency_path = f"skills/{name}/agents/openai.yaml"
        dependency = yaml.safe_load(read_file(root, dependency_path))
        require(set(dependency) == {"interface", "dependencies"}, f"Unexpected skill policy/config: {name}")
        require(dependency["dependencies"] == {"tools": [{"type": "mcp", "value": NAME,
            "description": "Anonymous CoverCount public discovery and website handoff", "transport": "streamable_http", "url": ENDPOINT}]},
            f"Wrong skill MCP dependency: {name}")
        require(25 <= len(dependency["interface"]["short_description"]) <= 64, f"Invalid UI description: {name}")
        skill_files |= {relative, dependency_path}
    actual_files = {path.relative_to(root).as_posix() for path in (root / "skills").rglob("*") if path.is_file()}
    require(actual_files == skill_files, "Unexpected files under skills")
    require(sum(map(len, descriptions)) <= 900, "Skill discovery metadata budget exceeded")
    require(references == TOOLS, "Public tool coverage mismatch")
    if server_source:
        catalog = Path(server_source).read_text(encoding="utf-8")
        names = set(re.findall(r'Describe<[^>]+>\("([a-z_]+)"', catalog))
        require(names == TOOLS, "Server catalog differs from client contract")

    files = COMMON_FILES | OPENAI_FILES | CLAUDE_FILES | skill_files
    entries = {name: read_file(root, name) for name in sorted(files)}
    for name, data in entries.items():
        if name.endswith(".md"):
            for target in re.findall(r"\]\(([^)]+)\)", data.decode("utf-8")):
                if target.startswith(("https://", "#")):
                    continue
                linked = (root / name).parent / target.split("#", 1)[0]
                require(linked.resolve().is_relative_to(root.resolve()), f"Escaping Markdown link: {name}: {target}")
                require(linked.relative_to(root).as_posix() in entries, f"Broken/unpackaged Markdown link: {name}: {target}")
    return {"version": version, "skills": versions, "tools": sorted(references), "entries": entries,
            "descriptionCharacters": sum(map(len, descriptions))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--server-source", type=Path)
    args = parser.parse_args()
    result = validate(args.root, args.server_source)
    print(f"Validated {NAME} {result['version']}: {len(result['skills'])} skills, {len(result['tools'])} public tools, "
          f"{len(result['entries'])} distributable files, {result['descriptionCharacters']} description characters.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, ET.ParseError) as error:
        print(f"Plugin validation failed: {error}", file=sys.stderr)
        sys.exit(1)
