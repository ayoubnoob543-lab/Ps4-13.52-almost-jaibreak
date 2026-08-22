# BD-J Hello World Disc

Proyecto **benigno** de prueba de authoring BD-J. Su objetivo es generar una aplicación Blu-ray Disc Java mínima que inicialice un Xlet y muestre un mensaje `Hello World` en pantalla. No contiene exploits, payloads, código nativo, acceso a kernel, escape de sandbox ni lógica de jailbreak.

## Estado

Este repositorio contiene el esqueleto reproducible del proyecto. La compilación final depende de una definición de plataforma/stubs BD-J compatible (`bdj.jar` o equivalente) y de las herramientas de authoring. El proyecto no afirma compatibilidad con PS4 13.52 hasta que una imagen sea generada, validada y probada en un reproductor BD-J autorizado.

## Estructura

```text
src/bdj/                 Código fuente del Xlet benigno
disc/BDMV/               Directorio reservado para la imagen BD-J
tools/                   Scripts estáticos de empaquetado/validación
docs/                    Notas de authoring y procedencia
manifest.sha256          Hashes de los artefactos generados (cuando existan)
```

## Dependencias esperadas

Se necesita un JDK compatible con el perfil BD-J, una definición de plataforma/stubs BD-J, las herramientas públicas de authoring y un generador de imagen Blu-ray/BDMV. Esas dependencias no se sustituyen por clases inventadas: si no están disponibles, el build debe detenerse y registrarlo.

## Validación segura

Las validaciones locales deben limitarse a comprobar estructura, nombres, tamaños, hashes, manifests y formato de la imagen. No se ejecutan JARs, ISOs, clases compiladas ni código procedente de la consola. La compatibilidad real con una PS4 sólo puede determinarse mediante una prueba autorizada en hardware propio.

## Fuentes públicas

- [BD-J SDK de john-tornblom](https://github.com/john-tornblom/bdj-sdk)
- [HDcookbook](https://github.com/enteractive-dev/hdcookbook)
- [Documentación Oracle BD-J](https://www.oracle.com/technical-resources/articles/javabluray.html)

## Alcance excluido

No se incluyen instrucciones para BD-JB, HEN, GoldHEN, payloads, escalada de privilegios, native usermode, kernel execution o bypasses de seguridad.
