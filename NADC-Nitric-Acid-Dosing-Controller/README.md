# Nitric Acid Dosing Controller
Developed by Hubert Hellwig	<sup>a</sup> under supervision of Jean-Christophe M. Monbaliu<sup>a,b</sup><br/><br/>
&nbsp; *a) Center for Integrated Technology and Organic Synthesis (CiTOS), MolSys Research Unit University of Liège,*<br/>
&nbsp; &nbsp; &nbsp; *B6a, Room 3/19, Allée du Six Août 13, 4000 Liège (Sart Tilman) (Belgium); webpage: https://www.citos.uliege.be*<br/>
&nbsp; *b)	WEL Research Institute, Avenue Pasteur 6, B-1300 Wavre (Belgium)*

&nbsp; *E-mail: hhellwig@uliege.be; jc.monbaliu@uliege.be*

#### The Nitric Acid Dosing Controller (NADC) is part of the Nitric Acid Dosing Module (NADM), designed to improve safety, enable automation, and minimize manual handling of corrosive acid mixtures. It was developed specifically for the continuous-flow furfural nitration platform to ensure the reliable and safe dosing of 90% nitric acid.

## Features:
- Arduino-based control for two electrically actuated valves and a peristaltic pump
- Serial communication (ASCII commands) for remote operation
- Manual control (priority) via rocker switches
- LED indicators for valve positions
- LCD display for detailed status

Additional information
- Additional details, schematics, and software are available in this part of the repository
- Modification of valves used in NADM is available within this repository ("Electrically-Actuated-Valves-for-Flow-Chemistry")

Construction of this device requires basic knowledge in electronics (soldering, understanding of simple circuit diagrams) and basic knowledge in Arduino programming. Modifications of the Arduino code may be required to fit this device for use with different servo motors or valves.


The system integrates a Flom UI-22-110DC HPLC-type pump, ensuring ergonomic priming, rinsing, and plunger seal compartment washing. The pump is accompanied by a balance used as a mass-flow meter, allowing flow rate measurement of corrosive media. Data from the balance and remote control of the pump were managed via a PC, utilizing a prototypical software written in Python for real-time monitoring and control.


### Acknowledgements
This research was supported by the U.S. Food and Drug Administration under the FDA BAA-22-00123 program, Award Number 75F40122C00192. The authors acknowledge the University of Liège and the “Fonds de la Recherche Scientifique de Belgique (F.R.S.-FNRS)” (Incentive grant for scientific research MIS under grant No F453020F, JCMM).
