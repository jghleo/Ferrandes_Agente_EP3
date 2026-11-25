"""Pruebas de los componentes de observabilidad, trazabilidad y seguridad (EP3)."""
import json
import unittest
from pathlib import Path

from src.config import RAIZ
from src.observabilidad.metricas import calcular_precision, normalizar, resumen, Medicion
from src.observabilidad.seguridad import GuardiaSeguridad, detectar_pii, redactar
from src.observabilidad.trazas import analizar_trazas


class TestObservabilidad(unittest.TestCase):
    def test_normalizar_ignora_ids_dinamicos(self):
        a = "Pedido PAT-000123 confirmado a las 2026-10-21T10:00:00"
        b = "Pedido PAT-000999 confirmado a las 2026-10-22T11:30:00"
        self.assertEqual(normalizar(a), normalizar(b))

    def test_precision_componentes(self):
        valor = calcular_precision("stock", "stock", {"consultar_stock"},
                                   {"consultar_stock"}, "tor-001", "Stock de TOR-001: 850")
        self.assertEqual(valor, 1.0)
        valor = calcular_precision("stock", "precio", {"consultar_stock"},
                                   set(), "tor-001", "sin dato")
        self.assertEqual(valor, 0.0)

    def test_resumen_calcula_p95(self):
        base = dict(consulta="q", variabilidad="nominal", intencion_esperada="stock",
                    intencion_observada="stock", precision=1.0, consistencia=1.0,
                    error_inesperado=False, error_esperado=False, respuesta_normalizada="r",
                    repeticiones=1, herramientas_esperadas=[], herramientas_observadas=[],
                    rss_inicial_mb=10, rss_final_mb=12, cpu_promedio_pct=5,
                    clasificacion_ms=0.1, rag_ms=0.1, ejecucion_ms=0.1,
                    timestamp="2026-10-21T00:00:00")
        mediciones = [Medicion(escenario=f"S{i}", latencia_ms=v, **base)
                      for i, v in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]
        res = resumen(mediciones)
        self.assertEqual(res["latencia_p50_ms"], 5.5)
        self.assertEqual(res["latencia_p95_ms"], 9.55)
        self.assertEqual(res["precision_media"], 1.0)


class TestSeguridad(unittest.TestCase):
    def test_redactar_pii(self):
        texto = "RUT 12.345.678-5, mail juan.perez@example.cl y telefono 912345678"
        limpio = redactar(texto)
        self.assertIn("[RUT]", limpio)
        self.assertIn("[EMAIL]", limpio)
        self.assertFalse(detectar_pii(limpio))

    def test_guardia_bloquea_sin_consentimiento(self):
        guardia = GuardiaSeguridad(ruta=RAIZ / "evidencia" / "consentimientos.json")
        ok, _ = guardia.puede_escribir("CL-9999")
        self.assertFalse(ok)
        ok, _ = guardia.puede_escribir("CL-001")
        self.assertTrue(ok)


class TestTrazabilidad(unittest.TestCase):
    def test_detecta_falso_negativo_historico(self):
        historico = [{"consulta": "stock HER-001",
                      "respuesta": "No existe el producto HER en el catalogo."}]
        analisis = analizar_trazas([], {}, historico, {"HER-001"})
        falsos = [h for h in analisis["hallazgos"] if h["id"] == "P01"]
        self.assertEqual(falsos[0]["cantidad"], 1)
        self.assertEqual(falsos[0]["estado"], "corregido")

    def test_evidencia_generada_es_valida(self):
        ruta = RAIZ / "evidencia" / "metricas.json"
        if not ruta.exists():
            self.skipTest("Ejecutar primero scripts/evaluar_observabilidad.py")
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertGreaterEqual(datos["n_escenarios"], 10)
        self.assertGreaterEqual(datos["precision_media"], 0.8)
        self.assertLess(datos["tasa_error_inesperado"], 0.2)


if __name__ == "__main__":
    unittest.main()
