"""Configuración de pytest para FillRateRetail.

Configura el PYTHONPATH para que los tests puedan importar los módulos de `app/`.
"""

import sys
from pathlib import Path

# Agregar la raíz del proyecto al sys.path para que `import app` funcione
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# También agregar el directorio tests para imports relativos si se necesitan
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
