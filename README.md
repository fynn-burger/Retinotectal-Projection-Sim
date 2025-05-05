# Topographic-Projection-Sim
Copyright (c) 2024 Yavuz Karaca

## Overview
This repository hosts a Python-based computational model for simulating retinotectal projections. 
Derived from a thorough analysis of a [MATLAB implementation](https://github.com/elifesciences-publications/RTP_Co-adapt_Model), 
this project translates and refines key concepts and methods into Python to enhance flexibility and experimental utility. 
The model explores the Ephrin-A/EphA interaction, a key molecular mechanism of axon guidance. 
It is underpinned by seminal studies on fiber-fiber chemoaffinity, co-adaptive desensitization, 
and balancing of forward and reverse signaling as the driving forces of adaptive topographic mapping.

**Foundational Studies**:  
- "Balancing of ephrin-Eph forward and reverse signaling" by Gebhardt at al., 2012. [Read the paper](https://journals.biologists.com/dev/article/139/2/335/45409/Balancing-of-ephrin-Eph-forward-and-reverse)
- "Fiber–fiber chemoaffinity in the genesis of topographic projections revisited" by Weth at al., 2014. [Read the paper](https://www.sciencedirect.com/science/article/abs/pii/S1084952114002213?via%3Dihub)
- "Ephrin-A/EphA specific co-adaptation as a novel mechanism in topographic axon guidance" by Fiederling et al., eLife, 2017. [Read the paper](http://dx.doi.org/10.7554/eLife.25533)

## Acknowledgments
Special thanks to Dr. Franco Weth from KIT's Department of Neurobiology for his expert guidance throughout this project. Additional thanks to Fynn Burger for helping with the implementation of several parameters, identifying/fixing bugs and analyzing the simulation logic.

## Features
- **Implemented in Python**: Completely reworked and refined in Python for improved accessibility, cleaner software design and enhanced performance.
- **Increased Configurability**: Enhanced parameter configurability allows for extensive experimentation.
- **Advanced Visualization Tools**: Integrated visualization tools to better observe and analyze the effects of parameter changes and simulation results.

## Getting Started
### Prerequisites
Ensure you have Python 3.x installed on your system. You may also need to install additional packages:

```bash
pip install numpy matplotlib scipy
```

### Installation
Clone this repository to your local machine using:
```bash
git clone https://github.com/yavuzkaraca/Retinotectal-Projection-Sim.git
```

### Configuring Simulations
You can configure the simulation by modifying the configuration dictionary found in the `config.py` file. Navigate to the configuration file using the following path:

```bash
cd Retinotectal-Projection-Sim/src/build/
```

### Running Simulations
To run a simulation, execute the main Python script:
```bash
python main.py
```
