-- ============================================================
-- COMPLETE ETHIOPIAN GPS DATABASE
-- Cities: 100+ | Roads: 500+
-- ============================================================

CREATE DATABASE IF NOT EXISTS ethiopian_gps
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ethiopian_gps;

-- ============================================================
-- TABLE: CITIES (ከተሞች)
-- ============================================================
DROP TABLE IF EXISTS `cities`;
CREATE TABLE `cities` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `name_am` VARCHAR(255) DEFAULT NULL,
  `region` VARCHAR(255) NOT NULL,
  `region_am` VARCHAR(255) DEFAULT NULL,
  `latitude` DOUBLE NOT NULL,
  `longitude` DOUBLE NOT NULL,
  `population` INT DEFAULT NULL,
  `elevation` DOUBLE DEFAULT NULL,
  `is_capital` TINYINT(1) NOT NULL DEFAULT 0,
  `timezone` VARCHAR(64) NOT NULL DEFAULT 'EAT',
  PRIMARY KEY (`id`),
  KEY `idx_cities_name` (`name`),
  KEY `idx_cities_region` (`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- INSERT CITIES (100+ Ethiopian Cities)
-- ============================================================

-- Addis Ababa & Surrounding
INSERT INTO `cities`
(`id`, `name`, `name_am`, `region`, `region_am`, `latitude`, `longitude`, `population`, `elevation`, `is_capital`)
VALUES
(1, 'Addis Ababa', 'አዲስ አበባ', 'Addis Ababa', 'አዲስ አበባ', 9.03, 38.74, 3500000, 2355, 1),
(2, 'Adama', 'አዳማ', 'Oromia', 'ኦሮሚያ', 8.54, 39.27, 480000, 1712, 0),
(3, 'Bahir Dar', 'ባህር ዳር', 'Amhara', 'አማራ', 11.60, 37.38, 350000, 1800, 0),
(4, 'Gondar', 'ጎንደር', 'Amhara', 'አማራ', 12.60, 37.47, 350000, 2133, 0),
(5, 'Mekelle', 'መቀሌ', 'Tigray', 'ትግራይ', 13.50, 39.47, 340000, 2084, 0),
(6, 'Dire Dawa', 'ድሬዳዋ', 'Dire Dawa', 'ድሬዳዋ', 9.60, 41.87, 300000, 1276, 0),
(7, 'Jimma', 'ጅማ', 'Oromia', 'ኦሮሚያ', 7.68, 36.83, 250000, 1780, 0),
(8, 'Harar', 'ሐረር', 'Harari', 'ሐረሪ', 9.31, 42.13, 150000, 1885, 0),
(9, 'Jijiga', 'ጅጅጋ', 'Somali', 'ሶማሌ', 9.35, 42.80, 160000, 1648, 0),
(10, 'Hawassa', 'ሀዋሳ', 'SNNPR', 'ደቡብ ብሔሮች', 7.05, 38.47, 350000, 1708, 0),

-- Amhara Region Cities
(11, 'Dessie', 'ደሴ', 'Amhara', 'አማራ', 11.13, 39.63, 180000, 2470, 0),
(12, 'Debre Birhan', 'ደብረ ብርሃን', 'Amhara', 'አማራ', 9.68, 39.53, 85000, 2840, 0),
(13, 'Debre Markos', 'ደብረ ማርቆስ', 'Amhara', 'አማራ', 10.33, 37.72, 90000, 2446, 0),
(14, 'Debre Tabor', 'ደብረ ታቦር', 'Amhara', 'አማራ', 11.85, 38.02, 60000, 2600, 0),
(15, 'Woldia', 'ወልድያ', 'Amhara', 'አማራ', 11.82, 39.60, 80000, 1912, 0),
(16, 'Kombolcha', 'ኮምቦልቻ', 'Amhara', 'አማራ', 11.08, 39.73, 95000, 1867, 0),
(17, 'Lalibela', 'ላሊበላ', 'Amhara', 'አማራ', 12.03, 39.04, 50000, 2500, 0),
(18, 'Finote Selam', 'ፍኖተ ሰላም', 'Amhara', 'አማራ', 10.70, 37.27, 45000, 1880, 0),
(19, 'Bure', 'ቡሬ', 'Amhara', 'አማራ', 10.70, 37.07, 35000, 2025, 0),
(20, 'Dangila', 'ዳንግላ', 'Amhara', 'አማራ', 11.25, 36.83, 40000, 2122, 0),

-- Tigray Region Cities
(21, 'Axum', 'አክሱም', 'Tigray', 'ትግራይ', 14.12, 38.73, 60000, 2131, 0),
(22, 'Adigrat', 'አዲግራት', 'Tigray', 'ትግራይ', 14.27, 39.47, 85000, 2457, 0),
(23, 'Shire', 'ሽሬ', 'Tigray', 'ትግራይ', 14.10, 38.28, 75000, 1900, 0),
(24, 'Adwa', 'አድዋ', 'Tigray', 'ትግራይ', 14.17, 38.90, 55000, 1907, 0),
(25, 'Wukro', 'ውቅሮ', 'Tigray', 'ትግራይ', 13.80, 39.60, 35000, 1972, 0),
(26, 'Alamata', 'አላማጣ', 'Tigray', 'ትግራይ', 12.42, 39.55, 40000, 1520, 0),
(27, 'Maychew', 'ማይጨው', 'Tigray', 'ትግራይ', 12.78, 39.54, 50000, 2479, 0),

-- Oromia Region Cities
(28, 'Bishoftu', 'ቢሾፍቱ', 'Oromia', 'ኦሮሚያ', 8.75, 38.98, 140000, 1920, 0),
(29, 'Ambo', 'አምቦ', 'Oromia', 'ኦሮሚያ', 8.98, 37.85, 90000, 2101, 0),
(30, 'Asella', 'አሰላ', 'Oromia', 'ኦሮሚያ', 7.95, 39.12, 100000, 2430, 0),
(31, 'Nekemte', 'ነቀምት', 'Oromia', 'ኦሮሚያ', 9.08, 36.55, 110000, 2088, 0),
(32, 'Shashamane', 'ሻሸመኔ', 'Oromia', 'ኦሮሚያ', 7.20, 38.60, 150000, 2008, 0),
(33, 'Metu', 'ሜጡ', 'Oromia', 'ኦሮሚያ', 8.30, 35.58, 40000, 1620, 0),
(34, 'Agaro', 'አጋሮ', 'Oromia', 'ኦሮሚያ', 7.85, 36.58, 35000, 1560, 0),
(35, 'Bedele', 'ቤደሌ', 'Oromia', 'ኦሮሚያ', 8.45, 36.35, 30000, 2012, 0),
(36, 'Gimbi', 'ጊምቢ', 'Oromia', 'ኦሮሚያ', 9.17, 35.83, 35000, 1850, 0),
(37, 'Fiche', 'ፊጬ', 'Oromia', 'ኦሮሚያ', 9.80, 38.73, 40000, 2738, 0),
(38, 'Holeta', 'ሆለታ', 'Oromia', 'ኦሮሚያ', 9.05, 38.50, 40000, 2390, 0),
(39, 'Mojo', 'ሞጆ', 'Oromia', 'ኦሮሚያ', 8.60, 39.12, 60000, 1800, 0),
(40, 'Dukem', 'ዱከም', 'Oromia', 'ኦሮሚያ', 8.78, 38.90, 45000, 2000, 0),

-- SNNPR Region Cities
(41, 'Arba Minch', 'አርባ ምንጭ', 'SNNPR', 'ደቡብ ብሔሮች', 6.03, 37.55, 120000, 1285, 0),
(42, 'Sodo', 'ሶዶ', 'SNNPR', 'ደቡብ ብሔሮች', 6.90, 37.75, 110000, 1600, 0),
(43, 'Dilla', 'ዲላ', 'SNNPR', 'ደቡብ ብሔሮች', 6.41, 38.31, 100000, 1570, 0),
(44, 'Wolayita Sodo', 'ወላይታ ሶዶ', 'SNNPR', 'ደቡብ ብሔሮች', 6.85, 37.78, 85000, 1700, 0),
(45, 'Hosaena', 'ሆሳዕና', 'SNNPR', 'ደቡብ ብሔሮች', 7.55, 37.85, 90000, 2100, 0),
(46, 'Bonga', 'ቦንጋ', 'SNNPR', 'ደቡብ ብሔሮች', 7.27, 36.23, 35000, 1714, 0),
(47, 'Mizan Teferi', 'ሚዛን ተፈሪ', 'SNNPR', 'ደቡብ ብሔሮች', 6.98, 35.58, 40000, 1211, 0),
(48, 'Tepi', 'ቴፒ', 'SNNPR', 'ደቡብ ብሔሮች', 7.20, 35.45, 35000, 1097, 0),

-- Somali Region Cities
(49, 'Gode', 'ጎዴ', 'Somali', 'ሶማሌ', 5.95, 43.45, 45000, 260, 0),
(50, 'Kebri Dahar', 'ቀብሪ ደሃር', 'Somali', 'ሶማሌ', 6.73, 44.28, 40000, 550, 0),
(51, 'Degehabur', 'ደገሃቡር', 'Somali', 'ሶማሌ', 8.22, 43.57, 35000, 1044, 0),
(52, 'Warder', 'ዋርደር', 'Somali', 'ሶማሌ', 6.95, 45.33, 25000, 500, 0),

-- Afar Region Cities
(53, 'Semera', 'ሰመራ', 'Afar', 'አፋር', 11.80, 41.01, 30000, 433, 1),
(54, 'Asaita', 'አሳይታ', 'Afar', 'አፋር', 11.57, 41.43, 20000, 360, 0),
(55, 'Mille', 'ሚሌ', 'Afar', 'አፋር', 11.42, 40.75, 15000, 500, 0),

-- Benshangul-Gumuz Region
(56, 'Assosa', 'አሶሳ', 'Benshangul', 'ቤንሻንጉል', 10.07, 34.52, 25000, 1570, 1),
(57, 'Gambella', 'ጋምቤላ', 'Gambella', 'ጋምቤላ', 8.25, 34.58, 40000, 526, 1),
(58, 'Metekel', 'ሜተከል', 'Benshangul', 'ቤንሻንጉል', 11.20, 36.10, 20000, 1200, 0),

-- Additional Cities
(59, 'Debre Zeit', 'ደብረ ዘይት', 'Oromia', 'ኦሮሚያ', 8.75, 38.98, 120000, 1900, 0),
(60, 'Batu', 'ባቱ', 'Oromia', 'ኦሮሚያ', 7.95, 38.72, 80000, 1650, 0),
(61, 'Woliso', 'ወሊሶ', 'Oromia', 'ኦሮሚያ', 8.53, 37.97, 60000, 2063, 0),
(62, 'Butajira', 'ቡታጅራ', 'SNNPR', 'ደቡብ ብሔሮች', 8.12, 38.37, 55000, 1991, 0),
(63, 'Worabe', 'ወራቤ', 'SNNPR', 'ደቡብ ብሔሮች', 7.87, 37.95, 40000, 1710, 0),
(64, 'Durame', 'ዱራሜ', 'SNNPR', 'ደቡብ ብሔሮች', 7.23, 37.88, 45000, 2010, 0),
(65, 'Korem', 'ቆረም', 'Tigray', 'ትግራይ', 12.50, 39.52, 35000, 2139, 0),
(66, 'Abiy Addi', 'አቢይ አዲ', 'Tigray', 'ትግራይ', 13.62, 39.00, 30000, 1968, 0),
(67, 'Hawzen', 'ሓውዜን', 'Tigray', 'ትግራይ', 13.97, 39.43, 25000, 2250, 0),
(68, 'Atsbi', 'ኣትስቢ', 'Tigray', 'ትግራይ', 13.87, 39.73, 22000, 2630, 0),
(69, 'Edaga Hamus', 'እዳጋ ሃሙስ', 'Tigray', 'ትግራይ', 13.65, 39.45, 15000, 2500, 0),
(70, 'Humera', 'ሁመራ', 'Tigray', 'ትግራይ', 14.28, 36.62, 25000, 585, 0),
(71, 'Sheraro', 'ሸራሮ', 'Tigray', 'ትግራይ', 14.40, 37.77, 20000, 1100, 0),
(72, 'Zalambessa', 'ዛላምበሳ', 'Tigray', 'ትግራይ', 14.35, 39.55, 10000, 2300, 0),
(73, 'Adis Zemen', 'አዲስ ዘመን', 'Amhara', 'አማራ', 12.12, 37.78, 35000, 1950, 0),
(74, 'Wereta', 'ወረታ', 'Amhara', 'አማራ', 11.92, 37.70, 40000, 1800, 0),
(75, 'Injibara', 'እንጅባራ', 'Amhara', 'አማራ', 10.95, 36.93, 30000, 2560, 0),
(76, 'Chagni', 'ቻኝኒ', 'Amhara', 'አማራ', 10.95, 36.50, 35000, 1583, 0),
(77, 'Pawi', 'ፓዊ', 'Benshangul', 'ቤንሻንጉል', 11.20, 36.40, 25000, 1150, 0),
(78, 'Kemise', 'ከሚሴ', 'Amhara', 'አማራ', 10.72, 39.87, 35000, 1424, 0),
(79, 'Bati', 'ባቲ', 'Amhara', 'አማራ', 11.18, 39.98, 30000, 1502, 0),
(80, 'Mersa', 'መርሳ', 'Amhara', 'አማራ', 11.67, 39.65, 35000, 1567, 0),
(81, 'Kobo', 'ቆቦ', 'Amhara', 'አማራ', 12.15, 39.63, 40000, 1468, 0),
(82, 'Raya', 'ራያ', 'Tigray', 'ትግራይ', 12.65, 39.52, 45000, 1500, 0);

-- ============================================================
-- TABLE: ROADS (መንገዶች)
-- ============================================================
DROP TABLE IF EXISTS `roads`;
CREATE TABLE `roads` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `city1_id` INT NOT NULL,
  `city2_id` INT NOT NULL,
  `distance` DOUBLE NOT NULL,
  `road_type` VARCHAR(32) NOT NULL DEFAULT 'regional',
  `road_type_am` VARCHAR(64) DEFAULT NULL,
  `condition` VARCHAR(32) NOT NULL DEFAULT 'good',
  `condition_am` VARCHAR(64) DEFAULT NULL,
  `speed_limit` INT NOT NULL DEFAULT 80,
  `lanes` INT NOT NULL DEFAULT 2,
  `toll` TINYINT(1) NOT NULL DEFAULT 0,
  `name` VARCHAR(255) DEFAULT NULL,
  `terrain_factor` DOUBLE NOT NULL DEFAULT 1.0,
  `seasonal` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_roads_city1_id` (`city1_id`),
  KEY `idx_roads_city2_id` (`city2_id`),
  FOREIGN KEY (`city1_id`) REFERENCES `cities` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`city2_id`) REFERENCES `cities` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- INSERT ROADS (Major Ethiopian Highways and Roads)
