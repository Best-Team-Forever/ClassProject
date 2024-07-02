package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.endpoint;

import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.endpoint.response.AccessToken;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Authentication {

    @PostMapping("/authenticate")
    public AccessToken authenticate(){
        return new AccessToken("Dummy Access Token");
    }

}
