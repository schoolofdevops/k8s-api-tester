import argparse
import time
from kubernetes import client, config

def main():
    parser = argparse.ArgumentParser(description="Kubernetes API Permission Tester")
    parser.add_argument("--namespace", default="default", help="Namespace to check permissions within")
    parser.add_argument("--interval", type=int, default=30, help="Time interval for permission checks loop in seconds")
    args = parser.parse_args()

    # Load in-cluster configuration
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    while True:
        print("Starting the permission check loop...")
        check_permissions(v1, apps_v1, args.namespace)
        print(f"Sleeping for {args.interval} seconds...\n")
        time.sleep(args.interval)

def check_permissions(v1, apps_v1, namespace):
    # Check permissions for Pods, Deployments, Services
    check_resource_permissions(v1, apps_v1, namespace)
    # Check permissions for PVCs, PVs, and Events cluster-wide
    check_cluster_permissions(v1)

def check_resource_permissions(v1, apps_v1, namespace):
    resources = [
        ("pods", v1.list_namespaced_pod),
        ("deployments", apps_v1.list_namespaced_deployment),
        ("services", v1.list_namespaced_service)
    ]
    for resource_name, list_func in resources:
        try:
            list_func(namespace=namespace)
            print(f"Success: Read permission for {resource_name} in namespace {namespace} is granted.")
        except Exception as e:
            print(f"Failure: Read permission for {resource_name} in namespace {namespace} is denied. Error: {e}")

def check_cluster_permissions(v1):
    # Persistent Volume Claims
    try:
        v1.list_persistent_volume_claim_for_all_namespaces()
        print("Success: Read permission for PVCs cluster-wide is granted.")
    except Exception as e:
        print(f"Failure: Read permission for PVCs cluster-wide is denied. Error: {e}")

    # Persistent Volumes
    try:
        v1.list_persistent_volume_for_all_namespaces()
        print("Success: Read permission for PVs cluster-wide is granted.")
    except Exception as e:
        print(f"Failure: Read permission for PVs cluster-wide is denied. Error: {e}")

    # Events
    try:
        v1.list_event_for_all_namespaces()
        print("Success: Read permission for events cluster-wide is granted.")
    except Exception as e:
        print(f"Failure: Read permission for events cluster-wide is denied. Error: {e}")

if __name__ == '__main__':
    main()
