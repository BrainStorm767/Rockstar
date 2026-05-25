import os

TARGET_OLD = "/add"
TARGET_NEW = "/add"

EXTENSIONS = [".py", ".html", ".js"]

def scan_and_fix(folder="."):
    changed_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):

                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if TARGET_OLD in content:

                        new_content = content.replace(TARGET_OLD, TARGET_NEW)

                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        changed_files.append(path)

                        print(f"✔ Updated: {path}")

                except Exception as e:
                    print(f"❌ Error in {path}: {e}")

    print("\n--- DONE ---")
    print(f"Total files changed: {len(changed_files)}")


if __name__ == "__main__":
    scan_and_fix()