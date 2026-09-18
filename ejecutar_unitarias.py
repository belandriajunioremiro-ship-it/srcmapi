import pytest
import sys
import os

class BeautifulReporter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0

    def pytest_sessionstart(self, session):
        print("\n" + "="*70)
        print("     >>> SUITE DE PRUEBAS UNITARIAS SRCM (NIVEL EXPERTO) <<<      ")
        print("="*70 + "\n")

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self.total += 1
            partes = report.nodeid.split("::")
            modulo = partes[0].split("/")[-1].replace("test_", "").replace(".py", "").upper()
            prueba = partes[-1].replace("test_", "").replace("_", " ").capitalize()
            
            display_name = f"  {modulo[:15]:<15} | {prueba[:40]}"
            
            if report.passed:
                self.passed += 1
                print(f"{display_name:.<62} [ OK ]")
            elif report.failed:
                self.failed += 1
                print(f"{display_name:.<62} [ERROR ]")
            elif report.skipped:
                print(f"{display_name:.<62} [OMITID]")

    def pytest_sessionfinish(self, session, exitstatus):
        print("\n" + "="*70)
        print(f" RESUMEN: {self.total} Pruebas Totales | {self.passed} Pasadas | {self.failed} Fallidas")
        if self.failed == 0:
            print("           [+] PRUEBAS UNITARIAS COMPLETADAS AL 100% [+]          ")
        else:
            print("               [-] SE ENCONTRARON ERRORES EN LAS PRUEBAS [-]      ")
        print("="*70 + "\n")

if __name__ == "__main__":
    # Desactivar variables de entorno que pudieran hacer ruido
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    
    # Ejecutar pytest y sobreescribir el comportamiento detallado del pytest.ini
    args = [
        "tests/unitarios/", 
        "-o", "addopts=", # Sobrescribe addopts de pytest.ini
        "-p", "no:terminal" # Desactiva el reporter por defecto
    ]
    
    # Usamos nuestro propio plugin
    pytest.main(args, plugins=[BeautifulReporter()])
