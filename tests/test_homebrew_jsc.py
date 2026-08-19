import json
import subprocess
import unittest
from pathlib import Path


class HomebrewJavaScriptCoreSmokeTest(unittest.TestCase):
    def test_minimal_browser_uses_public_jsc_api(self):
        binary = Path(__file__).parents[1] / "webkit-kit" / "homebrew" / "build" / "host" / "minimal-browser"
        if not binary.exists():
            self.skipTest("host minimal-browser has not been built")
        completed = subprocess.run(
            [str(binary)],
            check=True,
            capture_output=True,
            text=True,
        )
        lines = completed.stdout.splitlines()
        self.assertIn("homebrew-minimal-browser", lines)
        self.assertTrue(any(line.startswith("jsc-host-available") for line in lines))
        result = next(line for line in lines if line.startswith("{\"engine\""))
        report = json.loads(result)
        self.assertEqual(report["engine"], "JavaScriptCore-GTK-host")
        self.assertTrue(report["passed"])
        self.assertEqual(report["value"], "true")


if __name__ == "__main__":
    unittest.main()
