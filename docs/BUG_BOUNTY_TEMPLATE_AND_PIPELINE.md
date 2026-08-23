# Plantilla de reporte para Bug Bounty (Sony / HackerOne) + checklist de elegibilidad

> Uso previsto: cuando exista un hallazgo REAL y ACTIVO sobre firmware actual. No usar con hallazgos históricos o parcheados — ver checklist sección 2.

## 1. Estructura del reporte

```markdown
Título: [Componente] [Clase de bug] en [módulo] permite [impacto] en firmware X.XX

- Firmware afectado: X.XXX (probado) / rango estimado
- Hardware: modelo de consola, CUSA si aplica
- Clase CWE: CWE-XXX

### Resumen ejecutivo
2-4 frases: qué componente, qué condición, qué logra un atacante, qué prerequisitos necesita.

### Descripción técnica
- Ubicación exacta (módulo, función, offset si aplica)
- Condición vulnerable con pseudocódigo o fragmento
- Por qué las mitigaciones existentes no aplican

### Pasos de reproducción
1. Entorno exacto (firmware, settings)
2. Entrada necesaria (archivo, medio, red)
3. Secuencia precisa paso a paso
4. Resultado observado vs esperado

### Prueba de concepto
Código mínimo autocontenido. Solo lo necesario para demostrar la condición — nunca cadena completa de explotación.

### Impacto
Consecuencia concreta y acotada (crash, lectura, escritura, elevación). Sin especulación.

### Mitigación sugerida
Qué comprobación o diseño evitaría el bug.

### Divulgación
Preferencia de coordinación y timeline propuesto.
```

## 2. Checklist de elegibilidad (todo debe ser SÍ antes de redactar)

| # | Requisito | Verificado |
|---|---|---|
| 1 | La condición existe y es explotable en el firmware MÁS RECIENTE actual | ☐ |
| 2 | Hay PoC reproducible en hardware físico propio | ☐ |
| 3 | El impacto está demostrado (no especulado) | ☐ |
| 4 | No aparece en notas de parche de ninguna versión previa | ☐ |
| 5 | No está ya reportada por otro investigador (duplicado = rechazo) | ☐ |
| 6 | Está dentro del scope del programa vigente | ☐ |

Regla práctica: si el vendor ya publicó cualquier check/cambio relacionado con esa vía, la elegibilidad está muerta aunque nadie haya cobrado por ella.

## 3. Pipeline de vigilancia para el próximo firmware (13.53+)

Objetivo: detectar señales de bugs vivos comparando artefactos userland obtenibles SIN jailbreak.

1. **Capturar**: obtener `libkernel` (o equivalente userland) del nuevo firmware tan pronto sea accesible.
2. **Verificar procedencia**: SHA-256 contra este catálogo (`BINARY_ARTIFACT_TRIAGE_2026-08-23.md`).
3. **Comparar stubs**: contar wrappers de syscall (firma `4989ca0f057201c3`) viejos vs nuevos; números nuevos o eliminados = superficie cambiada.
4. **Diff de código R2**: desensamblar con Ghidra/r2 ambas versiones; cada check añadido señala un bug vivido; cada wrapper modificado, cambio de contrato.
5. **Registrar todo** como evidencia con hashes (formato de este repo).
6. **Si algo activo emerge**: validar en consola física propia → reporte con esta plantilla → bounty.

Nota de alcance: este pipeline trabaja en capa userland. Los módulos de kernel cifrados (UVFAT incluido) siguen fuera de alcance hasta disponer de volcado descifrado, que requiere consola con jailbreak en versión vulnerable.
