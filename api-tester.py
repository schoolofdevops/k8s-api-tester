import argparse
from kubernetes import client, config
import sys

def main():
    parser = argparse.ArgumentParser(description="Kubernetes API Tester App")
    parser.add_argument("--namespace", required=True, help="Namespace to interact with")
    args = parser.parse_args()

    # Load in-cluster configuration
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    # Read Pods, Deployments, Services in a specific namespace
    try:
        print(f"Reading pods in namespace {args.namespace}:")
        pods = v1.list_namespaced_pod(namespace=args.namespace)
        for pod in pods.items:
            print(f"- Pod: {pod.metadata.name}")

        print(f"Reading deployments in namespace {args.namespace}:")
        deployments = apps_v1.list_namespaced_deployment(namespace=args.namespace)
        for dep in deployments.items:
            print(f"- Deployment: {dep.metadata.name}")

        print(f"Reading services in namespace {args.namespace}:")
        services = v1.list_namespaced_service(namespace=args.namespace)
        for service in services.items:
            print(f"- Service: {service.metadata.name}")
    except Exception as e:
        print(f"Error reading resources in namespace {args.namespace}: {e}")

    # PVCs and PVs operations
    try:
        print("Reading and updating PVCs cluster-wide:")
        pvcs = v1.list_persistent_volume_claim_for_all_namespaces()
        for pvc in pvcs.items:
            print(f"- PVC: {pvc.metadata.name}")

        print("Creating, updating, and deleting PVs cluster-wide:")
        # Example create PV
        pv_body = client.V1PersistentVolume(
            metadata=client.V1ObjectMeta(name='api-tester-pv'),
            spec=client.V1PersistentVolumeSpec(
                capacity={'storage': '1Gi'},
                access_modes=['ReadWriteOnce'],
                persistent_volume_reclaim_policy='Retain',
                storage_class_name='manual',
                host_path=client.V1HostPathVolumeSource(path='/mnt/data')
            )
        )
        pv = v1.create_persistent_volume(body=pv_body)
        print(f"Created PV: {pv.metadata.name}")

        # Update the created PV
        pv.spec.capacity = {'storage': '2Gi'}
        updated_pv = v1.patch_persistent_volume(name=pv.metadata.name, body=pv)
        print(f"Updated PV: {updated_pv.metadata.name}")

        # Delete the PV
        v1.delete_persistent_volume(name=pv.metadata.name)
        print(f"Deleted PV: {pv.metadata.name}")

    except Exception as e:
        print(f"Error managing PVCs/PVs: {e}")

    # Reading and updating Events
    try:
        print("Reading and updating events cluster-wide:")
        events = v1.list_event_for_all_namespaces()
        for event in events.items:
            print(f"- Event: {event.metadata.name} in {event.involved_object.namespace}")
            if event.reason == "ExampleReason":
                event.message = "Updated by API Tester"
                v1.patch_namespaced_event(name=event.metadata.name, namespace=event.involved_object.namespace, body=event)
                print(f"Updated event {event.metadata.name}")
    except Exception as e:
        print(f"Error reading/updating events: {e}")

if __name__ == '__main__':
    main()
