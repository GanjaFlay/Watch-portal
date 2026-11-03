# Watch Portal

App personal de Nikolay (GitHub [GanjaFlay](https://github.com/GanjaFlay)) para el Samsung Galaxy Watch9 de 40 mm. Es un WebView a pantalla completa que abre una URL fija. Las esferas, los paneles y los simuladores de este repo se publican con GitHub Pages.

La página que abre el reloj es el menú: [https://ganjaflay.github.io/Watch-portal/](https://ganjaflay.github.io/Watch-portal/)

Si vas a tocar el proyecto (persona o agente), empieza por [`AGENTS.md`](AGENTS.md). Las decisiones de diseño están en [`DISENO.md`](DISENO.md). Cada diseño tiene su guía en `plantillas/<nombre>/PLANTILLA.md`.

- Paquete: `com.nikolay.portalwatch` · Nombre en el reloj: **Portal**
- minSdk 30, compileSdk/targetSdk 36, build-tools 36.0.0, AGP 8.13.0, Kotlin 2.1.21, Gradle 8.14.3
- App de Wear independiente (no hace falta compañera en el móvil). Permite HTTP sin cifrar.

## Qué hay en el reloj

`docs/index.html` es el menú (fondo negro, turquesa Tiffany). Desde ahí se abre:

| Diseño | En el reloj |
|---|---|
| Reloj fumeta | [`reloj-fumeta.html`](docs/reloj-fumeta.html) |
| Lluvia de hojas | [`reloj-lluvia-hojas.html`](docs/reloj-lluvia-hojas.html) |
| Bitcoin (datos horneados) | [`bitcoin-estatico.html`](docs/bitcoin-estatico.html) |
| Bitcoin en vivo | [`bitcoin.html`](docs/bitcoin.html) — deprecado, no conecta en el reloj |

Los `simulador-*.html` son para mirarlos en el móvil (fondo blanco, reloj en el centro). Están en una sección pequeña del menú.

## Publicar un cambio de página

El sitio sale de la carpeta `docs/` en la rama `main` (GitHub Pages → Deploy from a branch → **main** / **/docs**). Hay un `docs/.nojekyll` vacío para que Pages no pase Jekyll.

1. Cambia el HTML en `docs/` (si el diseño tiene script, usa el de `docs/src/`, no edites el HTML a mano).
2. Commit y push a `main`.
3. En el reloj, recarga (botón ↻, toque con dos dedos, o pulsación larga de un botón del vástago).

La URL por defecto está en `app/build.gradle.kts` (`defaultPortalUrl`). Se puede pisar sin editar el archivo:

```bash
./gradlew assembleDebug -PportalUrl=https://ganjaflay.github.io/Watch-portal/
```

Hace falta JDK 17 y el Android SDK (`ANDROID_HOME`). El APK de debug queda en `app/build/outputs/apk/debug/app-debug.apk`. Si quieres dejar el que se instala desde el móvil:

```bash
cp app/build/outputs/apk/debug/app-debug.apk Portal-debug.apk
```

`Portal-debug.apk` (el que está en el repo) se compiló con la URL antigua `https://example.github.io/watch-portal/`. Hasta que no se recompile e instale de nuevo, el reloj sigue abriendo esa URL. Cambiar el gradle no reescribe el APK.

## Instalar en el reloj (ADB por Wi-Fi)

1. Reloj: **Ajustes → Acerca del reloj → Software → toca «Versión de software» 7 veces**. Se activan las opciones de desarrollador.
2. **Ajustes → Opciones de desarrollador**: activa **Depuración ADB** y **Depuración inalámbrica**. Reloj y ordenador en la misma Wi-Fi.
3. En Depuración inalámbrica, **Emparejar dispositivo nuevo**. Anota el `ip:puerto` de emparejamiento y el código de 6 dígitos.
4. En el ordenador (platform-tools):

   ```bash
   adb pair 192.168.1.50:37123        # ip:puerto de emparejar; luego el código
   adb connect 192.168.1.50:41234     # el ip:puerto de la pantalla de depuración (es otro puerto)
   adb install -r Portal-debug.apk
   ```

5. Abre **Portal** en la lista de apps. Para actualizar: vuelve a `adb connect` y `adb install -r`.

Los `ip:puerto` de arriba son un ejemplo. Los de verdad salen en el reloj.

## Instalar desde el móvil (Galaxy S25)

Los pasos 1–3 del reloj son los mismos. Copia `Portal-debug.apk` al S25 (misma Wi-Fi) y usa una de estas dos apps:

- **Bugjaeger** (Play Store): empareja con el ip:puerto y el código, conecta al ip:puerto de depuración, y en *Paquetes → Instalar* elige el APK.
- **Wear Installer 2** (Play Store): mete el IP/puerto del reloj, empareja con el código, elige el APK y pulsa Instalar.

Apaga la depuración inalámbrica al terminar: gasta batería.

## Controles de la app

- **Recargar**: botón redondo ↻ abajo en el centro (se esconde a los 3 s; un toque cerca del borde inferior lo vuelve a sacar), toque con **dos dedos**, o **pulsación larga** de un botón del vástago. La tecla Home no se puede interceptar.
- El **bisel / corona** hace scroll.
- **Atrás** recorre el historial del WebView; si no hay historial, sale de la app.
- Si la página no carga, sale un error con **Retry**. Al volver a la app, reintenta sola.
- La pantalla se queda encendida mientras Portal está delante.
