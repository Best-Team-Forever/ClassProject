package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.web.client.RestClient;

import java.io.ByteArrayInputStream;
import java.io.IOException;

public class PredictorImplTest {

    @Test
    void whenPredictIsCalledAIModelIsInvoked() throws IOException {

        //setup
        RestClient restClient = Mockito.mock(RestClient.class);
        Predictor predictor = new PredictorImpl(restClient);

    }
/*
    @Test
    void whenPredictionIsDoneTheResultIsReturned() throws IOException {

        //setup
        ProcessBuilder processBuilder = Mockito.mock(ProcessBuilder.class);
        Process process = Mockito.mock(Process.class);
        Mockito.when(processBuilder.start()).thenReturn(process);
        Mockito.when(process.getInputStream()).thenReturn(new ByteArrayInputStream("0.67".getBytes()));

        PredictorImpl predictor = new PredictorImpl(processBuilder);

        //execute
        double result = predictor.predict();

        //assert
        Assertions.assertEquals(0.67, result);
    }

    @Test
    void whenPredictionProcessFailsAnExceptionIsThrown() throws IOException, InterruptedException {

        //setup
        ProcessBuilder processBuilder = Mockito.mock(ProcessBuilder.class);
        Process process = Mockito.mock(Process.class);
        Mockito.when(processBuilder.start()).thenReturn(process);
        Mockito.when(process.waitFor()).thenReturn(132);

        PredictorImpl predictor = new PredictorImpl(processBuilder);

        //execute and assert

        Exception exception = Assertions.assertThrows(RuntimeException.class, predictor::predict);
    }*/
}
