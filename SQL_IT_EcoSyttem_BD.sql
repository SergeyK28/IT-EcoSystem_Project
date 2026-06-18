-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: sql_it_ecosyttem_bd
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appealreasons`
--

DROP TABLE IF EXISTS `appealreasons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appealreasons` (
  `ReasonID` int unsigned NOT NULL AUTO_INCREMENT,
  `ReasonName` varchar(255) NOT NULL,
  `Description` text,
  `Category` varchar(100) DEFAULT 'Общая',
  PRIMARY KEY (`ReasonID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appealreasons`
--

LOCK TABLES `appealreasons` WRITE;
/*!40000 ALTER TABLE `appealreasons` DISABLE KEYS */;
INSERT INTO `appealreasons` VALUES (1,'Не включается',NULL,'Питание'),(2,'Разбит экран',NULL,'Дисплей'),(3,'Не работает камера',NULL,'Камера'),(4,'Не заряжается',NULL,'Зарядка'),(5,'Перегревается',NULL,'Перегрев'),(6,'Медленно работает',NULL,'Производительность'),(7,'Попала вода',NULL,'Влага'),(8,'Не работает звук',NULL,'Аудио'),(9,'Проблемы с Wi-Fi',NULL,'Сеть'),(10,'Не работает кнопка',NULL,'Кнопки'),(11,'Не работает тачскрин',NULL,'Сенсор'),(12,'Села батарея',NULL,'Аккумулятор'),(13,'Проблемы с микрофоном',NULL,'Аудио'),(14,'Не видит SIM-карту',NULL,'Связь'),(15,'Не работает динамик',NULL,'Аудио'),(16,'Глючит система',NULL,'Программное'),(17,'Не работает Bluetooth',NULL,'Беспроводная связь'),(18,'Треснул корпус',NULL,'Корпус'),(19,'Не работает разъем',NULL,'Разъемы'),(20,'Другая причина',NULL,'Общая');
/*!40000 ALTER TABLE `appealreasons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `CartID` int unsigned NOT NULL AUTO_INCREMENT COMMENT 'Первичный ключ записи в корзине',
  `UserID` int unsigned NOT NULL COMMENT 'ID пользователя (ссылка на Client)',
  `DeviceType` varchar(100) NOT NULL COMMENT 'Тип устройства',
  `DeviceBrand` varchar(100) NOT NULL COMMENT 'Бренд устройства',
  `DeviceModel` varchar(100) NOT NULL COMMENT 'Модель устройства',
  `Reason` varchar(255) NOT NULL COMMENT 'Причина обращения',
  `Price` decimal(10,2) NOT NULL COMMENT 'Цена услуги',
  `DateAdded` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата добавления в корзину',
  `Status` enum('active','ordered','removed') DEFAULT 'active' COMMENT 'Статус товара в корзине',
  PRIMARY KEY (`CartID`),
  KEY `idx_user` (`UserID`),
  KEY `idx_status` (`Status`),
  KEY `idx_date` (`DateAdded`),
  CONSTRAINT `Cart_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `client` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Корзина пользователей';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (1,16,'Смартфон','Samsung','Galaxy S23+','Разбитый экран',2800.00,'2026-02-25 12:24:41','removed'),(2,16,'Планшет','Apple','iPad Pro 11','Не включается',2500.00,'2026-02-25 13:06:23','removed'),(3,16,'Планшет','Apple','iPad Pro 12.9','Разбитый экран',8000.00,'2026-02-25 13:17:42','removed'),(4,16,'Ноутбук','Apple','MacBook Pro 16','Не заряжается',2000.00,'2026-02-25 13:54:53','removed');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `client`
--

DROP TABLE IF EXISTS `client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `NumClient` int DEFAULT NULL,
  `Login` varchar(50) NOT NULL,
  `PasswordHash` char(60) NOT NULL,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL,
  `Birthdate` date DEFAULT NULL,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(100) NOT NULL,
  `AvatarPath` text,
  `RegistrationDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `LastLogin` datetime DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Login` (`Login`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `NumClient` (`NumClient`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client`
--

LOCK TABLES `client` WRITE;
/*!40000 ALTER TABLE `client` DISABLE KEYS */;
INSERT INTO `client` VALUES (1,1001,'ivanov_i','$2a$10$ExampleHash12345678901234567890','Иван','Иванов','1990-05-15','+7 (912) 345-67-89','ivanov@example.com','/avatars/ivanov.jpg','2026-02-05 19:17:15','2024-01-10 14:30:00',1),(2,1002,'petrova_a','$2a$10$ExampleHash12345678901234567890','Анна','Петрова','1985-08-22','+7 (923) 456-78-90','petrova@example.com','/avatars/petrova.jpg','2026-02-05 19:17:15','2024-01-12 10:15:00',1),(3,1003,'sidorov_d','$2a$10$ExampleHash12345678901234567890','Дмитрий','Сидоров','1992-11-03','+7 (934) 567-89-01','sidorov@example.com','/avatars/sidorov.jpg','2026-02-05 19:17:15','2024-01-09 16:45:00',1),(4,1004,'smirnova_e','$2a$10$ExampleHash12345678901234567890','Елена','Смирнова','1988-03-28','+7 (945) 678-90-12','smirnova@example.com','/avatars/smirnova.jpg','2026-02-05 19:17:15','2024-01-11 09:20:00',1),(5,1005,'kuznetsov_m','$2b$12$KTCcmz2zmd13B6PdC7vCO.sjvNgv.vCCMCghQ6UT/yvO0oT6W4Qgq','Михаил','Кузнецов','1995-07-14','+7 (956) 789-01-23','kuznetsov@example.com','/avatars/kuznetsov.jpg','2026-02-05 19:17:15','2024-01-08 11:50:00',1),(6,1006,'nikolaeva_o','$2a$10$ExampleHash12345678901234567890','Ольга','Николаева','1991-12-05','+7 (967) 890-12-34','nikolaeva@example.com',NULL,'2026-02-05 19:17:15','2024-01-05 13:25:00',1),(7,1007,'fedorov_s','$2a$10$ExampleHash12345678901234567890','Сергей','Федоров','1983-09-19','+7 (978) 901-23-45','fedorov@example.com','/avatars/fedorov.jpg','2026-02-05 19:17:15','2024-01-13 15:40:00',1),(8,1008,'pavlova_t','$2a$10$ExampleHash12345678901234567890','Татьяна','Павлова','1993-04-30','+7 (989) 012-34-56','pavlova@example.com',NULL,'2026-02-05 19:17:15','2024-01-07 18:10:00',1),(9,1009,'vasiliev_a','$2a$10$ExampleHash12345678901234567890','Алексей','Васильев','1987-06-25','+7 (990) 123-45-67','vasiliev@example.com','/avatars/vasiliev.jpg','2026-02-05 19:17:15','2024-01-14 12:05:00',1),(10,1010,'mikhailova_k','$2a$10$ExampleHash12345678901234567890','Ксения','Михайлова','1994-02-17','+7 (901) 234-56-78','mikhailova@example.com','/avatars/mikhailova.jpg','2026-02-05 19:17:15','2024-01-06 17:30:00',1),(11,NULL,'super.penis','$2b$12$BZ/x9kBB4hSuuxZyNLVfvOlTv8HNJlWktDZ5bpqP5xFV.sNag98Mu','SUPER','PENIS','1999-01-01','+79999999999','',NULL,'2026-02-11 14:22:42',NULL,1),(12,NULL,'sisi.kaki','$2b$12$A3cChBJds0/8VSL0cCfNJ.EF9DYxf1XFIrXT9jtPRqt9pUU6dHoLG','НИКИТА','ПОПАВИЧ','1990-01-01','+79999999999','sisi.kaki@gmail.com',NULL,'2026-02-11 14:36:18',NULL,1),(16,NULL,'AdminKa','$2b$12$odH.Srr3fIVk4c3LKqb8KueXp5N6htieQnfI8eZxK.KiJ.segQUgC','Админ','Админ',NULL,NULL,'admon.admon20@gmail.com','/home/sk28/Изображения/channels4_profile.jpg','2026-02-11 17:11:45',NULL,1),(17,NULL,'temp','hash','Temp','User',NULL,NULL,'temp@example.com',NULL,'2026-06-05 13:59:47',NULL,1);
/*!40000 ALTER TABLE `client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detailstock`
--

DROP TABLE IF EXISTS `detailstock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detailstock` (
  `StockID` int unsigned NOT NULL AUTO_INCREMENT,
  `DetailCode` varchar(50) NOT NULL,
  `DetailName` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Category` varchar(100) DEFAULT 'Запчасть',
  `Brand` varchar(100) DEFAULT NULL,
  `CompatibleModels` text,
  `CountInStock` int NOT NULL DEFAULT '0',
  `MinStockLevel` int DEFAULT '5',
  `Price` decimal(10,2) NOT NULL,
  `CostPrice` decimal(10,2) DEFAULT '0.00',
  `Supplier` varchar(255) DEFAULT NULL,
  `WarrantyDays` int DEFAULT '90',
  `Location` varchar(100) DEFAULT NULL,
  `LastRestockDate` date DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`StockID`),
  UNIQUE KEY `DetailCode` (`DetailCode`),
  KEY `idx_category` (`Category`),
  KEY `idx_brand` (`Brand`),
  KEY `idx_stock_level` (`CountInStock`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detailstock`
--

LOCK TABLES `detailstock` WRITE;
/*!40000 ALTER TABLE `detailstock` DISABLE KEYS */;
INSERT INTO `detailstock` VALUES (1,'SCREEN-IPH12','Экран iPhone 12','Оригинальный экран для iPhone 12','Экран','Apple',NULL,14,5,8000.00,6000.00,NULL,90,NULL,NULL,1),(2,'BATT-SAMS21','Аккумулятор Samsung S21','Аккумулятор 4000mAh','Аккумулятор','Samsung',NULL,23,10,3000.00,2200.00,NULL,90,NULL,NULL,1),(3,'CHARGER-TYPE-C','Разъем Type-C','Разъем зарядки USB Type-C','Разъем','Generic',NULL,49,20,500.00,300.00,NULL,90,NULL,NULL,1),(4,'CAMERA-XM11','Камера Xiaomi 11','Основная камера 108MP','Камера','Xiaomi',NULL,8,3,4500.00,3500.00,NULL,90,NULL,NULL,1),(5,'SPEAKER-GEN','Динамик универсальный','Динамик для смартфонов','Динамик','Generic',NULL,40,15,800.00,500.00,NULL,90,NULL,NULL,1),(6,'GLASS-PROT','Защитное стекло','3D защитное стекло','Аксессуар','Generic',NULL,100,30,300.00,150.00,NULL,90,NULL,NULL,1),(7,'BACK-COV-BLK','Задняя крышка черная','Задняя крышка для смартфона','Корпус','Generic',NULL,20,8,1200.00,800.00,NULL,90,NULL,NULL,1),(8,'BUTTON-PWR','Кнопка питания','Кнопка включения/выключения','Кнопка','Generic',NULL,60,25,200.00,100.00,NULL,90,NULL,NULL,1),(9,'MIC-GEN','Микрофон','Встроенный микрофон','Микрофон','Generic',NULL,34,12,400.00,250.00,NULL,90,NULL,NULL,1),(10,'WIFI-MODULE','Wi-Fi модуль','Модуль беспроводной связи','Модуль','Generic',NULL,18,6,1500.00,1100.00,NULL,90,NULL,NULL,1);
/*!40000 ALTER TABLE `detailstock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devicemaintenance`
--

DROP TABLE IF EXISTS `devicemaintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devicemaintenance` (
  `MaintenanceID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `DeviceType` varchar(100) NOT NULL,
  `Brand` varchar(100) NOT NULL,
  `Model` varchar(100) NOT NULL,
  `SerialNumber` varchar(100) DEFAULT NULL,
  `PurchaseDate` date DEFAULT NULL,
  `WarrantyUntil` date DEFAULT NULL,
  `LastServiceDate` date DEFAULT NULL,
  `ServiceInterval` int DEFAULT '365',
  `Notes` text,
  PRIMARY KEY (`MaintenanceID`),
  KEY `OrderID` (`OrderID`),
  KEY `idx_device` (`DeviceType`,`Brand`,`Model`),
  CONSTRAINT `DeviceMaintenance_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devicemaintenance`
--

LOCK TABLES `devicemaintenance` WRITE;
/*!40000 ALTER TABLE `devicemaintenance` DISABLE KEYS */;
INSERT INTO `devicemaintenance` VALUES (1,3,'Ноутбук','Lenovo','ThinkPad X1','SN-LEN87654321','2021-08-10',NULL,'2024-01-07',180,'Проведена чистка и замена термопасты. Рекомендовано следующее обслуживание через 6 месяцев.'),(2,2,'Смартфон','Samsung','Galaxy S21','865432109876543','2023-01-20','2024-01-20','2024-01-09',365,'Заменен разъем зарядки по гарантии. Гарантия до 20.01.2024');
/*!40000 ALTER TABLE `devicemaintenance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `listemployee`
--

DROP TABLE IF EXISTS `listemployee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `listemployee` (
  `EmployeeID` int unsigned NOT NULL AUTO_INCREMENT,
  `EmployeeNumber` int DEFAULT NULL,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL,
  `Birthdate` date DEFAULT NULL,
  `Address` text,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `PasswordHash` char(60) NOT NULL,
  `Position` varchar(100) DEFAULT 'Специалист',
  `HireDate` date DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  `LockedUntil` datetime DEFAULT NULL,
  `LoginAttempts` int DEFAULT '0',
  `LastLogin` datetime DEFAULT NULL,
  `Role` enum('admin','manager','technician','consultant') DEFAULT 'technician',
  PRIMARY KEY (`EmployeeID`),
  UNIQUE KEY `EmployeeNumber` (`EmployeeNumber`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `listemployee`
--

LOCK TABLES `listemployee` WRITE;
/*!40000 ALTER TABLE `listemployee` DISABLE KEYS */;
INSERT INTO `listemployee` VALUES (1,NULL,'Александр','Петров','1985-04-15','г. Москва, ул. Ленина, д. 10, кв. 5','+7 (999) 100-01-01','admin@itecosystem.ru','$2b$12$9pkdV/xjitXZRRDky0rH4.1dLOC6u8ONJ5bQEoEMo.GK2X.Oituo2','Администратор','2023-01-15',1,NULL,0,'2026-06-08 09:26:21','admin'),(2,NULL,'Екатерина','Смирнова','1990-08-22','г. Москва, ул. Пушкина, д. 25, кв. 12','+7 (999) 100-01-02','manager@itecosystem.ru','','Менеджер','2023-03-10',1,NULL,0,NULL,'manager'),(3,NULL,'Дмитрий','Иванов','1988-11-05','г. Москва, пр. Мира, д. 15, кв. 8','+7 (999) 100-01-03','tech1@itecosystem.ru','','Старший техник','2022-11-05',1,NULL,0,NULL,'technician'),(4,NULL,'Ольга','Кузнецова','1992-03-20','г. Москва, ул. Гагарина, д. 30, кв. 14','+7 (999) 100-01-04','tech2@itecosystem.ru','','Техник','2023-05-20',1,NULL,0,NULL,'technician'),(5,NULL,'Михаил','Соколов','1991-07-14','г. Москва, ул. Советская, д. 5, кв. 3','+7 (999) 100-01-05','consultant@itecosystem.ru','','Консультант','2023-02-28',1,NULL,0,NULL,'consultant'),(6,NULL,'Анна','Морозова',NULL,NULL,NULL,NULL,'','Техник','2023-07-15',1,NULL,0,NULL,'technician'),(7,NULL,'Сергей','Васильев',NULL,NULL,NULL,NULL,'','Менеджер','2023-04-12',1,NULL,0,NULL,'manager'),(8,NULL,'Наталья','Попова',NULL,NULL,NULL,NULL,'','Техник','2023-06-08',1,NULL,0,NULL,'technician');
/*!40000 ALTER TABLE `listemployee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `NotificationID` int unsigned NOT NULL AUTO_INCREMENT,
  `EmployeeID` int unsigned NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Message` text NOT NULL,
  `Type` varchar(50) DEFAULT 'info',
  `IsRead` tinyint(1) DEFAULT '0',
  `LinkTo` varchar(500) DEFAULT NULL,
  `LinkType` varchar(50) DEFAULT NULL,
  `LinkID` int DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`NotificationID`),
  KEY `idx_employee` (`EmployeeID`),
  KEY `idx_read` (`IsRead`),
  KEY `idx_created` (`CreatedAt`),
  CONSTRAINT `fk_notifications_employee` FOREIGN KEY (`EmployeeID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordercomments`
--

DROP TABLE IF EXISTS `ordercomments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordercomments` (
  `CommentID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `EmployeeID` int unsigned DEFAULT NULL,
  `CommentDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `CommentText` text NOT NULL,
  `IsInternal` tinyint(1) DEFAULT '0',
  `AttachmentPath` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`CommentID`),
  KEY `EmployeeID` (`EmployeeID`),
  KEY `idx_order` (`OrderID`),
  KEY `idx_date` (`CommentDate`),
  CONSTRAINT `OrderComments_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `OrderComments_ibfk_2` FOREIGN KEY (`EmployeeID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordercomments`
--

LOCK TABLES `ordercomments` WRITE;
/*!40000 ALTER TABLE `ordercomments` DISABLE KEYS */;
INSERT INTO `ordercomments` VALUES (1,1,2,'2026-02-05 19:17:15','Клиент очень волнуется по поводу срочности ремонта. Просил сделать максимально быстро.',1,NULL),(2,1,3,'2026-02-05 19:17:15','Диагностика завершена. Требуется замена дисплейного модуля. Оригинальный экран в наличии.',0,NULL),(3,1,3,'2026-02-05 19:17:15','Начата замена экрана. Работы планирую завершить к 18:00.',0,NULL),(4,2,2,'2026-02-05 19:17:15','Гарантийный случай. Проверить дату покупки и гарантийный талон.',1,NULL),(5,2,4,'2026-02-05 19:17:15','Диагностика показала повреждение разъема. Замена произведена успешно.',0,NULL),(6,2,2,'2026-02-05 19:17:15','Клиенту отправлено SMS о готовности устройства.',0,NULL),(7,3,6,'2026-02-05 19:17:15','Ноутбук сильно запылен. Провел чистку и замену термопасты. Температура снизилась на 15°C.',0,NULL),(8,4,2,'2026-02-05 19:17:15','Срочный случай! Телефон упал в воду. Клиент просит восстановить данные.',1,NULL),(9,4,3,'2026-02-05 19:17:15','Устройство частично восстановлено. Ждем поставку аудиокодека. Ориентировочная дата поставки - 16 января.',0,NULL),(10,5,7,'2026-02-05 19:17:15','Клиент пожаловался на быстрый разряд батареи. Рекомендована замена аккумулятора.',0,NULL),(11,5,4,'2026-02-05 19:17:15','Диагностика аккумулятора показала износ 85%. Начата замена.',0,NULL),(12,10,2,'2026-02-05 19:17:15','Заказ создан в системе',0,NULL),(14,10,1,'2026-02-09 11:11:03','Заказ обновлен через форму редактирования: Изменения сохранены через форму редактирования',1,NULL),(15,10,1,'2026-02-09 11:13:15','Заказ обновлен через форму редактирования: Изменения сохранены через форму редактирования',1,NULL),(16,10,1,'2026-02-09 11:51:40','Заказ обновлен через форму редактирования: Изменения сохранены через форму редактирования',1,NULL),(17,9,1,'2026-02-10 09:44:15','Заказ обновлен через форму редактирования: Изменения сохранены через форму редактирования',1,NULL),(18,9,1,'2026-02-10 09:51:35','Заказ обновлен через форму редактирования: Изменения сохранены через форму редактирования',1,NULL),(19,11,1,'2026-02-11 14:36:18','Заказ создан в системе',1,NULL),(20,12,1,'2026-02-11 15:47:12','Заказ создан в системе',1,NULL),(21,12,1,'2026-02-11 16:39:47','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(22,12,1,'2026-02-11 16:39:58','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(23,12,1,'2026-02-11 16:40:13','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(24,12,1,'2026-02-11 16:40:30','Заказ завершен',1,NULL),(25,12,1,'2026-02-11 16:40:31','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(26,11,1,'2026-02-11 16:40:58','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(27,1,1,'2026-02-16 11:55:53','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(28,4,1,'2026-02-16 11:56:16','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(29,4,1,'2026-02-16 14:58:28','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(30,4,1,'2026-02-16 14:58:42','Заказ обновлен: Изменения сохранены через форму редактирования',1,NULL),(31,13,NULL,'2026-02-25 13:50:02','Клиент планирует принести технику 2026.02.27 в 10:00:00',1,NULL),(32,14,NULL,'2026-02-25 13:55:24','Клиент планирует принести технику 2026.02.27 в 10:00:00',1,NULL);
/*!40000 ALTER TABLE `ordercomments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderdetails`
--

DROP TABLE IF EXISTS `orderdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderdetails` (
  `OrderDetailID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `StockID` int unsigned NOT NULL,
  `Quantity` int NOT NULL DEFAULT '1',
  `UnitPrice` decimal(10,2) NOT NULL,
  `TotalPrice` decimal(10,2) GENERATED ALWAYS AS ((`Quantity` * `UnitPrice`)) STORED,
  `WarrantyDays` int DEFAULT NULL,
  `Notes` text,
  PRIMARY KEY (`OrderDetailID`),
  KEY `idx_order` (`OrderID`),
  KEY `idx_detail` (`StockID`),
  CONSTRAINT `OrderDetails_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `OrderDetails_ibfk_2` FOREIGN KEY (`StockID`) REFERENCES `detailstock` (`StockID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderdetails`
--

LOCK TABLES `orderdetails` WRITE;
/*!40000 ALTER TABLE `orderdetails` DISABLE KEYS */;
INSERT INTO `orderdetails` (`OrderDetailID`, `OrderID`, `StockID`, `Quantity`, `UnitPrice`, `WarrantyDays`, `Notes`) VALUES (2,2,3,1,500.00,90,NULL),(5,5,2,1,3000.00,365,NULL);
/*!40000 ALTER TABLE `orderdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `OrderID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderNumber` varchar(20) DEFAULT NULL,
  `ClientID` int unsigned NOT NULL,
  `OrderDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `CompletionDate` datetime DEFAULT NULL,
  `Status` enum('Новая','Активная','Срочное','Ждут запчасти','В работе','Готовое','Закрыто неуспешно','Завершен','Клиент несет заказ') NOT NULL DEFAULT 'Новая' COMMENT 'Статус заказа',
  `OrderType` enum('Платный','Гарантийный') NOT NULL DEFAULT 'Платный',
  `Priority` enum('Низкий','Средний','Высокий','Критичный') DEFAULT 'Средний',
  `DeviceType` varchar(100) DEFAULT NULL,
  `DeviceBrand` varchar(100) DEFAULT NULL,
  `DeviceModel` varchar(100) DEFAULT NULL,
  `DeviceIMEI_SN` varchar(50) DEFAULT NULL,
  `DeviceAppearance` text,
  `DevicePurchaseDate` date DEFAULT NULL,
  `DeviceWarrantyUntil` date DEFAULT NULL,
  `ManagerID` int unsigned DEFAULT NULL,
  `ExecutorID` int unsigned DEFAULT NULL,
  `AppealReasonID` int unsigned DEFAULT NULL,
  `ProblemDescription` text,
  `Diagnosis` text,
  `Recommendation` text,
  `Prepayment` decimal(10,2) DEFAULT '0.00',
  `TotalAmount` decimal(10,2) DEFAULT '0.00',
  `Discount` decimal(5,2) DEFAULT '0.00',
  `FinalAmount` decimal(10,2) DEFAULT '0.00',
  `IsPaid` tinyint(1) DEFAULT '0',
  `EstimatedCompletion` datetime DEFAULT NULL,
  `Notes` text,
  PRIMARY KEY (`OrderID`),
  UNIQUE KEY `OrderNumber` (`OrderNumber`),
  KEY `AppealReasonID` (`AppealReasonID`),
  KEY `idx_status` (`Status`),
  KEY `idx_order_date` (`OrderDate`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_manager` (`ManagerID`),
  KEY `idx_executor` (`ExecutorID`),
  CONSTRAINT `Orders_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `client` (`ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Orders_ibfk_2` FOREIGN KEY (`ManagerID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Orders_ibfk_3` FOREIGN KEY (`ExecutorID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Orders_ibfk_4` FOREIGN KEY (`AppealReasonID`) REFERENCES `appealreasons` (`ReasonID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'ORD-20260205-0001',1,'2024-01-10 09:15:00',NULL,'Ждут запчасти','Платный','Высокий','Смартфон','Apple','iPhone 12','356789012345678','Небольшие потертости по краям, разбит экран','2022-03-15','2024-03-15',2,3,2,'Упал телефон, разбился экран. Не реагирует на касания в нижней части.','Требуется замена дисплейного модуля. Поврежден тачскрин.','',2000.00,10000.00,5.00,17100.00,0,'2024-01-12 18:00:00','Клиент просит сделать срочно. Использовать оригинальный экран.'),(2,'ORD-20260205-0002',3,'2024-01-05 11:45:00',NULL,'Завершен','Платный','Низкий','Ноутбук','Lenovo','ThinkPad X1','SN-LEN87654321','Потертости на крышке, клавиатура в хорошем состоянии','2021-08-10',NULL,7,6,17,'Ноутбук сильно перегревается при нагрузке. Вентилятор шумит.','Запыленность системы охлаждения. Требуется чистка и замена термопасты.',NULL,1500.00,1900.00,0.00,2400.00,0,'2024-01-07 16:00:00',NULL),(3,'ORD-20260205-0003',4,'2024-01-12 16:20:00',NULL,'Ждут запчасти','Платный','Критичный','Смартфон','Xiaomi','Redmi Note 10','865123456789012','Следы влаги под стеклом, небольшие пятна на экране','2022-11-05','2023-11-05',2,3,7,'Упал в воду. После сушки включается, но не работает динамик и микрофон.','Короткое замыкание. Повреждены аудиокодек и микрофон. Требуется замена компонентов.',NULL,3000.00,2800.00,0.00,2800.00,0,'2024-01-18 14:00:00','Ждем поставку аудиокодека. Клиент предупрежден о задержке.'),(4,'ORD-20260205-0004',5,'2024-01-09 13:10:00',NULL,'В работе','Платный','Средний','Смартфон','Apple','iPhone 11','357654321098765','Небольшие царапины на задней панели','2020-09-12',NULL,7,4,12,'Батарея быстро садится. Заряд держит 2-3 часа.','Износ аккумулятора 85%. Требуется замена.','',1000.00,3950.00,10.00,4005.00,0,'2024-01-11 18:00:00','Клиент просил установить оригинальный аккумулятор.'),(5,'ORD-20260205-0005',6,'2024-01-11 10:00:00',NULL,'Новая','Платный','Средний','Планшет','Samsung','Tab S7',NULL,NULL,NULL,NULL,2,NULL,9,'Не подключается к Wi-Fi',NULL,NULL,0.00,4700.00,0.00,7700.00,0,NULL,NULL),(6,'ORD-20260205-0006',7,'2024-01-06 15:45:00',NULL,'Активная','Платный','Низкий','Смартфон','Huawei','P40 Pro',NULL,NULL,NULL,NULL,2,6,16,'Глючит интерфейс, вылетают приложения',NULL,NULL,0.00,0.00,0.00,0.00,0,NULL,NULL),(7,'ORD-20260205-0007',8,'2024-01-13 12:30:00',NULL,'Срочное','Платный','Высокий','Смартфон','Apple','iPhone 13',NULL,NULL,NULL,NULL,7,3,1,'Не включается после обновления',NULL,NULL,0.00,0.00,0.00,0.00,0,NULL,NULL),(8,'ORD-20260205-0008',9,'2024-01-04 09:20:00',NULL,'Завершен','Платный','Средний','Ноутбук','Asus','ROG Strix',NULL,NULL,NULL,NULL,7,8,6,'Медленно работает, долго загружается',NULL,NULL,0.00,0.00,0.00,0.00,0,NULL,NULL),(9,'ORD-20260205-0009',10,'2024-01-14 17:00:00',NULL,'Новая','Гарантийный','Средний','Смартфон','Google','Pixel 7','','',NULL,NULL,2,NULL,18,'Поврежден корпус ',NULL,NULL,0.00,0.00,0.00,0.00,0,'2000-01-01 18:00:00',''),(10,'ORD-20260205-0010',6,'2026-02-05 19:17:15',NULL,'Новая','Платный','Средний','Смартфон','OnePlus','9 Pro','','GHBDTN',NULL,NULL,2,NULL,19,'Не работает камера, размытые фото',NULL,NULL,500.00,1400.00,15.00,1190.00,0,'2000-01-01 18:00:00',''),(11,'ORD-20260211-7863',12,'2026-02-11 14:36:18',NULL,'Новая','Платный','Низкий','Ноутбук','Fifo','poco','poco','poco',NULL,NULL,NULL,NULL,16,'poco','','',0.00,0.00,0.00,0.00,0,'2026-02-14 18:00:00','poco'),(12,'ORD-20260211-7864',12,'2026-02-11 15:47:12',NULL,'Завершен','Платный','Низкий','Смартфон','POCO','POCO','POCO','POCO',NULL,NULL,NULL,NULL,16,'POCO','','',0.00,3000.00,0.00,3000.00,0,'2026-02-14 18:00:00','POCO'),(13,'ORD-20260225-0001',16,'2026-02-25 13:50:02',NULL,'Клиент несет заказ','Платный','Средний','Планшет','Apple','iPad Pro 12.9',NULL,NULL,NULL,NULL,NULL,NULL,20,'Несколько услуг:\n- Планшет Apple iPad Pro 12.9: Разбитый экран\n- Смартфон Samsung Galaxy S23+: Разбитый экран\n',NULL,NULL,0.00,10800.00,0.00,10800.00,0,'2026-02-27 10:00:00','Клиент принесет технику 2026-02-27 10:00:00'),(14,'ORD-20260225-0002',16,'2026-02-25 13:55:24',NULL,'Клиент несет заказ','Платный','Средний','Ноутбук','Apple','MacBook Pro 16',NULL,NULL,NULL,NULL,NULL,NULL,4,'Не заряжается',NULL,NULL,0.00,2000.00,0.00,2000.00,0,'2026-02-27 10:00:00','Клиент принесет технику 2026-02-27 10:00:00'),(15,'SYS-GENERAL-0001',11,'2026-06-05 14:08:22',NULL,'Завершен','Платный','Низкий',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Системные операции (доходы/расходы)',NULL,NULL,0.00,0.00,0.00,0.00,0,NULL,'Служебный заказ для учета доходов и расходов, не привязанных к конкретным заказам');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderservices`
--

DROP TABLE IF EXISTS `orderservices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderservices` (
  `OrderServiceID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `ServiceTypeID` int unsigned NOT NULL,
  `EmployeeID` int unsigned DEFAULT NULL,
  `Quantity` int NOT NULL DEFAULT '1',
  `UnitPrice` decimal(10,2) NOT NULL,
  `TotalPrice` decimal(10,2) GENERATED ALWAYS AS ((`Quantity` * `UnitPrice`)) STORED,
  `StartDate` datetime DEFAULT NULL,
  `EndDate` datetime DEFAULT NULL,
  `Status` enum('Запланировано','В процессе','Выполнено','Отменено') DEFAULT 'Запланировано',
  `Notes` text,
  PRIMARY KEY (`OrderServiceID`),
  KEY `EmployeeID` (`EmployeeID`),
  KEY `idx_order` (`OrderID`),
  KEY `idx_service` (`ServiceTypeID`),
  CONSTRAINT `OrderServices_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `OrderServices_ibfk_2` FOREIGN KEY (`ServiceTypeID`) REFERENCES `servicetypes` (`ServiceTypeID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `OrderServices_ibfk_3` FOREIGN KEY (`EmployeeID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderservices`
--

LOCK TABLES `orderservices` WRITE;
/*!40000 ALTER TABLE `orderservices` DISABLE KEYS */;
INSERT INTO `orderservices` (`OrderServiceID`, `OrderID`, `ServiceTypeID`, `EmployeeID`, `Quantity`, `UnitPrice`, `StartDate`, `EndDate`, `Status`, `Notes`) VALUES (1,1,1,3,1,500.00,'2024-01-10 10:00:00','2024-01-10 10:30:00','Выполнено','Проведена диагностика'),(2,1,2,3,1,1500.00,'2024-01-10 11:00:00',NULL,'В процессе','Замена экрана'),(3,2,1,4,1,500.00,'2024-01-08 15:00:00','2024-01-08 15:30:00','Выполнено',NULL),(4,2,5,4,1,900.00,'2024-01-09 09:00:00','2024-01-09 09:40:00','Выполнено',NULL),(5,3,4,6,1,800.00,'2024-01-05 13:00:00','2024-01-05 13:30:00','Выполнено',NULL),(6,3,20,6,1,2000.00,'2024-01-05 14:00:00','2024-01-07 15:30:00','Выполнено',NULL),(7,4,1,3,1,500.00,'2024-01-12 17:00:00',NULL,'Выполнено',NULL),(8,4,10,3,1,1800.00,'2024-01-13 09:00:00',NULL,'В процессе',NULL),(9,4,12,3,1,750.00,NULL,NULL,'Запланировано',NULL),(10,5,1,4,1,500.00,'2024-01-09 14:00:00',NULL,'Выполнено',NULL),(11,5,3,4,1,1200.00,'2024-01-10 10:00:00',NULL,'В процессе',NULL);
/*!40000 ALTER TABLE `orderservices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderstatushistory`
--

DROP TABLE IF EXISTS `orderstatushistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderstatushistory` (
  `HistoryID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `OldStatus` varchar(50) DEFAULT NULL,
  `NewStatus` varchar(50) NOT NULL,
  `ChangeDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `ChangedBy` int unsigned DEFAULT NULL,
  `ChangeReason` text,
  PRIMARY KEY (`HistoryID`),
  KEY `ChangedBy` (`ChangedBy`),
  KEY `idx_order` (`OrderID`),
  KEY `idx_change_date` (`ChangeDate`),
  CONSTRAINT `OrderStatusHistory_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `OrderStatusHistory_ibfk_2` FOREIGN KEY (`ChangedBy`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderstatushistory`
--

LOCK TABLES `orderstatushistory` WRITE;
/*!40000 ALTER TABLE `orderstatushistory` DISABLE KEYS */;
INSERT INTO `orderstatushistory` VALUES (1,1,'Новая','Активная','2024-01-10 09:30:00',2,'Принят предоплата'),(2,1,'Активная','В работе','2024-01-10 10:00:00',3,'Начата диагностика'),(3,2,'Новая','Активная','2024-01-08 14:45:00',2,NULL),(4,2,'Активная','В работе','2024-01-08 15:00:00',4,NULL),(5,2,'В работе','Готовое','2024-01-09 09:45:00',4,NULL),(6,3,'Новая','В работе','2024-01-05 12:00:00',6,NULL),(7,3,'В работе','Завершен','2024-01-07 16:00:00',6,NULL),(8,4,'Новая','Срочное','2024-01-12 16:25:00',2,'Попадание воды - срочный случай'),(9,4,'Срочное','Ждут запчасти','2024-01-13 10:00:00',3,'Ожидание поставки аудиокодека'),(10,5,'Новая','В работе','2024-01-09 14:00:00',4,NULL),(11,11,NULL,'Новая','2026-02-11 14:36:18',1,'Создание нового заказа'),(12,12,NULL,'Новая','2026-02-11 15:47:12',1,'Создание нового заказа'),(13,12,'Новая','Ждут запчасти','2026-02-11 16:39:47',NULL,NULL),(14,12,'Ждут запчасти','Завершен','2026-02-11 16:40:31',NULL,NULL),(15,1,'В работе','Ждут запчасти','2026-02-16 11:55:53',2,NULL),(16,4,'В работе','Ждут запчасти','2026-02-16 11:56:16',7,NULL),(17,4,'Ждут запчасти','Новая','2026-02-16 14:58:28',7,NULL),(18,4,'Новая','В работе','2026-02-16 14:58:42',7,NULL),(19,13,NULL,'Клиент несет заказ','2026-02-25 13:50:02',NULL,'Оформление через корзину'),(20,14,NULL,'Клиент несет заказ','2026-02-25 13:55:24',NULL,'Оформление через корзину');
/*!40000 ALTER TABLE `orderstatushistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `PaymentID` int unsigned NOT NULL AUTO_INCREMENT,
  `OrderID` int unsigned NOT NULL,
  `PaymentDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentMethod` enum('Наличные','Карта','Перевод','Онлайн') DEFAULT 'Наличные',
  `PaymentType` enum('Предоплата','Оплата','Возврат') DEFAULT 'Оплата',
  `ReceiptNumber` varchar(50) DEFAULT NULL,
  `Notes` text,
  `EmployeeID` int unsigned DEFAULT NULL,
  PRIMARY KEY (`PaymentID`),
  KEY `EmployeeID` (`EmployeeID`),
  KEY `idx_order` (`OrderID`),
  KEY `idx_payment_date` (`PaymentDate`),
  CONSTRAINT `Payments_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Payments_ibfk_2` FOREIGN KEY (`EmployeeID`) REFERENCES `listemployee` (`EmployeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,'2024-01-10 09:30:00',2000.00,'Карта','Предоплата','CHK-001234',NULL,2),(2,1,'2024-01-10 16:00:00',6075.00,'Наличные','Оплата','CHK-001235',NULL,2),(3,3,'2024-01-05 12:00:00',1500.00,'Перевод','Предоплата','CHK-001236',NULL,7),(4,3,'2024-01-07 16:30:00',1300.00,'Карта','Оплата','CHK-001237',NULL,7),(5,4,'2024-01-12 16:45:00',3000.00,'Онлайн','Предоплата','CHK-001238',NULL,2),(6,5,'2024-01-09 13:30:00',1000.00,'Наличные','Предоплата','CHK-001239',NULL,7);
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicetypes`
--

DROP TABLE IF EXISTS `servicetypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicetypes` (
  `ServiceTypeID` int unsigned NOT NULL AUTO_INCREMENT,
  `ServiceDescription` varchar(255) NOT NULL,
  `BasePrice` decimal(10,2) NOT NULL,
  `Category` varchar(100) DEFAULT 'Ремонт',
  `EstimatedTime` int DEFAULT '60',
  `IsActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`ServiceTypeID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicetypes`
--

LOCK TABLES `servicetypes` WRITE;
/*!40000 ALTER TABLE `servicetypes` DISABLE KEYS */;
INSERT INTO `servicetypes` VALUES (1,'Диагностика',500.00,'Диагностика',30,1),(2,'Замена экрана',1500.00,'Ремонт',60,1),(3,'Замена аккумулятора',1200.00,'Ремонт',45,1),(4,'Чистка от пыли',800.00,'Обслуживание',30,1),(5,'Замена разъема зарядки',900.00,'Ремонт',40,1),(6,'Переустановка ОС',1000.00,'Программное',60,1),(7,'Замена динамика',700.00,'Ремонт',30,1),(8,'Ремонт материнской платы',2500.00,'Ремонт',120,1),(9,'Замена кнопки',600.00,'Ремонт',25,1),(10,'Восстановление после воды',1800.00,'Ремонт',90,1),(11,'Замена камеры',1300.00,'Ремонт',45,1),(12,'Замена микрофона',750.00,'Ремонт',35,1),(13,'Ремонт Wi-Fi модуля',1600.00,'Ремонт',75,1),(14,'Замена корпуса',1100.00,'Ремонт',50,1),(15,'Настройка ПО',400.00,'Программное',25,1),(16,'Замена тачскрина',1400.00,'Ремонт',55,1),(17,'Чистка от вирусов',600.00,'Программное',40,1),(18,'Ремонт разъема наушников',850.00,'Ремонт',35,1),(19,'Замена стекла',950.00,'Ремонт',50,1),(20,'Полная профилактика',2000.00,'Обслуживание',90,1);
/*!40000 ALTER TABLE `servicetypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usernotifications`
--

DROP TABLE IF EXISTS `usernotifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usernotifications` (
  `NotificationID` int unsigned NOT NULL AUTO_INCREMENT,
  `UserID` int unsigned NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Message` text NOT NULL,
  `Type` varchar(50) DEFAULT 'info',
  `IsRead` tinyint(1) DEFAULT '0',
  `LinkTo` varchar(500) DEFAULT NULL,
  `LinkType` varchar(50) DEFAULT NULL,
  `LinkID` int DEFAULT NULL,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`NotificationID`),
  KEY `idx_user` (`UserID`),
  CONSTRAINT `fk_usernotifications_user` FOREIGN KEY (`UserID`) REFERENCES `client` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usernotifications`
--

LOCK TABLES `usernotifications` WRITE;
/*!40000 ALTER TABLE `usernotifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `usernotifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_active_orders`
--

DROP TABLE IF EXISTS `vw_active_orders`;
/*!50001 DROP VIEW IF EXISTS `vw_active_orders`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_active_orders` AS SELECT 
 1 AS `OrderID`,
 1 AS `OrderNumber`,
 1 AS `OrderDate`,
 1 AS `CompletionDate`,
 1 AS `Status`,
 1 AS `OrderType`,
 1 AS `Priority`,
 1 AS `DeviceType`,
 1 AS `DeviceBrand`,
 1 AS `DeviceModel`,
 1 AS `ClientName`,
 1 AS `ClientPhone`,
 1 AS `ClientEmail`,
 1 AS `ManagerName`,
 1 AS `ExecutorName`,
 1 AS `AppealReason`,
 1 AS `ProblemDescription`,
 1 AS `TotalAmount`,
 1 AS `Discount`,
 1 AS `FinalAmount`,
 1 AS `IsPaid`,
 1 AS `Prepayment`,
 1 AS `PaidAmount`,
 1 AS `DebtAmount`,
 1 AS `DaysInWork`,
 1 AS `ServicesCount`,
 1 AS `PartsCount`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_financial_report`
--

DROP TABLE IF EXISTS `vw_financial_report`;
/*!50001 DROP VIEW IF EXISTS `vw_financial_report`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_financial_report` AS SELECT 
 1 AS `Month`,
 1 AS `OrdersCount`,
 1 AS `TotalRevenue`,
 1 AS `PaidRevenue`,
 1 AS `WarrantyOrders`,
 1 AS `PaidOrders`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_low_stock`
--

DROP TABLE IF EXISTS `vw_low_stock`;
/*!50001 DROP VIEW IF EXISTS `vw_low_stock`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_low_stock` AS SELECT 
 1 AS `DetailCode`,
 1 AS `DetailName`,
 1 AS `Category`,
 1 AS `Brand`,
 1 AS `CountInStock`,
 1 AS `MinStockLevel`,
 1 AS `Price`,
 1 AS `Location`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_order_statistics`
--

DROP TABLE IF EXISTS `vw_order_statistics`;
/*!50001 DROP VIEW IF EXISTS `vw_order_statistics`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_order_statistics` AS SELECT 
 1 AS `Status`,
 1 AS `OrderCount`,
 1 AS `TotalAmount`,
 1 AS `AvgDays`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_orders_detailed`
--

DROP TABLE IF EXISTS `vw_orders_detailed`;
/*!50001 DROP VIEW IF EXISTS `vw_orders_detailed`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_orders_detailed` AS SELECT 
 1 AS `OrderID`,
 1 AS `OrderNumber`,
 1 AS `OrderDate`,
 1 AS `CompletionDate`,
 1 AS `Status`,
 1 AS `OrderType`,
 1 AS `Priority`,
 1 AS `DeviceType`,
 1 AS `DeviceBrand`,
 1 AS `DeviceModel`,
 1 AS `ClientName`,
 1 AS `ClientPhone`,
 1 AS `ClientEmail`,
 1 AS `ManagerName`,
 1 AS `ExecutorName`,
 1 AS `AppealReason`,
 1 AS `ProblemDescription`,
 1 AS `TotalAmount`,
 1 AS `Discount`,
 1 AS `FinalAmount`,
 1 AS `IsPaid`,
 1 AS `Prepayment`,
 1 AS `PaidAmount`,
 1 AS `DebtAmount`,
 1 AS `DaysInWork`,
 1 AS `ServicesCount`,
 1 AS `PartsCount`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_active_orders`
--

/*!50001 DROP VIEW IF EXISTS `vw_active_orders`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_active_orders` AS select `vw_orders_detailed`.`OrderID` AS `OrderID`,`vw_orders_detailed`.`OrderNumber` AS `OrderNumber`,`vw_orders_detailed`.`OrderDate` AS `OrderDate`,`vw_orders_detailed`.`CompletionDate` AS `CompletionDate`,`vw_orders_detailed`.`Status` AS `Status`,`vw_orders_detailed`.`OrderType` AS `OrderType`,`vw_orders_detailed`.`Priority` AS `Priority`,`vw_orders_detailed`.`DeviceType` AS `DeviceType`,`vw_orders_detailed`.`DeviceBrand` AS `DeviceBrand`,`vw_orders_detailed`.`DeviceModel` AS `DeviceModel`,`vw_orders_detailed`.`ClientName` AS `ClientName`,`vw_orders_detailed`.`ClientPhone` AS `ClientPhone`,`vw_orders_detailed`.`ClientEmail` AS `ClientEmail`,`vw_orders_detailed`.`ManagerName` AS `ManagerName`,`vw_orders_detailed`.`ExecutorName` AS `ExecutorName`,`vw_orders_detailed`.`AppealReason` AS `AppealReason`,`vw_orders_detailed`.`ProblemDescription` AS `ProblemDescription`,`vw_orders_detailed`.`TotalAmount` AS `TotalAmount`,`vw_orders_detailed`.`Discount` AS `Discount`,`vw_orders_detailed`.`FinalAmount` AS `FinalAmount`,`vw_orders_detailed`.`IsPaid` AS `IsPaid`,`vw_orders_detailed`.`Prepayment` AS `Prepayment`,`vw_orders_detailed`.`PaidAmount` AS `PaidAmount`,`vw_orders_detailed`.`DebtAmount` AS `DebtAmount`,`vw_orders_detailed`.`DaysInWork` AS `DaysInWork`,`vw_orders_detailed`.`ServicesCount` AS `ServicesCount`,`vw_orders_detailed`.`PartsCount` AS `PartsCount` from `vw_orders_detailed` where (`vw_orders_detailed`.`Status` in ('Новая','Активная','Срочное','Ждут запчасти','В работе')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_financial_report`
--

/*!50001 DROP VIEW IF EXISTS `vw_financial_report`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_financial_report` AS select date_format(`orders`.`OrderDate`,'%Y-%m') AS `Month`,count(0) AS `OrdersCount`,sum(`orders`.`FinalAmount`) AS `TotalRevenue`,sum((case when (`orders`.`IsPaid` = true) then `orders`.`FinalAmount` else 0 end)) AS `PaidRevenue`,sum((case when (`orders`.`OrderType` = 'Гарантийный') then 1 else 0 end)) AS `WarrantyOrders`,sum((case when (`orders`.`OrderType` = 'Платный') then 1 else 0 end)) AS `PaidOrders` from `orders` group by date_format(`orders`.`OrderDate`,'%Y-%m') order by `Month` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_low_stock`
--

/*!50001 DROP VIEW IF EXISTS `vw_low_stock`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_low_stock` AS select `detailstock`.`DetailCode` AS `DetailCode`,`detailstock`.`DetailName` AS `DetailName`,`detailstock`.`Category` AS `Category`,`detailstock`.`Brand` AS `Brand`,`detailstock`.`CountInStock` AS `CountInStock`,`detailstock`.`MinStockLevel` AS `MinStockLevel`,`detailstock`.`Price` AS `Price`,`detailstock`.`Location` AS `Location` from `detailstock` where ((`detailstock`.`CountInStock` <= `detailstock`.`MinStockLevel`) and (`detailstock`.`IsActive` = true)) order by `detailstock`.`CountInStock` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_order_statistics`
--

/*!50001 DROP VIEW IF EXISTS `vw_order_statistics`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_order_statistics` AS select `orders`.`Status` AS `Status`,count(0) AS `OrderCount`,sum(`orders`.`FinalAmount`) AS `TotalAmount`,avg(timestampdiff(DAY,`orders`.`OrderDate`,coalesce(`orders`.`CompletionDate`,now()))) AS `AvgDays` from `orders` group by `orders`.`Status` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_orders_detailed`
--

/*!50001 DROP VIEW IF EXISTS `vw_orders_detailed`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_orders_detailed` AS select `o`.`OrderID` AS `OrderID`,`o`.`OrderNumber` AS `OrderNumber`,`o`.`OrderDate` AS `OrderDate`,`o`.`CompletionDate` AS `CompletionDate`,`o`.`Status` AS `Status`,`o`.`OrderType` AS `OrderType`,`o`.`Priority` AS `Priority`,`o`.`DeviceType` AS `DeviceType`,`o`.`DeviceBrand` AS `DeviceBrand`,`o`.`DeviceModel` AS `DeviceModel`,concat(`c`.`FirstName`,' ',`c`.`LastName`) AS `ClientName`,`c`.`PhoneNumber` AS `ClientPhone`,`c`.`Email` AS `ClientEmail`,concat(`m`.`FirstName`,' ',`m`.`LastName`) AS `ManagerName`,concat(`e`.`FirstName`,' ',`e`.`LastName`) AS `ExecutorName`,`ar`.`ReasonName` AS `AppealReason`,`o`.`ProblemDescription` AS `ProblemDescription`,`o`.`TotalAmount` AS `TotalAmount`,`o`.`Discount` AS `Discount`,`o`.`FinalAmount` AS `FinalAmount`,`o`.`IsPaid` AS `IsPaid`,`o`.`Prepayment` AS `Prepayment`,(select sum(`payments`.`Amount`) from `payments` where (`payments`.`OrderID` = `o`.`OrderID`)) AS `PaidAmount`,(`o`.`FinalAmount` - coalesce((select sum(`payments`.`Amount`) from `payments` where (`payments`.`OrderID` = `o`.`OrderID`)),0)) AS `DebtAmount`,timestampdiff(DAY,`o`.`OrderDate`,coalesce(`o`.`CompletionDate`,now())) AS `DaysInWork`,(select count(0) from `orderservices` where (`orderservices`.`OrderID` = `o`.`OrderID`)) AS `ServicesCount`,(select count(0) from `orderdetails` where (`orderdetails`.`OrderID` = `o`.`OrderID`)) AS `PartsCount` from ((((`orders` `o` left join `client` `c` on((`o`.`ClientID` = `c`.`ID`))) left join `listemployee` `m` on((`o`.`ManagerID` = `m`.`EmployeeID`))) left join `listemployee` `e` on((`o`.`ExecutorID` = `e`.`EmployeeID`))) left join `appealreasons` `ar` on((`o`.`AppealReasonID` = `ar`.`ReasonID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-10 10:26:47
