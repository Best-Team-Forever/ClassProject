package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.service;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public class StorageServiceImplTest {

    @Test
    void whenFileIsEmptyAnExceptionIsThrown() {

        //setup
        MultipartFile file = Mockito.mock(MultipartFile.class);
        StorageService storageService = new StorageServiceImpl();
        Mockito.when(file.isEmpty()).thenReturn(true);

        //execute
        Exception exception = Assertions.assertThrows(IOException.class, () -> {
            storageService.store(file);
        });

    }

    @Test
    void whenFileExtensionIsNotValidAnExceptionIsThrown() {

        //setup
        MultipartFile file = Mockito.mock(MultipartFile.class);
        StorageService storageService = new StorageServiceImpl();
        Mockito.when(file.isEmpty()).thenReturn(false);
        Mockito.when(file.getOriginalFilename()).thenReturn("image.txt");

        //execute
        Exception exception = Assertions.assertThrows(IOException.class, () -> {
            storageService.store(file);
        });
    }

}
