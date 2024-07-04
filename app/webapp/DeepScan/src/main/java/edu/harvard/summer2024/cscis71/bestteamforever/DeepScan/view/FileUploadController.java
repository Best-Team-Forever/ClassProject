package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.view;

import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor.Predictor;
import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.service.StorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Controller
public class FileUploadController {

    private final StorageService storageService;
    private final Predictor predictor;

    @Autowired
    public FileUploadController(StorageService storageService, Predictor predictor) {
        this.storageService = storageService;
        this.predictor = predictor;
    }

    @PostMapping("/upload")
    public String uploadFile(@RequestParam("file") MultipartFile file, Model model) {

        if (file.isEmpty()) {
            return "error";
        }

        try {
            storageService.store(file);
        } catch (IOException e) {
            return "error";
        }

        double result = predictor.predict();

        model.addAttribute("score", String.format("%f", result));

        return "image";
    }

}
