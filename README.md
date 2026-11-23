# NCAA Soccer Pick’em — Mac editor + public viewer

## Important: keep your existing data
Copy your **current** `data/men.json` and `data/women.json` into this folder's `data/` directory before starting. These contain all the picks and game results you have entered. Do **not** overwrite them with freshly generated bracket data. You can also copy your existing `pdfs/` folder if you want original PDF downloads available to viewers.

If you have no data files yet, run `python3 build_data.py` once. This script now skips existing files, rather than overwriting them.

## Edit on your Mac
From Terminal in this folder:

```bash
PICKEM_MODE=editor python3 -m streamlit run app.py
```

Alternatively, double-click `run_local.command` (macOS may require right-click → Open on first use). Editor mode includes prediction editing, results entry, and JSON backup/restore.

## Preview the public read-only version

```bash
python3 -m streamlit run app.py
```

Viewer mode is the default. It hides editing tabs, Admin, and restore controls. More importantly, the `save()` function refuses all writes in viewer mode.

## Publish on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `build_data.py`, `requirements.txt`, and your **current** `data/men.json` and `data/women.json`. Optionally upload `pdfs/` if you want participants to download originals.
2. In Streamlit Community Cloud, create a new app from the repository, using `app.py` as the main file.
3. **Do not configure `PICKEM_MODE=editor` on the hosting service.** With the default settings, the public site is read-only.
4. Share the `.streamlit.app` URL.
5. When you save a new result on your Mac, commit and push the updated `data/men.json` or `data/women.json` using GitHub Desktop or Git. Streamlit Cloud redeploys the new data; the public leaderboard updates after the deployment finishes. It does not sync automatically from your Mac.

### Data safety

- Keep your original folder as a backup.
- Do not run `build_data.py` to update results; it only creates missing initial files.
- The public site is read-only by default. Editor mode is an environment setting, **not authentication**. Never set it on a publicly accessible deployment.
- If your repo is public, any uploaded PDFs and JSON data may be visible through GitHub. Omit PDFs if privacy matters.
