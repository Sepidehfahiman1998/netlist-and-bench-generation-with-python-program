# netlist and bench generation from yosys output with python program
 
 
developed by Sepideh Fahiman , bachelor student of Computer engineering at University of Tehran.


under the supervision of professor Zainalabedin Navabi Shirazi                     

                                                                                                      
special thanks to Mohammad rasoul Roshanshah , PHD student of Electrical engineering at University of Tehran


You can send your comments specifically to this address  <sepideh.fahiman@gmail.com>

*********************************************************************************************************************************

To know "yosys" and download it, refer to the following address:

<http://www.clifford.at/yosys/documentation.html>

It is recommended to use the following commands to generate output from yosys:

### #read design

read_verilog XXXX.v

### #generic synthesis , We need to use -auto-top command to automatically detect the top module and synthesize it accordingly

synth -auto-top 

### #also We need to use flatten command to get only one synthesized output file containing the top module name

flatten

### #mapping to mycells.lib

dfflibmap -liberty mycells.lib
abc -liberty mycells.lib

### #write synthesized design

write_verilog -noattr XXXX.v


Then you can give the yosys output file to our program to generate a netlist and a bench .
*********************************************************************************************************************************


## important points

Test each step , The file and its test and its synthesized output from yosys and related libraries must be the same as the final output of the netlist from our program and the component library in Modelsim.

*********************************************************************************************************************************
## example : ### shift register module

### shift register verilog code

![sh](https://user-images.githubusercontent.com/71797162/119122798-28347100-ba44-11eb-8358-9fc8a787c674.PNG)


### Pre synthesis simulation of shift_reg
![before synth](https://user-images.githubusercontent.com/71797162/120824326-97928080-c56d-11eb-8c60-dea44b6167e9.PNG)


### Post synthesis simulation of shift_reg

