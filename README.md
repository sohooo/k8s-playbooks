# RKE2-Cluster-Playbooks

## Schnellstart

### Einrichtung
1. Repository klonen und in das Verzeichnis wechseln:
   ```bash
git clone git@github.com:your-org/k8s-playbooks.git
cd k8s-playbooks
```
2. Lokale Python-Umgebung einrichten und aktivieren:
   ```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```
3. Installation überprüfen:
   ```bash
ansible --version
ansible-lint --version
```

### Beispiele
- Inventar visualisieren:
  ```bash
ansible-inventory -i inventories/hosts.ini --graph
```
- Wartung für einen Cluster als Trockenlauf ausführen:
  ```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha --check
```
- Wartung für einen einzelnen Host durchführen:
  ```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02
```

## Repository-Layout

```
.
├── docs/                     # Ausführliche Dokumentation und Onboarding-Material
├── inventories/
│   └── hosts.ini             # Statisches Inventar für die verwalteten Cluster
├── playbooks/
│   ├── maintenance.yml       # Einstiegspunkt für den Wartungs-Workflow
│   └── tasks/
│       └── common/           # Wiederverwendbare Aufgabenbausteine für Wartungsaktionen
└── scripts/
    └── setup-ansible.sh      # Hilfsskript zum Einrichten der Tooling-Umgebung
```

Weiterführende Informationen finden sich in [`docs/README.md`](docs/README.md).

## Anforderungen

- Ansible 2.12+ (getestete Syntax)
- Zugriff auf die Zielknoten mit Rechten zur Privileg-Erhöhung (`become`)
- `kubectl` auf Control-Plane-Knoten verfügbar (Worker delegieren Kubernetes-Operationen an einen Control-Plane-Host)

## Playbooks im Überblick

- `playbooks/maintenance.yml` – führt einen rollierenden Wartungsablauf pro Knoten durch (Drain, Update, Reboot, Uncordon) und priorisiert Control-Plane-Knoten.
- `playbooks/upgrade-rke2.yml` – aktualisiert RKE2-Server- und Agent-Knoten auf die Version aus `/etc/rke2-release`, inklusive Drain/Uncordon-Logik und Service-Neustarts.

## Lokale Entwicklungsumgebung

Richte eine lokale Python-Umgebung ein und installiere Ansible sowie die genutzten Linting-Tools mit dem Hilfsskript:

```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```

> Das Skript erzeugt standardmäßig ein `.venv`-Verzeichnis im Repository. Über die Umgebungsvariable `VENV_DIR` lässt sich ein alternativer Pfad festlegen.

Überprüfe anschließend die Installation:

```bash
ansible --version
ansible-lint --version
```

> **Tipp:** Aktiviere die virtuelle Umgebung (`source .venv/bin/activate`) in jeder neuen Shell, damit die installierten Werkzeuge verfügbar sind.

## Nutzung

Inventargraph ansehen:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

Wartungs-Workflow für einen einzelnen Cluster starten:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

Einen spezifischen Host oder Knotentyp ansteuern:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube02
```

> **Hinweis:** Die Plays laufen mit `serial: 1`, sodass die Wartung jeweils nur einen Knoten gleichzeitig betrifft.

### Ad-hoc-Kommandos ausführen

Mit Ansible-Ad-hoc-Kommandos lassen sich schnelle Prüfungen oder Eingriffe ohne kompletten Playbook-Lauf durchführen. Die Beispiele nutzen das Inventar `inventories/hosts.ini` und zeigen typische Aufgaben für einen RKE2-Cluster. Passe `--limit` an, um die Zielhosts einzugrenzen.

Kubernetes-Versionen der Control-Plane-Knoten prüfen:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube01,kube02,kube03' \
  -m ansible.builtin.command \
  -a 'kubectl version --short'
```

RKE2-Dienste auf Control-Plane- und Worker-Knoten verifizieren:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube01,kube02,kube03' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-server'

ansible -i inventories/hosts.ini kube_alpha \
  --limit 'kube04,kube05' \
  -m ansible.builtin.command \
  -a 'systemctl is-active rke2-agent'
```

Knotenstatus auf einem Control-Plane-Host anzeigen und nach `Ready` filtern:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit kube01 \
  -m ansible.builtin.shell \
  -a "kubectl get nodes --no-headers | awk '{print \$1, \$2}'"
```

Pod-Scheduling-Druck clusterweit analysieren:

```bash
ansible -i inventories/hosts.ini kube_alpha \
  --limit kube01 \
  -m ansible.builtin.shell \
  -a "kubectl get pods -A --field-selector=status.phase!=Running"
```

> **Tipp:** Ergänze `-b`, wenn Kommandos Privileg-Erhöhung erfordern, und passe `--limit` an, um die Zielhosts einzugrenzen.

## Verifikation

Nach Änderungen an Playbooks oder Inventar sollten folgende Kommandos in einer aktivierten virtuellen Umgebung ausgeführt werden:

```bash
# Inventar-Ladevorgang prüfen
ansible-inventory -i inventories/hosts.ini --graph

# Playbook-Inhalte linten
ansible-lint playbooks/maintenance.yml

# Syntax-Check ohne Host-Verbindungen
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```
