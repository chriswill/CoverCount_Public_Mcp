import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_plugin.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="covercount-explore-validation-")
        self.root = Path(self.temporary.name)
        for name in validator.COMMON_FILES | validator.OPENAI_FILES | validator.CLAUDE_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        shutil.copytree(ROOT / "skills", self.root / "skills")

    def tearDown(self):
        self.temporary.cleanup()

    def change_json(self, name, edit):
        path = self.root / name
        value = json.loads(path.read_text(encoding="utf-8"))
        edit(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_valid_source_and_exact_distributable_inventory(self):
        result = validator.validate(self.root)
        self.assertEqual(5, len(result["tools"]))
        self.assertEqual(3, len(result["skills"]))
        self.assertFalse(any(name.startswith(("scripts/", "tests/", ".git/")) for name in result["entries"]))

    def test_staff_connection_is_rejected(self):
        self.change_json(".mcp.json", lambda value: value["mcpServers"][validator.NAME].update(url="https://mcp.covercount.io/mcp"))
        with self.assertRaisesRegex(ValueError, "connection"):
            validator.validate(self.root)

    def test_directory_incompatible_svg_is_rejected(self):
        cases = [
            '<style>.color { fill: red; }</style>',
            '<path style="fill:red"/>',
            '<animate attributeName="opacity"/>',
            '<animateTransform attributeName="transform"/>',
            '<set attributeName="fill" to="red"/>',
            '<path onclick="run()"/>',
            '<foreignObject/>',
            '<script/>',
            '<use href="https://example.com/icon.svg#mark"/>',
            '<path fill="url(https://example.com/colors.svg#red)"/>',
        ]
        for fragment in cases:
            with self.subTest(fragment=fragment):
                (self.root / 'assets/icon.svg').write_text(
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">' + fragment + '</svg>', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, "SVG"):
                    validator.validate(self.root)

    def test_fragment_svg_reference_is_allowed(self):
        (self.root / 'assets/icon.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><path id="mark" d="M0 0"/></defs>'
            '<use href="#mark"/></svg>', encoding='utf-8')
        validator.validate(self.root)

    def test_nonsquare_submission_icon_is_rejected(self):
        (self.root / 'assets/icon.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"/>', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'square'):
            validator.validate(self.root)

    def test_wrong_claude_privacy_policy_is_rejected(self):
        self.change_json('.claude-plugin/plugin.json', lambda value: value.update(privacyPolicyUrl='https://example.com'))
        with self.assertRaisesRegex(ValueError, 'privacy policy'):
            validator.validate(self.root)

    def test_auth_header_is_rejected(self):
        self.change_json("mcp.json", lambda value: value["mcpServers"][validator.NAME].update(headers={"Authorization": "test-secret"}))
        with self.assertRaisesRegex(ValueError, "connection"):
            validator.validate(self.root)

    def test_mismatched_release_versions_are_rejected(self):
        self.change_json(".claude-plugin/plugin.json", lambda value: value.update(version="9.9.9"))
        with self.assertRaisesRegex(ValueError, "mismatch"):
            validator.validate(self.root)

    def test_escaping_manifest_path_is_rejected(self):
        self.change_json(".codex-plugin/plugin.json", lambda value: value.update(skills="./../staff/skills/"))
        with self.assertRaisesRegex(ValueError, "paths"):
            validator.validate(self.root)

    def test_staff_tool_dependency_is_rejected(self):
        path = self.root / "skills/covercount-find-reservations/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nUse `create_reservation`.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "skill tools"):
            validator.validate(self.root)

    def test_missing_skill_dependency_is_rejected(self):
        (self.root / "skills/covercount-find-events/agents/openai.yaml").unlink()
        with self.assertRaisesRegex(ValueError, "Missing file"):
            validator.validate(self.root)

    def test_duplicate_json_key_cannot_override_endpoint(self):
        path = self.root / ".mcp.json"
        path.write_text('{"mcpServers":{},"mcpServers":{}}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            validator.validate(self.root)

    def test_unexpected_skill_script_is_rejected(self):
        (self.root / "skills/covercount-find-events/run.py").write_text("print('unexpected')", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unexpected files"):
            validator.validate(self.root)

    def test_unpackaged_markdown_reference_is_rejected(self):
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[Missing](not-shipped.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Markdown link"):
            validator.validate(self.root)

    def test_server_catalog_drift_is_rejected(self):
        source = self.root / "catalog.cs"
        source.write_text('Describe<A, B>("search_events")', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Server catalog"):
            validator.validate(self.root, source)


if __name__ == "__main__":
    unittest.main()
