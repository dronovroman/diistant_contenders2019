package com.example.cas2029mobile;

import android.os.AsyncTask;
import android.os.Debug;
import android.util.Log;
import android.widget.EditText;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;


public class fetchData extends AsyncTask <Void, Void, Void>{
    String data = "";
    String dataParsed = "";
    String sinigleParsed = "";
    String dParsed1 = "";
    String dParsed2 = "";
    String CompoundURL = "";
    String etURL = MainActivity.urldata.getText().toString();
    String etLAT = MainActivity.varLAT.getText().toString();
    String etLON = MainActivity.varLON.getText().toString();
    String etRAD = MainActivity.varRAD.getText().toString();




    @Override
    protected Void doInBackground(Void... voids) {
        try {
            CompoundURL = etURL+"LAT="+etLAT+"&LON="+etLON+"&RADIUS="+etRAD;
            URL url = new URL(CompoundURL);
            HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
            InputStream inputStream = httpURLConnection.getInputStream();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
            String line = "";
            data = "";
            while (line !=null){
                line = bufferedReader.readLine();
                data = data + line;
            }
            JSONArray JA = new JSONArray(data);
            JSONObject JO = JA.getJSONObject(1); // cyclists data
            dParsed1 = Integer.toString((Integer) JO.get("Injury"));
            dParsed2 = Integer.toString((Integer)JO.get("Fatal"));




        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }


        return null;
    }

    @Override
    protected void onPostExecute(Void aVoid) {
        super.onPostExecute(aVoid);

        MainActivity.data1.setText(dParsed1);
        MainActivity.data2.setText(dParsed2);
        Log.i("DATAURL", CompoundURL);//dParsed1 + dParsed2);
        Log.i("DATARESP", data);//dParsed1 + dParsed2);
    }
}
