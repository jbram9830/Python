import os
import subprocess
import yaml
from pathlib import Path

# User settings
cluster_name = "mycluster"
base_domain = "example.com"
pull_secret_path = "/path/to/pull-secret.txt"
ssh_key_path = "/home/user/.ssh/id_rsa.pub"
output_dir = Path.home() / "openshift-install"
install_binary = "/usr/local/bin/openshift-install"

# Hosts config
master_nodes = [
    {"name": "master-0", "ip": "192.168.1.10", "mac": "52:54:00:00:00:10"},
    {"name": "master-1", "ip": "192.168.1.11", "mac": "52:54:00:00:00:11"},
    {"name": "master-2", "ip": "192.168.1.12", "mac": "52:54:00:00:00:12"},
]
worker_nodes = [
    {"name": "worker-0", "ip": "192.168.1.20", "mac": "52:54:00:00:00:20"},
]

# Red Hat CoreOS image
rhcos_image_url = "https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/latest/latest/rhcos-live.x86_64.iso"

def load_pull_secret():
    with open(pull_secret_path, "r") as f:
        return f.read()

def load_ssh_key():
    with open(ssh_key_path, "r") as f:
        return f.read()

def create_install_config():
    config = {
        "apiVersion": "v1",
        "baseDomain": base_domain,
        "metadata": {
            "name": cluster_name
        },
        "compute": [{
            "name": "worker",
            "replicas": len(worker_nodes),
            "platform": {}
        }],
        "controlPlane": {
            "name": "master",
            "replicas": len(master_nodes),
            "platform": {},
        },
        "platform": {
            "baremetal": {
                "apiVIP": "192.168.1.5",
                "ingressVIP": "192.168.1.6",
                "externalBridge": "baremetal",
                "provisioningBridge": "provisioning",
                "hosts": master_nodes + worker_nodes,
                "provisioningNetwork": "Disabled",
                "bootstrapOSImage": rhcos_image_url,
                "clusterOSImage": rhcos_image_url,
            }
        },
        "pullSecret": load_pull_secret(),
        "sshKey": load_ssh_key()
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "install-config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

def run_installer():
    os.chdir(output_dir)
    subprocess.run([install_binary, "create", "manifests"], check=True)
    subprocess.run([install_binary, "create", "ignition-configs"], check=True)

def main():
    print("Creating install-config.yaml...")
    create_install_config()
    print("Running OpenShift installer...")
    run_installer()
    print("Done. You can now boot nodes using the generated Ignition configs.")

if __name__ == "__main__":
    main()