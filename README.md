
# netlist and bench generation from yosys output with python program
 
 
developed by Sepideh Fahiman, bachelor student of Computer engineering at University of Tehran,


under the supervision of professor Zainalabedin Navabi Shirazi.                     

                                                                                                      
special thanks to Mohammad rasoul Roshanshah , PHD student of Electrical engineering at University of Tehran.


You can send your comments to this address  <sepideh.fahiman@gmail.com>

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


Then you can give the yosys output file to our program to generate a netlist and a bench .
*********************************************************************************************************************************


## important points

Test each step , The file and its test and its synthesized output from yosys and related libraries must be the same as the final output of the netlist from our program and the component library in Modelsim.

*********************************************************************************************************************************
## example1 : ### shift register module

### shift register verilog code:

![sh](https://user-images.githubusercontent.com/71797162/119122798-28347100-ba44-11eb-8358-9fc8a787c674.PNG)




### Pre synthesis simulation of shift_reg (use shift_reg.v,shift_reg_tb.v).
![before synth](https://user-images.githubusercontent.com/71797162/120824326-97928080-c56d-11eb-8c60-dea44b6167e9.PNG)




### Post synthesis simulation of shift_reg(use shift_reg_synth.v,shift_reg_tb.v,mycells.v (The library defined in yosys)).
![post synth](https://user-images.githubusercontent.com/71797162/120828554-e7734680-c571-11eb-97b2-e2cec46e6f67.PNG)




### We can now produce a new version of the synthesized file(netlist) based on component_library . 


![g](https://user-images.githubusercontent.com/71797162/120832638-20151f00-c576-11eb-9d7f-d1899735d187.PNG)




### Let's verify netlist.v, for this purpose we have to do the simulation again using netlist.v and component_library.v and shift_reg_tb.v.


![jj](https://user-images.githubusercontent.com/71797162/120834617-826f1f00-c578-11eb-8645-154ad9c8426a.PNG)



### As you can see, the output of the net list is exactly the same as the previous two.
### You can also generate a benchfile:
![nn](https://user-images.githubusercontent.com/71797162/120835695-e80fdb00-c579-11eb-9b25-27cd236e8c09.PNG)

![Capture](https://user-images.githubusercontent.com/71797162/120835924-38873880-c57a-11eb-920f-054b77288054.PNG)


