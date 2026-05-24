import json
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from flask import Flask, render_template, request

WEBHOOK_URL = os.getenv("SKDR_WEBHOOK_URL", "").strip()
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

app = Flask(__name__)
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

FILE_FIELDS = {
    "total_kasus": "kasus",
    "total_kematian": "kematian",
    "kasus_minggu_ini": "kasus",
    "kematian_minggu_ini": "kematian",
}

DISEASE_ALIASES = {
    "Pneumonia": "Pneumonia",
    "Pnemonia": "Pneumonia",
    "PNEMONIA": "Pneumonia",
    "PNUMONIA": "Pneumonia",
}


def extract_week_info(file_path: Path) -> tuple[int, int, int]:
    raw = pd.read_excel(file_path, header=None)
    minggu_text = " ".join(raw.fillna("").astype(str).iloc[10].tolist())
    subheader_text = " ".join(raw.fillna("").astype(str).iloc[12].tolist())
    tahun_text = " ".join(raw.fillna("").astype(str).iloc[11].tolist())

    range_match = re.search(r"Minggu\s+(\d+)\s*-\s*Minggu\s+(\d+)", minggu_text, re.IGNORECASE)
    subheader_weeks = [int(w) for w in re.findall(r"M-(\d+)", subheader_text, re.IGNORECASE)]
    year_match = re.search(r"\b(20\d{2})\b", tahun_text)

    if not range_match or not subheader_weeks or not year_match:
        raise ValueError(f"Tidak dapat membaca informasi minggu/tahun pada file: {file_path.name}")

    _, end_week = range_match.groups()
    end_week = int(end_week)
    last_subheader_week = max(subheader_weeks)
    year = int(year_match.group(1))

    return year, end_week, last_subheader_week


def validate_week_consistency(file_map: dict[str, Path]) -> None:
    year_cases, end_cases, last_col_cases = extract_week_info(file_map["total_kasus"])
    year_deaths, end_deaths, last_col_deaths = extract_week_info(file_map["total_kematian"])
    year_weekly_cases, end_weekly_cases, last_col_weekly_cases = extract_week_info(file_map["kasus_minggu_ini"])
    year_weekly_deaths, end_weekly_deaths, last_col_weekly_deaths = extract_week_info(file_map["kematian_minggu_ini"])

    if year_cases != year_deaths:
        raise ValueError(
            f"Tahun file total_kasus ({year_cases}) dan total_kematian ({year_deaths}) berbeda."
        )

    if last_col_cases != last_col_deaths or end_cases != end_deaths:
        raise ValueError(
            "Minggu terakhir file total_kasus dan total_kematian tidak sama. "
            f"total_kasus: range Minggu {end_cases}, kolom terakhir M-{last_col_cases}; "
            f"total_kematian: range Minggu {end_deaths}, kolom terakhir M-{last_col_deaths}."
        )

    if year_weekly_cases != year_weekly_deaths:
        raise ValueError(
            f"Tahun file kasus_minggu_ini ({year_weekly_cases}) dan kematian_minggu_ini ({year_weekly_deaths}) berbeda."
        )

    if last_col_weekly_cases != last_col_weekly_deaths or end_weekly_cases != end_weekly_deaths:
        raise ValueError(
            "Minggu file mingguan kasus/kematian tidak sama. "
            f"kasus_minggu_ini: range Minggu {end_weekly_cases}, kolom terakhir M-{last_col_weekly_cases}; "
            f"kematian_minggu_ini: range Minggu {end_weekly_deaths}, kolom terakhir M-{last_col_weekly_deaths}."
        )


def detect_metric_type(file_path: Path) -> str:
    raw = pd.read_excel(file_path, header=None)
    # Baris ini biasanya berisi "Total Jumlah Kasus ..." atau "Total Jumlah Kematian ..."
    descriptor = " ".join(raw.fillna("").astype(str).iloc[9].tolist()).lower()
    if "kematian" in descriptor:
        return "kematian"
    if "kasus" in descriptor:
        return "kasus"
    return "unknown"


