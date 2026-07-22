import sys
import os
import argparse
import urllib.request
import urllib.error


def get_working_directory():
    return os.getcwd()


def download_module(module_id: str):
    work_dir = get_working_directory()
    modules_dir = os.path.join(work_dir, "modules")

    try:
        os.makedirs(modules_dir, exist_ok=True)
    except Exception as e:
        print(f"[!] Directory creation error '{modules_dir}': {e}")
        sys.exit(1)

    filename = f"{module_id}.csc"
    output_path = os.path.join(modules_dir, filename)

    branch = "main"
    url = f"https://raw.githubusercontent.com/BFSDK/Cascade/{branch}/libraries/{filename}"

    print(f"[*] Downloading module '{module_id}'...")
    print(f"[*] URL: {url}")
    print(f"[*] Target: {output_path}")

    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        
        with urllib.request.urlopen(req) as response, open(output_path, "wb") as out_file:
            out_file.write(response.read())

        print(f"[+] The module is installed in {output_path}")

    except urllib.error.HTTPError as e:
        print(f"[!] HTTP Error {e.code}: Couldn't find or download the file.")
        if e.code == 404:
            print(f"[!] Make sure that the '{module_id}' module exists in the repository.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[!] Network error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unknown error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Cascade module downloader"
    )
    parser.add_argument(
        "moduleid", 
        type=str, 
        help="Module id"
    )

    args = parser.parse_args()
    download_module(args.moduleid)


if __name__ == "__main__":
    main()