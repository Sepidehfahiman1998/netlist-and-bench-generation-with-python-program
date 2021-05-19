import re
import os
import sys
import itertools

wire_sizes = {}
assign_num = 0
io_duplicates = []

ports = []
input_ports = []
single_fanout = {}

def bench():
        def wiredictgen (daata):
            global wire_sizes
            lines = daata.split('\n')

            for l in lines:
                if (l.find(' wire ') != -1) or (l.find(' input ') != -1) or (l.find(' output ') != -1):
                    token = l.split()
                    if (token[0] == '//'):
                        token = token[1:]
                    wname = ''
                    wsize = 1
                    if (token[1][0] == '['):
                        tok = token[1]
                        tok = tok[1:len(tok)-3]
                        wname = token[2].replace(';', '')
                        wsize = int(tok) + 1
                        #print(f'{wname}:{wsize}')
                    else:
                        wname = token[1].replace(';', '')
                        #print(f'{wname}:1')
                    wire_sizes[wname] = wsize



        def queue_up(daata):
            element_queue = []
            if(daata.find("{")!= -1):
                daata = daata[daata.find("{")+1 : daata.find("}")]
                tokens = daata.split(",")
                for token in tokens:
                    if(token.find("[") != -1 ):
                        if(token.find(":") != -1):
                            wire_name = token[:token.find("[")]
                            end = int(token[token.find("[")+1:token.find("]")].split(":")[0])
                            start = int(token[token.find("[")+1:token.find("]")].split(":")[1])
                            for i in range(end , start-1 , -1 ):
                                element_queue.append(f'{wire_name}[{i}]')
                        else:
                            element_queue.append(token)
                    elif (token.find("'b")!= -1):
                        bits = token.split("b")[1]
                        for bit in bits:
                            element_queue.append(bit)
                    else:
                        wire_name = token
                        #check if its multiple or signle
                        if(wire_sizes[wire_name] > 1):
                            for i in range(wire_sizes[wire_name]-1 , -1 , -1) :
                                element_queue.append(f'{wire_name}[{i}]')
                        else:
                            element_queue.append(f'{wire_name}')
            else:
                if(daata.find("[") != -1 ):
                    if(daata.find(":")!= -1):
                        wire_name = daata[:daata.find("[")]
                        end = int(daata[daata.find("[")+1:daata.find("]")].split(":")[0])
                        start = int(daata[daata.find("[")+1:daata.find("]")].split(":")[1])
                        for i in range(end , start-1 , -1):
                            element_queue.append(f'{wire_name}[{i}]')
                    else:
                        element_queue.append(daata)
                elif (daata.find("'b")!= -1):
                    bits = daata.split("b")[1]
                    for bit in bits:
                        element_queue.append(bit)
                else:
                    wire_name = daata
                    #check if its multiple or signle
                    if(wire_sizes[wire_name] > 1):
                        for i in range(wire_sizes[wire_name]-1 , -1 , -1) :
                            element_queue.append(f'{wire_name}[{i}]')
                    else:
                        element_queue.append(f'{wire_name}')

            return element_queue

        def generate_sub(lhs_queue , rhs_queue):
            global assign_num
            new_lines = ""
            assign_num += 1
            for i in range(len(lhs_queue)):
                wire1 = lhs_queue[i]
                wire2 = rhs_queue[i]
                if(wire2[0].isdigit()):
                    new_lines = new_lines + f"\nbufg _ASSIGN_{assign_num}_{i}_ (.out({wire1}),.in(1'b{wire2}));"    
                else:
                    new_lines = new_lines + f'\nbufg _ASSIGN_{assign_num}_{i}_ (.out({wire1}),.in({wire2}));'
            return new_lines

        def assign_fix(daata):
            global wire_sizes
            lines = daata.split('\n')
            for i in range(len(lines)):
                l = lines[i]
                if (l.find('assign') != -1 ):
                    text = l[l.find('assign') + len("assign")+1:]
                    text = text.replace(" " , "")
                    text = text[:text.find(";")]
                    lhs = text.split("=")[0]
                    rhs = text.split("=")[1]
                    lhs_queue = queue_up(lhs)
                    rhs_queue = queue_up(rhs)
                    newlines = generate_sub(lhs_queue , rhs_queue)
                    lines[i] = newlines[1:]
            return "\n".join(lines)




        def sanitize (cname):
            #buf = cname
            cname = cname.replace(".", "_")
            cname = cname.replace(" ", "_")
            #print(f'{buf} : {cname}')
            return cname

        def cleanname (cname):
            return cname.replace(';', '').replace(')', '').replace('(', '')

        def space_fix(data2, new_name):
            data2 = data2.replace(f'{new_name} [', f'{new_name}[')
            data2 = data2.replace(f'{new_name} )', f'{new_name})')
            data2 = data2.replace(f'{new_name} (', f'{new_name}(')
            data2 = data2.replace(f'{new_name} ;', f'{new_name};')
            return data2

        def clear_pios (data2):
            lines = data2.split('\n')
            outline = ''
            for line in lines:
                if (line.find(' pin ') == -1) and (line.find(' pout ') == -1):
                    outline += line + '\n'
            return outline

        def nametop(data2):
            global top  
            lines = data2.split('\n')
            modulename = []
            
            for line in lines:       
                if(line.find('module ') > -1):
                    modulename.append(line) 
            for i in modulename:
                y = i.split("(")[0]
                top = y[y.find(" ")+1:]
                
            return top



        def portfix (data2):
            global top_module, io_duplicates
        
            nametop(data2)  
            top_module = top
        
            pos = 0

            while pos > -1:
                pos = data2.find("module", pos+1)
                pos2 = data2.find(";", pos)

                if (pos > 0) and (pos2 > 0):
                    #par1 = data2.find('(', pos)
                    par1 = pos
                    par2 = data2.find(')', pos)
                    #print(f'{par1}:{par2}')
                    cstr = data2[par1+1:par2]
                    cstr = cstr.replace('(', ',')
                    wires = cstr.split(',')
                    wires[0] = wires[0][wires[0].find(' ')+1:]

                    
                    if (wires[0] == top_module):            # we have the IOs' list
                        wires = wires[1:]
                        sizes = {}
                        types = {}
                        ws = []
                        for wire in wires:
                            ws.append(wire.strip())
                        pos = data2.find('endmodule', pos)
                        module_body = data2[pos2+1:pos]
                        lines = module_body.split('\n')     # scan each line for i/o and length declarations

                        new_body = ''
                        
                        for line in lines:
                            size = 0
                            io = ''
                            if (line.find(' input') > -1):   #input!
                                io = 'i'
                            if (line.find(' output') > -1):   #output
                                io = 'o'
                            if (io != ''):
                                if (line.find('[') > -1):       #array
                                    size = int(line[line.find('[')+1:line.find(':')]) + 1
                                token = line[line.rfind(' ')+1 : len(line)-1].strip()
                                sizes[token] = size
                                types[token] = io
                                if (io == 'i'):         # change old I/Os to wires
                                    line = line.replace(' input', ' wire')
                                    io_duplicates.append(token)
                                else:
                                    line = line.replace(' output', ' wire')
                                    io_duplicates.append(token)
                                if (token == ''):
                                    print(f'${line}$')
                        
                            new_body += f'{line}\n'

                        # now we know the type and size of each wire
                        primary_io = ''
                        wire_decl = ''
                                
                        for wire in ws:          # replace existing names with new ones
                            new_body = new_body.replace(f' {wire};', f' _{wire}_;')
                            new_body = new_body.replace(f' {wire} ', f' _{wire}_ ')
                            new_body = new_body.replace(f'({wire})', f'(_{wire}_)')
                            new_body = new_body.replace(f'({wire}[', f'(_{wire}_[')
                            new_body = new_body.replace(f'({wire} ', f'(_{wire}_ ')
                            
                            if (types[wire] == 'o'):            # instantiate PIs and POs
                                primary_io += f'  pout '
                                wire_decl += '  output '
                                if (sizes[wire] > 0):
                                    primary_io += f'#({sizes[wire]}) '
                                    wire_decl += f'[{sizes[wire]-1}:0] '
                                primary_io += f'_POUT_{wire} (.in(_{wire}_), .out({wire}));\n'
                                wire_decl += f'{wire};\n'
                                    
                            if (types[wire] == 'i'):
                                primary_io += f'  pin '
                                wire_decl += '  input '
                                if (sizes[wire] > 0):
                                    primary_io += f'#({sizes[wire]}) '
                                    wire_decl += f'[{sizes[wire]-1}:0] '
                                primary_io += f'_PIN_{wire} (.in({wire}), .out(_{wire}_));\n'
                                wire_decl += f'{wire};\n'

                        new_body = f'\n\n{wire_decl}{new_body}\n{primary_io}\n'

                        data2 = data2.replace(module_body, new_body)
            return data2


        def wirenamefix (data2):
            lines = data2.split('\n')

            sub_comp = []
            bare_wire = []
            dot_wire = []
            
            for l in lines:
                if (l.find(' wire ') > -1):
                    tokens = l.split()
                    for token in tokens:
                        if (token.find('\\') > -1):
                            sub_comp.append(cleanname(token[1:]))
                        elif (token.find('_') > -1):
                            if (token[0] != '_'):
                                bare_wire.append(cleanname(token))
                            else:
                                dot_wire.append(cleanname(token))

            sub_comp.sort(reverse=True)
            bare_wire.sort(reverse=True)
            dot_wire.sort(reverse=True)


            
            for wire in sub_comp:
                sane = sanitize(wire)
                new_name = f'_{sane}_'
                data2 = data2.replace(f'\\{wire}', f'{new_name}')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{sane}#')

            for wire in dot_wire:
                sane = sanitize(wire)
                new_name = sane
                data2 = data2.replace(f'{wire}', f'{sane}')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{wire} : {sane} : {new_name}')

            for wire in bare_wire:
                sane = sanitize(wire)
                new_name = f'_{sane}_'
                data2 = data2.replace(f'{wire}', f'_{sane}_')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{sane}#')

            return data2

        def wiredictgen (data2):
            global wire_sizes
            lines = data2.split('\n')

            for l in lines:
                if (l.find(' wire ') != -1) or (l.find(' input ') != -1) or (l.find(' output ') != -1):
                    token = l.split()
                    if (token[0] == '//'):
                        token = token[1:]
                    wname = ''
                    wsize = 1
                    if (token[1][0] == '['):
                        tok = token[1]
                        tok = tok[1:len(tok)-3]
                        wname = token[2].replace(';', '')
                        wsize = int(tok) + 1
                        #print(f'{wname}:{wsize}')
                    else:
                        wname = token[1].replace(';', '')
                        #print(f'{wname}:1')
                    wire_sizes[wname] = wsize
                    #if (token[0] != 'wire'):
                    #    print(f'size({wname}) = {wsize}')
                    #print(wname)

        def assignfix (data2):
            global wire_sizes
            lines = data2.split('\n')
            assign_num = 0
            content_out = ''
            for line in lines:
                if (line.find('assign') > -1):
                    #print(line)
                    tokens = line.split()
                    if (len(tokens) == 4) or (len(tokens) == 5):              # The only sizes that are currently supported
                        assign_num += 1
                        wire1 = f'{tokens[1]}'
                        wire2 = f'{tokens[3].replace(";", "")}'
                        line = ''
                        #print(f'{wire1} <= {wire2}')
                        if (wire_sizes[wire1] > 1):
                            #print (wire_sizes[wire])
                            for i in range(wire_sizes[wire1]):
                                line += f'\n  bufg _ASSIGN_{assign_num}_{i}_ ({wire1}[{i}], {wire2}[{i}]);'
                        else:
                            #print('-1')
                            line = f'  bufg _ASSIGN_{assign_num}_ ({wire1}, {wire2});'
                            
                content_out += f'{line}\n'
            return content_out



        def remove_io_duplicates (data2):
            global io_duplicates
            io_duplicates = list(dict.fromkeys(io_duplicates))      # not necessary; just for optimizing running time
            for io in io_duplicates:
                query = f'wire (([\[[0-9:0-9\]])+ )*_{io}_(\s)*;'
                count = len(re.findall(query, data2))
                #print(f'#{query}# : #{count}#')
                if (count > 1):
                    data2 = re.sub(query, '', data2, count - 1)
                    #print(f'#{query}#')
            return data2




        def fix (data2):
            #global wire_sizes
            data2 = clear_pios(data2)
            if (data2.find("/// portfix = 1") == -1):
                data2 = f'/// portfix = 1\n' + portfix(data2)
            if (data2.find("/// wirenamefix = 1") == -1):
                data2 = f'/// wirenamefix = 1\n' + wirenamefix(data2)
            if (data2.find("/// assignfix = 1") == -1):
                wiredictgen(data2)
                #print (f'{wire_sizes}')
                data2 = f'/// assignfix = 1\n' + assignfix(data2)
            data2 = remove_io_duplicates(data2)
            return data2


        def between_par (instr):
            return instr[instr.find('(')+1 : instr.find(')')]

        def generic_fix (data3, search_for, replace_with):
            lines = data3.split('\n')
            replace_flag = False
            outlines = ''
            A_param = ''
            B_param = ''
            for line in lines:
                if (re.search(f'( |\\t){search_for}(\\t| )', line) != None):
                    line = line.replace(search_for, f'{replace_with} #(2, 0, 0)')
                    outlines += line + '\n'
                    replace_flag = True
                elif replace_flag == True:
                    if (line.find('.A') != -1):
                        A_param = between_par(line)
                    elif (line.find('.B(') != -1):
                        B_param = between_par(line)
                        outlines += f'    .in({{{A_param}, {B_param}}}),\n'
                    else:
                        outlines += line.replace('.Y(', '.out(') + '\n'
                        replace_flag = False
                else:
                    outlines += line + '\n'
            return outlines
                    


        def GATEhandle (content):
            lines = iter(content.split('\n'))
            modulename = []
            pi = []
            poo = []
            indlst = []
            odlst = []
            inlist = []
            olist = []
            bufl = []
            inand = []
            onand = []
            i1nand = []
            i2nand = []
            o1nand = []
            inor = []
            onor = []
            i1nor = []
            i2nor = []
            o1nor = []
            inot = []
            onot = []
            i1not = []
            o1not = []
            
            for line in lines:
                
                if(line.find('module ') > -1):
                    modulename.append(line) 

                elif(line.find('pin') > -1):
                    pii=line.split("(.")[1]
                    pi.append(pii) 

                elif (line.find('output [') > -1):
                    poo.append(line) 

                elif (line.find('.D(') > -1):
                    indlst.append(line) 

                elif(line.find('.Q(') > -1):
                    odlst.append(line) 

                elif (line.find('bufg') > -1):
                    bufl.append(line) 
                
                elif (line.find('nand_n') > -1):
                    next_l = next(lines)
                    next_ll = next(lines)
                    inand.append(next_l)
                    onand.append(next_ll)

                elif (line.find('nor_n') > -1):
                    next_l = next(lines)
                    next_ll = next(lines)
                    inor.append(next_l)
                    onor.append(next_ll)

                elif (line.find('NOT') > -1):
                    next_l = next(lines)
                    next_ll = next(lines)
                    inot.append(next_l)
                    onot.append(next_ll)


            for i in modulename:
                y = i.split("(")[0]
                modulname = y[y.find(" ")+1:y.find("(")]
                outfile.write('Bench file of module  ' + modulname + '\n\n')
                


            for i in pi: 
                y = i.split(", ")[0]
                inp = y[y.find("in")+3:y.find("),")]
                outfile.write('INPUT ('+ inp +')\n') 

        
            for i in poo:
                x = i.split("]")[0]
                sizeo = x[x.find("[")+1:x.find(":")]
                y = i.split("]")[1]
                nameo = y[y.find(" ")+1:y.find(";")]
                for i in range(0,int(sizeo)+1):
                    sze = int(sizeo) - i
                    szee = str(sze)
                    outfile.write('OUTPUT (_' + nameo + '_'+ szee +')\n')
        
                
            for i in indlst: 
                x = i.split("(")[1]
                indff = x[x.find("(")+1:x.find("),")]
                inlist.append(indff)

            for j in odlst:
                y = j.split("(")[1]
                outdff = y[y.find(".Q")+1:y.find(")")]
                olist.append(outdff)

            for i in range(len(olist)):
                outfile.write(olist[i] + ' = DFF(' + inlist[i] + ')\n') 



            for i in bufl:
                x = i.split(",")[0]
                y = i.split(",")[1]
                outbuf = x[x.find(".out(")+5:x.find("),")]
                inbuf = y[y.find(".in(")+4:y.find("));")]
                outfile.write(outbuf + ' = BUF(' + inbuf + ')\n')

            for i in inand:
                x = i.split(",")[0]
                y = i.split(",")[1]
                in1 = x[x.find("{")+1:]
                in2 = y[:y.find("})")]
                i1nand.append(in1)
                i2nand.append(in2)

            for i in onand:
                x = i.split("(")[1]
                o1 = x[:x.find(")")]
                o1nand.append(o1)

            for i in range(len(onand)):
                outfile.write(o1nand[i] + ' = NAND(' + i1nand[i] + ',' + i2nand[i] + ')\n') 

            for i in inor:
                x = i.split(",")[0]
                y = i.split(",")[1]
                in1 = x[x.find("{")+1:]
                in2 = y[:y.find("})")]
                i1nor.append(in1)
                i2nor.append(in2)

            for i in onor:
                x = i.split("(")[1]
                o1 = x[:x.find(")")]
                o1nor.append(o1)

            for i in range(len(onor)):
                outfile.write(o1nor[i] + ' = NOR(' + i1nor[i] + ',' + i2nor[i] + ')\n') 

            for i in inot:
                x = i.split("(")[1]
                i1 = x[:x.find("),")]
                i1not.append(i1)

            for i in onot:
                x = i.split("(")[1]
                o1 = x[:x.find(")")]
                o1not.append(o1)
            
            for i in range(len(onot)):
                outfile.write(o1not[i] + ' = NOT(' + i1not[i] +  ')\n') 


        def OPT (Data):
            lines = iter(Data.split('\n'))
            test = []
            test1 = []
            rewrte = []
            olst = []
            ilst = []
            o1lst = []
            i1lst = []
            total =[]
            extrawire = []
            rewrte1 =[]
            check = []

            for line in lines:
                    
                if((line.find('module') > -1) or (line.find('INPUT') > -1)or (line.find('OUTPUT') > -1) ):
                    rewrte.append(line)


                elif((line.find('=') > -1) and (line.find(',') ==-1)) :
                    test.append(line)
                    rewrte1.append(line)

                elif((line.find('=') > -1) and (line.find(',') >-1)) :
                    test1.append(line) 
                    rewrte1.append(line)



            for i in rewrte:    
                outf.write(i + '\n')

            for i in test:
                x = i.split("=")[0]
                y = i.split("=")[1]
                in1 = y[y.find("(")+1:y.find(")")]
                o1 = x[:x.find(" ")]
                olst.append(o1)
                ilst.append(in1)
                
            
            for i in test1:
                x = i.split("=")[0]
                y = i.split("=")[1] 
                in1 = y[y.find("(")+1:y.find(",")]   
                in2 = y[y.find(", ")+2:y.find(")")] 
                o1 = x[:x.find(" ")] 
                o1lst.append(o1)
                i1lst.append(in1)
                i1lst.append(in2)

            for i in ilst:
                i1lst.append(i)

            for i in olst:
                o1lst.append(i)
                        
            for x in o1lst:
                if i1lst.count(x) == 0: 
                    extrawire.append(x)
                    check.append(x)


            for i in test:
                x = i.split("=")[0]
                y = i.split("=")[1]
                in1 = y[y.find("(")+1:y.find(")")]
                o1 = x[:x.find(" ")]

                if ((extrawire.count(o1) >0) & (i1lst.count(in1) <= 1)) :

                    check.append(in1)

            for i in test1:
                x = i.split("=")[0]
                y = i.split("=")[1] 
                in1 = y[y.find("(")+1:y.find(",")]   
                in2 = y[y.find(", ")+2:y.find(")")] 
                o1 = x[:x.find(" ")] 

                if ((extrawire.count(o1) >0) & (i1lst.count(in1) <= 1)) :

                    check.append(in1)

                elif ((extrawire.count(o1) >0) & (i1lst.count(in2) <= 1)) :

                    check.append(in2)

            for j in rewrte1:
                x = j.split("=")[0]
                o1 = x[:x.find(" ")]
                    
                if (check.count(o1) == 0) :
                        
                    outf.write(j + '\n')

        print("Hello! I will generate a bench file from your file if you want to enter your file name :-)")
        name = input("file name >>")
        inpp = open(name, "r")
        outpp = open("bench1.txt", "w")

        daata = inpp.read()

        wiredictgen(daata)

        fixed = assign_fix(daata)
        outpp.write(fixed)

        inpp.close()
        outpp.close()


        inf2 = open("bench1.txt", "r")
        outf2 = open("bench2.txt", "w")

        data2 = inf2.read()
        data2 = fix(data2)
        outf2.write(data2)

        inf2.close()
        outf2.close()



        inf3 = open("bench2.txt", 'r')
        outf3 = open("bench3.txt", 'w')

        data3 = inf3.read()
        data3 = generic_fix(data3, 'NAND', 'nand_n')
        data3 = generic_fix(data3, 'NOR', 'nor_n')
        outf3.write(data3)

        inf3.close()
        outf3.close()


        infile = open('bench3.txt', 'r')
        outfile = open('bench4.txt', 'w')

        content = infile.read()
        content = GATEhandle(content)

        infile.close()
        outfile.close()


        inf = open('bench4.txt', 'r')
        outf = open('bench5.txt', 'w')

        Data = inf.read()
        Data = OPT(Data)
        outf.write('END') 

        inf.close()
        outf.close()


        inff = open('bench5.txt', 'r')
        outff = open('out.bench', 'w')

        dataa = inff.read()
        dataa = dataa.replace("]", "")
        dataa = dataa.replace("[", "")
        outff.write(dataa)

        inff.close()
        outff.close()

        os.remove("bench1.txt")
        os.remove("bench2.txt")
        os.remove("bench3.txt")
        os.remove("bench4.txt")
        os.remove("bench5.txt")

