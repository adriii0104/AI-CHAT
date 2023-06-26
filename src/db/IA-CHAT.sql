
# aqui almacenaremos los datos del usario, poniendo un ID principal y un idusuario.
CREATE TABLE `genuineai`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `idusuarios` VARCHAR(255) NULL,
  `name` VARCHAR(255) NULL,
  `last-name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `api` VARCHAR(255) NULL,
  `fecha` VARCHAR(255) NULL,
  `datos` VARCHAR(255) NULL,
  PRIMARY KEY (`id`));


#esta es la segunda tabla, es para verificar el usuarios
CREATE TABLE `IA`.`verificacion` (
  `idusuario` VARCHAR(255) NULL,
  `verificado` VARCHAR(255) NULL,
  `codigo` VARCHAR(255) NULL,
  `fecha` VARCHAR(255) NULL);


  #tabla sobre preferencias
  CREATE TABLE `genuineai`.`preferencias` (
  `idusuarios` VARCHAR(255) NOT NULL,
  `speak` VARCHAR(45) NULL,
  `2factor` VARCHAR(45) NULL,
  PRIMARY KEY (`idusuarios`));

  #tabla información
  CREATE TABLE `genuineai`.`datos` (
  `idusuarios` VARCHAR(255) NOT NULL,
  `edad` VARCHAR(45) NULL,
  `ano` VARCHAR(45) NULL,
  `mes` VARCHAR(45) NULL,
  `dia` VARCHAR(45) NULL,
  `genero` VARCHAR(45) NULL,
  PRIMARY KEY (`idusuarios`));
