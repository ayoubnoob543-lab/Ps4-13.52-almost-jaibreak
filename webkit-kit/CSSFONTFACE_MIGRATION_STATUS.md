# Migración estática CSSFontFace-Exploit → PS4 13.52

## Procedencia auditada

Repositorio: https://github.com/ntfargo/CSSFontFace-Exploit

HEAD auditado: `221baa6e7349b96a6fd299808a25a4178e47741c`

El árbol contiene servidor local, HTML/JavaScript del navegador, módulos de explotación userland/kernel y parches binarios históricos para 6.00–11.02. Se ha tratado exclusivamente como material de referencia estática. No se importan módulos JavaScript, no se ejecuta el servidor, no se generan cadenas ROP/JOP y no se cargan parches.

## Clasificación por capas

| Capa | Reutilizable como análisis | Dependencia específica | Estado para 13.52 |
|---|---|---|---|
| Servidor HTTP/HTTPS y estructura de página | Organización de fixtures y procedencia | Certificados, rutas y entorno local | `STRUCTURAL` |
| Reproducción del fallo CSSFontFace | Descripción de entradas y flujo de prueba | Versión exacta de WebKit y comportamiento de objetos | `UNVERIFIED` |
| Comunicación browser/worker | Interfaces conceptuales | Layouts de memoria y primitivas target | `STRUCTURAL_ONLY` |
| Resolución de bases/imports | Método de auditoría de dependencias | Módulos y símbolos de la build objetivo | `MISSING` |
| Lectura/escritura arbitraria | Sólo puede documentarse como resultado histórico | Primitiva de memoria y sandbox target | `NOT_MIGRATED` |
| ROP/JOP y syscalls | No se convierte en implementación | Gadgets, offsets, syscalls y ABI de firmware | `NOT_MIGRATED` |
| Parches binarios `600`–`1102` | Hashes y comparación histórica | Bytes de kernel de cada firmware | `HISTORICAL_ONLY` |
| WebKit/libkernel/libc 13.52 | Ningún módulo binario incluido | Bytes, Build ID, GOT/vtables y símbolos | `MISSING` |

## Qué puede derivarse legítimamente

El repositorio permite comparar de forma textual la arquitectura del exploit, identificar nombres de capas y registrar hashes de los parches históricos. También permite diseñar un analizador que, cuando el usuario aporte legalmente un módulo, calcule SHA-256, tamaño, tipo, cabeceras, segmentos y cadenas de identificación.

El laboratorio dispone de `libkernel_sys_13.52.bin` con SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. Ese blob no sustituye a `libSceNKWebKit.sprx`, `libkernel_web.sprx` ni `libSceLibcInternal.sprx` y no permite confirmar offsets WebKit.

## Qué permanece ausente

Permanecen `MISSING` para una migración 13.52 verificable: los tres módulos retail, identidad de build común, hashes de módulos, imports/GOT, vtables, estructuras de objetos, gadgets, offsets WebKit, offsets de kernel y una cadena de ejecución autorizada en hardware.

## Política de publicación

Se publican sólo documentación, inventarios, hashes y herramientas de inspección estática. No se publican módulos propietarios de Sony, parches operativos para 13.52, gadgets ni payloads. La privacidad del repositorio no cambia la clasificación técnica ni las condiciones de redistribución.
