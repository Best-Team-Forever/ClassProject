package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.view;

import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.predictor.Predictor;
import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.service.StorageService;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.ui.Model;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public class FileUploadControllerTest {

    @Test
    void whenFileIsNotNullItIsStored() {

        //setup
        MultipartFile file = Mockito.mock(MultipartFile.class);
        StorageService storageService = Mockito.mock(StorageService.class);
        Predictor predictor = Mockito.mock(Predictor.class);
        Model model = Mockito.mock(Model.class);
        FileUploadController fileUploadController = new FileUploadController(storageService, predictor);
        Mockito.when(file.isEmpty()).thenReturn(false);

        //execute
        fileUploadController.uploadFile(file, model);

        //assert
        try {
            Mockito.verify(storageService).store(file);
        } catch (IOException e) {
            Assertions.fail();
        }
    }

    @Test
    void whenFileIsEmptyFlowIsRedirectedToErrorPage() {

        //setup
        MultipartFile file = Mockito.mock();
        StorageService storageService = Mockito.mock(StorageService.class);
        Predictor predictor = Mockito.mock(Predictor.class);
        Model model = Mockito.mock(Model.class);
        FileUploadController fileUploadController = new FileUploadController(storageService, predictor);
        Mockito.when(file.isEmpty()).thenReturn(true);

        //execute
        String target = fileUploadController.uploadFile(file, model);

        //assert
        Assertions.assertEquals(target, "error");
    }

    @Test
    void whenStoringTheFileFailsFlowIsRedirectedToErrorPage() throws IOException {

        //setup
        MultipartFile file = Mockito.mock();
        StorageService storageService = Mockito.mock(StorageService.class);
        Predictor predictor = Mockito.mock(Predictor.class);
        Model model = Mockito.mock(Model.class);
        FileUploadController fileUploadController = new FileUploadController(storageService, predictor);
        Mockito.when(file.isEmpty()).thenReturn(false);
        Mockito.doThrow(new IOException()).when(storageService).store(file);

        //execute
        String target = fileUploadController.uploadFile(file, model);

        //assert
        Assertions.assertEquals(target, "error");
    }

    @Test
    void whenFileIsProcessedTheRiskScoreIsAddedToTheModel() {

        //setup
        double riskScore = 34.0;
        MultipartFile file = Mockito.mock();
        StorageService storageService = Mockito.mock(StorageService.class);
        Predictor predictor = Mockito.mock(Predictor.class);
        Model model = Mockito.mock(Model.class);
        FileUploadController fileUploadController = new FileUploadController(storageService, predictor);
        Mockito.when(file.isEmpty()).thenReturn(false);
        Mockito.when(predictor.predict()).thenReturn(riskScore);

        //execute
        fileUploadController.uploadFile(file, model);

        //assert
        Mockito.verify(model).addAttribute("score", String.format("%f", riskScore));
    }

    @Test
    void whenFileIsProcessedFlowIsRedirectedToResultsPage(){

        //setup
        MultipartFile file = Mockito.mock();
        StorageService storageService = Mockito.mock(StorageService.class);
        Predictor predictor = Mockito.mock(Predictor.class);
        Model model = Mockito.mock(Model.class);
        FileUploadController fileUploadController = new FileUploadController(storageService, predictor);
        Mockito.when(file.isEmpty()).thenReturn(false);

        //execute
        String target = fileUploadController.uploadFile(file, model);

        //assert
        Assertions.assertEquals(target, "image");
    }

}
