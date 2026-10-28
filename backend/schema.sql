CREATE DATABASE IF NOT EXISTS divine_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE divine_management;

CREATE TABLE IF NOT EXISTS temples (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  location VARCHAR(180) NOT NULL,
  deity VARCHAR(100) NOT NULL,
  history TEXT NOT NULL,
  image TEXT NOT NULL,
  services VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  temple_id VARCHAR(50) NOT NULL,
  date DATE NOT NULL,
  time VARCHAR(40) NOT NULL,
  FOREIGN KEY (temple_id) REFERENCES temples(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  booking_type VARCHAR(50) NOT NULL,
  temple_id VARCHAR(50) NULL,
  date DATE NULL,
  slot VARCHAR(40) NULL,
  persons INT DEFAULT 1,
  pooja VARCHAR(100) NULL,
  checkin DATE NULL,
  checkout DATE NULL,
  rooms INT NULL,
  meal VARCHAR(40) NULL,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(160) NOT NULL,
  event_name VARCHAR(180) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (temple_id) REFERENCES temples(id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS donations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  temple_id VARCHAR(50) NOT NULL,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(160) NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  purpose VARCHAR(100) NOT NULL,
  status VARCHAR(30) DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (temple_id) REFERENCES temples(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS complaints (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  category VARCHAR(60) NOT NULL,
  message TEXT NOT NULL,
  status VARCHAR(30) DEFAULT 'OPEN',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_registrations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_name VARCHAR(180) NOT NULL,
  event_date DATE NULL,
  event_time VARCHAR(40) NULL,
  temple_id VARCHAR(50) NULL,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(160) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (temple_id) REFERENCES temples(id) ON UPDATE CASCADE ON DELETE SET NULL
);

INSERT INTO temples (id,name,location,deity,history,image,services) VALUES
('siddhivinayak','Siddhivinayak Ganapati Temple','Mumbai, Maharashtra','Lord Ganesha','A famous Ganapati temple in Prabhadevi, Mumbai, visited by devotees seeking blessings for success and new beginnings.','https://commons.wikimedia.org/wiki/Special:Redirect/file/Shree%20Siddhivinayak%20Temple%20Mumbai.jpg','Darshan,Pooja,Donation,Events,Bhojan'),
('kashi','Kashi Vishwanath Temple','Varanasi, Uttar Pradesh','Lord Shiva','One of the most revered Shiva temples, located in the sacred city of Varanasi near the Ganga.','https://commons.wikimedia.org/wiki/Special:Redirect/file/Kashi%20Vishwanath%20Temple%20in%20Varanasi.jpg','Darshan,Pooja,Donation,Room Booking'),
('tirumala','Tirumala Venkateswara Temple','Tirupati, Andhra Pradesh','Lord Venkateswara','A major pilgrimage destination dedicated to Lord Venkateswara on the Tirumala hills.','https://commons.wikimedia.org/wiki/Special:Redirect/file/Tirupati%20Temple%20outside.jpg','Darshan,Pooja,Room Booking,Bhojan'),
('jagannath','Jagannath Temple','Puri, Odisha','Lord Jagannath','A historic temple famous for the annual Rath Yatra and its distinctive temple traditions.','https://commons.wikimedia.org/wiki/Special:Redirect/file/Jagannath%20Temple%20Puri.JPG','Darshan,Pooja,Donation,Events'),
('somnath','Somnath Temple','Prabhas Patan, Gujarat','Lord Shiva','A prominent Jyotirlinga temple on the Arabian Sea coast with a long and celebrated history.','https://commons.wikimedia.org/wiki/Special:Redirect/file/Somnath%20Temple.JPG','Darshan,Pooja,Donation,Room Booking,Bhojan')
ON DUPLICATE KEY UPDATE name=VALUES(name),location=VALUES(location),deity=VALUES(deity),history=VALUES(history),image=VALUES(image),services=VALUES(services);

INSERT INTO events (name,temple_id,date,time) VALUES
('Special Aarti','siddhivinayak','2026-11-02','7:00 PM'),
('Maha Shivratri Preparation','somnath','2026-11-08','6:00 PM'),
('Temple Cultural Evening','jagannath','2026-11-15','5:30 PM');