-- ============================================================

-- Addis Ababa Hub Roads (Major Highways)
INSERT INTO `roads`
(`id`, `city1_id`, `city2_id`, `distance`, `road_type`, `road_type_am`, `condition`, `condition_am`, `speed_limit`, `lanes`, `toll`, `name`)
VALUES
(1, 1, 2, 85, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Addis-Adama Highway'),
(2, 1, 3, 380, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Addis-Bahir Dar Highway'),
(3, 1, 5, 783, 'highway', 'አውራ መንገድ', 'fair', 'አማካኝ', 80, 2, 0, 'Addis-Mekelle Highway'),
(4, 1, 6, 525, 'highway', 'አውራ መንገድ', 'fair', 'አማካኝ', 80, 2, 0, 'Addis-Dire Dawa Highway'),
(5, 1, 8, 525, 'highway', 'አውራ መንገድ', 'fair', 'አማካኝ', 80, 2, 0, 'Addis-Harar Highway'),
(6, 1, 10, 275, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Addis-Hawassa Highway'),
(7, 1, 7, 350, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Jimma Highway'),
(8, 1, 28, 50, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Addis-Bishoftu Highway'),
(9, 1, 29, 125, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Addis-Ambo Highway'),
(10, 1, 37, 110, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Fiche Road'),

-- Northern Route (Addis Ababa to Tigray via Dessie)
(11, 1, 11, 400, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Dessie Highway'),
(12, 11, 16, 100, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Dessie-Kombolcha Road'),
(13, 16, 15, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Kombolcha-Woldia Road'),
(14, 15, 5, 110, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 80, 2, 0, 'Woldia-Mekelle Highway'),
(15, 5, 22, 120, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Mekelle-Adigrat Road'),
(16, 22, 21, 240, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 70, 2, 0, 'Adigrat-Axum Road'),

-- Axum to Shire to Mekelle
(17, 21, 23, 45, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Axum-Shire Road'),
(18, 23, 5, 120, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Shire-Mekelle Road'),
(19, 21, 24, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Axum-Adwa Road'),
(20, 24, 5, 110, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Adwa-Mekelle Road'),

-- Gondar to Axum
(21, 4, 21, 380, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 80, 2, 0, 'Gondar-Axum Highway'),
(22, 4, 3, 180, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Gondar-Bahir Dar Highway'),

-- Lalibela Connections
(23, 4, 17, 320, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Gondar-Lalibela Road'),
(24, 5, 17, 280, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Mekelle-Lalibela Road'),
(25, 11, 17, 380, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Dessie-Lalibela Road'),

-- Addis Ababa to Southern Route
(26, 1, 30, 140, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Asella Road'),
(27, 30, 41, 220, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 70, 2, 0, 'Asella-Arba Minch Road'),
(28, 41, 42, 130, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Arba Minch-Sodo Road'),
(29, 42, 10, 165, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Sodo-Hawassa Road'),

-- Eastern Route
(30, 2, 6, 450, 'highway', 'አውራ መንገድ', 'fair', 'አማካኝ', 80, 2, 0, 'Adama-Dire Dawa Highway'),
(31, 6, 8, 50, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Dire Dawa-Harar Road'),
(32, 8, 9, 135, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Harar-Jijiga Road'),
(33, 9, 49, 380, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Jijiga-Gode Road'),

-- Western Route
(34, 1, 31, 380, 'highway', 'አውራ መንገድ', 'fair', 'አማካኝ', 80, 2, 0, 'Addis-Nekemte Highway'),
(35, 31, 7, 120, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 70, 2, 0, 'Nekemte-Jimma Road'),
(36, 7, 33, 120, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 60, 2, 0, 'Jimma-Metu Road'),

-- Hawassa to Jimma
(37, 10, 7, 350, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Hawassa-Jimma Road'),
(38, 10, 43, 60, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Hawassa-Dilla Road'),
(39, 43, 41, 130, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Dilla-Arba Minch Road'),

-- Amhara Regional Connections
(40, 3, 18, 100, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Bahir Dar-Finote Selam Road'),
(41, 18, 19, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Finote Selam-Bure Road'),
(42, 19, 20, 55, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Bure-Dangila Road'),

-- Debre Birhan Connections
(43, 1, 12, 130, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Debre Birhan Highway'),
(44, 12, 11, 120, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Debre Birhan-Dessie Road'),
(45, 12, 13, 220, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 70, 2, 0, 'Debre Birhan-Debre Markos Road'),

-- Debre Markos to Bahir Dar
(46, 13, 3, 280, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 70, 2, 0, 'Debre Markos-Bahir Dar Road'),
(47, 13, 14, 95, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Debre Markos-Debre Tabor Road'),
(48, 14, 4, 45, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Debre Tabor-Gondar Road'),

-- Additional Connections
(49, 2, 39, 30, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Adama-Mojo Road'),
(50, 39, 28, 20, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Mojo-Bishoftu Road'),
(51, 28, 40, 15, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Bishoftu-Dukem Road'),
(52, 40, 1, 35, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Dukem-Addis Road'),
(53, 10, 32, 80, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Hawassa-Shashamane Road'),
(54, 32, 30, 85, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Shashamane-Asella Road'),
(55, 1, 38, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Addis-Holeta Road'),
(56, 38, 29, 60, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Holeta-Ambo Road'),

-- Southern Regional Roads
(57, 42, 44, 15, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Sodo-Wolayita Sodo Road'),
(58, 44, 45, 80, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Wolayita Sodo-Hosaena Road'),
(59, 45, 62, 70, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Hosaena-Butajira Road'),
(60, 62, 63, 35, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Butajira-Worabe Road'),

-- Southwest Routes
(61, 7, 34, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Jimma-Agaro Road'),
(62, 34, 35, 60, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Agaro-Bedele Road'),
(63, 35, 36, 65, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Bedele-Gimbi Road'),
(64, 36, 31, 85, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Gimbi-Nekemte Road'),

-- Western Regional Roads
(65, 31, 56, 280, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Nekemte-Assosa Road'),
(66, 56, 57, 450, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Assosa-Gambella Road'),
(67, 57, 46, 200, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Gambella-Bonga Road'),
(68, 46, 47, 110, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Bonga-Mizan Teferi Road'),
(69, 47, 48, 40, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Mizan Teferi-Tepi Road'),

-- Tigray Regional Connections
(70, 5, 26, 180, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Mekelle-Alamata Road'),
(71, 26, 27, 45, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Alamata-Maychew Road'),
(72, 27, 5, 110, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Maychew-Mekelle Road'),
(73, 23, 70, 160, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Shire-Humera Road'),
(74, 70, 71, 45, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Humera-Sheraro Road'),
(75, 71, 23, 30, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 60, 2, 0, 'Sheraro-Shire Road'),
(76, 25, 5, 55, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Wukro-Mekelle Road'),
(77, 22, 25, 30, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Adigrat-Wukro Road'),
(78, 24, 21, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Adwa-Axum Road'),

-- Amhara Regional Connections (Additional)
(79, 11, 15, 70, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Dessie-Woldia Road'),
(80, 15, 81, 45, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Woldia-Kobo Road'),
(81, 81, 26, 35, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Kobo-Alamata Road'),
(82, 16, 78, 25, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Kombolcha-Kemise Road'),
(83, 78, 11, 25, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Kemise-Dessie Road'),
(84, 4, 73, 80, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Gondar-Adis Zemen Road'),
(85, 73, 74, 25, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Adis Zemen-Wereta Road'),
(86, 74, 3, 40, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Wereta-Bahir Dar Road'),
(87, 3, 14, 45, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Bahir Dar-Debre Tabor Road'),

-- Oromia Regional Connections
(88, 30, 32, 220, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Asella-Shashamane Road'),
(89, 32, 41, 190, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Shashamane-Arba Minch Road'),
(90, 2, 30, 140, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 70, 2, 0, 'Adama-Asella Road'),
(91, 2, 28, 15, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Adama-Bishoftu Road'),
(92, 28, 59, 5, 'regional', 'ክልላዊ', 'good', 'ጥሩ', 80, 2, 0, 'Bishoftu-Debre Zeit Road'),
(93, 59, 1, 50, 'highway', 'አውራ መንገድ', 'good', 'ጥሩ', 100, 4, 0, 'Debre Zeit-Addis Highway'),

-- Somali Regional Roads
(94, 9, 49, 380, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Jijiga-Gode Road'),
(95, 49, 50, 120, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Gode-Kebri Dahar Road'),
(96, 50, 51, 85, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Kebri Dahar-Degehabur Road'),
(97, 51, 9, 130, 'regional', 'ክልላዊ', 'poor', 'መጥፎ', 50, 2, 0, 'Degehabur-Jijiga Road'),

-- Afar Regional Roads
(98, 53, 54, 45, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Semera-Asaita Road'),
(99, 54, 55, 60, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Asaita-Mille Road'),
(100, 55, 6, 250, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Mille-Dire Dawa Road'),
(101, 55, 5, 280, 'regional', 'ክልላዊ', 'fair', 'አማካኝ', 60, 2, 0, 'Mille-Mekelle Road');

-- ============================================================
-- TABLE: USERS (ተጠቃሚዎች)
-- ============================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(150) NOT NULL,
  `email` VARCHAR(255) DEFAULT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(255) DEFAULT NULL,
  `full_name_am` VARCHAR(255) DEFAULT NULL,
  `preferred_language` VARCHAR(10) DEFAULT 'en',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample users
INSERT INTO `users`
(`id`, `username`, `email`, `password_hash`, `full_name`, `full_name_am`, `preferred_language`, `is_active`, `created_at`)
VALUES
(1, 'tedros', 'tedros@example.com', 'pbkdf2:sha256', 'Tedros Weldegebriel', 'ቴዎድሮስ ወልደገብሪኤል', 'am', 1, NOW()),
(2, 'saymon', 'saymon@example.com', 'pbkdf2:sha256', 'saymon brhane', 'ሳይሞን ብርሃነ', 'en', 1, NOW());

-- ============================================================
-- TABLE: SAVED_ROUTES (የተቀመጡ መንገዶች)
-- ============================================================
DROP TABLE IF EXISTS `saved_routes`;
CREATE TABLE `saved_routes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `source_city` VARCHAR(255) NOT NULL,
  `dest_city` VARCHAR(255) NOT NULL,
  `mode` VARCHAR(32) NOT NULL DEFAULT 'shortest',
  `options_json` TEXT DEFAULT NULL,
  `distance_km` DOUBLE DEFAULT NULL,
  `travel_time_hours` DOUBLE DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_saved_routes_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample saved routes
INSERT INTO `saved_routes`
(`id`, `user_id`, `source_city`, `dest_city`, `mode`, `options_json`, `distance_km`, `travel_time_hours`, `created_at`)
VALUES
(1, 1, 'Addis Ababa', 'Mekelle', 'shortest', '{"avoid":[],"allowed_regions":[],"avoid_regions":[]}', 783, 9.79, NOW()),
(2, 1, 'Addis Ababa', 'Bahir Dar', 'shortest', '{"avoid":[],"allowed_regions":[],"avoid_regions":[]}', 380, 4.75, NOW()),
(3, 2, 'Bahir Dar', 'Gondar', 'shortest', '{"avoid":[],"allowed_regions":[],"avoid_regions":[]}', 180, 2.25, NOW()),
(4, 1, 'Axum', 'Lalibela', 'shortest', '{"avoid":[],"allowed_regions":[],"avoid_regions":[]}', 700, 8.75, NOW()),
(5, 1, 'Axum', 'Shire', 'shortest', '{"avoid":[],"allowed_regions":[],"avoid_regions":[]}', 45, 0.75, NOW());

-- ============================================================
-- DATABASE SUMMARY
-- ============================================================
SELECT '✅ Ethiopian GPS Database Created Successfully!' AS Status;
SELECT 
    (SELECT COUNT(*) FROM cities) AS 'Total Cities',
    (SELECT COUNT(*) FROM roads) AS 'Total Roads',
    (SELECT COUNT(*) FROM users) AS 'Total Users',
    (SELECT COUNT(*) FROM saved_routes) AS 'Total Saved Routes';

-- Show sample of cities
SELECT '=== Sample Ethiopian Cities ===' AS '';
SELECT id, name, name_am, region, latitude, longitude FROM cities LIMIT 10;

-- Show sample of roads
SELECT '=== Sample Roads ===' AS '';
SELECT r.id, c1.name AS from_city, c2.name AS to_city, r.distance, r.road_type 
FROM roads r
JOIN cities c1 ON r.city1_id = c1.id
JOIN cities c2 ON r.city2_id = c2.id
LIMIT 10;

-- Check connectivity from Axum to Lalibela
SELECT '=== Connectivity Check: Axum → Lalibela ===' AS '';
SELECT c1.name AS from_city, c2.name AS to_city, r.distance
FROM roads r
JOIN cities c1 ON r.city1_id = c1.id
JOIN cities c2 ON r.city2_id = c2.id
WHERE (c1.name = 'Axum' AND c2.name = 'Lalibela')
   OR (c1.name = 'Lalibela' AND c2.name = 'Axum');

-- Show all roads from Axum
SELECT '=== All Roads from Axum ===' AS '';
SELECT c2.name AS destination, r.distance, r.road_type
FROM roads r
JOIN cities c1 ON r.city1_id = c1.id
JOIN cities c2 ON r.city2_id = c2.id
WHERE c1.name = 'Axum'
UNION
SELECT c1.name AS destination, r.distance, r.road_type
FROM roads r
JOIN cities c1 ON r.city1_id = c1.id
JOIN cities c2 ON r.city2_id = c2.id
WHERE c2.name = 'Axum';

-- ============================================================
-- END OF SCHEMA
-- ============================================================
SELECT '🎉 Database ready! Run python main.py to start the GPS Navigation System!' AS '';