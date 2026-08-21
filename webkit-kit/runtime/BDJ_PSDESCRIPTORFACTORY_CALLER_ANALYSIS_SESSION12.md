# PSDescriptorFactory: análisis de `handles()` y `canWriteFile()`

## Alcance y método

Esta investigación se limita a `PSDescriptorFactory.handles(int,String)`, `PSDescriptorFactory.canWriteFile(String)` y sus callers públicos. Se revisó el texto normal y el wikitexto bruto de PSDevWiki, además de la búsqueda local en los repositorios autorizados. No se descargaron PUPs ni dumps privados y no se ejecutaron exploits, payloads, JAR, ELF/BIN o hardware.

La clasificación usada es `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## Resumen ejecutivo

Los cuerpos históricos de ambas funciones están publicados. Sin embargo, **no se encontró ningún caller público** que permita seguir desde el booleano devuelto hasta una escritura concreta, carga de clases, modificación de permisos o salida del sandbox.

La búsqueda exhaustiva en el texto capturado encontró:

| Símbolo | Apariciones relevantes | Resultado |
|---|---:|---|
| `handles(` | 3 cuerpos históricos | Sin caller publicado |
| `canWriteFile` | descripción y 3 cuerpos históricos | Sin caller publicado |
| `PSDescriptorFactory` | encabezados y cuerpos | Sin implementación/caller adicional |
| `PSAttributes.createDefaultAttributes` | sólo dentro de los cuerpos publicados | Sin caller externo publicado |

Por tanto, estas funciones son **predicados/ayudantes de autorización y selección** en la evidencia disponible, no una primitive de escritura o classloading demostrada.

## 1. `handles(int,String)`

### 1.1 Cuerpo previo: PS4 11.00 y PS3 4.92

PSDevWiki publica el siguiente cuerpo atribuido a `java/com/sony/gemstack/io/factories/ps/PSDescriptorFactory.java`:

```java
public boolean handles(int i, String path) {
    if (tempDir != null && path.startsWith(tempDir)) {
        return false;
    }
    persistentRoot = (String) AccessController.doPrivileged(new PrivilegedAction(this) {
        public Object run() {
            return System.getProperty("dvb.persistent.root", "/OS/persistent");
        }
    });
    if (path != null) {
        return path.startsWith(persistentRoot);
    }
    return false;
}
```

El cuerpo hace tres cosas observables: rechaza rutas bajo `tempDir`, obtiene una propiedad del sistema bajo `doPrivileged` y devuelve la comparación textual `path.startsWith(persistentRoot)`. No canonicaliza, no normaliza URI, no decodifica encoding y no comprueba separadores de componente de ruta.

### 1.2 Cuerpo previo: PS5 12.70

La versión publicada conserva el mismo comportamiento, expresado como operador ternario:

```java
public boolean handles(int i, String path) {
    if (tempDir != null && path.startsWith(tempDir)) {
        return false;
    } else {
        persistentRoot = (String) AccessController.doPrivileged(new 1(this));
        return path != null ? path.startsWith(persistentRoot) : false;
    }
}
```

### 1.3 Cuerpo posterior: PS5 13.00

El cambio publicado es concreto:

```java
public boolean handles(int i, String path) {
    if (tempDir != null && path.startsWith(tempDir)) {
        return false;
    } else {
        persistentRoot = (String) AccessController.doPrivileged(new 1(this));
        return path != null ? path.startsWith(RootCertManager.getOriginalPersistentRoot()) : false;
    }
}
```

La diferencia es que el prefijo comparado deja de ser la propiedad `dvb.persistent.root` y pasa a ser `RootCertManager.getOriginalPersistentRoot()`. Esto no prueba por sí solo una normalización más fuerte: el operador sigue siendo `startsWith`, según el cuerpo publicado.

### 1.4 Rango editorial y estado PS4

PSDevWiki atribuye la comparación de PS5 12.00/13.00 a zecoxao, basada en archivos BD-J decompilados compartidos anónimamente el 19 de marzo de 2026. La página clasifica el problema como `FW <= ?11.00?` y dice «Yes since PS4 FW ?13.50? and PS5 FW 13.00», pero no publica el cuerpo PS4 13.50/13.52 ni un commit de Sony.

La afirmación «desde PS4 aproximadamente 13.50» es **editorial/documental**, no bytes verificables. No debe convertirse en `DIRECT_13.52`.

### 1.5 Qué ocurre cuando devuelve true/false

Con el código público disponible sólo puede afirmarse:

```text
handles(...) == false → esta instancia de factory no maneja la ruta, según el contrato implícito del nombre.
handles(...) == true  → esta instancia declara que maneja la ruta.
```

El caller que usa el booleano para seleccionar un `PSDescriptor`, abrir un descriptor, leer/escribir un archivo o aplicar atributos **no aparece publicado** en la página ni en la búsqueda local. No es válido inventarlo.

### 1.6 Diferencias de representación

El cuerpo previo usa una comparación textual de prefijo:

```text
path.startsWith(persistentRoot)
```

No se observan en ese cuerpo llamadas a `File.getCanonicalPath`, `URI.normalize`, `URLDecoder`, validación de separador final, comprobación de `CodeSource` ni comparación de `JarEntry`. La versión PS5 13.00 cambia la fuente del prefijo, no la forma de comparación.

Esto crea una **posibilidad teórica** de falsos positivos de prefijo —por ejemplo, un path con el mismo comienzo textual pero distinto componente—, pero no hay caller ni efecto final publicados que permitan convertirlo en una vulnerabilidad 13.52.

Clasificación:

| Hallazgo | Estado |
|---|---|
| Cuerpo previo con `startsWith(persistentRoot)` | **HISTORICAL_ONLY** |
| Cuerpo posterior PS5 con `RootCertManager.getOriginalPersistentRoot()` | **HISTORICAL_ONLY** |
| Cambio equivalente confirmado en PS4 13.52 | **UNVERIFIED** |
| Variante de separador/canonicalización | **HYPOTHESIS** |
| Caller que convierte `true` en escritura o classloading | **UNVERIFIED** |

## 2. `canWriteFile(String)`

### 2.1 Cuerpo previo: PS4 9.00, PS5 2.00 y PS3 4.92

PSDevWiki publica:

```java
private static boolean canWriteFile(String userprefsPath) {
    CoreAppId coreAppId = CoreAppContext.getContext().getCoreAppId();
    if (!checkParent(coreAppId, userprefsPath, 2)) {
        return false;
    }
    PSAttributes attributes = PSAttributes.getAttributes(userprefsPath);
    if (attributes != null) {
        return attributes.canAccess(coreAppId, 2);
    }
    PSAttributes.createDefaultAttributes(userprefsPath, coreAppId);
    return true;
}
```

La operación tiene un efecto lateral: cuando no existen atributos, llama a `PSAttributes.createDefaultAttributes(userprefsPath, coreAppId)` y devuelve `true`. Eso demuestra creación de metadata/atributos, no escritura arbitraria de contenido.

### 2.2 Cuerpo posterior: PS4 11.00 y PS5 9.60

El cambio publicado añade una comparación explícita con la ruta original de `userprefs`:

```java
private static boolean canWriteFile(String userprefsPath) {
    CoreAppId coreAppId = CoreAppContext.getContext().getCoreAppId();
    if (userprefsPath.equals(
            new StringBuffer()
                .append(RootCertManager.getOriginalPersistentRoot())
                .append("/userprefs")
                .toString())
        || !checkParent(coreAppId, userprefsPath, 2)) {
        return false;
    }
    PSAttributes attributes = PSAttributes.getAttributes(userprefsPath);
    if (attributes != null) {
        return attributes.canAccess(coreAppId, 2);
    }
    PSAttributes.createDefaultAttributes(userprefsPath, coreAppId);
    return true;
}
```

El parche bloquea explícitamente la ruta `RootCertManager.getOriginalPersistentRoot() + "/userprefs"` antes de consultar `checkParent`. La versión PS5 9.60 publicada presenta la misma condición.

### 2.3 Rango editorial

La página atribuye los cuerpos PS4 a CelesteBlue, mediante diffing decompilado de PS4 9.00 y 11.00. Dice que el parche existe desde PS4 11.00 y quizá antes, y que PS5 fue parcheada entre 2.00 y 10.01. También afirma que `canReadWriteFile()` parecía seguir sin parche en PS5 13.00.

Estas son versiones decompiladas y notas editoriales. No identifican el caller ni demuestran el estado PS4 13.52.

### 2.4 Qué es el supuesto problema `userprefs`

El problema histórico descrito es que la versión antigua no excluía de forma explícita la ruta original de `userprefs`. Si `checkParent` permitía el path y no había atributos, `createDefaultAttributes` podía crear los atributos por defecto y devolver `true`. El cuerpo no muestra, por sí mismo, que escriba los bytes de `userprefs`, cargue clases o altere `SecurityManager`.

Para convertir esta condición en una operación real habría que encontrar un caller que:

1. pase un `userprefsPath` controlable;
2. use `canWriteFile()` como autorización;
3. escriba o reemplace el contenido después de recibir `true`;
4. vuelva a cargar o deserialice el archivo en un contexto privilegiado.

Ninguna de esas cuatro relaciones está publicada como caller de `PSDescriptorFactory` en las fuentes revisadas.

Clasificación:

| Hallazgo | Estado |
|---|---|
| Cuerpo PS4 9.00 sin exclusión explícita de `userprefs` | **HISTORICAL_ONLY** |
| Cuerpo PS4 11.00 con exclusión de `originalPersistentRoot/userprefs` | **HISTORICAL_ONLY** |
| El supuesto problema alcanza escritura de contenido | **UNVERIFIED** sin caller |
| La ruta sigue presente en PS4 13.52 | **UNVERIFIED** |
| `canReadWriteFile()` constituye automáticamente el mismo bug | **DISCARDED** |

## 3. Callers y efectos finales

### 3.1 Callers encontrados

La búsqueda local y el texto completo de PSDevWiki no contienen referencias de implementación para:

- llamadas a `PSDescriptorFactory.handles(...)`;
- llamadas a `PSDescriptorFactory.canWriteFile(...)`;
- callers de `PSAttributes.createDefaultAttributes(...)` fuera del propio cuerpo publicado;
- una secuencia `handles → open/write`;
- una secuencia `canWriteFile → write userprefs`;
- una secuencia `PSDescriptorFactory → ClassLoader`;
- una secuencia `PSDescriptorFactory → CodeSource/Policy`.

PSDevWiki publica los métodos y sus cuerpos, pero sus subsecciones «Implementation» aparecen sin implementación/caller adicional para estas dos entradas.

### 3.2 Lo que sí puede afirmarse estáticamente

| Paso | Evidencia |
|---|---|
| Leer `dvb.persistent.root` | Sí, dentro de `handles()` y bajo `doPrivileged` en la versión previa |
| Comparar un prefijo de path | Sí, con `startsWith` |
| Rechazar `tempDir` | Sí, si la condición aplica |
| Consultar `checkParent` | Sí, dentro de `canWriteFile()` |
| Consultar o crear `PSAttributes` | Sí |
| Escribir bytes de un archivo | No demostrado |
| Cargar una clase/JAR | No demostrado |
| Cambiar permisos Java | No demostrado |
| Salir del sandbox | No demostrado |

### 3.3 Cadena histórica máxima demostrable

La cadena máxima que permiten las fuentes es:

```text
caller desconocido
  → PSDescriptorFactory.handles(path)
  → true/false para selección de factory
  → efecto final desconocido
```

Y para `canWriteFile()`:

```text
caller desconocido
  → canWriteFile(userprefsPath)
  → checkParent / PSAttributes.canAccess
  → opcionalmente createDefaultAttributes
  → true/false
  → escritura o reapertura desconocida
```

No se puede extender legítimamente el diagrama a classloading o sandbox escape sin el caller y la función que realiza la operación posterior.

## 4. Clasificación específica para PS4 13.52

| Hallazgo | Clasificación |
|---|---|
| Cuerpo PS4 13.52 de `handles()` | **UNVERIFIED** |
| Cuerpo PS4 13.52 de `canWriteFile()` | **UNVERIFIED** |
| Nota editorial: `handles()` parcheado aproximadamente desde 13.50 | **INDIRECT_13.52**, pero no directa |
| Nota editorial: `canWriteFile()` parcheado en PS4 11.00 o quizá antes | **INDIRECT_13.52** sólo como indicio temporal |
| `handles()` permite escritura en 13.52 | **DISCARDED** como afirmación no demostrada |
| `canWriteFile()` permite reescribir `userprefs` en 13.52 | **DISCARDED** como afirmación no demostrada |
| Caller público que llegue a carga de clases | **UNVERIFIED** |
| Caller público que cambie permisos o salga del sandbox | **UNVERIFIED** |

## 5. Dato mínimo faltante

El siguiente eslabón mínimo no identificado es el **caller**. Para resolver la hipótesis se necesita una decompilación o fuente pública que muestre, para cada función:

1. quién invoca `handles()` o `canWriteFile()`;
2. qué tipo de descriptor se selecciona o qué operación ocurre tras `true`;
3. qué método abre, crea o escribe el archivo;
4. si `userprefs` se vuelve a cargar/deserializar;
5. qué `CodeSource`, policy o classloader se aplica después.

Sin ese caller, `handles()` sólo es un predicado textual y `canWriteFile()` sólo demuestra una autorización/creación de atributos, no una cadena completa.

## Conclusión

El hallazgo nuevo es negativo pero preciso: **PSDevWiki sí conserva cuerpos históricos y cambios de versión, pero no conserva los callers que convierten esas decisiones en una operación final**.

La única relación temporal relevante para 13.52 es editorial: `handles()` figura como parcheado aproximadamente desde PS4 13.50. Para `canWriteFile()`, el cuerpo ya aparece parcheado en PS4 11.00. Ninguna de las dos notas es evidencia directa de bytes PS4 13.52.

Por tanto, el resultado es:

> **No se identificó una cadena PSDescriptorFactory → escritura de archivos → carga de clases/salida del sandbox.**

La siguiente acción útil es localizar una implementación pública de la clase que llame a estos métodos, no repetir el análisis de los cuerpos ni inferir un caller desde los nombres.

## Referencias

[1]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"

[2]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw "PS4 Developer Wiki — Vulnerabilities raw wikitext"

[3]: https://hackerone.com/reports/1379975 "PlayStation #1379975: bd-j exploit chain"

[4]: https://hackerone.com/reports/3452696 "PlayStation #3452696: PS4 BD-J privilege escalation using nested JAR"
