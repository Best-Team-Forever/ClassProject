package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class PredictorImpl implements Predictor {

    private final RestClient restClient;

    public PredictorImpl() {
        this.restClient = RestClient.builder().baseUrl("http://ai:5001").build();
    }

    public PredictorImpl(RestClient restClient) {
        this.restClient = restClient;
    }

    public double predict() {

        ResponseEntity<String> response = restClient.get().retrieve().toEntity(String.class);

        if (response.getStatusCode().is2xxSuccessful()) {
            return Double.parseDouble(response.getBody());
        }

        return -1.0;
    }
}
