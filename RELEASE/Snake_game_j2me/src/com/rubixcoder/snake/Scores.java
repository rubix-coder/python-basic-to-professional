package com.rubixcoder.snake;

import javax.microedition.rms.RecordStore;
import javax.microedition.rms.RecordStoreException;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public final class Scores {

    private static final String STORE_NAME = "snake_hs";

    private Scores() {}

    public static int[] loadAll() {
        int[] out = new int[3];
        RecordStore rs = null;
        try {
            rs = RecordStore.openRecordStore(STORE_NAME, true);
            if (rs.getNumRecords() == 0) return out;
            byte[] data = rs.getRecord(1);
            if (data == null || data.length < 12) return out;
            DataInputStream in = new DataInputStream(new ByteArrayInputStream(data));
            for (int i = 0; i < 3; i++) out[i] = in.readInt();
            in.close();
        } catch (Exception e) {
            // fall through with zeros
        } finally {
            closeQuiet(rs);
        }
        return out;
    }

    public static int loadOne(int mode) {
        int[] all = loadAll();
        if (mode < 0 || mode >= all.length) return 0;
        return all[mode];
    }

    public static void saveOne(int mode, int value) {
        int[] all = loadAll();
        if (mode < 0 || mode >= all.length) return;
        if (value <= all[mode]) return;
        all[mode] = value;
        saveAll(all);
    }

    public static void saveAll(int[] vals) {
        RecordStore rs = null;
        try {
            rs = RecordStore.openRecordStore(STORE_NAME, true);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            DataOutputStream out = new DataOutputStream(bos);
            for (int i = 0; i < 3; i++) {
                int v = (i < vals.length) ? vals[i] : 0;
                out.writeInt(v);
            }
            out.close();
            byte[] data = bos.toByteArray();
            if (rs.getNumRecords() == 0) {
                rs.addRecord(data, 0, data.length);
            } else {
                rs.setRecord(1, data, 0, data.length);
            }
        } catch (Exception e) {
            // ignore
        } finally {
            closeQuiet(rs);
        }
    }

    private static void closeQuiet(RecordStore rs) {
        if (rs == null) return;
        try { rs.closeRecordStore(); }
        catch (RecordStoreException e) {}
    }
}
