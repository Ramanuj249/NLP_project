-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: document_generator
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `category_id` tinyint unsigned DEFAULT NULL,
  `document_type_id` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_documents_categories` (`category_id`),
  KEY `fk_documents_types` (`document_type_id`),
  CONSTRAINT `fk_documents_categories` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_documents_types` FOREIGN KEY (`document_type_id`) REFERENCES `document_type` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (1,'Remote Work Policy',1,1),(2,'PTO / Leave Policy',1,1),(3,'Code of Conduct',1,1),(4,'Anti-Harassment Policy',1,1),(5,'Compensation Philosophy',1,1),(6,'Sabbatical Policy',1,1),(7,'Travel & Expense Policy',1,1),(8,'Equipment Policy',1,1),(9,'Privacy Policy',2,1),(10,'Cookie Policy',2,1),(11,'Acceptable Use Policy',2,1),(12,'Security Policy',2,1),(13,'Copyright Policy (DMCA)',2,1),(14,'API Rate Limiting Policy',3,1),(15,'Dependency Update Policy',3,1),(16,'Expense Reimbursement Policy',4,1),(17,'Procurement Policy',4,1),(18,'Financial Controls Policy',4,1),(19,'Revenue Recognition Policy',4,1),(20,'Social Media Policy',5,1),(21,'Performance Review Process',1,2),(22,'Offboarding Procedure',1,2),(23,'Incident Response Plan',2,2),(24,'Customer Onboarding Checklist',6,2),(25,'Incident Response Runbook',3,2),(26,'Deployment SOP',3,2),(27,'Database Migration SOP',3,2),(28,'Backup & Recovery Procedure',3,2),(29,'Security Incident Playbook',3,2),(30,'On-Call Rotation Guide',3,2),(31,'Monitoring & Alerting Setup',3,2),(32,'Employee Handbook',1,3),(33,'Benefits Guide',1,3),(34,'Data Security Training',1,3),(35,'Training Materials',6,3),(36,'Feature Comparison Sheet',6,3),(37,'Pricing & Packaging Doc',6,3),(38,'Security Questionnaire Responses',6,3),(39,'API Documentation',6,3),(40,'Integration Guides',6,3),(41,'Code Review Guidelines',3,3),(42,'Architecture Decision Records (ADR)',3,3),(43,'CI/CD Pipeline Documentation',3,3),(44,'Infrastructure as Code (IaC) Docs',3,3),(45,'Design System Documentation',7,3),(46,'User Persona Docs',7,3),(47,'Accessibility Guidelines',7,3),(48,'Brand Guidelines',5,3),(49,'Content Style Guide',5,3),(50,'Implementation Plan',6,4),(51,'Testing Strategy',3,4),(52,'Disaster Recovery Plan',3,4),(53,'Product Roadmap',7,4),(54,'SEO Strategy Document',5,4),(55,'Go-to-Market Plan',5,4),(56,'Capital Allocation Framework',4,4),(57,'Onboarding Checklist',1,2),(58,'Referral Program',1,1),(59,'Sales Proposal Template',6,4),(60,'Statement of Work (SOW)',6,6),(61,'Case Study Template',6,7),(62,'ROI Calculator',6,3),(63,'Release Notes Template',7,7),(64,'A/B Test Analysis Template',7,7),(65,'Press Release Template',5,3),(66,'Blog Post Template',5,3),(67,'Email Template Library',5,3),(68,'Webinar Script Template',5,4),(69,'Invoice Template',4,7),(70,'Budget Planning Template',4,4),(71,'Vendor Agreement Template',4,6),(72,'Contract Review Checklist',4,2),(73,'Board Meeting Template',4,7),(74,'Terms of Service',2,6),(75,'Data Processing Agreement (DPA)',2,6),(76,'SLA (Service Level Agreement)',2,6),(77,'Master Services Agreement (MSA)',6,6),(78,'Non-Disclosure Agreement (NDA)',6,6),(79,'Subprocessor List',2,7),(80,'GDPR Compliance Docs',2,7),(81,'CCPA Compliance Docs',2,7),(82,'Accessibility Statement',2,7),(83,'Trademark Guidelines',2,7),(84,'Open Source Licenses',2,7),(85,'Compliance Certifications',6,7),(87,'Product Requirements Doc (PRD)',7,7),(88,'Feature Spec',7,7),(89,'User Research Report',7,7),(90,'Usability Test Report',7,7),(91,'Competitive Analysis',5,7);
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-03 19:29:45
