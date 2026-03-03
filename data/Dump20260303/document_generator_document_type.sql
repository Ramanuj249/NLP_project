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
-- Table structure for table `document_type`
--

DROP TABLE IF EXISTS `document_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_type` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `document_type_name` varchar(100) NOT NULL,
  `components` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_type`
--

LOCK TABLES `document_type` WRITE;
/*!40000 ALTER TABLE `document_type` DISABLE KEYS */;
INSERT INTO `document_type` VALUES (1,'Policy','[Policy Title, Executive Summary, Purpose, Scope, Policy Statement, Roles & Responsibilities, Procedures / Guidelines, Compliance & Enforcement, Exceptions & Special Cases, Related Policies & References, Review & Updates, Approval & Effective Date]'),(2,'Procedure','[Purpose, Scope, Basic Company Information, Roles & Responsibilities, Preconditions & Triggers, Required Tools or Inputs, Health & Safety Considerations, Step-by-Step Procedure, Quality Checks & Verification, Exceptions & Escalation, Related Documents & References, Review & Ownership]'),(3,'Guide','[Document Header, Purpose & Scope, Intended Audience, Prerequisites & Assumptions, Core Content, Step-by-Step Instructions, Roles & Responsibilities, Tools, Resources & References, Troubleshooting & FAQs, Best Practices & Recommendations, Compliance, Security & Legal Notes, Change Log / Revision History]'),(4,'Plan','[Document Title, Executive Summary, Purpose / Objective, Scope / Context, Assumptions & Constraints, Key Stakeholders / Team, Approach / Strategy / Steps, Timeline / Schedule, Budget & Resources, Risks / Challenges / Dependencies, Contingency Plan, Expected Outcomes / Success Metrics, Communication Plan, Additional Notes / References]'),(6,'Agreement','[Title & Parties, Recitals & Background, Purpose, Scope & Obligations, Representations & Warranties, Commercial Terms, Payment Terms & Invoicing, Confidentiality & Data Protection, Ownership & Intellectual Property Rights, Limitation of Liability, Indemnification, Term & Termination, Dispute Resolution, Legal & General Terms, Signatures & Execution]'),(7,'Record','[Document Title, Purpose, Context & Background, Scope, Main Content, Data & Evidence, Responsibilities, Constraints & Considerations, Findings & Analysis, Outcome / Usage, Version & Updates]');
/*!40000 ALTER TABLE `document_type` ENABLE KEYS */;
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
