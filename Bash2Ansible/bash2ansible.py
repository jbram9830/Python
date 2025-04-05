import re
import sys
import yaml
from typing import List, Dict


def bash_to_ansible_task(bash_line: str) -> Dict:
    """
    Converts a single line of a Bash command into an Ansible task dictionary.
    Now supports hammer CLI commands for Red Hat Satellite.
    """
    bash_line = bash_line.strip()

    if bash_line.startswith("mkdir"):
        match = re.findall(r"mkdir\s+-p\s+([^\s]+)", bash_line)
        if match:
            return {
                "name": f"Create directory {match[0]}",
                "file": {"path": match[0], "state": "directory"}
            }

    elif bash_line.startswith("chmod"):
        match = re.findall(r"chmod\s+([0-7]+)\s+([^\s]+)", bash_line)
        if match:
            mode, path = match[0]
            return {
                "name": f"Set permissions for {path}",
                "file": {"path": path, "mode": mode}
            }

    elif bash_line.startswith("chown"):
        match = re.findall(r"chown\s+([^\s:]+):?([^\s]*)\s+([^\s]+)", bash_line)
        if match:
            user, group, path = match[0]
            return {
                "name": f"Set owner for {path}",
                "file": {"path": path, "owner": user, "group": group if group else user}
            }

    elif "yum install" in bash_line:
        pkgs = re.findall(r"yum install\s+(-y\s+)?(.+)", bash_line)
        if pkgs:
            packages = pkgs[0][1].split()
            return {
                "name": f"Install packages {' '.join(packages)}",
                "yum": {"name": packages, "state": "present"}
            }

    elif bash_line.startswith("git clone"):
        match = re.findall(r"git clone\s+([^\s]+)", bash_line)
        if match:
            return {
                "name": f"Clone repository {match[0]}",
                "git": {"repo": match[0], "dest": "/home/user/repo"}
            }

    elif bash_line.startswith("cp"):
        match = re.findall(r"cp\s+([^\s]+)\s+([^\s]+)", bash_line)
        if match:
            src, dest = match[0]
            return {
                "name": f"Copy {src} to {dest}",
                "copy": {"src": src, "dest": dest}
            }

    elif bash_line.startswith("make"):
        return {
            "name": f"Run make command: {bash_line}",
            "command": bash_line,
            "args": {"chdir": "/home/user/repo"}
        }

    elif bash_line.startswith("hammer"):
        # Translate basic hammer commands into ansible foreman module calls
        match = re.findall(r"hammer\s+(\S+)\s+(\S+)\s+(.+)", bash_line)
        if match:
            resource, action, params = match[0]
            return {
                "name": f"Manage Satellite resource: {resource} {action}",
                "shell": bash_line  # For now, use shell. Can be improved with specific modules.
            }

    else:
        return {
            "name": f"Run raw command: {bash_line}",
            "shell": bash_line
        }

    return {}


def translate_bash_script(bash_script: List[str]) -> List[Dict]:
    """ Converts a list of Bash script lines into a list of Ansible tasks """
    tasks = []
    for line in bash_script:
        if line.strip() and not line.strip().startswith("#"):
            task = bash_to_ansible_task(line)
            if task:
                tasks.append(task)
    return tasks


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_bash_script.sh> <output_ansible.yml>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, "r") as f:
            bash_script = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    tasks = translate_bash_script(bash_script)

    ansible_playbook = {
        "name": "Convert Bash Script to Ansible Playbook",
        "hosts": "all",
        "become": True,
        "tasks": tasks
    }

    with open(output_file, "w") as f:
        yaml.dump(ansible_playbook, f, default_flow_style=False)

    print(f"✅ Ansible playbook saved to {output_file}")


if __name__ == "__main__":
    main()
