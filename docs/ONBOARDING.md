# Onboarding-Leitfaden

Dieser Leitfaden hilft dir, mit den Playbooks schnell produktiv zu werden.

## 1. Repository klonen

```bash
git clone git@github.com:your-org/k8s-playbooks.git
cd k8s-playbooks
```

> Passe die Remote-URL an, wenn du über einen eigenen Fork beiträgst.

## 2. Tooling-Umgebung erstellen und aktivieren

Führe das Hilfsskript aus und aktiviere die Umgebung in derselben Shell:

```bash
./scripts/setup-ansible.sh
source .venv/bin/activate
```

Wenn du die virtuelle Umgebung außerhalb des Repositories ablegen möchtest, setze vor dem Aufruf die Variable `VENV_DIR`:

```bash
VENV_DIR=$HOME/.virtualenvs/k8s-playbooks ./scripts/setup-ansible.sh
source $HOME/.virtualenvs/k8s-playbooks/bin/activate
```

## 3. Installation validieren

Prüfe nach der Aktivierung, ob Ansible und der Linter verfügbar sind:

```bash
ansible --version
ansible-lint --version
```

## 4. Inventar erkunden

Visualisiere den Cluster-Aufbau, um sicherzustellen, dass du die verwalteten Knoten erreichst:

```bash
ansible-inventory -i inventories/hosts.ini --graph
```

Solltest du die Hosts nicht erreichen können, kontaktiere eine Administratorin oder einen Administrator, um SSH-Zugriff zu erhalten oder die Inventardatei anpassen zu lassen.

## 5. Wartungs-Playbook im Trockenlauf

Bevor du Änderungen vornimmst, führe einen Syntax-Check aus. So stellst du sicher, dass das Playbook ohne Host-Zugriff korrekt geparst wird:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
```

## 6. Änderungen verantwortungsvoll anwenden

Wenn du den Wartungs-Workflow gegen eine Testumgebung laufen lassen möchtest, beschränke die Ausführung auf den relevanten Cluster oder Host:

```bash
ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --limit kube_alpha
```

Nutze `--check` für einen sicheren Vorab-Run und beobachte die Ausgabe stets auf fehlgeschlagene Aufgaben. Wende dich an das Plattform-Team, falls du unerwartetes Verhalten feststellst.
