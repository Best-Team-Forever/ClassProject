package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.model;

import java.sql.Date;

import org.springframework.format.annotation.DateTimeFormat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Patient {

    @Id
    private Integer id;
    @Column(name = "external_id")
    private String externalId;
    @Column(name = "first_name")
    private String firstName;
    @Column(name = "last_name")
    private String lastName;
    @DateTimeFormat
    private Date dateOfBirth;
    @Column(name = "gender")
    private String gender;
    @Column(name = "image_path")
    private String imagePath;
    @Column(name = "ai_score")
    private double aiScore;
    @Column(name = "creation_user")
    private int creationUser;

    public Integer getId() {
        return id;
    }

    public String getExternalId(){
        return externalId;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public Date getBirthDate(){
        return dateOfBirth;
    }

    public String getGender(){
        return gender;
    }

    public String getImagePath(){
        return imagePath;
    }

    public double getScore(){
        return aiScore;
    }

    public int getCreationUser(){
        return creationUser;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public void setExternalId(String externalId){
        this.externalId = externalId;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setBirthDate(Date date){
        this.dateOfBirth = date;
    }

    public void setGender(String gender){
        this.gender = gender;
    }

    public void setImagePath(String imagepath){
        this.imagePath = imagepath;
    }

    public void setScore(double score){
        this.aiScore = score;
    }

    public void setCreationUser(int creation_user){
        this.creationUser = creation_user;
    }

}
