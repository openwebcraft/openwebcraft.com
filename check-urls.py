#!/usr/bin/env python3
"""Check old openwebcraft.com URLs against owc.blot.im."""

import csv
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_CSV = "internal_html.csv"
OUTPUT_CSV = "url-check-results.csv"
OLD_HOST = "https://openwebcraft.com"
NEW_HOST = "https://owc.blot.im"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
TIMEOUT = 15


def check_url(old_url, old_status):
    path = old_url.replace(OLD_HOST, "", 1)
    new_url = NEW_HOST + path
    try:
        req = urllib.request.Request(new_url, headers={"User-Agent": UA})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        new_status = resp.status
        final_url = resp.url
    except urllib.error.HTTPError as e:
        new_status = e.code
        final_url = new_url
    except Exception as e:
        new_status = f"ERR: {e}"
        final_url = new_url

    result = "OK" if str(new_status).startswith("2") else "BROKEN"
    return {
        "old_url": old_url,
        "path": path or "/",
        "old_status": old_status,
        "new_status": new_status,
        "final_url": final_url,
        "result": result,
    }


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [(row["Address"], row["Status Code"]) for row in reader]

    print(f"Checking {len(rows)} URLs against {NEW_HOST} ...\n")

    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(check_url, url, status): url for url, status in rows}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            mark = "OK" if r["result"] == "OK" else "BROKEN"
            print(f"  [{mark:6s}] {r['new_status']:>4} {r['path']}")

    results.sort(key=lambda r: r["old_url"])

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["old_url", "path", "old_status", "new_status", "final_url", "result"])
        writer.writeheader()
        writer.writerows(results)

    ok = sum(1 for r in results if r["result"] == "OK")
    broken = [r for r in results if r["result"] != "OK"]

    print(f"\n{'='*60}")
    print(f"Total: {len(results)}  |  OK: {ok}  |  Broken: {len(broken)}")
    if broken:
        print(f"\nBroken URLs:")
        for r in broken:
            print(f"  {r['new_status']:>4}  {r['path']}")
    print(f"\nResults written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
