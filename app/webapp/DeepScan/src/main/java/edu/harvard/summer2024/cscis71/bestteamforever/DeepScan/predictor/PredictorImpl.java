package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor;

import org.springframework.stereotype.Service;

import java.io.IOException;

@Service
public class PredictorImpl implements Predictor {

    private final ProcessBuilder processBuilder;

    public PredictorImpl() {
        processBuilder = new ProcessBuilder("python3", "/python-docker/predict.py", "/data/images/image");
    }

    public PredictorImpl(ProcessBuilder processBuilder) {
        this.processBuilder = processBuilder;
    }


    public double predict() {

        try {
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();
            int exitCode = process.waitFor();

            if (exitCode != 0) {
                throw new RuntimeException("Predictor failed with exit code: " + exitCode);
            }

            double result = Double.parseDouble(new String(process.getInputStream().readAllBytes()));
            System.out.println("Result: " + result);

            return result;

        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }

        return -1;
    }
}
