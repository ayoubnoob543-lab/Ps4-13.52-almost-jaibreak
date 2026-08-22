package org.homebrew;

import java.awt.Color;
import java.awt.Container;
import java.awt.Font;
import java.awt.Graphics;
import org.havi.ui.HScene;
import org.havi.ui.HSceneFactory;
import javax.tv.xlet.Xlet;
import javax.tv.xlet.XletContext;

/** Minimal benign BD-J Xlet used only to validate disc authoring. */
public final class MyXlet implements Xlet {
    private HScene scene;
    private HelloPanel panel;

    public void initXlet(XletContext context) {
        panel = new HelloPanel();
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

    private static final class HelloPanel extends Container {
        private final Font title = new Font("SansSerif", Font.PLAIN, 36);
        private final Font subtitle = new Font("SansSerif", Font.PLAIN, 18);
        private final Color background = new Color(5, 5, 5);
        private final Color foreground = new Color(240, 240, 240);

        public void paint(Graphics graphics) {
            graphics.setColor(background);
            graphics.fillRect(0, 0, getWidth(), getHeight());
            graphics.setColor(foreground);
            graphics.setFont(title);
            graphics.drawString("Hello World — BD-J test", 80, 180);
            graphics.setFont(subtitle);
            graphics.drawString("Benign authoring validation only", 80, 220);
        }
    }
}
