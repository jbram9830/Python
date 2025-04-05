import os
import subprocess
import yaml

# Customize these values
CLUSTER_NAME = "ocp-cluster"
BASE_DOMAIN = "example.com"
PULL_SECRET_PATH = "/path/to/pull-secret.txt"
SSH_KEY_PATH = "/home/user/.ssh/id_rsa.pub"
VSPHERE_DETAILS = {
    "vcenter": "vcenter.example.com",
    "username": "administrator@vsphere.local",
    "password": "your-vcenter-password",
    "datacenter": "Datacenter",
    "defaultDatastore": "datastore1",
    "network": "VM Network",
    "cluster": "vSphereCluster",
    "folder": "/Datacenter/vm/OpenShift"
}
OPENSHIFT_INSTALL_DIR = "./ocp-install"

INSTALL_CONFIG_PATH = os.path.join(OPENSHIFT_INSTALL_DIR, "install-config.yaml")

def create_install_config():
    with open(SSH_KEY_PATH, "r") as f:
        ssh_key = f.read().strip()

    with open(PULL_SECRET_PATH, "r") as f:
        pull_secret = f.read().strip()

    config = {
        "apiVersion": "v1",
        "baseDomain": BASE_DOMAIN,
        "metadata": {
            "name": CLUSTER_NAME
        },
        "platform": {
            "vsphere": {
                "vcenter": VSPHERE_DETAILS["vcenter"],
                "username": VSPHERE_DETAILS["username"],
                "password": VSPHERE_DETAILS["password"],
                "datacenter": VSPHERE_DETAILS["datacenter"],
                "defaultDatastore": VSPHERE_DETAILS["defaultDatastore"],
                "network": VSPHERE_DETAILS["network"],
                "cluster": VSPHERE_DETAILS["cluster"],
                "folder": VSPHERE_DETAILS["folder"]
            }
        },
        "compute": [
            {
                "name": "worker",
                "replicas": 3
            }
        ],
        "controlPlane": {
            "name": "master",
            "replicas": 3
        },
        "pullSecret": pull_secret,
        "sshKey": ssh_key
    }

    os.makedirs(OPENSHIFT_INSTALL_DIR, exist_ok=True)
    with open(INSTALL_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"install-config.yaml written to {INSTALL_CONFIG_PATH}")

def run_installer():
    cmd = ["openshift-install", "create", "cluster", "--dir", OPENSHIFT_INSTALL_DIR, "--log-level", "info"]
    subprocess.run(cmd)

def main():
    create_install_config()
    print("Running OpenShift Installer...")
    run_installer()

if __name__ == "__main__":
    main()
