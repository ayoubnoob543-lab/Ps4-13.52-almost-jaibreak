# Linux environment check

## Resultado

El entorno local no contiene un reproductor BD-J equivalente al runtime propietario de PlayStation. Se encontraron `java`, `javac` y `ffmpeg`, pero no `vlc`, `xorriso` ni `bdjview`. El rootfs de `/home/ubuntu/wpe-artifacts-2526/arch/rootfs` contiene componentes WPE/Linux y datos de Java auxiliares, pero no un runtime BD-J de PS4.

La ISO fue inspeccionada sin montarla ni extraerla. El parser ISO9660 local informó `no ISO9660 primary volume descriptor`, lo cual es coherente con que la imagen fue generada como UDF 2.50. La búsqueda estática encontró las marcas `*NetBSD UDF`, `*OSTA UDF Compliant`, el volumen `BDJHELLO`, `CERTIFICATE`, `BDJO0200` y `org.homebrew.MyXlet`.

## Conclusión

Linux permite validar la identidad, el formato UDF, la estructura generada, la presencia del BDJO y la correspondencia entre BDJO y JAR. No puede ejecutar el Xlet como lo haría el reproductor BD-J propietario de PS4. Ejecutar el JAR con el Java del host tampoco sería una prueba válida y no se realizó.

La prueba definitiva sigue requiriendo una unidad BD-J autorizada. La ISO no se modificó durante esta comprobación.
