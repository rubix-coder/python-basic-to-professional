package com.rubixcoder.snake;

import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Font;
import java.util.Random;

public class SnakeCanvas extends Canvas implements Runnable, CommandListener {

    public static final int GRID_W = 16;
    public static final int GRID_H = 20;

    private static final int[] SPEEDS_MS = {300, 180, 100};

    private static final int DIR_UP = 0;
    private static final int DIR_DOWN = 1;
    private static final int DIR_LEFT = 2;
    private static final int DIR_RIGHT = 3;

    private SnakeMIDlet midlet;
    private int mode;
    private int tickMs;

    private int[] snakeX = new int[GRID_W * GRID_H];
    private int[] snakeY = new int[GRID_W * GRID_H];
    private int snakeLen;
    private int dir;
    private int nextDir;
    private int foodX, foodY;
    private int score;
    private int best;
    private boolean alive;
    private boolean paused;
    private boolean gameOver;

    private Thread loop;
    private boolean running;
    private Random rng = new Random();

    private int cellPx;
    private int boardW, boardH;
    private int boardX, boardY;
    private int hudH;

    private Command cmdHome;
    private Command cmdPause;

    public SnakeCanvas(SnakeMIDlet m, int mode) {
        this.midlet = m;
        this.mode = mode;
        this.tickMs = SPEEDS_MS[mode];
        this.best = Scores.loadOne(mode);
        cmdHome = new Command("HOME", Command.BACK, 1);
        cmdPause = new Command("PAUSE", Command.OK, 2);
        addCommand(cmdHome);
        addCommand(cmdPause);
        setCommandListener(this);
        computeLayout();
    }

    private void computeLayout() {
        int w = getWidth();
        int h = getHeight();
        hudH = 18;
        int availW = w;
        int availH = h - hudH;
        int cellByW = availW / GRID_W;
        int cellByH = availH / GRID_H;
        cellPx = cellByW < cellByH ? cellByW : cellByH;
        if (cellPx < 4) cellPx = 4;
        boardW = cellPx * GRID_W;
        boardH = cellPx * GRID_H;
        boardX = (w - boardW) / 2;
        boardY = hudH + (availH - boardH) / 2;
    }

    protected void sizeChanged(int w, int h) {
        computeLayout();
        repaint();
    }

    public void startGame() {
        snakeLen = 3;
        snakeX[0] = 8; snakeY[0] = 10;
        snakeX[1] = 7; snakeY[1] = 10;
        snakeX[2] = 6; snakeY[2] = 10;
        dir = DIR_RIGHT;
        nextDir = DIR_RIGHT;
        score = 0;
        alive = true;
        paused = false;
        gameOver = false;
        placeFood();
        if (loop == null || !running) {
            running = true;
            loop = new Thread(this);
            loop.start();
        }
        repaint();
    }

    public void pauseGame() {
        if (alive && !gameOver) paused = true;
        repaint();
    }

    public void stopGame() {
        running = false;
        alive = false;
        Thread t = loop;
        if (t != null) {
            try { t.join(200); } catch (InterruptedException e) {}
        }
        loop = null;
    }

    public void run() {
        while (running) {
            try {
                Thread.sleep(tickMs);
            } catch (InterruptedException e) {}
            if (!running) break;
            if (alive && !paused && !gameOver) {
                step();
                repaint();
            }
        }
    }

    private void step() {
        dir = nextDir;
        int hx = snakeX[0];
        int hy = snakeY[0];
        if (dir == DIR_UP) hy--;
        else if (dir == DIR_DOWN) hy++;
        else if (dir == DIR_LEFT) hx--;
        else if (dir == DIR_RIGHT) hx++;

        if (hx < 0 || hx >= GRID_W || hy < 0 || hy >= GRID_H) {
            doGameOver();
            return;
        }
        for (int i = 0; i < snakeLen - 1; i++) {
            if (snakeX[i] == hx && snakeY[i] == hy) {
                doGameOver();
                return;
            }
        }

        boolean ate = (hx == foodX && hy == foodY);
        int newLen = ate ? snakeLen + 1 : snakeLen;
        for (int i = newLen - 1; i > 0; i--) {
            snakeX[i] = snakeX[i - 1];
            snakeY[i] = snakeY[i - 1];
        }
        snakeX[0] = hx;
        snakeY[0] = hy;
        snakeLen = newLen;

        if (ate) {
            score += 10;
            placeFood();
        }
    }

