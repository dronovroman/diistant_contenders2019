package com.example.cas2029mobile;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.os.Environment;
import android.view.SurfaceView;
import android.view.View;
import android.widget.Toast;
import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.CameraBridgeViewBase;
import org.opencv.android.JavaCameraView;
import org.opencv.android.OpenCVLoader;
import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfFloat;
import org.opencv.core.MatOfInt;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.dnn.Net;
import org.opencv.imgproc.Imgproc;
import org.opencv.dnn.Dnn;
import org.opencv.utils.Converters;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;




public class Activity2 extends AppCompatActivity implements CameraBridgeViewBase.CvCameraViewListener2 {
    BaseLoaderCallback baseLoaderCallback;

    CameraBridgeViewBase cameraBridgeViewBase;
    public boolean startYolo = false;
    public boolean loadYolo = false;
    //EditText updTimer = (EditText) findViewById(R.id.editText);
    //EditText updTimer = (EditText) findViewById(R.id.editText);

    Net modelYolo;

    public void processYOLO(View Button){
        if (startYolo == false){
            startYolo = true;
            if (loadYolo == false){
                loadYolo = true;
                //config for tiny
                String tinyYoloCfg = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3cbr.cfg" ;
                String tinyYoloWeights = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3cbr.weights";
                //config for full
                //String tinyYoloCfg = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3.cfg" ;
                //String tinyYoloWeights = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3.weights";
                modelYolo = Dnn.readNetFromDarknet(tinyYoloCfg, tinyYoloWeights);

            }
        }
        else{
            startYolo = false;

        }
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_2);
        cameraBridgeViewBase = (JavaCameraView)findViewById(R.id.CameraView);
        cameraBridgeViewBase.setVisibility(SurfaceView.VISIBLE);
        cameraBridgeViewBase.setCvCameraViewListener(this);

        baseLoaderCallback = new BaseLoaderCallback(this) {
            @Override
            public void onManagerConnected(int status) {
                super.onManagerConnected(status);
                switch(status){
                    case BaseLoaderCallback.SUCCESS:
                        cameraBridgeViewBase.enableView();
                        break;
                    default:
                        super.onManagerConnected(status);
                        break;
                }
            }
        };
    }

    @Override
    public Mat onCameraFrame(CameraBridgeViewBase.CvCameraViewFrame inputFrame) {
        Mat frame = inputFrame.rgba();

        if (startYolo == true) {

            Imgproc.cvtColor(frame, frame, Imgproc.COLOR_RGBA2RGB);
            Mat imageBlob = Dnn.blobFromImage(frame, 0.00392, new Size(416,416),new Scalar(0, 0, 0),/*swapRB*/false, /*crop*/false);
            modelYolo.setInput(imageBlob);
            java.util.List<Mat> result = new java.util.ArrayList<Mat>(3);
            List<String> outBlobNames = new java.util.ArrayList<>();
            //config for tiny
            outBlobNames.add(0, "yolo_16");
            outBlobNames.add(1, "yolo_23");
            //config to full
            //outBlobNames.add(0, "yolo_82");
            //outBlobNames.add(1, "yolo_94");
            //outBlobNames.add(1, "yolo_106");
            modelYolo.forward(result,outBlobNames);
            float confThreshold = 0.3f;
            List<Integer> clsIds = new ArrayList<>();
            List<Float> confs = new ArrayList<>();
            List<Rect> rects = new ArrayList<>();
            for (int i = 0; i < result.size(); ++i)
            {
                Mat level = result.get(i);
                for (int j = 0; j < level.rows(); ++j)
                {
                    Mat row = level.row(j);
                    Mat scores = row.colRange(5, level.cols());
                    Core.MinMaxLocResult mm = Core.minMaxLoc(scores);
                    float confidence = (float)mm.maxVal;
                    Point classIdPoint = mm.maxLoc;
                    if (confidence > confThreshold)
                    {
                        int centerX = (int)(row.get(0,0)[0] * frame.cols());
                        int centerY = (int)(row.get(0,1)[0] * frame.rows());
                        int width   = (int)(row.get(0,2)[0] * frame.cols());
                        int height  = (int)(row.get(0,3)[0] * frame.rows());
                        int left    = centerX - width  / 2;
                        int top     = centerY - height / 2;
                        clsIds.add((int)classIdPoint.x);
                        confs.add((float)confidence);
                        rects.add(new Rect(left, top, width, height));
                    }
                }
            }
            int ArrayLength = confs.size();

            if (ArrayLength>=1) {
                // Apply NMS
                float nmsThresh = 0.15f;
                MatOfFloat confidences = new MatOfFloat(Converters.vector_float_to_Mat(confs));
                Rect[] boxesArray = rects.toArray(new Rect[0]);
                MatOfRect boxes = new MatOfRect(boxesArray);
                MatOfInt indices = new MatOfInt();
                Dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThresh, indices);
                // Draw result boxes:
                int[] ind = indices.toArray();
                for (int i = 0; i < ind.length; ++i) {
                    int idx = ind[i];
                    Rect box = boxesArray[idx];
                    int idInd = clsIds.get(idx);
                    float conf = confs.get(idx);
                    List<String> cocoNames = Arrays.asList("person", "bicycle", "vehicle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "car", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racquet", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "doughnut", "cake", "chair", "sofa", "potted plant", "bed", "dining table", "toilet", "TV monitor", "laptop", "computer mouse", "remote control", "keyboard", "mobile phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush");
                    int intConf = (int) (conf * 100);
                    Imgproc.putText(frame,cocoNames.get(idInd) + " " + intConf + "%",box.tl(),Core.FONT_HERSHEY_SIMPLEX, 1, new Scalar(255,255,0),4);
                    Imgproc.rectangle(frame, box.tl(), box.br(), new Scalar(255, 0, 0), 2);
                }
            }
        }
        return frame;
    }


    @Override
    public void onCameraViewStarted(int width, int height) {
        if (startYolo == true){

            //String tinyYoloCfg = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3-tiny.cfg" ;
            //String tinyYoloWeights = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3-tiny.weights";
            String tinyYoloCfg = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3.cfg" ;
            String tinyYoloWeights = Environment.getExternalStorageDirectory() + "/nnmodel/yolov3.weights";
            modelYolo = Dnn.readNetFromDarknet(tinyYoloCfg, tinyYoloWeights);
        }
    }


    @Override
    public void onCameraViewStopped() {
    }


    @Override
    protected void onResume() {
        super.onResume();
        if (!OpenCVLoader.initDebug()){
            Toast.makeText(getApplicationContext(),"Could not resume", Toast.LENGTH_SHORT).show();
        } else {
            baseLoaderCallback.onManagerConnected(baseLoaderCallback.SUCCESS);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if(cameraBridgeViewBase!=null){
            cameraBridgeViewBase.disableView();
        }
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraBridgeViewBase!=null){
            cameraBridgeViewBase.disableView();
        }
    }
}