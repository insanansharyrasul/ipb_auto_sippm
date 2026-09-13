import argparse
import csv
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Playwright, expect, sync_playwright


logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {
    "kegiatan",
    "tempat",
    "TMT",
    "TST",
    "bukti_dokumentasi",
}


def read_activities(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file was not found: {csv_path}")

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
            evidence_path = Path(row["bukti_dokumentasi"])
            if not evidence_path.is_absolute():
                evidence_path = csv_path.parent / evidence_path
            if not evidence_path.is_file():
                raise FileNotFoundError(
                    f"Evidence file in CSV row {row_number} was not found: {evidence_path}"
                )
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
    delay_seconds: float,
) -> None:
    logger.info("Starting browser")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    try:
        page = context.new_page()

        def pause() -> None:
            page.wait_for_timeout(round(delay_seconds * 1000))

        logger.info("Opening login page")
        page.goto("https://sippm.ipb.ac.id/Account/Login")
        logger.info("Logging in as %s", username)
        page.get_by_role("textbox", name="Username").fill(username)
        page.get_by_role("textbox", name="Password").fill(password)
        page.get_by_role("button", name="Masuk").click()
        logger.info("Opening activity log")
        page.get_by_role("link", name=" Detail").click()
        page.get_by_role("link", name="Log Kegiatan").click()

        for activity_number, activity in enumerate(activities, start=1):
            logger.info(
                "Submitting activity %d/%d: %s",
                activity_number,
                len(activities),
                activity["kegiatan"],
            )
            page.get_by_role("link", name=" Tambah").click()
            pause()
            page.locator("#Kegiatan").fill(activity["kegiatan"])
            pause()
            page.locator("#Tempat").fill(activity["tempat"])
            pause()
            page.keyboard.press("Tab")
            page.keyboard.type(activity["TMT"])
            page.keyboard.press("Escape")
            page.keyboard.press("Tab")
            pause()
            page.keyboard.type(activity["TST"])
            page.keyboard.press("Escape")
            page.keyboard.press("Tab")
            pause()
            evidence_path = Path(activity["bukti_dokumentasi"])
            if not evidence_path.is_absolute():
                evidence_path = csv_directory / evidence_path
            logger.info("Uploading evidence: %s", evidence_path)
            page.get_by_role("button", name="This field is required.").set_input_files(
                str(evidence_path)
            )
            pause()
            page.get_by_role("button", name="Simpan").click()
            expect(
                page.get_by_text("x Data berhasil disimpan.", exact=True).last
            ).to_be_visible(timeout=10_000)
            pause()
            logger.info("Activity %d submitted successfully", activity_number)
            if activity_number < len(activities):
                page.get_by_role("link", name="Log Kegiatan").click()
                pause()
        logger.info("All %d activities submitted successfully", len(activities))
    finally:
        context.close()
        browser.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Submit SIPPm activities from a CSV file.")
    parser.add_argument("csv_file", type=Path, help="CSV containing activity rows")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Seconds to wait between browser actions (default: 1)",
    )
    args = parser.parse_args()

    if args.delay < 0:
        parser.error("--delay must be zero or greater")

    username = os.environ.get("SIPPM_USERNAME")
    password = os.environ.get("SIPPM_PASSWORD")
    if not username or not password:
        raise SystemExit("Set SIPPM_USERNAME and SIPPM_PASSWORD before running the script.")

    try:
        activities = read_activities(args.csv_file)
        logger.info("Loaded %d activities from %s", len(activities), args.csv_file)
        with sync_playwright() as playwright:
            run(
                playwright,
                activities,
                username,
                password,
                args.csv_file.parent,
                args.delay,
            )
    except Exception:
        logger.exception("The script stopped because of an error")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
