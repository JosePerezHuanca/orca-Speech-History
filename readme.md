# Historial de voz para orca

Esta extensión está basada en el complemento para NVDA[Speech History](https://github.com/jscholes/nvda-speech-history).

Speech History es una extensión que permite revisar los últimos 500 elementos verbalizados por orca.

## Instalación

Para ejecutar esta extensión necesitas mínimo la versión 51 alfa de orca.
Copia el script speech_history.py a `/home/tuusuario/.local/share/orca/extensions`
Necesitas aprobar la extensión. Puedes hacerlo desde la configuración de orca o ejecutando el siguiente comando:
`orca --approve-extension speech_history.py`

## Atajos

Nota: los siguientes atajos se pueden personalizar desde la configuración de orca en la categoría comandos/Speech History.

- Verbalizar el elemento anterior en el historial: shift+f11
- Verbalizar el siguiente elemento en el historial: shift+f12
- Copiar el elemento seleccionado en el historial o la última frase verbalizada por orca: f12
