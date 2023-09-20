---
title: Prometheus

description: "Exposing Prometheus metrics using ServiceMonitor."
weight: 2000
doctypes: [""]
aliases:
    - /prometheus-servicemonitor/
toc: true
docs: "DOCS-614"
---

This document demonstrates deploying a Prometheus `ServiceMonitor` resource as part of an NGINX Ingress Controller Helm deployment.
The `ServiceMonitor` resource will describe the target `Service` to be monitored by a `Prometheus` resource.

# Preface
This document does **NOT** configure or deploy a `Prometheus` resource or a Prometheus Operator.
For details on deploying a Prometheus Operator, as well as deploying/configuring a `Prometheus` resource, see the [getting-started](https://prometheus-operator.dev/docs/user-guides/getting-started/) guide in the prometheus-operator docs.


# Prerequisites
Install the latest ServiceMonitor CRD from the [prometheus-operator](https://github.com/prometheus-operator/prometheus-operator) repo:
```console
LATEST=$(curl -s https://api.github.com/repos/prometheus-operator/prometheus-operator/releases/latest | jq -cr .tag_name)
curl https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/$LATEST/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml | kubectl create -f -
```


# Install
To configure a `ServiceMonitor` resource with your Helm to installation, set the following paramaters:
```shell
--set prometheus.service.create=true
--set prometheus.serviceMonitor.create=true
--set prometheus.serviceMonitor.labels.<you_custom_label_key>="<you_custom_label_value>"
```

This will deploy:
1. A `Service` to expose prometheus metrics from the Ingress Controller on port `9113`.
2. A `ServiceMonitor` resource configured to monitor the service exposing the metrics.

NOTE: The value of `prometheus.serviceMonitor.labels` can be set to any value that you wish to use.
The value of this label **must** match the value of `serviceMonitorSelector.matchLabels` in your `Prometheus` resource.

# Example YAMLs
The below YAML files are examples of what resources are deployed.
These YAML files are used to visualise what these configurations look like after deployment.

## Example ServiceMonitor and Service YAML

Example `ServiceMonitor` resource YAML:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    product: nic
  name: <you-release>-nginx-ingress-controller
spec:
  selector:
    matchLabels:
      service: nginx-ingress-prometheus-service # Matches on the label set by the Service.
  endpoints:
  - port: prometheus # Matches on the `name` of the port set by the Service.
```

Example `Service` resource YAML:
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    service: nginx-ingress-prometheus-service
  name: <your-release>-nginx-ingress-prometheus-service
spec:
  type: ClusterIP
  clusterIP: None
  ports:
    - name: prometheus
      port: 9113
      protocol: TCP
      targetPort: 9113
```

## Example Prometheus resource YAML
If you have a `Prometheus` resource deployed capture the `ServiceMonitor` resource, the YAML of that file will look something like this:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
    name: prometheus
spec:
  serviceAccountName: prometheus
  serviceMonitorNamespaceSelector: {} ## all namespaces
  serviceMonitorSelector:
    matchLabels:
      product: nic # Matches on the label set for the ServiceMonitor resource
```
