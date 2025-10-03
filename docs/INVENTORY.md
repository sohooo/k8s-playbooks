# Inventar-Konventionen

Das Repository liefert ein statisches Inventar unter [`inventories/hosts.ini`](../inventories/hosts.ini). Die Struktur erleichtert das gezielte Ansprechen einzelner Cluster und hält die pro Host gepflegten Metadaten schlank.

## Gruppenaufbau

- Jede Gruppe `kube_<name>` steht für einen einzelnen RKE2-Cluster.
- Jeder Cluster setzt die Variable `kube_cluster`, damit Plays sicherstellen können, dass Wartungsvorgänge immer nur einen Cluster betreffen.
- Jeder Cluster listet alle Knoten direkt unter seiner Gruppe auf und vererbt so `kube_cluster` an die Hosts.
- Control-Plane-Knoten setzen innerhalb des Clusters `controlplane=true`. Worker-Knoten lassen die Variable weg.

Beispielausschnitt:

```ini
[all:children]
kube_alpha

[kube_alpha:vars]
kube_cluster=kube_alpha

[kube_alpha]
kube01 controlplane=true
kube02 controlplane=true
kube03 controlplane=true
kube04
kube05
```

## Hosts ansteuern

- **Cluster:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha`
- **Einzelner Host:** `ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02`

Das Wartungs-Playbook unterscheidet automatisch zwischen Control-Plane- und Worker-Rollen, indem es die Host-Variable `controlplane` prüft. Zusätzliche Hilfsgruppen sind daher nicht nötig. Beim Anlegen neuer Cluster genügt es, einen vorhandenen Abschnitt zu kopieren und die Hostnamen anzupassen. Eine konsistente Benennung erleichtert Filterung und Monitoring.
