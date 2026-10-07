# Verificación de captura automática — 7 de octubre de 2026

## Actualización tras la ejecución en GitHub Actions

El usuario confirmó 13 bancos OK y un `ConnectTimeout` para Prodem desde Actions.
El 14/14 indicado abajo corresponde al entorno local, no al runner de GitHub.
Se añadieron diagnóstico en tres runners y selección mediante `COTIZACIONES_RUNNER`.
La conectividad remota queda pendiente de esa prueba; no se afirma resuelto el timeout.

Resultado: **14/14 bancos OK**, cuatro pruebas de regresión OK y `docs/` sin cambios
(comparación SHA-256 antes y después). Los valores son los observados durante esta prueba,
en Bs por USD; no son constantes del código.

| Banco | Compra | Venta | Oficial | Resultado |
|---|---:|---:|---:|---|
| BCB | — | — | 11.97 | OK |
| BCP | 11.47 | 12.27 | — | OK |
| BNB | 11.47 | 12.27 | 11.97 | OK |
| Unión | 10.97 | 12.27 | 11.97 | OK |
| Mercantil Santa Cruz | 10.87 | 12.27 | 11.97 | OK |
| BISA | 11.27 | 12.27 | — | OK |
| Ganadero | — | 12.27 | — | OK |
| Económico | 11.07 | 12.32 | 11.97 | OK |
| BancoSol | 10.77 | 12.27 | 11.97 | OK |
| Prodem | 11.67 | 12.07 | 11.97 | OK |
| Fortaleza | 11.67 | 12.27 | 11.97 | OK |
| Ecofuturo | 10.97 | 12.37 | 11.97 | OK |
| FIE | 11.07 | 12.17 | 11.97 | OK |
| Bancomunidad | 11.57 | 12.22 | 11.97 | OK |

Los guiones indican campos no esperados por la configuración de ese banco. La prueba
comprueba presencia de todos los campos esperados, no solo el código de salida del comando.

## Diagnóstico de Prodem

La versión anterior dependía de Playwright, cierre de modales y espera de visibilidad,
aunque la respuesta HTTP pública ya contiene `#prodem-compra`, `#prodem-venta` y
`#dolar-bcb`. Además, el extractor descartaba siempre la tasa oficial.

En este equipo faltaba Chromium al iniciar las pruebas. Tras instalarlo, la captura
original obtuvo compra y venta: el fallo de GitHub Actions no se pudo reproducir
localmente y no se revisaron sus logs remotos. Por tanto, no se afirma una causa
confirmada para ese fallo remoto. La corrección elimina las dependencias de navegador
y modal para Prodem y añade la tasa oficial publicada.

Se mantienen los selectores específicos para evitar confundir las cotizaciones propias
con otros valores de la página. Si falta compra o venta válida, el extractor falla
explícitamente y el flujo conserva el archivo anterior.

## Repetir las pruebas

```console
python -m playwright install chromium
python -m unittest discover -s pruebas -p "test_*.py" -v
python pruebas/verificar_bancos.py
python actualizar.py --probar prodem
```

`resultado_bancos.json` contiene la fecha UTC, salida y resultado de cada proceso individual.
Las pruebas usan las mismas funciones de descarga y extracción del flujo automático.
No ejecutan el workflow remoto ni publican cambios en GitHub; los cambios quedan en
esta carpeta local para subirlos al repositorio usado por Actions.
