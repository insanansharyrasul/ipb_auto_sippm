import argparse
import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright


REQUIRED_COLUMNS = {
    "kegiatan",
    "tempat",
    "TMT",
    "TST",
    "bukti_dokumentasi",
}


def read_activities(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required columns: {missing}")

        activities = []
        for row_number, row in enumerate(reader, start=2):
            if not any(value and value.strip() for value in row.values()):
                continue
            if any(not row[column].strip() for column in REQUIRED_COLUMNS):
                raise ValueError(f"CSV row {row_number} contains an empty required field")
            activities.append(row)

    if not activities:
        raise ValueError("CSV does not contain any activity rows")
    return activities


def run(
    playwright: Playwright,
    activities: list[dict[str, str]],
    username: str,
    password: str,
    csv_directory: Path,
) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto("https://sippm.ipb.ac.id/Account/Login")
        page.get_by_role("textbox", name="Username").fill(username)
        page.get_by_role("textbox", name="Password").fill(password)
        page.get_by_role("button", name="Masuk").click()
        page.get_by_role("link", name=" Detail").click()
        page.get_by_role("link", name="Log Kegiatan").click()

        for activity_number, activity in enumerate(activities, start=1):
            page.get_by_role("link", name=" Tambah").click()
            page.locator("#Kegiatan").fill(activity["kegiatan"])
            page.locator("#Tempat").fill(activity["tempat"])
            page.locator("#TMT").fill(activity["TMT"])
            page.locator("#TST").fill(activity["TST"])
            evidence_path = Path(activity["bukti_dokumentasi"])
            if not evidence_path.is_absolute():
                evidence_path = csv_directory / evidence_path
            page.get_by_role("button", name="This field is required.").set_input_files(
                str(evidence_path)
            )
            page.get_by_role("button", name="Simpan").click()
            print(f"Submitted activity {activity_number}/{len(activities)}")
            if activity_number < len(activities):
                page.get_by_role("link", name="Log Kegiatan").click()
    finally:
        context.close()
        browser.close()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Submit SIPPm activities from a CSV file.")
    parser.add_argument("csv_file", type=Path, help="CSV containing activity rows")
    args = parser.parse_args()

    username = os.environ.get("SIPPM_USERNAME")
    password = os.environ.get("SIPPM_PASSWORD")
    if not username or not password:
        raise SystemExit("Set SIPPM_USERNAME and SIPPM_PASSWORD before running the script.")

    activities = read_activities(args.csv_file)
    with sync_playwright() as playwright:
        run(playwright, activities, username, password, args.csv_file.parent)


if __name__ == "__main__":
    main()
