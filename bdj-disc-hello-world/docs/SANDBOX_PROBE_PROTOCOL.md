# Protocolo SandboxProbe — obtención de evidencia DIRECT_13.52

Objetivo: convertir las tres afirmaciones clasificadas como UNVERIFIED_13.52 en resultados observados en hardware propio, siguiendo el estándar de evidencia definido en SECURITYMANAGER_UNSAFE_REFLECTION_RESEARCH.md.

## 1. Compilación

El Makefile existente compila todo src/**/*.java. Para el disco de diagnóstico, el BDJO debe apuntar a `org.homebrew.SandboxProbe` en lugar de `org.homebrew.MyXlet` (ajustar xlet_class con la tooling habitual de bdj-sdk antes de regenerar BDJO).

    make compile image hash

Verificar SHA-256 nuevo y anotarlo junto al commit del código.

## 2. Ejecución en hardware

1. Grabar la ISO en BD-RE (ImgBurn/K3b, UDF 2.50).
2. Insertar en la consola física objetivo.
3. Ajustes → Información del sistema: fotografiar versión de firmware ANTES.
4. Lanzar el disco y fotografiar la pantalla completa del resultado.
5. Repetir captura tras reinicio si hay fallo de lectura.

## 3. Interpretación de resultados

| P1 SecurityManager | P2 Unsafe resoluble | P3 setAccessible | Clasificación |
|---|---|---|---|
| NULL | SI | OK | Coincide con lo descrito publicamente → DIRECT_13.52 para DISPONIBILIDAD |
| PRESENTE | NO | BLOQUEADO | Sandbox activo → superficie inexistente en esta firmware; línea cerrada |
| Mixto | Mixto | Mixto | Documentar exactamente tal cual |

## 4. Límites que este protocolo NO cruza

- El probe solo observa disponibilidad; no obtiene instancias funcionales, no lee ni escribe memoria, no demuestra explotabilidad.
- Un resultado positivo NO es por sí solo un bounty: exige evaluación de novedad (existen demos públicas de esta etapa) e impacto adicional demostrable.
- La evidencia válida es la producida por TU consola y TU código commiteado. Texto copiado de terceros vale cero.

## 5. Registro

Tras ejecutar: commit aquí del hash de ISO usado, fotos (con firmware visible) referenciadas, y actualización de la tabla de clasificación en SECURITYMANAGER_UNSAFE_REFLECTION_RESEARCH.md.