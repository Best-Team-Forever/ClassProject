package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.endpoint;

import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.endpoint.response.AccessToken;
import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.repository.UserRepository;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Authentication {

    private UserRepository userRepository;

    @PostMapping("/authenticate")
    public AccessToken authenticate(){

        userRepository.findByUsername("radiologist");

        return new AccessToken("Dummy Access Token");
    }

}
