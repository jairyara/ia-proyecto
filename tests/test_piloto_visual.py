"""Fixtures propias y temporales; ninguna prueba requiere imágenes externas/red/BD."""

from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image, PngImagePlugin

from src.vision.adquisicion import adquirir, descargar_bytes, guardar_nuevo, verificar_inventario_remoto
from src.vision.manifiesto import (
    MAX_BYTES, ErrorVisual, auditar_imagen, auditar_piloto, cargar_fuente,
    interpretar_ruta, json_bytes, ruta_segura, validar_inventario,
)


RUTA = "damaged/side/0101069901524_side.png"


def png(color=(10, 20, 30), size=(960, 540), mode="RGB", texto=None):
    salida = BytesIO()
    info = PngImagePlugin.PngInfo()
    if texto:
        info.add_text("nota", texto)
    Image.new(mode, size, color).save(salida, format="PNG", pnginfo=info)
    return salida.getvalue()


class ManifiestoVisualTests(unittest.TestCase):
    def test_inventario_real_fijado_balance_grupos_y_bytes(self):
        fuente, inventario = cargar_fuente()
        self.assertEqual(fuente["licencia_declarada"], "GPL 2")
        self.assertEqual(len(inventario), 400)
        side = [f for f in inventario if "/side/" in f["ruta"]]
        self.assertEqual(len({interpretar_ruta(f["ruta"])[2] for f in side}), 200)
        self.assertEqual(sum(f["bytes"] for f in side), 126285817)

    def test_inventario_rechaza_duplicados_etiquetas_y_grupos_cruzados(self):
        _, archivos = cargar_fuente()
        mutaciones = [
            lambda f: f.append(f[0]),
            lambda f: f.pop(),
            lambda f: f[0].update(ruta="unknown/side/0101069901524_side.png"),
            lambda f: f[0].update(bytes=True),
            lambda f: f[0].update(bytes=MAX_BYTES + 1),
            lambda f: f[100].update(ruta="damaged/top/9999999999999_top.png"),
        ]
        for mutar in mutaciones:
            f = deepcopy(archivos)
            mutar(f)
            with self.subTest(mutar=mutar), self.assertRaises(ErrorVisual):
                validar_inventario({"version": 2, "archivos": f})

    def test_rutas_inseguras_o_vistas_inconsistentes(self):
        for ruta in ("../secreto.png", "/tmp/x.png", "damaged\\side\\x.png", "damaged/side/0101069901524_top.png", "intact/top/1_top.png", "damaged/side/0101069901524_side.jpg"):
            with self.subTest(ruta=ruta), self.assertRaises(ErrorVisual):
                interpretar_ruta(ruta)

    def test_symlinks_fuera_y_dentro_se_rechazan(self):
        with TemporaryDirectory() as d:
            raiz = Path(d) / "visual"
            raiz.mkdir()
            destino = Path(d) / "fuera"
            destino.mkdir()
            (raiz / "damaged").symlink_to(destino, target_is_directory=True)
            with self.assertRaises(ErrorVisual):
                ruta_segura(raiz, RUTA)
            (raiz / "damaged").unlink()
            (raiz / "otra").mkdir()
            (raiz / "damaged").symlink_to(raiz / "otra", target_is_directory=True)
            with self.assertRaises(ErrorVisual):
                ruta_segura(raiz, RUTA)

    def test_png_valido_sin_conversion_y_etiqueta_de_origen(self):
        contenido = png()
        registro = auditar_imagen(contenido, RUTA)
        self.assertEqual((registro.ancho, registro.alto, registro.modo), (960, 540, "RGB"))
        self.assertEqual(registro.etiqueta_origen, "damaged")
        self.assertEqual(registro.etiqueta, "danado")
        self.assertEqual(registro.grupo_origen, "0101069901524")
        self.assertEqual(registro.bytes, len(contenido))

    def test_hash_pixeles_detecta_duplicado_con_metadatos_distintos(self):
        a = auditar_imagen(png(texto="a"), RUTA)
        b = auditar_imagen(png(texto="b"), RUTA)
        self.assertNotEqual(a.sha256, b.sha256)
        self.assertEqual(a.sha256_pixeles, b.sha256_pixeles)

    def test_imagenes_corruptas_truncadas_y_limites(self):
        for contenido in (b"", b"<html>login</html>", png()[:120], b"x" * (MAX_BYTES + 1), png(size=(961, 540)), png(mode="RGBA", color=(1, 2, 3, 4)), png(size=(2000, 2000))):
            with self.subTest(bytes=len(contenido)), self.assertRaises(ErrorVisual):
                auditar_imagen(contenido, RUTA)

    def test_jpeg_disfrazado_png_rechazado(self):
        salida = BytesIO()
        Image.new("RGB", (960, 540)).save(salida, format="JPEG")
        with self.assertRaises(ErrorVisual):
            auditar_imagen(salida.getvalue(), RUTA)

    def test_guardar_nuevo_no_sobrescribe_ni_deja_temporales(self):
        with TemporaryDirectory() as d:
            ruta = Path(d) / "original.png"
            guardar_nuevo(ruta, b"original")
            with self.assertRaises(FileExistsError):
                guardar_nuevo(ruta, b"otro")
            self.assertEqual(ruta.read_bytes(), b"original")
            self.assertEqual(list(Path(d).iterdir()), [ruta])

    def test_dry_run_sin_red_sin_directorios_y_sin_manifiesto(self):
        with TemporaryDirectory() as d, patch("src.vision.adquisicion.descargar_bytes", side_effect=AssertionError("Red prohibida")):
            raiz, manifiesto = Path(d) / "visual", Path(d) / "piloto.json"
            resultado = adquirir(raiz, manifiesto, dry_run=True)
            self.assertEqual(resultado["imagenes"], 200)
            self.assertFalse(raiz.exists())
            self.assertFalse(manifiesto.exists())

    def test_respuesta_remota_paginada_y_version_en_url(self):
        _, archivos = cargar_fuente()
        pages = [
            {"datasetFiles": [{"name": f["ruta"], "totalBytes": f["bytes"]} for f in archivos[:200]], "nextPageToken": "pagina2"},
            {"datasetFiles": [{"name": f["ruta"], "totalBytes": f["bytes"]} for f in archivos[200:]]},
        ]
        with patch("src.vision.adquisicion.descargar_bytes", side_effect=[json_bytes(p) for p in pages]) as descargar:
            verificar_inventario_remoto(archivos)
        self.assertEqual(descargar.call_count, 2)
        self.assertTrue(all("datasetVersionNumber=2" in c.args[0] for c in descargar.call_args_list))
        self.assertIn("pageToken=pagina2", descargar.call_args_list[1].args[0])

    def test_inventario_remoto_alterado_y_bucle_paginacion(self):
        _, archivos = cargar_fuente()
        with patch("src.vision.adquisicion.descargar_bytes", return_value=json_bytes({"datasetFiles": [], "nextPageToken": "repetido"})):
            with self.assertRaisesRegex(ErrorVisual, "repetido"):
                verificar_inventario_remoto(archivos)
        with patch("src.vision.adquisicion.descargar_bytes", return_value=json_bytes({"datasetFiles": []})):
            with self.assertRaises(ErrorVisual):
                verificar_inventario_remoto(archivos)


