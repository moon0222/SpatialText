#  Spatial Reasoning Benchmark Dataset

## Overview

The **Spatial Reasoning Benchmark Dataset** is an open-source dataset generation toolkit designed to evaluate the spatial reasoning capabilities of large models. It supports automatic generation of complex spatial scenes containing multiple objects and produces diverse spatial reasoning questions for each scene.

The benchmark currently supports:

- **2D Spatial Reasoning Benchmark**
- **3D Spatial Reasoning Benchmark**
- **Enhanced Versions with Incomplete Information (Breakpoint Mechanism)**

The toolkit simulates realistic spatial layouts and requires models to understand relative positions, directional relationships, block structures, and perform multi-step logical reasoning. It generates structured JSON data, providing a standardized and configurable benchmark for evaluating spatial cognition.

---

## Part I:  2D Spatial Reasoning Benchmark Dataset

## Project Overview

The **2D Spatial Reasoning Benchmark Dataset** automatically generates complex 2D scenes based on an X/Y coordinate system. Each scene contains multiple objects distributed across independent blocks, along with natural language spatial relationship descriptions and structured reasoning questions.

It evaluates models’ abilities in:

- Understanding 2D directional relations
- Mapping natural language to coordinate reasoning
- Performing multi-step inference
- Handling incomplete spatial information (enhanced version)

---

## Core Features

- **2D Spatial Modeling** (X/Y axes)
- **Multiple Question Types** (FR, YN, CO, FB)
- **Highly Configurable Command-Line Parameters**
- **Algorithmic Optimization for Diversity**
- **Standardized JSON Output**
- **Optional Incomplete Information Simulation**

---

## Scene Description Format

Each scene contains:

1. **Block Descriptions** – Objects within each independent block  
2. **Spatial Relationship Descriptions** – Relative 2D positions between objects  

### Example Scene Description

```

In block 0, there is a medium black cone, a large blue frustum, a large red sphere, and a large blue cube.
In block 1, there is a large orange cuboid, a small orange cube, and a large white cube.
The medium black cone is located at the upper-left of the large orange cuboid;
the large white cube is at the upper-left of the small orange cube;
the large red sphere is at the lower-left of the medium black cone...

````

---

## Question Types (2D)

| Code | Type Name       | Description         | Evaluated Ability |
|------|----------------|--------------------|------------------|
| FR   | Find Relation | Identify spatial relationship between two objects |
| YN   | Yes/No        | Determine correctness of a spatial statement |
| CO   | Choose Object | Select object satisfying a spatial condition |
| FB   | Find Block    | Identify which block contains a given object |

Enhanced version supports **"Unknown"** answer options.

---

## Output Data Format (2D Example)

```json
[
  {
    "id": "Spatial_0",
    "scene": {
      "scene_id": 0,
      "block_count": 3,
      "object_count": 8,
      "objects": [
        {
          "object_id": 0,
          "number": [0, 1, 2],
          "name": "small red sphere",
          "coordinate": [25, -17],
          "block": 0
        }
      ],
      "description": "In block 0, there is a small red sphere..."
    },
    "questions": [
      {
        "question_type": "FR",
        "question": "What is the spatial relation between the red sphere and the green cylinder?",
        "answer": "E",
        "options": ["A. Above", "B. Below", "C. Left", "D. Right", "E. Unknown"]
      }
    ]
  }
]
````

---

## Evaluation Dimensions (2D)

* Direction recognition (Left/Right, Up/Down)
* Relative position reasoning
* Multi-step inference
* Contradiction detection
* Block reasoning
* Uncertainty handling (enhanced)

---

# Part II:  3D Spatial Reasoning Benchmark Dataset

## Project Overview

The **3D Spatial Reasoning Benchmark Dataset** extends the 2D version into a full **X/Y/Z coordinate system**. It generates complex 3D spatial scenes and evaluates models’ ability to understand spatial relations including inside/outside dimensions.

---

## Core Features

* **3D Spatial Modeling (X/Y/Z axes)**
* **Four Question Types**
* **Configurable Generation Parameters**
* **Optional Incomplete Information Mechanism**
* **Structured JSON Output**

---

## Scene Description Format (3D)

Each scene includes:

1. Block descriptions
2. 3D spatial relationship descriptions

### Example

```
In block 0, there is a small red sphere and a medium blue cuboid.
In block 1, there is a large green cylinder.
The red sphere is located to the right, above, and outside of the blue cuboid.
The green cylinder is located to the left of the blue cuboid.
```

---

## Question Types (3D)

