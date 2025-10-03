# Ansible-Tipps für die Entwicklung

Diese Techniken helfen dir, gefahrlos zu experimentieren, schneller zu iterieren und unerwartetes Verhalten zu analysieren, wenn du an den Playbooks in diesem Repository arbeitest.

## Sichere Probeläufe

- **Syntax validieren** – Starte immer mit einem Parse-Check, um Einrückungs- oder YAML-Fehler zu finden, bevor Hosts angesprochen werden:
  ```bash
  ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml --syntax-check
  ```
- **No-Op-Trockenläufe** – Nutze den Check-Mode, um geplante Änderungen ohne Ausführung zu sehen. In Kombination mit `--limit` bleibt die Ausgabe übersichtlich:
  ```bash
  ansible-playbook -i inventories/hosts.ini playbooks/maintenance.yml \
    --check --limit kube_alpha
  ```
- **Diff-Ausgabe** – Ergänze `--diff`, wenn du Datei- oder Template-Änderungen einsehen möchtest, die Ansible in einem echten Lauf anwenden würde.

## Spezifische Aufgaben ansteuern

- **Nur getaggte Schritte ausführen** – Versehen lange oder optionale Tasks mit Tags und führe sie bei Bedarf mit `--tags some_tag` aus. Unterdrücke laute Abschnitte mit `--skip-tags`.
- **An einer Aufgabe fortsetzen** – Nach einem fehlgeschlagenen Lauf kannst du mit `--start-at-task "Task name"` an der nächsten relevanten Aufgabe weiterarbeiten, ohne bereits erledigte Schritte zu wiederholen.
- **Betroffene Hosts und Tasks listen** – Kombiniere `--list-hosts`, `--list-tasks` oder `--list-tags` mit anderen Flags, um vorab zu prüfen, was ausgeführt würde.

## Debug-Ausgabe

- **Verbosity erhöhen** – Verwende `-v`, `-vv` oder `-vvv`, um Modulargumente, templated Werte und SSH-Details zu sehen. `-vvvv` sollte speziellen SSH-Analysen vorbehalten sein.
- **Vor jedem Task bestätigen** – Mit `--step` bestätigst du jede Aufgabe einzeln und kannst komplexe Logik Schritt für Schritt untersuchen.
- **Task-Kontext erfassen** – Füge temporäre `debug:`-Tasks ein, um Variablen auszugeben. Für große Strukturen sorgt `var` dafür, dass Ansible das Format automatisch aufbereitet:
  ```yaml
  - name: Host-Konfiguration prüfen
    ansible.builtin.debug:
      var: hostvars[inventory_hostname]
  ```

## Tipps für die lokale Iteration

- **Gleiche virtuelle Umgebung wiederverwenden** – Aktiviere die Tooling-Umgebung (`source .venv/bin/activate`), damit die richtige Ansible-Version und benötigte Collections geladen werden.
- **Fakten während Tests cachen** – Das Sammeln von Fakten kann bei großen Inventaren dauern. Setze `ANSIBLE_FACT_PATH` auf ein beschreibbares Verzeichnis und aktiviere `fact_caching=jsonfile` in `ansible.cfg`, um die Ergebnisse während der Iteration zwischenzuspeichern.
- **Variablen-Priorität validieren** – Bei der Fehlersuche rund um Überschreibungen hilft `ansible-inventory ... --host <hostname>`, um die zusammengeführten Variablen eines Hosts anzuzeigen.

## Analyse nach dem Lauf

- **Recap auswerten** – Achte auf `changed`- und `failed`-Zähler pro Host. Wenn ein Host im Check-Mode dauerhaft `changed=0` zeigt, würde in einem echten Lauf nichts passieren.
- **Logs speichern** – Leite Ausgaben nach `tee` um (`ansible-playbook ... | tee logs/maintenance.log`), damit du Details später prüfen oder mit dem Team teilen kannst.

Setze diese Muster kombiniert ein, um Änderungen abzusichern, die benötigten Informationen zu sammeln und reproduzierbare Abläufe zu gewährleisten.
