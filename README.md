# Datacentric BIM Research Project

## Quick Overview

This project is an early-stage research initiative focused on developing a **standalone operational BIM ecosystem** for construction projects. It implements datacentric approaches to integrate 4D (schedule) and 5D (cost) information directly into IFC models through ontology-driven data ingestion.

**Core Objective**: Build an operational BIM ecosystem that supports planning, execution, and operational phases of construction projects with seamless data integration and interoperability.

---

## Table of Contents

- [Project Status](#project-status)
- [What This Project Does](#what-this-project-does)
- [Directory Structure](#directory-structure)
- [Detailed Process Explanation](#detailed-process-explanation)
- [Related Works](#related-works)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Future Development](#future-development)

---

## Project Status

🚧 **Early Stage Testing** - This is a proof-of-concept implementation demonstrating core capabilities for datacentric BIM workflows.

---

## What This Project Does

This project transforms standard 3D IFC building models into enriched 4D/5D models by:

1. **Loading 3D IFC models** containing building elements
2. **Creating construction tasks** with detailed scheduling information (4D)
3. **Assigning resources** (materials, labor, equipment) to tasks
4. **Adding cost data** including budgeted and actual values (5D)
5. **Establishing task sequences** and dependencies
6. **Linking tasks to specific building elements** for complete lifecycle tracking
7. **Following designated ontology schemas** for standardized data representation

---

## Directory Structure

```
project-root/
│
├── /ontology_schema/
│   └── Contains designated ontology schemas that guide data ingestion
│       - Defines standardized structure for BIM data
│       - Ensures interoperability and semantic consistency
│       - Based on IPROK ontology framework (https://w3id.org/iprok/)
│
├── /Models/
│   ├── Input models (e.g., Duplex_House_Modified.ifc)
│   ├── Output models (e.g., Duplex_House_4D_Complete.ifc, Duplex_House_5D_From_Ontology.ifc)
│   └── Testing notebook files demonstrating various processes
│
├── IfcProcess.ipynb
│   └── Main Jupyter notebook for research and testing workflows
│
└── script.py
    └── Executable script for automated operations
```

### `/ontology_schema/` Directory

This directory contains the ontology schemas that serve as the blueprint for data ingestion:

- **Purpose**: Define standardized vocabulary and relationships for construction data
- **Function**: Guide the transformation of raw data into semantically rich IFC entities
- **Standards**: Aligns with Industry Foundation Classes (IFC) and IPROK ontology
- **Usage**: Referenced during data ingestion to ensure consistent data structure

### `/Models/` Directory

Contains all IFC model files and demonstration notebooks:

- **Input Models**: Original 3D IFC files (e.g., architectural models)
- **Output Models**: Enhanced models with 4D/5D information
- **Test Notebooks**: Various Jupyter notebooks demonstrating specific processes and validating results

### `script.py`

The main execution file that:
- Orchestrates the complete data ingestion workflow
- Applies ontology-based transformations
- Generates enriched output models
- Can be run as a standalone script for production workflows

---

## Detailed Process Explanation

### 1. Model Loading and Element Identification

The process begins by loading an IFC model and identifying target building elements:

```python
# Load IFC file
ifc_file = ifcopenshell.open("Models/Duplex_House_Modified.ifc")

# Identify target element by GUID
building_element = ifc_file.by_guid("2FUQJjpVj9wBkoUxY59XRk")
```

### 2. Task Creation (4D - Scheduling)

Construction tasks are created with detailed scheduling information:

- **Task Properties**:
  - Unique Global ID
  - Task name and description
  - Task type classification

- **Schedule Data (IfcTaskTime)**:
  - Schedule Start/Finish dates
  - Schedule Duration
  - Actual Start/Finish dates
  - Actual Duration

Example:
```
Task: "Slab and Beam Concrete Casting"
├── Scheduled: 04-09-2023 to [Finish Date]
├── Actual: 08-09-2023 to [Finish Date]
└── Duration: Calculated automatically
```

### 3. Resource Assignment

Resources are formally created and assigned to tasks:

- **Material Resources**: Construction materials (concrete, formwork, binding wire)
- **Labor Resources**: Workers and skilled personnel
- **Equipment Resources**: Machinery and tools

Each resource includes:
- Unique identification
- Resource type classification
- Quantity information (budgeted vs. actual units)

Example:
```
Task: "Slab and Beam Formwork"
├── Resource: FormWork
│   ├── Budgeted Units: 50.0
│   └── Actual Units: 62.0
```

### 4. Cost Integration (5D - Cost Management)

Cost data is added through IfcCostItem entities:

- **Cost Categories**:
  - Material Costs
  - Labor Costs
  - Equipment Costs

- **Cost Values**:
  - Budgeted amounts
  - Actual amounts
  - Variance tracking

Example:
```
Task: "Slab and Beam Steel Reinforcement"
├── Material Cost: Budgeted $9,508 | Actual $13,145
├── Labor Cost: Budgeted $10,215 | Actual $9,822
└── Equipment Cost: Budgeted $25,795 | Actual $27,144
```

### 5. Task Sequencing

Tasks are connected through sequence relationships:

- **Sequence Types**:
  - Finish-to-Start (FS)
  - Start-to-Start (SS)
  - Finish-to-Finish (FF)
  - Start-to-Finish (SF)

- **Purpose**: Define workflow dependencies and critical path

### 6. Element-Task Linking

Tasks are linked to specific building elements using `IfcRelAssignsToProduct`:

```
Building Element: "Concrete-Rectangular Beam:PBEAM_230X300"
├── Task 1: Formwork
├── Task 2: Steel Reinforcement
├── Task 3: Concrete Casting
└── Task 4: Curing
```

### 7. Verification Process

A comprehensive verification system ensures data integrity:

```
Verification Checks:
✅ Tasks assigned to building elements
✅ Schedule data presence and validity
✅ Resource assignments
✅ Cost item associations
✅ Sequence relationships
```

### 8. Ontology-Driven Data Ingestion

The process follows designated ontology schemas from `/ontology_schema/`:

1. **Schema Loading**: Read ontology definitions
2. **Data Mapping**: Map source data to ontology classes
3. **Validation**: Ensure compliance with schema rules
4. **Instantiation**: Create IFC entities following ontology structure
5. **Relationship Building**: Establish semantic connections

This ensures:
- Semantic consistency across datasets
- Interoperability with other BIM tools
- Standardized data exchange
- Machine-readable construction knowledge

---

## Related Works

This research builds upon and integrates with existing frameworks:

### IPROK Framework

- **Web Application**: [iprok-web.streamlit.app](https://iprok-web.streamlit.app/)
- **Repository**: [github.com/konevenkatesh/Iprok-web.git](https://github.com/konevenkatesh/Iprok-web.git)
- **Ontology**: [w3id.org/iprok/](https://w3id.org/iprok/)

**IPROK (Integrated Project Knowledge)** provides:
- Standardized ontology for construction projects
- Semantic framework for BIM data
- Interoperability guidelines
- Knowledge representation structures

### Key Differences

This project extends IPROK by:
- Implementing direct IFC model manipulation
- Adding automated 4D/5D data integration
- Providing executable scripts for production use
- Focusing on operational workflows

---

## Technology Stack

### Core Libraries

- **ifcopenshell**: IFC file manipulation and API
- **Python 3.11+**: Primary programming language
- **Jupyter**: Interactive development and testing

### Data Standards

- **IFC (Industry Foundation Classes)**: Building information model standard
- **IPROK Ontology**: Construction knowledge representation
- **ISO 19650**: BIM information management

### Key Capabilities

1. **IFC Entity Creation**: Direct manipulation of IFC schema
2. **GUID Management**: Unique identification system
3. **Relationship Management**: Complex entity relationships
4. **Property Sets**: Extended data attachment
5. **Validation**: Data integrity verification

---

## Getting Started

### Prerequisites

```bash
pip install ifcopenshell
pip install jupyter
```

### Basic Usage

1. **Place input IFC models** in `/Models/` directory
2. **Configure ontology schemas** in `/ontology_schema/`
3. **Run the main notebook**:
   ```bash
   jupyter notebook IfcProcess.ipynb
   ```
4. **Execute automated script**:
   ```bash
   python script.py
   ```

### Testing the Process

The `IfcProcess.ipynb` notebook demonstrates:
- 4D model creation
- 5D cost integration
- Ontology-driven data ingestion
- Verification workflows

Each cell can be run independently for testing specific functions.

---

## Key Features

### ✅ Implemented

- [x] 3D to 4D transformation (scheduling)
- [x] 5D cost data integration
- [x] Resource management
- [x] Task sequencing
- [x] Element-task linking
- [x] Ontology-based data structure
- [x] Comprehensive verification system

### 🚧 In Development

- [ ] Automated data extraction from project management tools
- [ ] Real-time model updates
- [ ] Advanced analytics and reporting
- [ ] Multi-model coordination
- [ ] Web-based visualization interface

---

## Future Development

### Short-term Goals

1. **Enhanced Ontology Integration**
   - Expand ontology schema coverage
   - Implement automatic schema validation
   - Add custom property set templates

2. **Automation Improvements**
   - Batch processing capabilities
   - Automated data source integration
   - Scheduled model updates

3. **Validation Enhancement**
   - More comprehensive verification checks
   - Automated error detection and correction
   - Compliance checking against standards

### Long-term Vision

**Standalone Operational BIM Ecosystem** that supports:

1. **Planning Phase**
   - Automated schedule generation from design
   - Cost estimation and budgeting
   - Resource planning and allocation

2. **Execution Phase**
   - Real-time progress tracking
   - As-built model updates
   - Variance analysis (planned vs. actual)

3. **Operational Phase**
   - Facility management integration
   - Maintenance scheduling
   - Lifecycle cost analysis
   - Asset information management

### Research Objectives

- Develop comprehensive datacentric BIM methodology
- Establish best practices for ontology-driven construction data
- Create reusable frameworks for industry adoption
- Enable seamless data flow across project lifecycle
- Support digital twin implementation

---

## Use Cases

### Construction Project Management

- Link tasks to physical building elements
- Track schedule adherence
- Monitor cost performance
- Manage resource allocation

### Facility Management

- Access as-built information
- Trace construction history
- Plan maintenance activities
- Analyze lifecycle costs

### Collaboration and Coordination

- Standardized data exchange
- Semantic interoperability
- Multi-stakeholder access
- Version control and history

---

## Data Flow

```
Raw Project Data
    ↓
Ontology Schema Mapping (/ontology_schema/)
    ↓
Data Validation
    ↓
IFC Entity Creation
    ↓
Relationship Establishment
    ↓
Enhanced BIM Model (/Models/output)
    ↓
Verification & Quality Check
    ↓
Operational BIM Ecosystem
```

---

## Contributing

This is a research project in active development. Contributions, suggestions, and collaborations are welcome.

**Areas for Contribution**:
- Ontology schema development
- Additional IFC entity support
- Verification algorithm improvements
- Documentation and examples
- Integration with other tools

---

## Research Context

This work is part of ongoing research in datacentric approaches to Building Information Modeling. The goal is to move beyond file-based BIM workflows toward data-driven, semantically rich construction information management that supports the entire project lifecycle.

**Key Research Questions**:
- How can ontologies improve BIM data quality and interoperability?
- What are the best practices for integrating schedule and cost data in IFC models?
- How can we automate the transformation of project data into semantic BIM models?
- What frameworks support true operational BIM ecosystems?

---

## License

[CC BY 4.0 (Creative Commons Attribution 4.0 International)]

---

## Contact

[[Kone Venkatesh](https://www.linkedin.com/in/venkatesh-kone-66149a13b/)]

---

## Acknowledgments

- IPROK Framework developers
- IFCOpenShell community
- Building SMART International
- Open BIM research community

---


**Note**: This is an active research project. Features, structure, and methodology are subject to change as the research progresses.
