#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

try:
    import numpy as np
except ImportError:  # optional
    np = None  # type: ignore

from datetime import date, datetime, time


DEFAULT_SHEET_INDEX = 0
DEFAULT_HEADER_ROW_1_BASED = 1
DEFAULT_OUTPUT_SHEET_NAME = "Sheet1"
DEFAULT_KEY_FIELD = "id"


def read_excel(excel_path: Path) -> pd.DataFrame:
    header = DEFAULT_HEADER_ROW_1_BASED - 1
    df = pd.read_excel(
        excel_path,
        sheet_name=DEFAULT_SHEET_INDEX,
        header=header,
        engine="openpyxl",
        dtype=object,
    )
    return df


def normalize_value_for_json(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return value.isoformat()
    if isinstance(value, (datetime, date, time)):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    if np is not None and isinstance(value, np.generic):
        return value.item()
    return value


def detect_key_column(df: pd.DataFrame) -> Optional[str]:
    if df.empty:
        return None
    normalized_columns = {str(c).strip().lower(): str(c) for c in df.columns}
    preferred_names = ["id", "key", "docid", "uid"]
    for name in preferred_names:
        if name in normalized_columns:
            column_name = normalized_columns[name]
            series = df[column_name]
            if series.dropna().duplicated().any():
                continue
            return column_name
    for col in df.columns:
        series = df[col]
        if not series.dropna().duplicated().any() and series.dropna().shape[0] > 0:
            return str(col)
    return None


def dataframe_to_firebase_record(df: pd.DataFrame, key_column: str) -> Dict[str, Dict[str, Any]]:
    if key_column not in df.columns:
        raise ValueError(f"키 컬럼 '{key_column}' 이(가) 엑셀에 없습니다.")
    df_valid = df.dropna(subset=[key_column]).copy()
    df_valid[key_column] = df_valid[key_column].astype(str)
    if df_valid[key_column].duplicated().any():
        dups = df_valid[df_valid[key_column].duplicated()][key_column].unique().tolist()
        raise ValueError(f"키 컬럼 '{key_column}' 값이 중복됩니다: {dups}")
    record: Dict[str, Dict[str, Any]] = {}
    for _, row in df_valid.iterrows():
        key = row[key_column]
        item: Dict[str, Any] = {}
        for col in df_valid.columns:
            if col == key_column:
                continue
            item[col] = normalize_value_for_json(row[col])
        record[str(key)] = item
    return record


def dataframe_to_firebase_record_with_generated_keys(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    record: Dict[str, Dict[str, Any]] = {}
    for row_index, (_, row) in enumerate(df.iterrows(), start=1):
        key = str(row_index)
        item: Dict[str, Any] = {}
        for col in df.columns:
            item[col] = normalize_value_for_json(row[col])
        record[key] = item
    return record


def write_json(json_path: Path, data: Any) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def excel_to_json(excel_path: Path, json_path: Path) -> None:
    df = read_excel(excel_path)
    key_col = detect_key_column(df)
    if key_col is None:
        raise ValueError("키 컬럼이 없어 변환을 중단합니다. 엑셀에 고유한 ID 컬럼을 추가해 주세요.")
    data = dataframe_to_firebase_record(df, key_col)
    write_json(json_path, data)


def read_json(json_path: Path) -> Any:
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def record_json_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for key, value in data.items():
        if isinstance(value, dict):
            row = {DEFAULT_KEY_FIELD: key, **value}
        else:
            row = {DEFAULT_KEY_FIELD: key, "value": value}
        rows.append(row)
    return pd.DataFrame(rows)


def write_excel(df: pd.DataFrame, excel_path: Path) -> None:
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=DEFAULT_OUTPUT_SHEET_NAME, index=False)


def json_to_excel(json_path: Path, excel_path: Path) -> None:
    data = read_json(json_path)
    if not isinstance(data, dict):
        raise ValueError("입력 JSON은 Firebase 레코드(최상위 객체)여야 합니다.")
    df = record_json_to_dataframe(data)
    write_excel(df, excel_path)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Excel ↔ JSON 변환기 (Firebase 레코드 전용, 간단 모드)")
    sub = p.add_subparsers(dest="command", required=True)

    p_x2j = sub.add_parser("x2j", help="Excel → JSON(Firebase)")
    p_x2j.add_argument("excel", type=Path, help="입력 Excel(.xlsx)")
    p_x2j.add_argument("json", type=Path, help="출력 JSON 파일 경로")

    p_j2x = sub.add_parser("j2x", help="JSON(Firebase) → Excel")
    p_j2x.add_argument("json", type=Path, help="입력 JSON (Firebase 레코드)")
    p_j2x.add_argument("excel", type=Path, help="출력 Excel(.xlsx)")

    p_detect = sub.add_parser("detect", help="Excel 키 컬럼 자동 감지 결과 출력")
    p_detect.add_argument("excel", type=Path, help="입력 Excel(.xlsx)")

    return p


# ---------------- GUI -----------------

def launch_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Excel ↔ JSON 변환기 (Firebase 전용·간단)")
    root.geometry("560x420")

    direction = tk.StringVar(value="x2j")  # x2j or j2x
    input_path = tk.StringVar()
    output_path = tk.StringVar()

    def browse_input():
        if direction.get() == "x2j":
            path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        else:
            path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if path:
            input_path.set(path)

    def browse_output():
        if direction.get() == "x2j":
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        else:
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if path:
            output_path.set(path)

    def append_log(text: str) -> None:
        log.configure(state="normal")
        log.insert("end", text + "\n")
        log.see("end")
        log.configure(state="disabled")

    def run_conversion():
        try:
            in_path = Path(input_path.get())
            out_path = Path(output_path.get())
            if not in_path:
                messagebox.showwarning("입력 파일", "입력 파일을 선택하세요.")
                return
            if not out_path:
                messagebox.showwarning("출력 파일", "출력 파일을 선택하세요.")
                return
            if direction.get() == "x2j":
                excel_to_json(in_path, out_path)
                append_log("Excel → JSON(Firebase) 변환 완료")
                messagebox.showinfo("완료", "Excel → JSON(Firebase) 변환이 완료되었습니다.")
            else:
                json_to_excel(in_path, out_path)
                append_log("JSON(Firebase) → Excel 변환 완료")
                messagebox.showinfo("완료", "JSON(Firebase) → Excel 변환이 완료되었습니다.")
        except Exception as e:
            append_log(f"오류: {e}")
            messagebox.showerror("오류", str(e))

    # Layout
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="변환 방향:").grid(row=0, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Excel → JSON(Firebase)", variable=direction, value="x2j").grid(row=0, column=1, sticky="w")
    ttk.Radiobutton(frm, text="JSON(Firebase) → Excel", variable=direction, value="j2x").grid(row=0, column=2, sticky="w")

    ttk.Label(frm, text="입력 파일:").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=input_path, width=60).grid(row=1, column=1, columnspan=2, sticky="we")
    ttk.Button(frm, text="찾기", command=browse_input).grid(row=1, column=3, sticky="w")

    ttk.Label(frm, text="출력 파일:").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=output_path, width=60).grid(row=2, column=1, columnspan=2, sticky="we")
    ttk.Button(frm, text="저장", command=browse_output).grid(row=2, column=3, sticky="w")

    ttk.Button(frm, text="실행", command=run_conversion).grid(row=3, column=0, sticky="w", pady=(12, 6))

    log = tk.Text(frm, height=12, state="disabled")
    log.grid(row=4, column=0, columnspan=4, sticky="nsew")

    frm.columnconfigure(1, weight=1)
    frm.rowconfigure(4, weight=1)

    root.mainloop()


# --------------- CLI entry ---------------

def main() -> None:
    if len(sys.argv) == 1:
        launch_gui()
        return

    parser = build_arg_parser()
    args = parser.parse_args()

    if args.command == "x2j":
        excel_to_json(args.excel, args.json)
    elif args.command == "j2x":
        json_to_excel(args.json, args.excel)
    elif args.command == "detect":
        df = read_excel(args.excel)
        key = detect_key_column(df)
        if key is None:
            print("감지된 키 컬럼: (없음)")
        else:
            print(f"감지된 키 컬럼: {key}")
    else:
        parser.error("unknown command")


if __name__ == "__main__":
    main()
