
# netlist and bench generation from yosys output with python program
 
 developed by Sepideh Fahiman, bachelor student of Computer engineering at the University of Tehran,
under the supervision of professor Zainalabedin Navabi Shirazi.
special thanks to Mohammad Rasoul Roshanshah, Ph.D. student of Electrical engineering at the University of Tehran.


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


Then you can give the yosys output file to our program to generate a netlist and a bench file.
*********************************************************************************************************************************


## important points

Test each step, The file and it's test and it's synthesized output from yosys and related libraries must be the same as the final output of the netlist from our program and the component library in Modelsim.

*********************************************************************************************************************************
## example1 : ### shift register module

### shift register verilog code:
// Code your design here
module shift_reg  #(parameter MSB=16) (  input d,                      // Declare input for data to the first flop in the shift register
                                        input clk,                    // Declare input for clock to all flops in the shift register
                                        input en,                     // Declare input for enable to switch the shift register on/off
                                        input dir,                    // Declare input to shift in either left or right direction
                                        input rstn,                   // Declare input to reset the register to a default value
                                        output reg [MSB-1:0] out);    // Declare output to read out the current value of all flops in this register


   // This always block will "always" be triggered on the rising edge of clock
   // Once it enters the block, it will first check to see if reset is 0 and if yes then reset register
   // If no, then check to see if the shift register is enabled
   // If no => maintain previous output. If yes, then shift based on the requested direction
   always @ (posedge clk)
      if (!rstn)
         out <= 0;
      else begin
         if (en)
            case (dir)
               0 :  out <= {out[MSB-2:0], d};
               1 :  out <= {d, out[MSB-1:1]};
            endcase
         else
            out <= out;
      end
endmodule
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


