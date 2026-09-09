package com.demjastudio.gooblaster;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(BattleReportPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
