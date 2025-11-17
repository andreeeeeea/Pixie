"""
Helper functions for registry search and process management
"""

import os
import winreg
import glob
import subprocess
import logging

logger = logging.getLogger(__name__)


def extract_exe_from_registry(subkey, display_name):
    """Helper: Extracts executable path from a registry subkey.

    Tries multiple registry values in order of preference:
    1. DisplayIcon (usually points to app icon/exe)
    2. InstallLocation + searching for main exe
    3. UninstallString (filtered to exclude uninstallers)

    Args:
        subkey: Open registry subkey
        display_name: Display name of the application

    Returns:
        Full path to .exe file, or None if not found
    """
    try:
        icon_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
        full_path = icon_path.replace('"', '').split(',')[0]
        if full_path.endswith('.exe') and 'uninstall' not in full_path.lower() and os.path.exists(full_path):
            logger.debug(f"Found executable from DisplayIcon: {full_path}")
            return full_path
    except Exception as e:
        logger.debug(f"DisplayIcon lookup failed: {e}")

    try:
        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
        if install_location and os.path.exists(install_location):
            logger.debug(f"Found InstallLocation: {install_location}")

            exe_files = glob.glob(os.path.join(install_location, "*.exe"))

            excluded_keywords = ['uninstall', 'uninst', 'setup', 'config', 'update', 'launcher']
            valid_exes = [
                exe for exe in exe_files
                if not any(keyword in os.path.basename(exe).lower() for keyword in excluded_keywords)
            ]

            if valid_exes:
                app_name_parts = display_name.lower().split()
                for exe in valid_exes:
                    exe_name = os.path.basename(exe).lower()
                    if any(part in exe_name for part in app_name_parts if len(part) > 3):
                        logger.debug(f"Found matching executable in InstallLocation: {exe}")
                        return exe

                logger.debug(f"Using first valid executable from InstallLocation: {valid_exes[0]}")
                return valid_exes[0]
    except Exception as e:
        logger.debug(f"InstallLocation lookup failed: {e}")

    try:
        uninstall_path = winreg.QueryValueEx(subkey, "UninstallString")[0]
        if '.exe' in uninstall_path:
            full_path = uninstall_path.split('.exe')[0] + '.exe'
            full_path = full_path.replace('"', '')

            if 'uninstall' not in full_path.lower() and os.path.exists(full_path):
                logger.debug(f"Found executable from UninstallString: {full_path}")
                return full_path
            else:
                logger.debug(f"Skipping UninstallString path: {full_path}")
    except Exception as e:
        logger.debug(f"UninstallString lookup failed: {e}")

    return None


def find_application_registry(app_name):
    """Helper: Finds application path from Windows registry.

    Args:
        app_name: Name of the application to find

    Returns:
        Full path to .exe file, or None if not found
    """
    app_name_lower = app_name.lower()
    logger.debug(f"Searching registry for application: {app_name}")

    registry_roots = [
        (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
        (winreg.HKEY_CURRENT_USER, "HKCU")
    ]

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    partial_matches = []

    for root, root_name in registry_roots:
        for reg_path in registry_paths:
            try:
                key = winreg.OpenKey(root, reg_path)
                num_subkeys = winreg.QueryInfoKey(key)[0]
                logger.debug(f"Checking registry path: {root_name}\\{reg_path} with {num_subkeys} entries")

                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        display_name_lower = display_name.lower()

                        if app_name_lower == display_name_lower:
                            logger.debug(f"Found exact match: {display_name}")

                            full_path = extract_exe_from_registry(subkey, display_name)
                            if full_path:
                                winreg.CloseKey(subkey)
                                winreg.CloseKey(key)
                                return full_path

                        elif app_name_lower in display_name_lower:
                            logger.debug(f"Found partial match: {display_name}")
                            partial_matches.append((subkey_name, display_name, root, reg_path))

                        winreg.CloseKey(subkey)
                    except Exception:
                        continue

                winreg.CloseKey(key)
            except Exception as e:
                logger.debug(f"Could not open registry path {root_name}\\{reg_path}: {e}")

    if partial_matches:
        logger.debug(f"No exact match found, checking {len(partial_matches)} partial matches")
        for subkey_name, display_name, root, reg_path in partial_matches:
            try:
                key = winreg.OpenKey(root, reg_path)
                subkey = winreg.OpenKey(key, subkey_name)

                full_path = extract_exe_from_registry(subkey, display_name)
                if full_path:
                    winreg.CloseKey(subkey)
                    winreg.CloseKey(key)
                    return full_path

                winreg.CloseKey(subkey)
                winreg.CloseKey(key)
            except Exception:
                continue

    logger.debug(f"Application not found in registry: {app_name}")
    return None


def get_running_processes():
    """Helper: Gets list of currently running process names.

    Returns:
        List of process names (e.g., ['notepad.exe', 'chrome.exe', ...])"""

    try:
        import psutil
        processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        return processes
    except ImportError:
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            lines = result.stdout.split('\n')[3:]
            processes = []

            for line in lines:
                if line.strip():
                    process_name = line.split()[0].lower()
                    processes.append(process_name)
            return processes
        except Exception as e:
            logger.debug(f"Could not retrieve process list: {e}")
            return []

def is_app_running(app_name):
    """Helper: Checks if an application is currently running.

    Args:
        app_name: Name of app to check (e.g. 'notepad', 'chrome')

    Returns:
        Boolean indicating if app is running"""

    processes = get_running_processes()
    app_lower = app_name.lower()

    checks = [
        f"{app_lower}.exe",
        app_lower,
    ]
    logger.debug(f"Checking for running processes matching: {checks}")

    for process in processes:
        for check in checks:
            if check in process:
                logger.debug(f"Found running process: {process}")
                return True

    return False
