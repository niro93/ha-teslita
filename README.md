# Teslita für Home Assistant

Diese Integration zeigt in Home Assistant die von Teslita gespeicherten Fahrzeugdaten an. Sie fragt Fahrzeugdaten ausschließlich lesend ab und sendet keine Befehle an das Fahrzeug.

## Installation

### Marketplace (Home Assistant 2026.11 und neuer)

1. Öffne **Einstellungen → Marketplace** und wähle **Add from link**.
2. Gib `https://github.com/niro93/ha-teslita` ein und wähle **Add**. Falls nötig, wähle den Typ **Integration**.
3. Öffne **Teslita** im Marketplace und wähle **Install**.
4. Folge dem Einrichtungsdialog. Falls er nicht automatisch startet, füge **Teslita** unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** hinzu.

Bei der Einrichtung wird ein Teslita-API-Schlüssel mit dem Lesebereich `read` benötigt. Die Bereiche `write` und `control` sind nicht erforderlich.

## Fahrzeugdaten

Die Integration stellt folgende Daten bereit:

- Batteriestand, Ladestatus, Ladelimit und Restenergie
- Reichweite und Kilometerstand
- Reifendrücke (`tpms_bar`)
- Standort als Geräte-Tracker
- Bewegungsstatus als Binärsensor
- Zeitpunkt des letzten Signals (`last_signal_at`)

Die Integration liest Teslitas gespeicherte Telemetrie aus. Sie weckt oder steuert das Fahrzeug nicht. Wenn das Fahrzeug keine Daten sendet, können Werte und Standort veraltet sein. `last_signal_at` gibt den Zeitpunkt des letzten beliebigen Signals an, nicht den individuellen Aktualisierungszeitpunkt jedes Werts.

## Abfrageintervall

Das Intervall ist in den Optionen der Integration einstellbar. Standardmäßig werden Daten alle 300 Sekunden abgerufen; möglich sind 60 bis 3600 Sekunden. Teslita dokumentiert ein Limit von 120 Anfragen pro Minute und API-Schlüssel. Dieses Limit teilen sich alle Anwendungen, die denselben Schlüssel verwenden.

## API-Schlüssel entfernen

Beim Löschen des Integrationseintrags entfernt Home Assistant den gespeicherten API-Schlüssel. Der Schlüssel bleibt in Teslita aktiv und muss dort separat widerrufen werden.

## Entwicklung

Die Entwicklung dieser Integration erfolgte mit Unterstützung generativer KI.
