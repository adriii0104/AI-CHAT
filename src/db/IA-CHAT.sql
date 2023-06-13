
# aqui almacenaremos los datos del usario, poniendo un ID principal y un idusuario.
CREATE TABLE `IA`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `idusuarios` VARCHAR(255) NULL,
  `name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `api` VARCHAR(255) NULL,
  `fecha` VARCHAR(255) NULL,
  PRIMARY KEY (`id`));


#esta es la segunda tabla, es para verificar el usuarios
CREATE TABLE `IA`.`verificacion` (
  `idusuario` VARCHAR(255) NULL,
  `verificado` VARCHAR(255) NULL,
  `codigo` VARCHAR(255) NULL,
  `fecha` VARCHAR(255) NULL);
