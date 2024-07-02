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
    @Id(name = "external_id")
    private String external_id;
    @Column(name = "first_name")
    private String firstName;
    @Column(name = "last_name")
    private String lastName;
    @DateTimeFormat
    private Date date_of_birth;
    @Column(name = "gender")
    private String gender;
    @Column(name = "image_path")
    private String image_path;
    @Column(name = "ai_score")
    private double ai_score;
    @Column(name = "creation_user")
    private int creation_user;

    public Integer getId() {
        return id;
    }

    public String getExternalId(){
        return external_id;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public Date getBirthDate(){
        return date_of_birth;
    }

    public String getGender(){
        return gender;
    }

    public String getImagePath(){
        return image_path;
    }

    public double getScore(){
        return ai_score;
    }

    public int getCreationUser(){
        return creation_user;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public void setExternalId(String externalId){
        this.external_id = externalId;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setBirthDate(Date date){
        this.date_of_birth = date;
    }

    public void setGender(String gender){
        this.gender = gender;
    }

    public void setImagePath(String imagepath){
        this.image_path = imagepath;
    }

    public void setScore(double score){
        this.ai_score = score;
    }

    public void setCreationUser(int creation_user){
        this.creation_user = creation_user;
    }

}
