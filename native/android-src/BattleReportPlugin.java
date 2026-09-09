package com.demjastudio.gooblaster;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.util.Base64;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.OutputStream;

/** User-selected document export; no broad storage or photo permissions. */
@CapacitorPlugin(name = "BattleReport")
public class BattleReportPlugin extends Plugin {
    private volatile boolean busy;

    private byte[] image(PluginCall call) {
        String encoded = call.getString("base64", "");
        if (encoded.length() > 4_000_000) throw new IllegalArgumentException("Report too large");
        byte[] bytes = Base64.decode(encoded, Base64.DEFAULT);
        byte[] signature = {(byte)137, 80, 78, 71, 13, 10, 26, 10};
        if (bytes.length < signature.length) throw new IllegalArgumentException("Empty report");
        for (int i = 0; i < signature.length; i++) {
            if (bytes[i] != signature[i]) throw new IllegalArgumentException("Expected PNG");
        }
        return bytes;
    }

    @PluginMethod
    public void saveImage(PluginCall call) {
        if (busy) { call.reject("Export already open"); return; }
        try {
            image(call);
            String filename = call.getString("filename", "");
            if (!filename.matches("goo-blaster-L[0-9]{1,3}\\.png")) throw new IllegalArgumentException("Invalid filename");
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("image/png");
            intent.putExtra(Intent.EXTRA_TITLE, filename);
            busy = true;
            startActivityForResult(call, intent, "documentSelected");
        } catch (Exception error) {
            busy = false;
            call.reject("Could not open document picker", error);
        }
    }

    @ActivityCallback
    private void documentSelected(PluginCall call, ActivityResult result) {
        if (call == null) { busy = false; return; }
        if (result.getResultCode() == Activity.RESULT_CANCELED) {
            busy = false;
            call.resolve(new JSObject().put("status", "cancelled"));
            return;
        }
        Uri uri = result.getData() == null ? null : result.getData().getData();
        if (result.getResultCode() != Activity.RESULT_OK || uri == null) {
            busy = false; call.reject("No document selected"); return;
        }
        getBridge().execute(() -> {
            try {
                byte[] bytes = image(call);
                try (OutputStream output = getContext().getContentResolver().openOutputStream(uri, "w")) {
                    if (output == null) throw new java.io.IOException("No output stream");
                    output.write(bytes);
                    output.flush();
                }
                call.resolve(new JSObject().put("status", "saved"));
            } catch (Exception error) {
                call.reject("Could not write report", error);
            } finally { busy = false; }
        });
    }
}
