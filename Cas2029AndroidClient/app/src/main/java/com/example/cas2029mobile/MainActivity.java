package com.example.cas2029mobile;

import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.pm.PackageManager;
import android.location.Location;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;
import android.content.Intent;

import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.tasks.OnSuccessListener;

public class MainActivity extends AppCompatActivity {
    private FusedLocationProviderClient client;
    public boolean voicePromptsEnabled = false; //
    public static EditText data1;
    public static EditText data2;
    public static EditText urldata;
    public static EditText varLAT;
    public static EditText varLON;
    public static EditText varRAD;

    Boolean gStartAnalysis=false;
    int count = 0;
    Thread t;
    String gLON;
    String gLAT;
    public String apiURL;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);
        data1 = findViewById(R.id.editText4);
        data2 = findViewById(R.id.editText5);
        urldata = findViewById(R.id.editTextURL);
        varLAT = findViewById(R.id.editTextLAT);
        varLON = findViewById(R.id.editTextLON);
        varRAD = findViewById(R.id.editText8);
        Button button2 = (Button) findViewById(R.id.button2);

        button2.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                openActivity2();
            }
        });

        final EditText eTextLAT = (EditText) findViewById(R.id.editTextLAT);
        final EditText eTextLON = (EditText) findViewById(R.id.editTextLON);
        final EditText updTimer = (EditText) findViewById(R.id.editText);


        client = LocationServices.getFusedLocationProviderClient(this);


        // timer thread part
        t = new Thread() {
            @Override
            public void run() {
                int dl;
                while (!isInterrupted()) {
                    try {

                        try {
                            dl = Integer.parseInt(updTimer.getText().toString());
                        } catch (NumberFormatException exception) {
                            dl = 3;
                        }

                        int delay = dl * 1000;
                        Thread.sleep(delay);

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                // Runnable
                                count++;

                                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ) {
                                    // TODO: Consider calling
                                    //    Activity#requestPermissions
                                    // here to request the missing permissions, and then overriding
                                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                    //                                          int[] grantResults)
                                    // to handle the case where the user grants the permission. See the documentation
                                    // for Activity#requestPermissions for more details.
                                    return;
                                }
                                client.getLastLocation().addOnSuccessListener(MainActivity.this, new OnSuccessListener<Location>() {
                                    @Override
                                    public void onSuccess(Location location) {
                                        if (location!=null){
                                            String latt = String.valueOf(location.getLatitude());
                                            String lonn = String.valueOf(location.getLongitude());
                                            eTextLAT.setText(latt);
                                            gLAT=latt;
                                            eTextLON.setText(lonn);
                                            gLON=lonn;
                                        }

                                    }
                                });
                                //
                                // if Start analysis is true
                                // call API
                                if (gStartAnalysis){
                                    fetchData updateAPI = new fetchData();
                                    updateAPI.execute();
                                }

                            }
                        });
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        };
        t.start();
        // end timer thread part


        final Switch onOffSwitch = (Switch)  findViewById(R.id.voice_switch);
        onOffSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                //Log.v("Switch State=", ""+isChecked);
                if (isChecked) {
                    onOffSwitch.setText("ON");
                    voicePromptsEnabled = true;
                } else {
                    onOffSwitch.setText("OFF");
                    voicePromptsEnabled = false;
                }
            }

        });



    }

    public void openActivity2() {
        Intent intent = new Intent (this, Activity2.class);
        startActivity(intent);
    }


    public void btnStartAnalysis(View view){
        // on start analysis - API calls
        Button bsa = findViewById(R.id.buttonApply);
        EditText etURL = (EditText) findViewById(R.id.editTextURL);
        if(bsa.getText().toString()=="Start Analysis"){
            bsa.setText("Stop Analysis");
            gStartAnalysis=true;
            apiURL= etURL.getText().toString();
        }else{
            bsa.setText("Start Analysis");
            gStartAnalysis=false;
        }


    }






}