def validate_file_semantics(file_map: dict[str, Path]) -> None:
    for field_name, expected in FILE_FIELDS.items():
        actual = detect_metric_type(file_map[field_name])
        if actual != expected:
            raise ValueError(
                f"File {field_name} tidak sesuai. Diharapkan file {expected}, tetapi terdeteksi {actual}."
            )


def clean_and_pick_total(file_path: Path, value_column: str) -> pd.DataFrame:
    df = pd.read_excel(file_path, header=11)

    if "Puskesmas" in df.columns:
        df = df.rename(columns={"Puskesmas": "Penyakit"})

    if "Penyakit" not in df.columns or "Total" not in df.columns:
        raise ValueError(f"Format file tidak valid untuk {value_column}.")

    df = df[["Penyakit", "Total"]].copy()
    df = df[df["Penyakit"].notna()].copy()
    df["Penyakit"] = df["Penyakit"].astype(str).str.strip()
    df = df[
        (df["Penyakit"] != "")
        & (df["Penyakit"].str.lower() != "nan")
        & (~df["Penyakit"].str.contains("total", case=False, na=False))
    ].copy()

    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0).astype(int)
    df = df.groupby("Penyakit", as_index=False)["Total"].sum()
    return df.rename(columns={"Total": value_column})


def get_minggu_epidemiologi(file_path: Path) -> str:
    raw = pd.read_excel(file_path, header=None)
    minggu_text = " ".join(raw.fillna("").astype(str).iloc[10].tolist())
    tahun_text = " ".join(raw.fillna("").astype(str).iloc[11].tolist())

    week_match = re.search(r"Minggu\s+(\d+)\s*-\s*Minggu\s+(\d+)", minggu_text, re.IGNORECASE)
    year_match = re.search(r"\b(20\d{2})\b", tahun_text)
    if not week_match or not year_match:
        return "unknown-ME00"

    _, end_week = week_match.groups()
    year = year_match.group(1)
    return f"{year}-ME{int(end_week)}"


def extract_trends(file_path: Path) -> dict:
    """
    Ambil data trend (kolom M-1 ... M-terakhir) dari file total_kasus.
    Hasil: { "Nama Penyakit": { "M-1": 12, "M-2": 9, ... }, ... }
    """
    df = pd.read_excel(file_path, header=None)

    # 1) Find the row that contains the most week labels like "M-1", "M-2", ...
    def is_week_label(s: str) -> bool:
        s = s.strip()
        return bool(re.match(r"^M-\d+$", s, flags=re.IGNORECASE))

    search_rows = min(60, len(df))
    weekly_row_idx = None
    best_week_count = 0
    for r in range(search_rows):
        row = df.iloc[r].fillna("")
        week_count = 0
        for v in row.tolist():
            if is_week_label(str(v)):
                week_count += 1
        if week_count > best_week_count:
            best_week_count = week_count
            weekly_row_idx = r

    if weekly_row_idx is None or best_week_count < 2:
        return {}

    # 2) Determine disease column. Prefer a column whose header (somewhere above) contains "penyakit/puskesmas".
    disease_col_idx = None
    header_search_top = max(0, weekly_row_idx - 8)
    for r in range(weekly_row_idx, header_search_top - 1, -1):
        row = df.iloc[r].fillna("")
        for j, v in enumerate(row.tolist()):
            s = str(v).strip().lower()
            if "penyakit" in s or s == "puskesmas":
                disease_col_idx = j
                break
        if disease_col_idx is not None:
            break

    # Fallback: in many SKDR templates, disease names are in column B (index 1)
    if disease_col_idx is None:
        disease_col_idx = 1 if df.shape[1] > 1 else 0

    weekly_row = df.iloc[weekly_row_idx].fillna("")

    weekly_cols: list[tuple[int, str]] = []
    for idx, val in enumerate(weekly_row.tolist()):
        s = str(val).strip()
        if is_week_label(s):
            weekly_cols.append((idx, s))

    if not weekly_cols:
        return {}

    trends: dict[str, dict[str, int]] = {}
    data_start = weekly_row_idx + 1
    for i in range(data_start, len(df)):
        penyakit_raw = df.iloc[i, disease_col_idx] if disease_col_idx < df.shape[1] else ""
        penyakit = str(penyakit_raw).strip()
        if not penyakit or penyakit.lower() == "nan" or "total" in penyakit.lower():
            continue

        # Sinkronisasi nama penyakit dengan hasil agregasi
        penyakit = DISEASE_ALIASES.get(penyakit, penyakit)

        trend_data: dict[str, int] = {}
        for idx, m_col in weekly_cols:
            val = df.iloc[i, idx] if idx < df.shape[1] else 0
            try:
                trend_data[m_col] = int(val)
            except Exception:
                trend_data[m_col] = 0
        trends[penyakit] = trend_data

    return trends


