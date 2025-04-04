# Tools for Flow Chemistry

## Research Context

The tools described in this repository were developed as part of the research on the furfural nitration platform published in:

### **"Continuous Flow Synthesis of Nitrofuran Pharmaceuticals Using Acetyl Nitrate"**

**Hubert Hellwig**<sup>a</sup>, **Loïc Bovy**<sup>a</sup>, **Kristof Van Hecke**<sup>b</sup>, **Cornelis P. Vlaar**<sup>c</sup>, **Rodolfo J. Romañach**<sup>d</sup>, **Md. Noor-E-Alam**<sup>e</sup>, **Allan S. Myerson**<sup>f</sup>, **Torsten Stelzer**<sup>c,f,g</sup>, and **Jean-Christophe M. Monbaliu**<sup>a,h</sup>

**Affiliations:**  
*a) Dr. H. Hellwig, L. Bovy, Prof. Dr. J.-C. M. Monbaliu*  
&nbsp;&nbsp;&nbsp; Center for Integrated Technology and Organic Synthesis (CiTOS), MolSys Research Unit, University of Liège  
&nbsp;&nbsp;&nbsp; B6a, Room 3/19, Allée du Six Août 13, 4000 Liège (Sart Tilman), Belgium  
&nbsp;&nbsp;&nbsp; *Homepage: [www.citos.uliege.be](https://www.citos.uliege.be)*  
&nbsp;&nbsp;&nbsp; *E-mail: [jc.monbaliu@uliege.be](mailto:jc.monbaliu@uliege.be)*

*b) Prof. Dr. K. Van Hecke*  
&nbsp;&nbsp;&nbsp; XStruct, Department of Inorganic and Physical Chemistry, Ghent University, Krijgslaan 281-S3, B-9000 Ghent, Belgium  

*c) Prof. Dr. C. P. Vlaar, Prof. Dr. T. Stelzer*  
&nbsp;&nbsp;&nbsp; Department of Pharmaceutical Sciences, University of Puerto Rico – Medical Sciences Campus, San Juan, Puerto Rico 00936, USA  

*d) Prof. Dr. R. J. Romañach*  
&nbsp;&nbsp;&nbsp; Department of Chemistry, University of Puerto Rico – Mayagüez, Mayagüez, Puerto Rico 00681, USA  

*e) Prof. Dr. Md. Noor-E-Alam*  
&nbsp;&nbsp;&nbsp; Department of Mechanical and Industrial Engineering, College of Engineering, <br> 
&nbsp;&nbsp;&nbsp; Center for Health Policy and Healthcare Research, Northeastern University, Boston, Massachusetts 02115, USA  

*f) Prof. Dr. A. S. Myerson, Prof. Dr. T. Stelzer*  
&nbsp;&nbsp;&nbsp; Department of Chemical Engineering, Massachusetts Institute of Technology, Cambridge, Massachusetts 02139, USA  

*g) Prof. Dr. T. Stelzer*  
&nbsp;&nbsp;&nbsp; Crystallization Design Institute, Molecular Sciences Research Center, University of Puerto Rico, San Juan, Puerto Rico 00926, USA  

*h) Prof. Dr. J.-C. M. Monbaliu*  
&nbsp;&nbsp;&nbsp; WEL Research Institute, Avenue Pasteur 6, B-1300 Wavre, Belgium  

---

### This repository contains subfolders with useful hardware tools for use in flow chemistry

All described tools were developed by **Hubert Hellwig**<sup>a</sup> under the supervision of **Jean-Christophe M. Monbaliu**<sup>a,h</sup> <br>
*E-mail: [hhellwig@uliege.be](mailto:hhellwig@uliege.be); [jc.monbaliu@uliege.be](mailto:jc.monbaliu@uliege.be)*

---

### How to cite this material
DOI: 10.5281/zenodo.15106903

---

## **Repository Content**
This repository is organized into multiple subfolders, each containing a specific project:

- **Pressure transducer** <br> 
&nbsp;&nbsp;&nbsp; A pressure sensor holder to be used with ceramic pressure sensors, creating a pressure transducer <br>
&nbsp;&nbsp;&nbsp; characterized by excellent chemical resistance. <br> 
&nbsp;&nbsp;&nbsp; See: "Pressure-Transducer-CiTOS-V1"

- **Electrically actuated valves** <br> 
&nbsp;&nbsp;&nbsp; A low-cost modification of commercially available valves enabling their automation. <br> 
&nbsp;&nbsp;&nbsp; See: "Electrically-Actuated-Valves-for-Flow-Chemistry"

- **Device for pressure and temperature measurement (PTMB)** <br> 
&nbsp;&nbsp;&nbsp; An affordable device for the acquisition and display of data from sensors based on Arduino. <br> 
&nbsp;&nbsp;&nbsp; See: "PTMB-Pressure-Temperature-Measurement-Box"

- **Software for pressure and temperature acquisition** <br> 
&nbsp;&nbsp;&nbsp; A simple Python script for the real-time acquisition of data from PTMB and saving it to a file. <br> 
&nbsp;&nbsp;&nbsp; See: "pyPTMB_v2"

- **Nitric acid dosing controller** <br>
&nbsp;&nbsp;&nbsp; An Arduino-based device designed to improve the safety and reliability of nitric acid dosing. <br> 
&nbsp;&nbsp;&nbsp; See: "NADC-Nitric-Acid-Dosing-Controller" <br>

- **Filtration and separation module control unit (FSM)** <br>
&nbsp;&nbsp;&nbsp; **Including continuous-flow gravity separator with magnetic phase boundary tracking** <br>
&nbsp;&nbsp;&nbsp; A system allowing non-interrupted filtration followed by continuous separation of two immiscible liquids. <br>
&nbsp;&nbsp;&nbsp; See: "FSMCU_Filtration_Separation_Control_Module" <br>

- **UV-Vis Flow Cell Design** <br>
&nbsp;&nbsp;&nbsp; A 3D-printed holder for 1/16” PFA tubing, creating a chemically resistant UV-Vis flow cell. <br> 
&nbsp;&nbsp;&nbsp; See: "UV-Vis-Flow-Cell-V1" <br>

- **Furfural Nitration Data Acquisition & Process Control Software** <br>
&nbsp;&nbsp;&nbsp; A Python-based software developed for data acquisition and process control during the research. <br>
&nbsp;&nbsp;&nbsp; This repository also includes examples of saved data and some plotted charts. <br>
&nbsp;&nbsp;&nbsp; See: "FUR_DACP" <br>

Each subfolder contains relevant design files, documentation and developed software implementations.

---

### Acknowledgements
This research was supported by the U.S. Food and Drug Administration under the FDA BAA-22-00123 program, Award Number 75F40122C00192. The authors acknowledge the University of Liège and the “Fonds de la Recherche Scientifique de Belgique (F.R.S.-FNRS)” (Incentive grant for scientific research MIS under grant No F453020F, JCMM).

### License

This project is licensed under the **CERN Open Hardware License Version 2 - Permissive (CERN-OHL-P)** for the hardware design and associated documentation. You are free to use, modify, and distribute the hardware under the terms of this license.

The code in this repository is licensed under the **MIT License**. You are free to use, modify, and distribute the code under the terms of this license.
