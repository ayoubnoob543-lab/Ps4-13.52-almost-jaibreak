package org.homebrew;

import java.awt.Color;
import java.awt.Container;
import java.awt.Font;
import java.awt.Graphics;
import org.havi.ui.HScene;
import org.havi.ui.HSceneFactory;
import javax.tv.xlet.Xlet;
import javax.tv.xlet.XletContext;

/**
 * Benign BD-J compatibility shell.
 *
 * This Xlet only displays static capability/status information. It does not
 * load external code, access devices, inspect files, use native interfaces,
 * or attempt to bypass any security boundary.
 */
public final class MyXlet implements Xlet {
    private HScene scene;
    private StatusPanel panel;

    public void initXlet(XletContext context) {
        panel = new StatusPanel();
        panel.setSize(1280, 720);
        scene = HSceneFactory.getInstance().getDefaultHScene();
        scene.add(panel);
        scene.validate();
        scene.repaint();
    }

    public void startXlet() {
        if (panel != null) {
            panel.setVisible(true);
        }
        if (scene != null) {
            scene.setVisible(true);
        }
    }

    public void pauseXlet() {
        if (panel != null) {
            panel.setVisible(false);
        }
    }

    public void destroyXlet(boolean unconditional) {
        if (scene != null && panel != null) {
            scene.remove(panel);
            scene.setVisible(false);
        }
        panel = null;
        scene = null;
    }

    private static final class StatusPanel extends Container {
        private final Font title = new Font("SansSerif", Font.PLAIN, 32);
        private final Font line = new Font("SansSerif", Font.PLAIN, 19);
        private final Color background = new Color(5, 5, 5);
        private final Color foreground = new Color(240, 240, 240);
        private final Color safe = new Color(150, 220, 150);

        public void paint(Graphics graphics) {
            graphics.setColor(background);
            graphics.fillRect(0, 0, getWidth(), getHeight());
            graphics.setColor(foreground);
            graphics.setFont(title);
            graphics.drawString("BD-J compatibility shell", 70, 130);
            graphics.setFont(line);
            graphics.drawString("Lifecycle: INIT / START reached", 70, 190);
            graphics.drawString("Public APIs: Xlet + HScene linked", 70, 230);
            graphics.drawString("WebKit/JSC: not part of this Xlet", 70, 270);
            graphics.drawString("Native/kernel/device access: not requested", 70, 310);
            graphics.drawString("External loading: not requested", 70, 350);
            graphics.setColor(safe);
            graphics.drawString("RESULT: benign shell only; no exploit", 70, 420);
        }
    }
}