######################################################################################################################

def netlist():
        def wiredictgen (daata):
            global wire_sizes
            lines = daata.split('\n')

            for l in lines:
                if (l.find(' wire ') != -1) or (l.find(' input ') != -1) or (l.find(' output ') != -1):
                    token = l.split()
                    if (token[0] == '//'):
                        token = token[1:]
                    wname = ''
                    wsize = 1
                    if (token[1][0] == '['):
                        tok = token[1]
                        tok = tok[1:len(tok)-3]
                        wname = token[2].replace(';', '')
                        wsize = int(tok) + 1
                        #print(f'{wname}:{wsize}')
                    else:
                        wname = token[1].replace(';', '')
                        #print(f'{wname}:1')
                    wire_sizes[wname] = wsize



        def queue_up(daata):
            element_queue = []
            if(daata.find("{")!= -1):
                daata = daata[daata.find("{")+1 : daata.find("}")]
                tokens = daata.split(",")
                for token in tokens:
                    if(token.find("[") != -1 ):
                        if(token.find(":") != -1):
                            wire_name = token[:token.find("[")]
                            end = int(token[token.find("[")+1:token.find("]")].split(":")[0])
                            start = int(token[token.find("[")+1:token.find("]")].split(":")[1])
                            for i in range(end , start-1 , -1 ):
                                element_queue.append(f'{wire_name}[{i}]')
                        else:
                            element_queue.append(token)
                    elif (token.find("'b")!= -1):
                        bits = token.split("b")[1]
                        for bit in bits:
                            element_queue.append(bit)
                    else:
                        wire_name = token
                        #check if its multiple or signle
                        if(wire_sizes[wire_name] > 1):
                            for i in range(wire_sizes[wire_name]-1 , -1 , -1) :
                                element_queue.append(f'{wire_name}[{i}]')
                        else:
                            element_queue.append(f'{wire_name}')
            else:
                if(daata.find("[") != -1 ):
                    if(daata.find(":")!= -1):
                        wire_name = daata[:daata.find("[")]
                        end = int(daata[daata.find("[")+1:daata.find("]")].split(":")[0])
                        start = int(daata[daata.find("[")+1:daata.find("]")].split(":")[1])
                        for i in range(end , start-1 , -1):
                            element_queue.append(f'{wire_name}[{i}]')
                    else:
                        element_queue.append(daata)
                elif (daata.find("'b")!= -1):
                    bits = daata.split("b")[1]
                    for bit in bits:
                        element_queue.append(bit)
                else:
                    wire_name = daata
                    #check if its multiple or signle
                    if(wire_sizes[wire_name] > 1):
                        for i in range(wire_sizes[wire_name]-1 , -1 , -1) :
                            element_queue.append(f'{wire_name}[{i}]')
                    else:
                        element_queue.append(f'{wire_name}')

            return element_queue

        def generate_sub(lhs_queue , rhs_queue):
            global assign_num
            new_lines = ""
            assign_num += 1
            for i in range(len(lhs_queue)):
                wire1 = lhs_queue[i]
                wire2 = rhs_queue[i]
                if(wire2[0].isdigit()):
                    new_lines = new_lines + f"\nbufg _ASSIGN_{assign_num}_{i}_ (.out({wire1}),.in(1'b{wire2}));"    
                else:
                    new_lines = new_lines + f'\nbufg _ASSIGN_{assign_num}_{i}_ (.out({wire1}),.in({wire2}));'
            return new_lines

        def assign_fix(daata):
            global wire_sizes
            lines = daata.split('\n')
            for i in range(len(lines)):
                l = lines[i]
                if (l.find('assign') != -1 ):
                    text = l[l.find('assign') + len("assign")+1:]
                    text = text.replace(" " , "")
                    text = text[:text.find(";")]
                    lhs = text.split("=")[0]
                    rhs = text.split("=")[1]
                    lhs_queue = queue_up(lhs)
                    rhs_queue = queue_up(rhs)
                    newlines = generate_sub(lhs_queue , rhs_queue)
                    lines[i] = newlines[1:]
            return "\n".join(lines)




        def sanitize (cname):
            #buf = cname
            cname = cname.replace(".", "_")
            cname = cname.replace(" ", "_")
            #print(f'{buf} : {cname}')
            return cname

        def cleanname (cname):
            return cname.replace(';', '').replace(')', '').replace('(', '')

        def space_fix(data2, new_name):
            data2 = data2.replace(f'{new_name} [', f'{new_name}[')
            data2 = data2.replace(f'{new_name} )', f'{new_name})')
            data2 = data2.replace(f'{new_name} (', f'{new_name}(')
            data2 = data2.replace(f'{new_name} ;', f'{new_name};')
            return data2

        def clear_pios (data2):
            lines = data2.split('\n')
            outline = ''
            for line in lines:
                if (line.find(' pin ') == -1) and (line.find(' pout ') == -1):
                    outline += line + '\n'
            return outline

        def nametop(data2):
            global top  
            lines = data2.split('\n')
            modulename = []
            
            for line in lines:       
                if(line.find('module ') > -1):
                    modulename.append(line) 
            for i in modulename:
                y = i.split("(")[0]
                top = y[y.find(" ")+1:]
                
            return top



        def portfix (data2):
            global top_module, io_duplicates
        
            nametop(data2)  
            top_module = top
        
            pos = 0

            while pos > -1:
                pos = data2.find("module", pos+1)
                pos2 = data2.find(";", pos)

                if (pos > 0) and (pos2 > 0):
                    #par1 = data2.find('(', pos)
                    par1 = pos
                    par2 = data2.find(')', pos)
                    #print(f'{par1}:{par2}')
                    cstr = data2[par1+1:par2]
                    cstr = cstr.replace('(', ',')
                    wires = cstr.split(',')
                    wires[0] = wires[0][wires[0].find(' ')+1:]

                    
                    if (wires[0] == top_module):            # we have the IOs' list
                        wires = wires[1:]
                        sizes = {}
                        types = {}
                        ws = []
                        for wire in wires:
                            ws.append(wire.strip())
                        pos = data2.find('endmodule', pos)
                        module_body = data2[pos2+1:pos]
                        lines = module_body.split('\n')     # scan each line for i/o and length declarations

                        new_body = ''
                        
                        for line in lines:
                            size = 0
                            io = ''
                            if (line.find(' input') > -1):   #input!
                                io = 'i'
                            if (line.find(' output') > -1):   #output
                                io = 'o'
                            if (io != ''):
                                if (line.find('[') > -1):       #array
                                    size = int(line[line.find('[')+1:line.find(':')]) + 1
                                token = line[line.rfind(' ')+1 : len(line)-1].strip()
                                sizes[token] = size
                                types[token] = io
                                if (io == 'i'):         # change old I/Os to wires
                                    line = line.replace(' input', ' wire')
                                    io_duplicates.append(token)
                                else:
                                    line = line.replace(' output', ' wire')
                                    io_duplicates.append(token)
                                if (token == ''):
                                    print(f'${line}$')
                        
                            new_body += f'{line}\n'

                        # now we know the type and size of each wire
                        primary_io = ''
                        wire_decl = ''
                                
                        for wire in ws:          # replace existing names with new ones
                            new_body = new_body.replace(f' {wire};', f' _{wire}_;')
                            new_body = new_body.replace(f' {wire} ', f' _{wire}_ ')
                            new_body = new_body.replace(f'({wire})', f'(_{wire}_)')
                            new_body = new_body.replace(f'({wire}[', f'(_{wire}_[')
                            new_body = new_body.replace(f'({wire} ', f'(_{wire}_ ')
                            
                            if (types[wire] == 'o'):            # instantiate PIs and POs
                                primary_io += f'  pout '
                                wire_decl += '  output '
                                if (sizes[wire] > 0):
                                    primary_io += f'#({sizes[wire]}) '
                                    wire_decl += f'[{sizes[wire]-1}:0] '
                                primary_io += f'_POUT_{wire} (.in(_{wire}_), .out({wire}));\n'
                                wire_decl += f'{wire};\n'
                                    
                            if (types[wire] == 'i'):
                                primary_io += f'  pin '
                                wire_decl += '  input '
                                if (sizes[wire] > 0):
                                    primary_io += f'#({sizes[wire]}) '
                                    wire_decl += f'[{sizes[wire]-1}:0] '
                                primary_io += f'_PIN_{wire} (.in({wire}), .out(_{wire}_));\n'
                                wire_decl += f'{wire};\n'

                        new_body = f'\n\n{wire_decl}{new_body}\n{primary_io}\n'

                        data2 = data2.replace(module_body, new_body)
            return data2


        def wirenamefix (data2):
            lines = data2.split('\n')

            sub_comp = []
            bare_wire = []
            dot_wire = []
            
            for l in lines:
                if (l.find(' wire ') > -1):
                    tokens = l.split()
                    for token in tokens:
                        if (token.find('\\') > -1):
                            sub_comp.append(cleanname(token[1:]))
                        elif (token.find('_') > -1):
                            if (token[0] != '_'):
                                bare_wire.append(cleanname(token))
                            else:
                                dot_wire.append(cleanname(token))

            sub_comp.sort(reverse=True)
            bare_wire.sort(reverse=True)
            dot_wire.sort(reverse=True)


            
            for wire in sub_comp:
                sane = sanitize(wire)
                new_name = f'_{sane}_'
                data2 = data2.replace(f'\\{wire}', f'{new_name}')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{sane}#')

            for wire in dot_wire:
                sane = sanitize(wire)
                new_name = sane
                data2 = data2.replace(f'{wire}', f'{sane}')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{wire} : {sane} : {new_name}')

            for wire in bare_wire:
                sane = sanitize(wire)
                new_name = f'_{sane}_'
                data2 = data2.replace(f'{wire}', f'_{sane}_')
                data2 = space_fix(data2, new_name)
                #if wire[0] == '_':
                #    print(f'wire: {wire}')
                #print(f'{sane}#')

            return data2

        def wiredictgen (data2):
            global wire_sizes
            lines = data2.split('\n')

            for l in lines:
                if (l.find(' wire ') != -1) or (l.find(' input ') != -1) or (l.find(' output ') != -1):
                    token = l.split()
                    if (token[0] == '//'):
                        token = token[1:]
                    wname = ''
                    wsize = 1
                    if (token[1][0] == '['):
                        tok = token[1]
                        tok = tok[1:len(tok)-3]
                        wname = token[2].replace(';', '')
                        wsize = int(tok) + 1
                        #print(f'{wname}:{wsize}')
                    else:
                        wname = token[1].replace(';', '')
                        #print(f'{wname}:1')
                    wire_sizes[wname] = wsize
                    #if (token[0] != 'wire'):
                    #    print(f'size({wname}) = {wsize}')
                    #print(wname)

        def assignfix (data2):
            global wire_sizes
            lines = data2.split('\n')
            assign_num = 0
            content_out = ''
            for line in lines:
                if (line.find('assign') > -1):
                    #print(line)
                    tokens = line.split()
                    if (len(tokens) == 4) or (len(tokens) == 5):              # The only sizes that are currently supported
                        assign_num += 1
                        wire1 = f'{tokens[1]}'
                        wire2 = f'{tokens[3].replace(";", "")}'
                        line = ''
                        #print(f'{wire1} <= {wire2}')
                        if (wire_sizes[wire1] > 1):
                            #print (wire_sizes[wire])
                            for i in range(wire_sizes[wire1]):
                                line += f'\n  bufg _ASSIGN_{assign_num}_{i}_ ({wire1}[{i}], {wire2}[{i}]);'
                        else:
                            #print('-1')
                            line = f'  bufg _ASSIGN_{assign_num}_ ({wire1}, {wire2});'
                            
                content_out += f'{line}\n'
            return content_out



        def remove_io_duplicates (data2):
            global io_duplicates
            io_duplicates = list(dict.fromkeys(io_duplicates))      # not necessary; just for optimizing running time
            for io in io_duplicates:
                query = f'wire (([\[[0-9:0-9\]])+ )*_{io}_(\s)*;'
                count = len(re.findall(query, data2))
                #print(f'#{query}# : #{count}#')
                if (count > 1):
                    data2 = re.sub(query, '', data2, count - 1)
                    #print(f'#{query}#')
            return data2




        def fix (data2):
            #global wire_sizes
            data2 = clear_pios(data2)
            if (data2.find("/// portfix = 1") == -1):
                data2 = f'/// portfix = 1\n' + portfix(data2)
            if (data2.find("/// wirenamefix = 1") == -1):
                data2 = f'/// wirenamefix = 1\n' + wirenamefix(data2)
            if (data2.find("/// assignfix = 1") == -1):
                wiredictgen(data2)
                #print (f'{wire_sizes}')
                data2 = f'/// assignfix = 1\n' + assignfix(data2)
            data2 = remove_io_duplicates(data2)
            return data2

        def between_par (instr):
            return instr[instr.find('(')+1 : instr.find(')')]

        def generic_fix (datad, search_for, replace_with):
            lines = datad.split('\n')
            replace_flag = False
            outlines = ''
            A_param = ''
            B_param = ''
            for line in lines:
                if (re.search(f'( |\\t){search_for}(\\t| )', line) != None):
                    line = line.replace(search_for, f'{replace_with} #(2, 0, 0)')
                    outlines += line + '\n'
                    replace_flag = True
                elif replace_flag == True:
                    if (line.find('.A') != -1):
                        A_param = between_par(line)
                    elif (line.find('.B(') != -1):
                        B_param = between_par(line)
                        outlines += f'    .in({{{A_param}, {B_param}}}),\n'
                    else:
                        outlines += line.replace('.Y(', '.out(') + '\n'
                        replace_flag = False
                else:
                    outlines += line + '\n'
            return outlines

        def parse_wire(file_path):
            r_page = open(file_path, 'r')
            for line in r_page:
                if (re.search("^wire", line.strip()) != None):
                    size = 0
                    i = line.find("_")
                    j = line.find(";", i + 1)
                    
                    # check whether its an array or single_ports
                    if (line.find("[")) > -1:
                        #  brac = n.find("[")
                        #  end = n.find(";", brac)
                        size = int(line[line.find('[')+1:line.find(':')]) + 1
                        for indx in range(size):
                            ports.append(line[i:j] + "[" + str(indx) + "]")
                    else:
                        ports.append(line[i:j])
            r_page.close()


        def find_fanout(file_path):
            nop = 0
            r_page = open(file_path, 'r')
            temp_page = r_page.read()
            r_page.close()

            for port in ports:
                if (port != "" and port != " "):
                    # print(page.read().count("wire " + port.strip()))
                    if (port.find("[") > -1):
                        # because mulriports wire doesn`t delare explicitly we increment nop by 1
                        nop = (temp_page.count(port.strip())) + 1
                    else:
                        nop = len(re.findall(r"\b" + port, temp_page))

                    if ( nop > 3 ):
                        single_fanout.update({port:nop}) 

                # if (port.find("[") > -1):
                #     bpi = port.find("[")
                #     input_temp1 = port[:bpi]
                #     if ( input_ports.count(input_temp1.strip()) != 0):
                #         if (temp_page.count(port.strip()) == 2):
                #             single_fanout.update({port:3}) 
                
                


        def inputfinder(file_path, input_ports):
            r_page = open(file_path, "r")
            temp_page = r_page.read()
            r_page.close()

            # parse file into lines
            lines = temp_page.splitlines()

            # look for inputs and put them in a list
            for line in lines:
                if (re.search("^input", line.strip()) != None):
                        if (line.find("]") > -1):
                                i = line.find("]") + 2
                        else:
                                i = line.find("input") + 1

                        j = line.find(";")
                        inpname = "_" + line[i:j] + "_"
                        input_ports.append(inpname) 

        

        # infect_fanout ; take a list of single fanout, generate 
        #                               extra declaration for each branch  
        #                               fanout declaration
        #                               and write it into file
        def inject_fanout(file_path, single_fanout, synth_res):
            r_page = open(file_path, "r")
            temp_page = r_page.read()
            r_page.close()
            
            # look for last "wire" declararion to parse the text file
            s1 = 0 
            ls = []
            for line in temp_page.splitlines():
                if (line != ""):
                    if (re.search("^wire", line.strip()) != None):
                        s1 = 1
                    if ((re.search("^wire", line.strip()) == None) and (s1 == 1)):
                        ls = temp_page.split(line, 1)
                        temp_page = ls[0]
                        ls[1] = line + ls[1]
                        break
            
            i = 0
            # for each fanout candidate write a fanout declararion
            for sf_key, sf_value in single_fanout.items(): 
                # if (re.search("\[", sf_key) != None):
                #     temp_page += "wire " + sf_key + ";\n"
                # print(sf_key, sf_value)
                if (re.search("\[", sf_key) != None):
                    # remove brackets and iterate over indexes
                    bp = sf_key.find("[")
                    bp2 = sf_key.find("]")
                    wname = sf_key[:bp] + sf_key[bp + 1:bp2]
                    
                    input_temp = sf_key[:bp]
                    if ( input_ports.count(input_temp.strip()) != 0):
                        NoIter = sf_value - 1
                    else:
                        NoIter = sf_value - 2
                else:
                    wname = sf_key
                    NoIter = sf_value - 2
                # print(wname)
                # print(NoIter)
                # write stem
                fan_instance = "fanout_n #(" + str(NoIter) + ", 0,0) FANOUT_" + str(i) + " (" + sf_key + ", {"
                

                
                # write branches in regard to number of iteration
                for sfk in range(NoIter):
                    # check if it`s multiport or not and assign a name accordingly
                    wire_name = "wire " + wname + str(sfk) + ";\n"
                    temp_page += wire_name
                    fan_instance += wname + str(sfk) 
                    if (sfk != (NoIter - 1)):
                        fan_instance += ", "

                fan_instance += "});\n"
                temp_page += fan_instance
                i += 1
            
            # atach endmodule
            temp_page += ls[1]
            
            # write back to file
            w_page = open(synth_res, "w")
            w_page.write(temp_page)
            w_page.close()


        # replace_fanout ; find only branches and assign a new name accordingly
        def replace_fanout(synth_res):

            r_page = open(synth_res, "r")
            page_parsed2line = r_page.read().splitlines(keepends=True)
            for sf_key in single_fanout:
                if (sf_key != ""):
                    # search line by line
                    i = 0
                    for line in page_parsed2line:
                        if (line.find(sf_key) > -1):
                            if (re.search("^wire", line.strip()) == None):
                                if (re.search("^fanout_n", line.strip()) == None):
                                    if (re.search("Y|Q", line.strip()) == None):  
                                        if (re.search("out", line.strip()) == None):  
                                            # at this point we know that this is one of branches (which one of them, we don`t care)
                                            #       and its also input (not output)
                                            # so all we have to do is to find 
                                            if (re.search("\[", sf_key) != None):
                                                bp = sf_key.find("[")
                                                bp2 = sf_key.find("]")
                                                wname = sf_key[:bp] + sf_key[bp + 1:bp2]
                                            else:
                                                wname = sf_key
                                            newline = line.replace(sf_key, (wname + str(i)))
                                            page_parsed2line[page_parsed2line.index(line)] = newline

                                            i += 1
            
            # file handling
            page = "".join(page_parsed2line)
            # print(page)
            r_page.close()
            w_page = open(synth_res, "w")
            w_page.write(page)
            w_page.close()



        def Not_Resolve(file_path):
            r_page = open(file_path, "r")
            tpage = r_page.read()
            r_page.close()

            lines = tpage.splitlines(keepends=True)
            for line in lines:
                    if (re.search("^NOT", line.strip()) != None):
                            indx = lines.index(line)
                            newline1 = line.replace("NOT", "notg #(0, 0)")
                            newline2 = lines[indx + 1].replace(".A", ".in")
                            newline3 = lines[indx + 2].replace(".Y", ".out")
                            
                            lines[indx] = newline1
                            lines[indx + 1] = newline2
                            lines[indx + 2] = newline3
            
            # file handling
            page = "".join(lines)
            
            w_page = open(file_path, "w")
            w_page.write(page)
            w_page.close()


        def DFF_Resolve(file_path):
            r_page = open(file_path, "r")
            tpage = r_page.read()
            r_page.close()

            lines = tpage.splitlines(keepends=True)
            for line in lines:
                    if (re.search("^DFF", line.strip()) != None):
                            indx = lines.index(line)
                            newline1 = line.replace("DFF", "dff")
                            newline1 += "    .CLR(1'b0), .PRE(1'b0), .CE(1'b1), .NbarT(NbarT), .Si(Si), .global_reset(1'b0),\n"

                            lines[indx] = newline1
            
            # file handling
            page = "".join(lines)
            
            w_page = open(file_path, "w")
            w_page.write(page)
            w_page.close()

        print("Hello! I will generate a netlist file from your file if you want to enter your file name :-) ")
        name = input("file name >>")   
        inpp = open(name, "r")
        outpp = open("netlist1.txt", "w")

        daata = inpp.read()

        wiredictgen(daata)

        fixed = assign_fix(daata)
        outpp.write(fixed)

        inpp.close()
        outpp.close()


        inf2 = open("netlist1.txt", "r")
        outf2 = open("netlist2.txt", "w")

        data2 = inf2.read()
        data2 = fix(data2)
        outf2.write(data2)

        inf2.close()
        outf2.close()


        inf3 = open("netlist2.txt", 'r')
        outf3 = open("netlist3.txt", 'w')

        datad = inf3.read()
        datad = generic_fix(datad, 'NAND', 'nand_n')
        datad = generic_fix(datad, 'NOR', 'nor_n')
        outf3.write(datad)

        inf3.close()
        outf3.close()

        parse_wire("netlist3.txt")

        inputfinder("netlist3.txt", input_ports)

        find_fanout("netlist3.txt")


        inject_fanout("netlist3.txt", single_fanout, "netlist.v")

        replace_fanout("netlist.v")

        Not_Resolve("netlist.v")

        DFF_Resolve("netlist.v")

        os.remove("netlist1.txt")
        os.remove("netlist2.txt")
        os.remove("netlist3.txt")