    private void placeFood() {
        int tries = 0;
        while (tries < 500) {
            int fx = (rng.nextInt() & 0x7fffffff) % GRID_W;
            int fy = (rng.nextInt() & 0x7fffffff) % GRID_H;
            boolean clash = false;
            for (int i = 0; i < snakeLen; i++) {
                if (snakeX[i] == fx && snakeY[i] == fy) { clash = true; break; }
            }
            if (!clash) { foodX = fx; foodY = fy; return; }
            tries++;
        }
        foodX = 0; foodY = 0;
    }

    private void doGameOver() {
        gameOver = true;
        alive = false;
        if (score > best) {
            best = score;
            Scores.saveOne(mode, best);
        }
    }

    protected void paint(Graphics g) {
        int w = getWidth();
        int h = getHeight();
        g.setColor(0x000000);
        g.fillRect(0, 0, w, h);

        // HUD
        g.setColor(0x4cff7a);
        Font f = Font.getFont(Font.FACE_MONOSPACE, Font.STYLE_BOLD, Font.SIZE_SMALL);
        g.setFont(f);
        String hud = SnakeMIDlet.MODE_NAMES[mode] + "  SCORE:" + score + "  BEST:" + best;
        g.drawString(hud, 2, 2, Graphics.TOP | Graphics.LEFT);

        // Board border
        g.setColor(0x4cff7a);
        g.drawRect(boardX - 1, boardY - 1, boardW + 1, boardH + 1);

        // Board background
        g.setColor(0x0f1a12);
        g.fillRect(boardX, boardY, boardW, boardH);

        // Food
        g.setColor(0xffd14c);
        g.fillRect(boardX + foodX * cellPx + 1, boardY + foodY * cellPx + 1, cellPx - 2, cellPx - 2);

        // Snake
        for (int i = 0; i < snakeLen; i++) {
            g.setColor(i == 0 ? 0xcfffd2 : 0x4cff7a);
            g.fillRect(boardX + snakeX[i] * cellPx + 1, boardY + snakeY[i] * cellPx + 1, cellPx - 2, cellPx - 2);
        }

        if (paused) {
            drawOverlay(g, "PAUSED", 0x4cff7a);
        } else if (gameOver) {
            drawOverlay(g, "GAME OVER  SCORE " + score, 0xff4c5e);
        }
    }

    private void drawOverlay(Graphics g, String msg, int color) {
        int w = getWidth();
        int h = getHeight();
        g.setColor(color);
        Font big = Font.getFont(Font.FACE_MONOSPACE, Font.STYLE_BOLD, Font.SIZE_MEDIUM);
        g.setFont(big);
        int tw = big.stringWidth(msg);
        int x = (w - tw) / 2;
        int y = h / 2 - big.getHeight() / 2;
        g.setColor(0x000000);
        g.fillRect(x - 4, y - 2, tw + 8, big.getHeight() + 4);
        g.setColor(color);
        g.drawRect(x - 4, y - 2, tw + 8, big.getHeight() + 4);
        g.drawString(msg, x, y, Graphics.TOP | Graphics.LEFT);
        if (gameOver) {
            Font sm = Font.getFont(Font.FACE_MONOSPACE, Font.STYLE_PLAIN, Font.SIZE_SMALL);
            g.setFont(sm);
            String hint = "FIRE = RETRY";
            int hw = sm.stringWidth(hint);
            g.drawString(hint, (w - hw) / 2, y + big.getHeight() + 6, Graphics.TOP | Graphics.LEFT);
        }
    }

    protected void keyPressed(int keyCode) {
        int ga;
        try { ga = getGameAction(keyCode); }
        catch (Exception e) { ga = 0; }

        if (gameOver) {
            if (ga == FIRE || keyCode == Canvas.KEY_NUM5 || keyCode == -5) {
                startGame();
            }
            return;
        }

        if (ga == UP || keyCode == Canvas.KEY_NUM2) {
            if (dir != DIR_DOWN) nextDir = DIR_UP;
        } else if (ga == DOWN || keyCode == Canvas.KEY_NUM8) {
            if (dir != DIR_UP) nextDir = DIR_DOWN;
        } else if (ga == LEFT || keyCode == Canvas.KEY_NUM4) {
            if (dir != DIR_RIGHT) nextDir = DIR_LEFT;
        } else if (ga == RIGHT || keyCode == Canvas.KEY_NUM6) {
            if (dir != DIR_LEFT) nextDir = DIR_RIGHT;
        } else if (ga == FIRE || keyCode == Canvas.KEY_NUM5) {
            paused = !paused;
            repaint();
        }
    }

    public void commandAction(Command c, Displayable d) {
        if (c == cmdHome) {
            stopGame();
            midlet.backToMenu();
        } else if (c == cmdPause) {
            if (!gameOver) {
                paused = !paused;
                repaint();
            }
        }
    }
}
