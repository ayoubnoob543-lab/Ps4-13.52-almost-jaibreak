package bdj;

import java.awt.Font;
import java.awt.Graphics;
import java.awt.GraphicsConfiguration;
import java.awt.HScene;
import java.awt.HSceneFactory;
import javax.tv.xlet.Xlet;
import javax.tv.xlet.XletContext;
import javax.tv.xlet.XletStateChangeException;

/**
 * Minimal, benign BD-J Xlet for authoring validation.
 * It performs no filesystem, network, reflection, native, or privileged work.
 */
public final class HelloWorldXlet implements Xlet {
    private XletContext context;
    private HScene scene;
    private HelloCanvas canvas;

    public void initXlet(XletContext ctx) throws XletStateChangeException {
        this.context = ctx;
        GraphicsConfiguration configuration = null;
        this.scene = HSceneFactory.getInstance().getDefaultHScene();
        this.canvas = new HelloCanvas();
        this.scene.add(canvas);
        this.scene.setSize(1280, 720);
        this.scene.setVisible(true);
    }

    public void startXlet() throws XletStateChangeException {
        if (scene != null) {
            scene.setVisible(true);
            scene.requestFocus();
        }
    }

    public void pauseXlet() throws XletStateChangeException {
        if (scene != null) {
            scene.setVisible(false);
        }
    }

    public void destroyXlet(boolean unconditional) throws XletStateChangeException {
        if (scene != null) {
            scene.removeAll();
            scene.setVisible(false);
            scene = null;
        }
        canvas = null;
        context = null;
    }

    private static final class HelloCanvas extends java.awt.Canvas {
        public void paint(Graphics graphics) {
            graphics.setFont(new Font("SansSerif", Font.PLAIN, 36));
            graphics.drawString("Hello World — BD-J test", 80, 180);
            graphics.setFont(new Font("SansSerif", Font.PLAIN, 18));
            graphics.drawString("Benign authoring validation only", 80, 220);
        }
    }
}
