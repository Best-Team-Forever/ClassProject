Feature: Save patient information
  As a radiologist, I want to save a patient's information and be able to retrieve it later, so that I can review the
  patient's analysis results and comments

  Rule: The radiologist can save the patient's information, including comments, and then can retrieve that information

    Scenario: The radiologist saves Molly's information
      Given Molly's image has been uploaded
      When A radiologist saves Molly's information
      Then Molly's information is available in the application
