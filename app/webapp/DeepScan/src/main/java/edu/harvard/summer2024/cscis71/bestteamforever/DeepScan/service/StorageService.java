package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public interface StorageService {

    void store(MultipartFile file) throws IOException;
}
