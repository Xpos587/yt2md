import os
import sys
import subprocess
import sysconfig


def is_admin():
    return os.geteuid() == 0


def install_package():
    print("Installing the package...")
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = script_dir

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            print("pip is not available in the current Python environment.")
            print(
                "Please install pip or use a Python interpreter that has pip installed."
            )
            sys.exit(1)

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", package_dir], check=True
        )
        print("Package installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the package: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    scripts_path = sysconfig.get_path("scripts")
    if not scripts_path:
        print("Warning: Could not determine the scripts directory.")
        return None

    scripts_path = os.path.abspath(scripts_path)
    return scripts_path


def check_and_create_symlink_unix(scripts_path):
    yt2md_script = os.path.join(scripts_path, "yt2md")
    target_path = "/usr/local/bin/yt2md"

    if os.path.exists(target_path):
        print(f"{target_path} already exists.")
        return

    print(f"{target_path} does not exist.")
    choice = (
        input(
            "Do you want to create a symlink to yt2md in /usr/local/bin? [y/N]: ")
        .strip()
        .lower()
    )
    if choice != "y":
        print("No changes were made.")
        return

    if not is_admin():
        print("Root privileges are required to create a symlink in /usr/local/bin.")
        subprocess.check_call(["sudo", "ln", "-s", yt2md_script, target_path])
    else:
        try:
            if os.path.islink(target_path) or os.path.exists(target_path):
                overwrite = (
                    input(
                        f"A file already exists at {
                            target_path}. Do you want to overwrite it? [y/N]: "
                    )
                    .strip()
                    .lower()
                )
                if overwrite != "y":
                    print("No changes were made.")
                    return
                else:
                    os.remove(target_path)
            os.symlink(yt2md_script, target_path)
            print(f"Successfully created symlink to yt2md at {target_path}")
        except Exception as e:
            print(f"An error occurred while creating symlink: {e}")


def main():
    scripts_path = install_package()
    if scripts_path is None:
        sys.exit(1)

    print(f"Python Scripts path: {scripts_path}")

    check_and_create_symlink_unix(scripts_path)


if __name__ == "__main__":
    main()