def process_files(file_map: dict[str, Path]) -> pd.DataFrame:
    cleaned = [
        clean_and_pick_total(file_map[field_name], field_name)
        for field_name in FILE_FIELDS
    ]
    merged = cleaned[0]
    for df in cleaned[1:]:
        merged = pd.merge(merged, df, on="Penyakit", how="outer")

    for col in FILE_FIELDS:
        if col not in merged.columns:
            merged[col] = 0
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0).astype(int)

    merged["Penyakit"] = merged["Penyakit"].replace(DISEASE_ALIASES)
    merged = merged.sort_values("Penyakit").reset_index(drop=True)
    me = get_minggu_epidemiologi(file_map["kasus_minggu_ini"])

    result_df = pd.DataFrame(
        {
            "minggu_epidemiologi": me,
            "penyakit": merged["Penyakit"],
            "total_kasus": merged["total_kasus"],
            "total_kematian": merged["total_kematian"],
            "kasus_minggu_ini": merged["kasus_minggu_ini"],
            "kematian_minggu_ini": merged["kematian_minggu_ini"],
        }
    )

    # Guard untuk mencegah mapping tertukar: nilai mingguan tidak boleh melampaui total periode.
    invalid_weekly_kasus = (result_df["kasus_minggu_ini"] > result_df["total_kasus"]).any()
    invalid_weekly_death = (result_df["kematian_minggu_ini"] > result_df["total_kematian"]).any()
    if invalid_weekly_kasus or invalid_weekly_death:
        raise ValueError(
            "Validasi gagal: ada nilai mingguan yang melebihi total periode. "
            "Periksa apakah file total_kasus/total_kematian/kasus_minggu_ini/kematian_minggu_ini tertukar."
        )

    return result_df


