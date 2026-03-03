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
-- Table structure for table `generated_documents`
--

DROP TABLE IF EXISTS `generated_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generated_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int DEFAULT NULL,
  `document_name` varchar(255) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `document_type` varchar(50) DEFAULT NULL,
  `version` varchar(20) DEFAULT '1.0',
  `author` varchar(100) DEFAULT NULL,
  `document_content` longtext,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `document_id` (`document_id`),
  CONSTRAINT `generated_documents_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `generated_documents`
--

LOCK TABLES `generated_documents` WRITE;
/*!40000 ALTER TABLE `generated_documents` DISABLE KEYS */;
INSERT INTO `generated_documents` VALUES (1,1,'Remote Work Policy','HR & People Operations','POLICY','1.0','Unknown','# Remote Work Policy\n**Version:** 1.0  \n**Date:** 2026-03-03  \n**Author:** HR Department  \n**Company:** [Your Company Name]\n\n---\n\n## Executive Summary\nThe Remote Work Policy outlines the framework and guidelines for employees of [Your Company Name] who engage in remote work arrangements. This policy aims to provide clarity on the expectations, responsibilities, and procedures associated with remote work, ensuring that both the organization and its employees can maintain productivity, collaboration, and compliance with applicable laws and regulations. As remote work becomes an integral part of our operational strategy, this policy serves to align our workforce with the company\'s goals while fostering a flexible work environment.\n\n## Purpose\nThe purpose of this document is to establish a clear and comprehensive policy governing remote work at [Your Company Name]. This policy aims to facilitate a structured approach to remote work that balances employee flexibility with organizational needs. By defining eligibility criteria, approval processes, and performance expectations, this policy seeks to enhance employee satisfaction while safeguarding the company\'s interests.\n\n## Scope\nThis policy applies to all employees of [Your Company Name] who are eligible to work remotely. The following groups are included under this policy:\n\n- Full-time employees\n- Part-time employees\n- Temporary employees\n- Interns\n\nThis policy is applicable across all company locations and operating countries where [Your Company Name] conducts business.\n\n## Policy Statement\n[Your Company Name] recognizes the benefits of remote work arrangements and is committed to providing employees with the opportunity to work remotely, subject to the following conditions:\n\n1. **Eligibility**: Employees must meet specific criteria to qualify for remote work, including but not limited to job function, performance history, and departmental needs. Approval from the direct supervisor is required prior to commencing remote work.\n\n2. **Approval Process**: Employees seeking to work remotely must submit a formal request to their supervisor, detailing the proposed remote work schedule and location. Supervisors will evaluate requests based on operational requirements and employee performance.\n\n3. **Work Environment**: Employees are expected to maintain a professional work environment while working remotely. This includes ensuring a reliable internet connection, a designated workspace free from distractions, and adherence to company policies regarding data security and confidentiality.\n\n4. **Revocation of Remote Work**: The company reserves the right to revoke remote work privileges at any time based on performance issues, changes in business needs, or violations of this policy.\n\n## Roles & Responsibilities\n\n| Role                     | Responsibilities                                                                 |\n|--------------------------|---------------------------------------------------------------------------------|\n| **Employees**            | - Submit remote work requests to supervisors.<br>- Maintain productivity and communication.<br>- Adhere to company policies and guidelines. |\n| **Supervisors**         | - Evaluate remote work requests based on operational needs.<br>- Monitor employee performance and productivity.<br>- Provide support and resources for remote work. |\n| **HR Department**       | - Develop and maintain the Remote Work Policy.<br>- Provide training and resources for employees and supervisors.<br>- Ensure compliance with legal and regulatory requirements. |\n| **IT Department**       | - Provide necessary equipment and technical support for remote work.<br>- Ensure data security and system access for remote employees.<br>- Monitor compliance with IT security policies. |\n\n## Procedures / Guidelines\n1. **Request Submission**: Employees must submit a remote work request form to their supervisor at least two weeks in advance of the desired start date. The request should include the proposed work schedule, location, and justification for remote work.\n\n2. **Approval Process**: Supervisors will review requests within five business days and communicate their decision to the employee. If approved, the employee will receive a confirmation email outlining the terms of the remote work arrangement.\n\n3. **Work Hours**: Employees are expected to maintain regular working hours as defined by their department. Any changes to work hours must be communicated to the supervisor in advance.\n\n4. **Communication**: Employees must remain accessible during working hours through company-approved communication channels (e.g., email, instant messaging, video conferencing). Regular check-ins with supervisors are encouraged to ensure alignment on tasks and projects.\n\n5. **Performance Monitoring**: Supervisors will monitor employee performance through regular feedback sessions and performance evaluations. Employees are expected to meet established performance metrics while working remotely.\n\n## Compliance & Enforcement\nCompliance with this policy is mandatory for all employees engaged in remote work. Non-compliance may result in disciplinary action, up to and including termination of employment. The following enforcement mechanisms will be in place:\n\n- **Monitoring**: Supervisors will regularly assess employee performance and adherence to remote work guidelines.\n- **Reporting Violations**: Employees are encouraged to report any violations of this policy to their supervisor or the HR department.\n- **Escalation**: Serious violations may be escalated to senior management for further action.\n\n## Exceptions & Special Cases\nExceptions to this policy may be granted under specific circumstances, such as:\n\n- Temporary medical conditions that require a flexible work arrangement.\n- Unique job functions that necessitate alternative remote work arrangements.\n\nAll exceptions must be documented and approved by the HR department and the employee\'s supervisor.\n\n## Related Policies & References\n- **Data Security Policy**: Outlines the requirements for protecting company data and maintaining confidentiality while working remotely.\n- **IT Equipment Policy**: Details the provision and use of company equipment for remote work.\n- **Employee Handbook**: Contains general policies and procedures applicable to all employees.\n\n## Review & Updates\nThis policy will be reviewed annually by the HR department to ensure its relevance and effectiveness. Any necessary updates will be communicated to all employees.\n\n## Approval & Effective Date\nThis Remote Work Policy was approved by [Approving Authority] on [Approval Date] and is effective as of March 3, 2026.\n\n---\n\n**Confidentiality Notice**: This document contains confidential information intended for the use of [Your Company Name] employees only. Unauthorized use or distribution is prohibited.','2026-03-03 15:49:13','2026-03-03 15:49:13');
/*!40000 ALTER TABLE `generated_documents` ENABLE KEYS */;
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
