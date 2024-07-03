package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.view;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.multipart.MultipartFile;

@Controller
public class FileUploadController {

    @PostMapping("/upload")
    public String uploadFile(MultipartFile file) {

        return "redirect:/";
    }

}
