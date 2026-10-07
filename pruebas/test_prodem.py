"""Regresiones del HTML de Prodem: valores propios, oficial y errores."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from actualizar import extraer
from bancos import BANCOS

PRODEM = next(b for b in BANCOS if b['id'] == 'prodem')

class ProdemTests(unittest.TestCase):
    def test_tasas_independientes_del_modal_y_de_otros_valores(self):
        html = '''<div class="modal">Compra 6.86 Venta 6.96</div>
                  <div id="dolar-bcb">11.97</div>
                  <div id="prodem-compra">11.67</div>
                  <div id="prodem-venta">12.07</div>'''
        self.assertEqual(extraer(html, PRODEM),
                         {'compra':'11.67', 'venta':'12.07', 'oficial':'11.97'})

    def test_decimales_con_coma_y_elementos_anidados(self):
        html = '''<div id="prodem-compra"><span>Bs 11,67000</span></div>
                  <div id="prodem-venta">Bs 12,07000</div>'''
        self.assertEqual(extraer(html, PRODEM),
                         {'compra':'11.67', 'venta':'12.07', 'oficial':''})

    def test_no_acepta_solo_la_tasa_oficial(self):
        with self.assertRaises(ValueError):
            extraer('<div id="dolar-bcb">11.97</div>', PRODEM)

    def test_no_acepta_tasa_propia_incompleta_o_fuera_de_rango(self):
        for venta in ('', '0.00', '99.00'):
            with self.subTest(venta=venta), self.assertRaises(ValueError):
                extraer(f'<div id="prodem-compra">11.67</div><div id="prodem-venta">{venta}</div>', PRODEM)

if __name__ == '__main__':
    unittest.main()
