# radphoto-online
# RADPHOTO ONLINE — Backend API

**See Your Health Clearly**

RADPHOTO ONLINE is a healthcare technology platform designed to help healthcare facilities manage patient records, clinical encounters, diagnostic investigations, laboratory workflows, and related operational processes.

The backend is built with Python, Django, and Django REST Framework. It exposes REST APIs that connect the backend services with the React and TypeScript frontend.

> **Project status:** Active development. API routes, authentication methods, and features should be verified against the current implementation before use.

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Backend Architecture](#backend-architecture)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [API Modules](#api-modules)
- [Authentication](#authentication)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Security](#security)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Maintainer](#maintainer)

## Overview

The RADPHOTO ONLINE backend provides a modular foundation for healthcare information management and diagnostic workflows.

### Key objectives

- Provide REST APIs for frontend and external integrations.
- Support user authentication and role-based access control.
- Manage healthcare facilities and patient records.
- Support clinical encounters and diagnostic investigations.
- Facilitate laboratory order, result, and verification workflows.
- Support audit-related functionality and traceability.
- Provide a foundation for future medical imaging and healthcare interoperability integrations.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend framework | Django |
| API framework | Django REST Framework |
| API architecture | REST over HTTP |
| Frontend integration | React and TypeScript |
| Database | Relational database configured in project settings |
| Version control | Git and GitHub |

Refer to the project's dependency and configuration files for exact package versions and database requirements.

## Backend Architecture

The backend uses separate Django applications to organize different healthcare domains.

```text
RADPHOTO ONLINE
|
|-- React + TypeScript Frontend
|          |
|          | REST API / JSON
|          v
|-- Django REST Framework
|          |
|          |-- identity
|          |-- facilities
|          |-- patients
|          |-- encounters
|          |-- investigations
|          |-- laboratory
|          |-- audit
|          |
|          v
|-- Relational Database
|
|-- Future Integrations
           |-- PACS / DICOM
           |-- ECG / Echocardiography
           |-- Pathology
           |-- HL7 / FHIR

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/ee4cadb0-373a-4048-a502-7396a0e39e9e" />
