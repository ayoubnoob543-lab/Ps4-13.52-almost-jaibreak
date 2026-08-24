import pathlib
import shutil
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HOME_BREW = ROOT / "webkit-kit" / "homebrew"
OUTPUT = HOME_BREW / "build" / "host" / "modern-webkitgtk-output.txt"


def _pkg_config_exists(module: str) -> bool:
    pkg_config = shutil.which("pkg-config")
    if not pkg_config:
        return False
    return subprocess.run(
        [pkg_config, "--exists", module], capture_output=True
    ).returncode == 0


@unittest.skipUnless(
    _pkg_config_exists("webkit2gtk-4.1"),
    "host webkit2gtk-4.1 development package is not available",
)
@unittest.skipUnless(shutil.which("xvfb-run"), "host xvfb-run is not available")
class ModernWebKitGTKSmokeTest(unittest.TestCase):
    def test_real_webkitgtk_capability_matrix(self):
        result = subprocess.run(
            ["make", "-C", str(HOME_BREW), "modern-webkit-smoke"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = OUTPUT.read_text(encoding="utf-8")
        self.assertIn(
            'stage=1 result={"dom":true,"event":true,"text":"clicked","flex":true,"grid":true,"animation":true,"form":true,"svg":true,"image":true,"canvas":true,"storage":true}',
            output,
        )
        self.assertIn(
            'stage=2 result={"page":true,"storage":true,"dom":"page2-ok","js":true,"event":true}',
            output,
        )
        self.assertIn(
            'stage=3 result={"page":true,"history":true,"dom":true,"js":true}',
            output,
        )


if __name__ == "__main__":
    unittest.main()