| Code | Type Name     | Description                        |
| ---- | ------------- | ---------------------------------- |
| FR   | Find Relation | Identify 3D spatial relation       |
| YN   | Yes/No        | Determine correctness              |
| CO   | Choose Object | Select object satisfying condition |
| FB   | Find Block    | Identify block location            |

Enhanced version adds **Unknown option (G. Unknown)**.

---

## Output Data Format (3D Example)

```json
[
  {
    "id": "Spatial_0",
    "scene": {
      "scene_id": 0,
      "block_count": 3,
      "object_count": 8,
      "objects": [
        {
          "object_id": 0,
          "number": [0, 1, 2],
          "name": "small red sphere",
          "coordinate": [25, -17, 42],
          "block": 0
        }
      ],
      "description": "In block 0, there is a small red sphere..."
    },
    "questions": [
      {
        "question_type": "FR",
        "question": "What is the spatial relation between the red sphere and the blue cuboid?",
        "answer": "G",
        "options": [
          "A. Above",
          "B. Below",
          "C. Left",
          "D. Right",
          "E. Inside",
          "F. Outside",
          "G. Unknown"
        ]
      }
    ]
  }
]
```

---

# Enhanced Version: Incomplete Information Mechanism

## Breakpoint Mechanism

The enhanced version introduces a **breakpoint mechanism** to simulate incomplete real-world information.

### Key Properties

* 25% probability of skipping adjacent object relation description per axis
* Breakpoints recorded for X/Y (2D) or X/Y/Z (3D)
* Mathematical guarantee:

  * If A–B and B–C relations are known
  * But there exists a breakpoint between A and C
  * Then A–C relation is unknown

---

## Breakpoint Algorithm

```java
public boolean hasBreakBetween(int a, int b, int dimension) {
    int left = Math.min(a, b);
    int right = Math.max(a, b);

    Integer firstBreak = switch(dimension){
        case 1 -> breakpoints_x.ceiling(left);
        case 2 -> breakpoints_y.ceiling(left);
        case 3 -> breakpoints_z.ceiling(left);
        default -> null;
    };

    return firstBreak != null && firstBreak < right;
}
```

---

# Technical Architecture

```
├── Startup Layer (run.sh)
├── Interface Layer (BashHandler.java)
├── Core Generation Layer
│   ├── ObjectGenerator/
│   ├── SceneGenerator/
│   ├── QAGenerator/
│   └── SpatialDatasetGenerator/
└── JSON Output Layer
```

---

# Core Algorithms

1. **Object Feature Generation**

   * 7 shapes × 7 colors × 3 sizes
   * Combinatorial uniqueness

2. **Coordinate Assignment**

   * Latin rectangle algorithm
   * Uniform distribution

3. **Block Partitioning**

   * Fast random allocation
   * Dynamic block count

4. **Natural Language Generation**

   * Coordinate comparison
   * Implicit symmetry and transitivity

---

# Installation

## Requirements

* Java 8+
* Linux / macOS / Windows (Git Bash required)
* 2GB RAM minimum

---

# Quick Start

```bash
chmod +x run.sh
./run.sh
```

---

# Command-Line Parameters

| Parameter               | Description          | Default   |
| ----------------------- | -------------------- | --------- |
| --objects_range         | Object count range   | [5,10]    |
| --blocks_range          | Block count range    | [2,4]     |
| --max_coordinate        | Max coordinate value | 100       |
| --question_num          | Questions per scene  | 5         |
| --spatial_dataset_count | Total scenes         | 100       |
| --output                | Output file          | data.json |

---

# Usage Examples

```bash
./run.sh --objects_range [3,6] --blocks_range [1,2] --spatial_dataset_count 10
./run.sh --objects_range [8,15] --max_coordinate 200 --spatial_dataset_count 1000
./run.sh --output my_dataset.json
./run.sh --help
./run.sh --compile-only
./run.sh --clean
```

---

# Recommended Evaluation Metrics

* Accuracy
* Logical consistency
* Reasoning depth
* Unknown detection accuracy
* Overconfidence rate
* Error pattern analysis

---

# Data Diversity

* 147 feature combinations
* Configurable coordinate range (default ±100)
* Adjustable difficulty
* Optional incomplete information

---

# Suggested Prompt Template

```
Each independent block in the 3D scene is a non-overlapping cuboid aligned with coordinate axes.
Treat objects as points since distances are much larger than object sizes.
The positive x-axis is right, positive y-axis is up, positive z-axis is inside.
Only partial relationships are provided. Some relations may be unknown.
Do not assume missing relations.
Answer the following spatial reasoning questions.
```

---

Through this benchmark, researchers can systematically evaluate and improve spatial reasoning capabilities of AI systems, including robust handling of incomplete information.

```
```
