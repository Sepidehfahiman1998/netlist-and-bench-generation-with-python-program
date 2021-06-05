
# netlist and bench generation from yosys output with python program
 
 ## Acknowledgments:
 
 developed by Sepideh Fahiman, bachelor student of Computer engineering at the University of Tehran,
 
under the supervision of professor Zainalabedin Navabi Shirazi.

special thanks to Mohammad Rasoul Roshanshah, Ph.D. student of Electrical engineering at the University of Tehran.

## Refrences:

[1] Digital System Test and Testable Design, Authors: Navabi, Zainalabedin.
[2] http://www.clifford.at/yosys/


You can send your comments to this address  <sepideh.fahiman@gmail.com>

*********************************************************************************************************************************
# Introduction

Digital system testing involves various tools for simulation, fault list generation, fault reduction, and test generation. Because test generation programs are time consuming, it is best to be able to generate tests for only those faults that can be distinguished, so that the redundancy in test vectors is minimized. Fault collapsing is the process of reducing faults in a circuit to only those that can be distinguished. An inexpensive method for fault collapsing is the local fault collapsing. This method is particularly efficient for gate level combinational circuits. In local equivalent fault collapsing faults on ports of logical gates are collapsed such that only one fault from each equivalent class of faults remain on the ports of the gate. A typical test environment uses fault collapsing to obtain a reduced fault list, uses test generation to generate test vectors for the list of faults, and uses fault simulation for discarding faults detected by a generated test.
In order to be able to use VHDL in an integrated design, simulation and test environment, appropriate VHDL models must be developed. In such an environment, the same VHDL gate level description can be bound to simulation models for design verification, to test models for test generation, or it can be bound to fault collapsing models for finding an optimum fault list.
VHDL gate models for local fault collapsing start with a set of all possible faults of a gate. The gate models by communicating through their IO ports decide on a minimum list of distinguishable faults and report such faults to a text file. Fault collapsing can be done for a VHDL gate level description by binding the structures of this description to the fault collapsing models. A fault list report generated for this description specifies a reduced list of faults for the entire circuit.

The first step for fault simulation is converting the high level of Verilog code of a given circuit to the gate level code. In this step, synthetic tools, e.g. yosys are used in order to optimize the given circuit and produce the lower level design code. Then the synthesised code is used for fault diagnosis. Therefore, generating the synthesised code is one of the main steps in fault identification and testing procedures.


*********************************************************************************************************************************
To know "yosys" and download it, refer to the following address:

<http://www.clifford.at/yosys/documentation.html>

It is recommended to use the following commands to generate output from yosys:

### #read design

read_verilog XXXX.v

### #generic synthesis, We need to use -auto-top command to automatically detect the top module and synthesize it accordingly

synth -auto-top 

### #also We need to use flatten command to get only one synthesized output file containing the top module name

flatten

### #mapping to mycells.lib

dfflibmap -liberty mycells.lib
abc -liberty mycells.lib

### #write synthesized design

write_verilog -noattr XXXX.v


Then you can give the yosys output file to our program to generate a netlist and a bench file.
*********************************************************************************************************************************


## important points

Test each step, The file and it's test and it's synthesized output from yosys and related libraries must be the same as the final output of the netlist from our program and the component library in Modelsim.

*********************************************************************************************************************************
## example1 : ### shift register module

### shift register verilog code:
![sh](https://user-images.githubusercontent.com/71797162/119122798-28347100-ba44-11eb-8358-9fc8a787c674.PNG)




### Pre synthesis simulation of shift_reg (use shift_reg.v,shift_reg_tb.v).
![before synth](https://user-images.githubusercontent.com/71797162/120886647-41bce780-c604-11eb-9d1b-c30e7f6d9259.PNG)

*********************************************************************************************************************************



### Post synthesis simulation of shift_reg(use shift_reg_synth.v,shift_reg_tb.v,mycells.v (The library defined in yosys)).
![post synth](https://user-images.githubusercontent.com/71797162/120886689-61541000-c604-11eb-9688-179c1ff67517.PNG)

*********************************************************************************************************************************


### We can now produce a new version of the synthesized file(netlist) based on component_library . 


![g](https://user-images.githubusercontent.com/71797162/120832638-20151f00-c576-11eb-9d7f-d1899735d187.PNG)

*********************************************************************************************************************************



### Let's verify netlist.v, for this purpose we have to do the simulation again using netlist.v and component_library.v and shift_reg_tb.v.

![jj](https://user-images.githubusercontent.com/71797162/120886707-89437380-c604-11eb-910a-c90b48da4cc7.PNG)

*********************************************************************************************************************************


### As you can see, the output of the net list is exactly the same as the previous two.
### You can also generate a benchfile:
![nn](https://user-images.githubusercontent.com/71797162/120835695-e80fdb00-c579-11eb-9b25-27cd236e8c09.PNG)

![Capture](https://user-images.githubusercontent.com/71797162/120835924-38873880-c57a-11eb-920f-054b77288054.PNG)


