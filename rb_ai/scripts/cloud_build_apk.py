#!/usr/bin/env python3
"""
RB.AI - Cloud APK Builder & Artifact Downloader
Triggers and tracks the GitHub Actions Flutter APK compilation workflow,
and downloads the final generated app-release.apk to the local output path.
"""

import os
import sys
import json
import time
import re
import zipfile
import io
import urllib.request
import urllib.error

REPO = "rambinaypandit798-sudo/RB-Agent-by-jarvas"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "flutter_client", "build", "app", "outputs", "flutter-apk")
CREDENTIALS_FILE = os.path.expanduser("~/.git-credentials")

def get_github_token():
    if not os.path.exists(CREDENTIALS_FILE):
        return None
    with open(CREDENTIALS_FILE, "r") as f:
        for line in f:
            match = re.search(r'https://([^:]+):([^@]+)@github\.com', line)
            if match:
                return match.group(2)
    return None

class NoAuthRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        new_req = super().redirect_request(req, fp, code, msg, hdrs, newurl)
        if new_req:
            new_req.headers = {k: v for k, v in new_req.headers.items() if k.lower() != 'authorization'}
        return new_req

def main():
    token = get_github_token()
    if not token:
        print("❌ Error: GitHub token not found in ~/.git-credentials.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RB-Agent-Builder/2.0"
    }

    # 1. Fetch latest commit SHA
    try:
        import subprocess
        head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE_DIR).decode().strip()
        print(f"📦 Local Commit SHA: {head_sha[:7]}")
    except Exception as e:
        print(f"⚠️ Warning reading git sha: {e}")
        head_sha = ""

    # 2. Find workflow run corresponding to the latest commit
    print(f"🔍 Monitoring GitHub Actions CI/CD for repository '{REPO}'...")
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10"

    run_id = None
    for attempt in range(30):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                runs = data.get("workflow_runs", [])
                for r in runs:
                    if head_sha and r.get("head_sha") == head_sha:
                        run_id = r["id"]
                        break
            if run_id:
                break
        except Exception as e:
            pass
        if attempt % 3 == 0:
            print(f"   Waiting for GitHub Actions to trigger run for {head_sha[:7]}... (attempt {attempt+1}/30)")
        time.sleep(3)

    if not run_id:
        # Fallback: check latest run if head_sha was empty or latest run is in_progress
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            runs = data.get("workflow_runs", [])
            for r in runs:
                if r.get("status") in ["queued", "in_progress"] or (head_sha and r.get("head_sha") == head_sha):
                    run_id = r["id"]
                    break
            if not run_id and runs:
                run_id = runs[0]["id"]
            elif not run_id:
                print("❌ No workflow runs found.")
                sys.exit(1)

    print(f"⚡ Tracking Build Workflow Run #{run_id}...")

    # 3. Poll run status until completion
    run_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}"
    start_time = time.time()
    conclusion = None

    while time.time() - start_time < 600:
        req = urllib.request.Request(run_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                run_data = json.loads(resp.read().decode())
                status = run_data.get("status")
                conclusion = run_data.get("conclusion")
                elapsed = int(time.time() - start_time)
                print(f"⏱️ [{elapsed}s] Build Status: {status.upper()} (Conclusion: {conclusion})")
                if status == "completed":
                    break
        except Exception as e:
            print(f"Polling update: {e}")
        time.sleep(15)

    if conclusion != "success":
        print(f"\n❌ Build did not succeed. (Conclusion: {conclusion})")
        # Fetch failure log
        try:
            jobs_url = f"{run_url}/jobs"
            req_jobs = urllib.request.Request(jobs_url, headers=headers)
            with urllib.request.urlopen(req_jobs, timeout=15) as resp:
                jobs_data = json.loads(resp.read().decode())
                job_id = jobs_data["jobs"][0]["id"]

            opener = urllib.request.build_opener(NoAuthRedirect)
            req_log = urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/jobs/{job_id}/logs", headers=headers)
            with opener.open(req_log) as resp:
                log_lines = resp.read().decode("utf-8", errors="ignore").splitlines()
                print("\n--- Failure Log Snippet ---")
                print("\n".join(log_lines[-40:]))
        except Exception as e:
            print(f"Could not retrieve error log: {e}")
        sys.exit(1)

    # 4. Download Release APK Artifact
    print("\n🎉 Build compiled successfully! Fetching release APK artifact...")
    artifacts_url = f"{run_url}/artifacts"
    req_art = urllib.request.Request(artifacts_url, headers=headers)
    with urllib.request.urlopen(req_art, timeout=15) as resp:
        art_data = json.loads(resp.read().decode())
        artifacts = art_data.get("artifacts", [])

    if not artifacts:
        print("❌ Error: No artifacts found in workflow run.")
        sys.exit(1)

    target_artifact = artifacts[0]
    dl_url = target_artifact["archive_download_url"]
    print(f"⬇️ Downloading artifact '{target_artifact['name']}' ({target_artifact.get('size_in_bytes', 0) // 1024} KB)...")

    opener = urllib.request.build_opener(NoAuthRedirect)
    dl_req = urllib.request.Request(dl_url, headers=headers)
    with opener.open(dl_req, timeout=120) as resp:
        zip_bytes = resp.read()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target_apk_path = os.path.join(OUTPUT_DIR, "app-release.apk")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for fname in z.namelist():
            z.extract(fname, OUTPUT_DIR)
            extracted_file = os.path.join(OUTPUT_DIR, fname)
            if fname.endswith(".apk"):
                # Copy or rename to app-release.apk
                if extracted_file != target_apk_path:
                    with open(extracted_file, "rb") as f_in, open(target_apk_path, "wb") as f_out:
                        f_out.write(f_in.read())

    apk_size_mb = round(os.path.getsize(target_apk_path) / (1024 * 1024), 2)
    print("\n========================================================")
    print("✅ SUCCESS! RELEASE ANDROID APK COMPILED & READY:")
    print(f"📍 Path: {target_apk_path}")
    print(f"📊 Size: {apk_size_mb} MB")
    print("========================================================\n")

if __name__ == "__main__":
    main()
