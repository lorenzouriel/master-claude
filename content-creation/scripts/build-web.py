"""Build the claude.ai upload bundle from the Claude Code layout.

Usage: python scripts/build-web.py

Output: dist/content-creation-web/ and dist/content-creation-web.zip

Layout of the bundle:
  SKILL.md                  <- web/SKILL.md (router)
  context/, brand/          <- copied (brand/inspirations/ excluded)
  skills/<name>/<name>.md   <- .claude/skills/<name>/SKILL.md
  skills/<name>/references/ <- copied; scripts/ excluded (no shell on the web)
Files in web/overrides/ replace their source counterpart (same relative path).
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = DIST / "content-creation-web"
OVERRIDES = ROOT / "web" / "overrides"
TEXT = {".md", ".html", ".js", ".py", ".csv"}
SKIP_DIRS = {"scripts", "inspirations"}


def bundle_path(rel):
    """Map a source-relative path to its bundle-relative path."""
    parts = rel.parts
    if parts[:2] == (".claude", "skills"):
        name = parts[2]
        rest = parts[3:]
        if rest == ("SKILL.md",):
            rest = (f"{name}.md",)
        return Path("skills", name, *rest)
    return rel


def rewrite(text, skill=None):
    text = re.sub(r"\.claude/skills/([a-z-]+)/SKILL\.md", r"skills/\1/\1.md", text)
    text = text.replace(".claude/skills/", "skills/")
    if skill:
        text = text.replace("`SKILL.md`", f"`{skill}.md`")
    return text


def sources():
    yield Path("web/SKILL.md"), Path("SKILL.md")
    for top in ("context", "brand", ".claude/skills"):
        for path in sorted((ROOT / top).rglob("*")):
            rel = path.relative_to(ROOT)
            if path.is_file() and not SKIP_DIRS.intersection(rel.parts):
                override = OVERRIDES / rel
                yield (override.relative_to(ROOT) if override.exists() else rel), bundle_path(rel)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    count = 0
    for src, dst in sources():
        target = OUT / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in TEXT:
            skill = dst.parts[1] if dst.parts[0] == "skills" else None
            text = (ROOT / src).read_bytes().decode("utf-8")
            target.write_bytes(rewrite(text, skill).encode("utf-8"))
        else:
            shutil.copyfile(ROOT / src, target)
        count += 1
    unused = [p for p in OVERRIDES.rglob("*") if p.is_file()
              and not (ROOT / p.relative_to(OVERRIDES)).exists()]
    for p in unused:
        print(f"warning: override has no source file: {p.relative_to(ROOT)}")
    archive = shutil.make_archive(str(OUT), "zip", root_dir=DIST, base_dir=OUT.name)
    print(f"{count} files -> {OUT.relative_to(ROOT)}")
    print(f"zip -> {Path(archive).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