def build_payload(df: pd.DataFrame, rumah_sakit: str) -> dict:
    work_df = df.copy()
    work_df["cfr"] = work_df.apply(
        lambda r: round((r["total_kematian"] / r["total_kasus"]) * 100, 2)
        if r["total_kasus"] > 0
        else None,
        axis=1,
    )
    work_df["cfr_valid"] = work_df["total_kasus"] >= 10
    work_df["ranking_kasus"] = (
        work_df["total_kasus"].rank(method="min", ascending=False).astype(int)
    )
    death_rank = work_df["total_kematian"].where(work_df["total_kematian"] > 0)
    work_df["ranking_kematian"] = death_rank.rank(method="dense", ascending=False)
    work_df["ranking_kematian"] = work_df["ranking_kematian"].where(
        work_df["total_kematian"] > 0, None
    )
    work_df["ranking_kematian"] = work_df["ranking_kematian"].apply(
        lambda x: int(x) if pd.notna(x) else None
    )

    periode = df["minggu_epidemiologi"].iloc[0] if not df.empty else "unknown-ME00"
    dominant_row = work_df.loc[work_df["total_kasus"].idxmax()] if not work_df.empty else None
    fatal_row = work_df.loc[work_df["total_kematian"].idxmax()] if not work_df.empty else None

    # CFR tertinggi hanya dihitung untuk penyakit dengan minimal 10 kasus
    cfr_df = work_df[work_df["total_kasus"] >= 10].copy()
    if not cfr_df.empty:
        cfr_df["cfr"] = cfr_df["total_kematian"] / cfr_df["total_kasus"]
        cfr_row = cfr_df.loc[cfr_df["cfr"].idxmax()]
        cfr_name = cfr_row["penyakit"]
    else:
        cfr_name = "-"

    data_records = work_df[
        [
            "penyakit",
            "total_kasus",
            "total_kematian",
            "kasus_minggu_ini",
            "kematian_minggu_ini",
            "cfr",
            "cfr_valid",
            "ranking_kasus",
            "ranking_kematian",
        ]
    ].to_dict(orient="records")

    for row in data_records:
        row["ranking_kasus"] = int(row["ranking_kasus"])
        if pd.isna(row["ranking_kematian"]):
            row["ranking_kematian"] = None
        else:
            row["ranking_kematian"] = int(row["ranking_kematian"])

    payload = {
        "metadata": {
            "rumah_sakit": rumah_sakit,
            "periode_epi": periode,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "summary": {
            "total_kasus": int(df["total_kasus"].sum()),
            "total_kematian": int(df["total_kematian"].sum()),
            "total_kasus_mingguan": int(df["kasus_minggu_ini"].sum()),
            "total_kematian_mingguan": int(df["kematian_minggu_ini"].sum()),
        },
        "validation": {
            "is_valid": True,
            "total_row": int(len(work_df)),
        },
        "indikator": {
            "penyakit_dominan": dominant_row["penyakit"] if dominant_row is not None else "-",
            "penyakit_fatal_tertinggi": fatal_row["penyakit"] if fatal_row is not None else "-",
            "cfr_tertinggi": cfr_name,
        },
        "data": data_records,
    }
    return payload


def save_and_send_json(df: pd.DataFrame, rumah_sakit: str) -> tuple[dict, str]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"hasil_skdr_{ts}.json"

    payload = build_payload(df, rumah_sakit)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # If no webhook is configured, keep the app usable (charts + preview still work).
    if not WEBHOOK_URL:
        return payload, ""

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=180,
    )
    response.raise_for_status()

    # Parse HTML report from webhook JSON response
    html_report = ""
    try:
        result = response.json()
        html_report = result.get("html", "")
    except (ValueError, KeyError):
        pass

    return payload, html_report


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    try:
        rumah_sakit = request.form.get("rumah_sakit", "").strip()
        if not rumah_sakit:
            raise ValueError("Nama fasyankes/rumah sakit wajib diisi.")

        saved_files: dict[str, Path] = {}

        for field_name in FILE_FIELDS:
            file = request.files.get(field_name)
            if file is None or file.filename == "":
                raise ValueError(f"File {field_name} wajib diupload.")

            ext = Path(file.filename).suffix.lower()
            if ext not in {".xlsx", ".xls"}:
                raise ValueError(f"File {field_name} harus Excel (.xlsx/.xls).")

            safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{field_name}{ext}"
            save_path = UPLOAD_DIR / safe_name
            file.save(save_path)
            saved_files[field_name] = save_path

        validate_week_consistency(saved_files)
        validate_file_semantics(saved_files)

        df = process_files(saved_files)
        payload, html_report = save_and_send_json(df, rumah_sakit)
        trends = extract_trends(saved_files["total_kasus"])

        return render_template(
            "index.html",
            success=True,
            rumah_sakit=rumah_sakit,
            periode=payload["metadata"]["periode_epi"],
            summary=payload["summary"],
            preview=sorted(payload["data"], key=lambda x: x["total_kasus"], reverse=True)[:10],
            trends=trends,
            html_report=html_report,
        )
    except Exception as e:
        # Sanitize: strip URLs from error messages to avoid exposing webhook endpoints
        error_msg = re.sub(r'https?://\S+', '[URL disembunyikan]', str(e))
        return render_template("index.html", error=error_msg, rumah_sakit=request.form.get("rumah_sakit", ""))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
