# Azure Logic App for Service Desk Ticket Classification

This repository contains code to classify service desk tickets using Azure OpenAI and deploy the solution in Azure Logic Apps.

## Contents

### Local Python Script

- `classify_tickets.py` - Standalone Python script to classify tickets from a CSV file.
- `config.ini` - Configuration file for the local script (contains Azure OpenAI settings).

### Azure Function App

- `azure-function/` - Complete Azure Function App with two endpoints:
  - `classify_tickets` - Process a CSV file with multiple tickets.
  - `classify_single` - Process a single ticket description.

### Deployment Instructions

- `azure_logic_app_instructions.md` - Step-by-step guide to deploy and use the Azure Function with Logic Apps.

## How to Use

### Local Testing

1. Update `config.ini` with your Azure OpenAI credentials.
2. Run `python classify_tickets.py` to process the CSV file.

### Azure Deployment

1. Deploy the Azure Function App (see instructions in `azure_logic_app_instructions.md`).
2. Configure Logic Apps for automated ticket classification.

## Solution Architecture

```ascii
┌─────────────────┐    ┌────────────────┐    ┌───────────────┐
│                 │    │                │    │               │
│  CSV/Ticket     │───▶│  Azure         │───▶│ Azure OpenAI  │
│  Source         │    │  Function      │    │               │
│                 │    │                │    │               │
└─────────────────┘    └────────────────┘    └───────────────┘
                              │
                              ▼
┌─────────────────┐    ┌────────────────┐
│                 │    │                │
│  Result         │◀───│  Logic App     │
│  Destination    │    │  Workflow      │
│                 │    │                │
└─────────────────┘    └────────────────┘
```

## Categories

The solution classifies tickets into the following categories:

- NHSUK Spam/Marketing
- NHSUK Profiles
- NHSuk Unsupported Service
- And more... (see code for full list)