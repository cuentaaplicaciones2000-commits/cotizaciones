"""Diagnóstico público de conexión y HTML de Prodem sin escribir docs/."""
import concurrent.futures
import json
from pathlib import Path
import socket
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import requests
from actualizar import UA, extraer

URLS = ('https://prodem.bo/Inicio', 'https://www.prodem.bo/Inicio')

def comprobar(url):
    inicio = time.monotonic()
    host = url.split('/')[2]
    resultado = {'url': url}
    try:
        resultado['ips'] = sorted({a[4][0] for a in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)})
        r = requests.get(url, headers={'User-Agent': UA}, timeout=(15, 30))
        resultado.update(status=r.status_code, url_final=r.url)
        r.raise_for_status()
        resultado['tasas'] = extraer(r.text, {'id':'prodem', 'extractor':'prodem'})
        resultado['ok'] = True
    except (OSError, requests.RequestException, ValueError) as e:
        resultado.update(ok=False, error=str(e))
    resultado['segundos'] = round(time.monotonic()-inicio,2)
    return resultado

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(comprobar, URLS))
    print(json.dumps(resultados, ensure_ascii=False, indent=2))
    sys.exit(0 if any(r['ok'] for r in resultados) else 1)