print("//////////////////////////////////////////////////////////////////////////////////////////////////////////////")
print("//                                                                                                          //")
print("//                                                                                                          //")
print("// developed by Sepideh Fahiman , bachelor student of Computer engineering at University of Tehran          //")
print("//                                                                                                          //")
print("//              *** under the supervision of professor Zainalabedin Navabi Shirazi ***                      //")
print("//                                                                                                          //")
print("// special thanks to Mohammad.r Roshanshah , PHD student of Electrical engineering at University of Tehran  //")
print("//                                                                                                          //")
print("//                                                                                                          //")
print("//////////////////////////////////////////////////////////////////////////////////////////////////////////////")
print( "                                                                                              ")
type = input(
             "  What kind of file do you want? bench or netlist? please enter it  :"
             "                                                     "
             " type >>") 
if type == "bench": 
    bench()
    contnue = input("do you want netlist type, too? (y/n) >>")
    if ((contnue == "y")|(contnue == "Y")):
        netlist()
    elif ((contnue == "n")|(contnue == "N")):
        print("  ")
    print(" see you soon! ")

elif type == "netlist": 
    netlist()
    cntnue = input("do you want bench type, too? (y/n) >>")
    if ((cntnue == "y")|(cntnue == "Y")):
        bench()
    elif ((cntnue == "n")|(cntnue == "N")):
        print("  ")
    print(" see you soon! ")