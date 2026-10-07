"""Pruebas de red individuales sin escribir cotizaciones en docs/."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bancos import BANCOS

def huellas():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / 'docs').rglob('*') if p.is_file()}

def probar(banco):
    try:
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'actualizar.py', '--probar', banco['id']],
                              cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=180)
        campos = dict(re.findall(r'(compra|venta|oficial)=([^\s]+)', proc.stdout))
        esperados = ['oficial'] if banco['id'] == 'bcb' else ['venta'] if banco['id'] == 'ganadero' else ['compra', 'venta']
        if banco.get('regex_oficial') or banco['id'] in ('bnb', 'bancomunidad', 'prodem'):
            if 'oficial' not in esperados:
                esperados.append('oficial')
        faltantes = [c for c in esperados if not re.fullmatch(r'\d+\.\d+', campos.get(c, ''))]
        return {'banco': banco['id'], 'ok': proc.returncode == 0 and not faltantes,
                'campos': campos, 'campos_faltantes': faltantes,
                'codigo': proc.returncode, 'salida': proc.stdout, 'error': proc.stderr}
    except subprocess.TimeoutExpired:
        return {'banco': banco['id'], 'ok': False, 'error': 'Tiempo máximo de 180 segundos excedido'}

if __name__ == '__main__':
    antes = huellas()
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for resultado in pool.map(probar, BANCOS):
            resultados.append(resultado)
            print(json.dumps(resultado, ensure_ascii=False), flush=True)
    informe = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'resultados': resultados,
               'docs_sin_cambios': antes == huellas()}
    ruta = ROOT / 'pruebas' / 'resultado_bancos.json'
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Resumen: {sum(r['ok'] for r in resultados)}/{len(resultados)} OK; docs sin cambios: {informe['docs_sin_cambios']}")
    sys.exit(0 if all(r['ok'] for r in resultados) and informe['docs_sin_cambios'] else 1)
