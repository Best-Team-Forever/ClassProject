CREATE SCHEMA `deepscan`;

CREATE TABLE `deepscan`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(256) NOT NULL,
  `role` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE
);

CREATE TABLE `deepscan`.`patient` (
  `id` int NOT NULL AUTO_INCREMENT,
  `external_id` varchar(255) DEFAULT NULL,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` varchar(10) NOT NULL,
  `image_path` varchar(256) DEFAULT NULL,
  `ai_score` decimal(5,2) DEFAULT NULL,
  `creation_user` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `external_id_UNIQUE` (`external_id`),
  CONSTRAINT `fk_patient_user` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
);
