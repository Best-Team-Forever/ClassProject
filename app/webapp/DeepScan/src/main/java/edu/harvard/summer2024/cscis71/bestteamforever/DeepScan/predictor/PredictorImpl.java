package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor;

import org.springframework.stereotype.Service;

import java.io.IOException;

@Service
public class PredictorImpl implements Predictor {

    public double predict() {

        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "/python-docker/predict.py", "/data/images/image");

            processBuilder.redirectErrorStream(true);

            Process process = processBuilder.start();
            int exitCode = process.waitFor();

            double result = Double.parseDouble(new String(process.getInputStream().readAllBytes()));
            System.out.println("Result: " + result);

            if (exitCode != 0) {
                System.out.println("Error exit code: " + exitCode);
            }

            return result;

        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }

        return -1;
    }
}
