import csv
import io
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rf4-fish-search-local-change-me")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "fish.db"

PATTERN = re.compile(
    r"^(.*?)\s+吃\s*(.*?)(?:\s+喜爱窝子\s*(.*?))?(?:\s+限制[：:]?\s*(.*))?$"
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                food TEXT NOT NULL DEFAULT '',
                groundbait TEXT NOT NULL DEFAULT '',
                limits TEXT NOT NULL DEFAULT '',
                raw TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fish_name ON fish(name)")


def parse_record(line):
    raw = line.strip().lstrip("\ufeff")
    if not raw or raw.startswith("#"):
        return None
    match = PATTERN.match(raw)
    if not match:
        return None
    name, food, groundbait, limits = match.groups()
    name = (name or "").strip().strip(",，;；")
    if not name:
        return None
    return {
        "name": name,
        "food": (food or "").strip(),
        "groundbait": (groundbait or "").strip(),
        "limits": (limits or "").strip(),
        "raw": raw,
    }


def save_records(records, source="manual"):
    added = 0
    updated = 0
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_db() as conn:
        for item in records:
            if not item:
                continue
            exists = conn.execute(
                "SELECT id FROM fish WHERE name = ?", (item["name"],)
            ).fetchone()
            conn.execute("""
                INSERT INTO fish(name, food, groundbait, limits, raw, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    food=excluded.food,
                    groundbait=excluded.groundbait,
                    limits=excluded.limits,
                    raw=excluded.raw,
                    updated_at=excluded.updated_at
            """, (
                item["name"], item["food"], item["groundbait"],
                item["limits"], item["raw"], now
            ))
            if exists:
                updated += 1
            else:
                added += 1
    return added, updated


def decode_upload(data):
    for encoding in ("utf-8-sig", "gb18030", "utf-8"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def search_fish(query):
    query = query.strip()
    if not query:
        with get_db() as conn:
            return conn.execute(
                "SELECT * FROM fish ORDER BY name COLLATE NOCASE LIMIT 200"
            ).fetchall()
    with get_db() as conn:
        exact = conn.execute(
            "SELECT * FROM fish WHERE name = ?", (query,)
        ).fetchall()
        if exact:
            return exact
        like = "%" + query + "%"
        return conn.execute("""
            SELECT * FROM fish
            WHERE name LIKE ? OR food LIKE ? OR groundbait LIKE ?
               OR limits LIKE ? OR raw LIKE ?
            ORDER BY CASE WHEN name LIKE ? THEN 0 ELSE 1 END,
                     name COLLATE NOCASE
            LIMIT 200
        """, (like, like, like, like, like, like)).fetchall()


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "")
    results = search_fish(query)
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM fish").fetchone()[0]
    return render_template("index.html", results=results, query=query, total=total)


@app.route("/import", methods=["POST"])
def import_text():
    text = request.form.get("records", "")
    upload = request.files.get("file")
    if upload and upload.filename:
        if Path(upload.filename).suffix.lower() not in {".txt", ".md", ".csv"}:
            flash("仅支持 TXT、MD、CSV 文件。", "error")
            return redirect(url_for("index"))
        text += "\n" + decode_upload(upload.read())
    records = [parse_record(line) for line in text.splitlines()]
    valid = [item for item in records if item]
    if not valid:
        flash("没有识别到有效记录。请检查每行格式：鱼名 吃饵料 喜爱窝子... 限制：...", "error")
        return redirect(url_for("index"))
    added, updated = save_records(valid)
    skipped = len(records) - len(valid)
    flash(f"导入完成：新增 {added} 条，更新 {updated} 条，跳过 {skipped} 行。", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:fish_id>", methods=["POST"])
def delete_fish(fish_id):
    with get_db() as conn:
        conn.execute("DELETE FROM fish WHERE id = ?", (fish_id,))
    flash("记录已删除。", "success")
    return redirect(url_for("index", q=request.form.get("q", "")))


@app.route("/sample", methods=["POST"])
def import_sample():
    sample_path = Path(__file__).with_name("samples.txt")
    content = sample_path.read_text(encoding="utf-8")
    valid = [parse_record(line) for line in content.splitlines()]
    added, updated = save_records([item for item in valid if item])
    flash(f"示例资料导入完成：新增 {added} 条，更新 {updated} 条。", "success")
    return redirect(url_for("index"))


@app.errorhandler(413)
def too_large(_error):
    flash("文件过大，单次上传上限为 32 MB。", "error")
    return redirect(url_for("index"))


init_db()
