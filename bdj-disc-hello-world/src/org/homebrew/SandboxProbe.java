package org.homebrew;

import java.awt.Color;
import java.awt.Container;
import java.awt.Font;
import java.awt.Graphics;
import java.lang.reflect.Field;
import javax.tv.xlet.Xlet;
import javax.tv.xlet.XletContext;
import org.havi.ui.HScene;
import org.havi.ui.HSceneFactory;

/**
 * SandboxProbe - diagnostico pasivo del entorno BD-J.
 * Solo OBSERVA disponibilidad de clases/permisos y pinta el resultado.
 * No lee ni escribe memoria, no modifica estado, no carga codigo, no accede a red ni disco.
 */
public class SandboxProbe implements Xlet {

    private HScene scene;
    private ProbePanel panel;

    public void initXlet(XletContext ctx) {
        panel = new ProbePanel();
        panel.setSize(1280, 720);
        scene = HSceneFactory.getInstance().getDefaultHScene();
        scene.add(panel);
        scene.validate();
    }

    public void startXlet() {
        panel.collect();
        scene.setVisible(true);
        panel.repaint();
    }

    public void pauseXlet() { panel.setVisible(false); }

    public void destroyXlet(boolean unconditional) {
        if (scene != null && panel != null) { scene.remove(panel); scene.setVisible(false); }
        panel = null; scene = null;
    }

    public static class ProbePanel extends Container {
        private String[] lines = new String[0];
        private final Font title = new Font("SansSerif", Font.PLAIN, 28);
        private final Font line = new Font("SansSerif", Font.PLAIN, 17);

        public void collect() {
            String[] r = new String[6];
            int i = 0;

            try {
                SecurityManager sm = System.getSecurityManager();
                r[i++] = "P1 System.getSecurityManager(): " + (sm == null ? "NULL" : "PRESENTE");
            } catch (Throwable t) {
                r[i++] = "P1 error: " + t.getClass().getName();
            }

            try {
                Class c = Class.forName("sun.misc.Unsafe");
                r[i++] = "P2 sun.misc.Unsafe resoluble: SI (" + c.getName() + ") [solo identidad, sin instancia]";
            } catch (Throwable t) {
                r[i++] = "P2 sun.misc.Unsafe resoluble: NO (" + t.getClass().getName() + ")";
            }

            try {
                Field f = java.lang.System.class.getDeclaredField("props");
                try {
                    f.setAccessible(true);
                    r[i++] = "P3 setAccessible(System.props): OK [valor NO leido]";
                } catch (SecurityException se) {
                    r[i++] = "P3 setAccessible BLOQUEADO (SecurityException)";
                } catch (Throwable t) {
                    r[i++] = "P3 setAccessible error: " + t.getClass().getName();
                }
            } catch (Throwable t) {
                r[i++] = "P3 campo System.props no existe aqui";
            }

            r[i++] = " ";
            r[i++] = "RESULTADOS SOLO LECTURA - sin explotacion";
            lines = r;
        }

        public void paint(Graphics g) {
            g.setColor(new Color(5, 5, 5));
            g.fillRect(0, 0, getWidth(), getHeight());
            g.setColor(new Color(240, 240, 240));
            g.setFont(title);
            g.drawString("SandboxProbe - diagnostico BD-J", 70, 90);
            g.setFont(line);
            for (int j = 0; j < lines.length; j++) {
                if (lines[j] != null) g.drawString(lines[j], 70, 150 + j * 34);
            }
        }
    }
}