package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

@Service
public class StorageServiceImpl implements StorageService {

    private final Path rootLocation;

    public StorageServiceImpl() {
        this.rootLocation = Path.of("/data", "images");
    }

    public void store(MultipartFile file) throws IOException {

        if (file.isEmpty()) {
            throw new IOException("Failed to store empty file.");
        }

        String fileName = file.getOriginalFilename();
        if (!fileName.endsWith(".jpg") && !fileName.endsWith(".JPG")) {
            throw new IOException("Invalid file");
        }

        Path destinationFile = this.rootLocation.resolve(Paths.get("image")).normalize();

        try (InputStream inputStream = file.getInputStream()) {
            Files.copy(inputStream, destinationFile,
                    StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException ex) {
            throw ex;
        }
    }
}