class PilotoConFixturesTests(unittest.TestCase):
    """200 originales artificiales propios solo para probar la lógica, nunca el dataset."""

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name) / "originales"
        self.manifiesto = Path(self.tmp.name) / "manifiesto.json"
        self.datos = {}
        inventario = []
        for i in range(200):
            clase = "damaged" if i < 100 else "intact"
            serial = f"{i:013d}"
            ruta = f"{clase}/side/{serial}_side.png"
            datos = png(color=(i, i // 2, 100))
            self.datos[ruta] = datos
            inventario.append({"ruta": ruta, "bytes": len(datos)})
        self.inventario = inventario
        for modulo in ("src.vision.manifiesto", "src.vision.adquisicion"):
            parche = patch(modulo + ".cargar_fuente", return_value=({}, inventario))
            parche.start()
            self.addCleanup(parche.stop)

    def llenar(self):
        for ruta, datos in self.datos.items():
            destino = ruta_segura(self.raiz, ruta)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(datos)

    def test_piloto_completo_reverificacion_y_tamper_manifiesto(self):
        self.llenar()
        resultado = auditar_piloto(self.raiz)
        self.assertEqual(len(resultado["imagenes"]), 200)
        self.assertEqual(auditar_piloto(self.raiz, manifiesto=resultado), resultado)
        cambiado = deepcopy(resultado)
        cambiado["imagenes"][0]["etiqueta"] = "intacto"
        with self.assertRaisesRegex(ErrorVisual, "difieren"):
            auditar_piloto(self.raiz, manifiesto=cambiado)

    def test_faltante_y_duplicado_no_se_completan(self):
        self.llenar()
        primero, segundo = list(self.datos)[:2]
        path = ruta_segura(self.raiz, segundo)
        path.unlink()
        with self.assertRaises(ErrorVisual):
            auditar_piloto(self.raiz)
        path.write_bytes(self.datos[primero])
        self.inventario[1]["bytes"] = len(self.datos[primero])
        with self.assertRaisesRegex(ErrorVisual, "duplicadas"):
            auditar_piloto(self.raiz)

    def test_adquisicion_reanudable_idempotente_y_versionada(self):
        from urllib.parse import unquote, urlparse
        def descargar(url, limite):
            ruta = unquote(urlparse(url).path.split("industrial-quality-control-of-packages/")[1])
            self.assertIn("datasetVersionNumber=2", url)
            return self.datos[ruta]
        with patch("src.vision.adquisicion.verificar_inventario_remoto"), patch("src.vision.adquisicion.descargar_bytes", side_effect=descargar) as red:
            # El progreso es texto: suprimirlo sin sustituir el procesamiento real.
            with patch("src.vision.adquisicion.print"):
                resultado = adquirir(self.raiz, self.manifiesto)
                self.assertEqual(red.call_count, 200)
                original = self.manifiesto.read_bytes()
                repetido = adquirir(self.raiz, self.manifiesto)
        self.assertEqual(resultado["estado"], "adquirido_y_auditado")
        self.assertEqual(repetido["estado"], "sin_cambios")
        self.assertEqual(red.call_count, 200)
        self.assertEqual(self.manifiesto.read_bytes(), original)

    def test_fallo_parcial_no_publica_manifiesto_y_reintento_reusa_originales(self):
        from urllib.parse import unquote, urlparse
        llamadas = 0
        def descargar(url, limite):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 3:
                raise ErrorVisual("fallo simulado")
            return self.datos[unquote(urlparse(url).path.split("industrial-quality-control-of-packages/")[1])]
        with patch("src.vision.adquisicion.verificar_inventario_remoto"), patch("src.vision.adquisicion.descargar_bytes", side_effect=descargar), patch("src.vision.adquisicion.print"):
            with self.assertRaisesRegex(ErrorVisual, "simulado"):
                adquirir(self.raiz, self.manifiesto)
            self.assertFalse(self.manifiesto.exists())
            self.assertEqual(len(list(self.raiz.rglob("*.png"))), 2)
            adquirir(self.raiz, self.manifiesto)
        self.assertTrue(self.manifiesto.exists())
        self.assertEqual(llamadas, 201)  # dos originales reutilizados, una llamada fallida.

    def test_original_local_corrupto_no_se_sobrescribe(self):
        self.llenar()
        ruta = ruta_segura(self.raiz, next(iter(self.datos)))
        ruta.write_bytes(b"corrupto")
        with patch("src.vision.adquisicion.verificar_inventario_remoto"), patch("src.vision.adquisicion.descargar_bytes", side_effect=AssertionError("No descargar")):
            with self.assertRaises(ErrorVisual):
                adquirir(self.raiz, self.manifiesto)
        self.assertEqual(ruta.read_bytes(), b"corrupto")
