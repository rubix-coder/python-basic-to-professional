package com.rubixcoder.snake;

import javax.microedition.midlet.MIDlet;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.List;
import javax.microedition.lcdui.Choice;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Alert;
import javax.microedition.lcdui.AlertType;

public class SnakeMIDlet extends MIDlet implements CommandListener {

    public static final int MODE_EASY = 0;
    public static final int MODE_MEDIUM = 1;
    public static final int MODE_HARD = 2;
    public static final String[] MODE_NAMES = {"EASY", "MEDIUM", "HARD"};

    private Display display;
    private List mainMenu;
    private List modeMenu;
    private List scoresMenu;
    private SnakeCanvas gameCanvas;

    private Command cmdSelect;
    private Command cmdExit;
    private Command cmdBack;

    private int currentMode = MODE_EASY;

    protected void startApp() {
        if (display == null) {
            display = Display.getDisplay(this);
            cmdSelect = new Command("SELECT", Command.OK, 1);
            cmdExit = new Command("EXIT", Command.EXIT, 2);
            cmdBack = new Command("BACK", Command.BACK, 1);
            buildMainMenu();
        }
        display.setCurrent(mainMenu);
    }

    protected void pauseApp() {
        if (gameCanvas != null) gameCanvas.pauseGame();
    }

    protected void destroyApp(boolean unconditional) {
        if (gameCanvas != null) gameCanvas.stopGame();
    }

    private void buildMainMenu() {
        mainMenu = new List("RETRO SNAKE", Choice.IMPLICIT);
        mainMenu.append("NEW GAME", null);
        mainMenu.append("MODE: " + MODE_NAMES[currentMode], null);
        mainMenu.append("HIGH SCORES", null);
        mainMenu.append("ABOUT", null);
        mainMenu.append("EXIT", null);
        mainMenu.addCommand(cmdSelect);
        mainMenu.addCommand(cmdExit);
        mainMenu.setCommandListener(this);
    }

    private void refreshMainMenu() {
        mainMenu.set(1, "MODE: " + MODE_NAMES[currentMode], null);
    }

    private void showModeMenu() {
        modeMenu = new List("GAME MODE", Choice.IMPLICIT);
        for (int i = 0; i < MODE_NAMES.length; i++) {
            modeMenu.append(MODE_NAMES[i], null);
        }
        modeMenu.setSelectedIndex(currentMode, true);
        modeMenu.addCommand(cmdSelect);
        modeMenu.addCommand(cmdBack);
        modeMenu.setCommandListener(this);
        display.setCurrent(modeMenu);
    }

    private void showScores() {
        scoresMenu = new List("HIGH SCORES", Choice.IMPLICIT);
        int[] best = Scores.loadAll();
        for (int i = 0; i < MODE_NAMES.length; i++) {
            String line = MODE_NAMES[i] + ": " + best[i];
            scoresMenu.append(line, null);
        }
        scoresMenu.addCommand(cmdBack);
        scoresMenu.setCommandListener(this);
        display.setCurrent(scoresMenu);
    }

    private void showAbout() {
        Alert a = new Alert("ABOUT", "RETRO SNAKE v1\n\nDEVELOPED BY\nJESAL P\n(rubix-coder)\n\nMove: D-PAD\nPause: FIRE\nBack: SOFTKEY", null, AlertType.INFO);
        a.setTimeout(Alert.FOREVER);
        display.setCurrent(a, mainMenu);
    }

    private void startGame() {
        gameCanvas = new SnakeCanvas(this, currentMode);
        display.setCurrent(gameCanvas);
        gameCanvas.startGame();
    }

    public void backToMenu() {
        gameCanvas = null;
        display.setCurrent(mainMenu);
    }

    public Display getDisplay() {
        return display;
    }

    public void commandAction(Command c, Displayable d) {
        if (d == mainMenu) {
            if (c == cmdExit || c == List.SELECT_COMMAND && mainMenu.getSelectedIndex() == 4) {
                destroyApp(true);
                notifyDestroyed();
                return;
            }
            if (c == cmdSelect || c == List.SELECT_COMMAND) {
                int idx = mainMenu.getSelectedIndex();
                if (idx == 0) startGame();
                else if (idx == 1) showModeMenu();
                else if (idx == 2) showScores();
                else if (idx == 3) showAbout();
                else if (idx == 4) { destroyApp(true); notifyDestroyed(); }
            }
        } else if (d == modeMenu) {
            if (c == cmdBack) {
                display.setCurrent(mainMenu);
            } else if (c == cmdSelect || c == List.SELECT_COMMAND) {
                currentMode = modeMenu.getSelectedIndex();
                refreshMainMenu();
                display.setCurrent(mainMenu);
            }
        } else if (d == scoresMenu) {
            if (c == cmdBack || c == List.SELECT_COMMAND) {
                display.setCurrent(mainMenu);
            }
        }
    }
}
