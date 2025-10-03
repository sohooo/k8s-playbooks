# Referenz zum Wartungs-Playbook

Die Datei `playbooks/maintenance.yml` ist der zentrale Einstiegspunkt für die geplante Wartung der RKE2-Cluster. Sie enthält zwei Plays, die denselben Wartungsblock nutzen und über die Host-Variable `controlplane` steuern, welche Aufgaben greifen.

## Ablaufreihenfolge

1. **Server-Play** – Ziel ist jeder Host im Inventar, allerdings werden Knoten ohne `controlplane=true` sofort übersprungen. Durch `serial: 1` wird die Wartung pro Server nacheinander abgeschlossen.
2. **Agent-Play** – Führt die gleiche Sequenz für Worker-Knoten aus. Jeder Host überspringt sich selbst, sobald `controlplane=true` gesetzt ist, und findet den passenden Delegations-Server, indem er seine Cluster-Mitgliedschaft mit Hosts kreuzt, die das `controlplane`-Flag tragen.

Die Aufteilung in zwei Plays hält die Orchestrierungslogik nachvollziehbar, während die geteilte Host-Variable den Pflegeaufwand für parallele Inventargruppen erspart.

...
Jede Befehlsaufgabe besitzt explizite `failed_when`-Regeln, sodass unerwartete Rückgabewerte sofort sichtbar werden.

> **Delegationshinweis:** RKE2-Worker-Knoten liefern weder `kubectl` noch eine KUBECONFIG mit. Das Playbook delegiert daher sämtliche Kubernetes-Kommandos an einen Control-Plane-Host desselben Clusters, sobald der aktuelle Zielhost das Werkzeug nicht bereitstellt. Dadurch bleibt der Wartungs-Workflow auf allen Knotentypen funktionsfähig, ohne die spezifische Scheduling-Logik zu verlieren.

## Workflow erweitern

- Ergänze neue Schritte im gemeinsamen Wartungsblock in `playbooks/maintenance.yml`, damit Server- und Agent-Plays synchron bleiben.
- Für optionale Schritte empfiehlt sich ein `block` mit klaren Bedingungen, damit das Verhalten nachvollziehbar bleibt.
- Benötigt eine neue Wartungsaktion zusätzliche Variablen, dokumentiere sie in der Task-Datei und lege nach Möglichkeit Default-Werte in `group_vars` fest.

Die Haupt-Playbook-Datei bleibt so schlank, während die eigentliche Umsetzung in gemeinsamen Task-Dateien die Lesbarkeit erhält und Erweiterungen erleichtert.

## Störungen beim Drain beheben

`kubectl drain` kann auf unbestimmte Zeit warten, wenn Pods sich nicht vertreiben lassen. Das Playbook stellt daher mehrere Variablen bereit, um das Verhalten anzupassen:

- `kube_drain_include_daemonsets` (Standard: `false`) – Bei `true` setzt der Befehl `--ignore-daemonsets=false` und wartet dadurch auf Pods, die von DaemonSets verwaltet werden. DaemonSets werden typischerweise sofort neu erstellt; der Drain wirkt daher blockiert, bis das DaemonSet vorher skaliert oder deaktiviert wird.
- `kube_drain_delete_emptydir_data` (Standard: `true`) – Aktiviert `--delete-emptydir-data`, sodass Pods mit `emptyDir`-Volumes beendet werden, anstatt den Drain zu blockieren.
- `kube_drain_timeout` (Standard: `10m`) – Mapped auf das native `--timeout` von `kubectl drain` und bricht die Aktion ab, sobald die Karenz abläuft. Die Angabe benötigt eine Einheit (z. B. `5m`, `30s`).
- `kube_kubectl_command_timeout` (Standard: `900`) – Begrenzt die Laufzeit aller delegierten `kubectl`-Aufrufe, damit Ansible-Tasks nicht unendlich laufen, wenn der Client hängt oder die Verbindung verliert.

Wenn ein Drain hängen bleibt oder abbricht, helfen diese Schritte:

1. Mit `kubectl get pods -A --field-selector spec.nodeName=<node> -o wide` prüfen, welche Pods blockieren. DaemonSet-Pods müssen gelöscht werden, indem das zugehörige DaemonSet auf null skaliert oder die Drain-Option, die sie einschließt, temporär deaktiviert wird.
2. Auf Pod-Disruption-Budgets achten (`kubectl get pdb -A`), die freiwillige Unterbrechungen verhindern können. Erhöhe deren `maxUnavailable` kurzfristig oder entferne sie, solange die Wartung läuft.
3. Wurde das Playbook in der Mitte abgebrochen, `kubectl uncordon <node>` ausführen, um Scheduling wieder zu ermöglichen und den Cluster zu stabilisieren, bevor ein neuer Versuch startet.
4. Nach der Fehlerbehebung das Wartungs-Play erneut ausführen. Die Drain-Aufgabe respektiert die konfigurierten Timeouts und schlägt schnell fehl, wenn Pods weiterhin blockieren, sodass manuelle Eingriffe möglich bleiben, ohne den Knoten dauerhaft zu sperren.
