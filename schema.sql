CREATE TABLE `db`.`users` (
  `user_id` BIGINT NULL AUTO_INCREMENT,
  `user_username` VARCHAR(45) NULL,
  `user_password` VARCHAR(45) NULL,
  PRIMARY KEY (`user_id`)
);

CREATE TABLE `db`.`entries` (
  `entry_id` BIGINT NULL AUTO_INCREMENT,
  `entry_owner` BIGINT NULL,
  `entry_title` VARCHAR(45) NULL,
  `entry_text` VARCHAR(255) NULL,
  PRIMARY KEY (`entry_id`),
  FOREIGN KEY (`entry_owner`) REFERENCES users(`user_id`)
);

INSERT INTO `db`.`users` (user_username, user_password) VALUES ('guest', 'default');