import json
import os
import subprocess
from pathlib import Path

root = Path('/home/ubuntu/firmware-lab')
base = root / 'research/webkit-1302/upstream/adri-suid-history/full-stage2/followup'
raw = base / 'ntfargo_forks_clean.json'
out = base / 'ntfargo_forks_tree_audit.txt'
data = json.loads(raw.read_text())
lines = [f'fork_count={len(data)}']
for fork in data:
    name = fork['full_name']
    branch = fork.get('default_branch') or 'main'
    lines.append(f'\n## {name} branch={branch} updated={fork.get("updated_at")}')
    url = f'https://api.github.com/repos/{name}/git/trees/{branch}?recursive=1'
    token = os.environ.get('GH_TOKEN') or subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
    p = subprocess.run(['curl', '-fsSL', '-H', f'Authorization: Bearer {token}', '-H', 'Accept: application/vnd.github+json', url], capture_output=True, text=True, timeout=30)
    try:
        tree = json.loads(p.stdout).get('tree', [])
    except Exception as exc:
        lines.append(f'tree_parse_error={exc}')
        continue
    paths = [x.get('path', '') for x in tree]
    hits = [x for x in paths if any(k in x.lower() for k in ('jordy', 'stage2', 'celsius', 'mount', 'kernel', 'netctrl', 'lapse', 'ffs'))]
    lines.append('paths=' + ('; '.join(hits[:160]) if hits else '(none)'))
out.write_text('\n'.join(lines) + '\n')
print(out)
print('\n'.join(lines[:12]))
