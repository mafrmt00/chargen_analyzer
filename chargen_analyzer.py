#! /usr/bin/python3
#
## @file chargen_analyzer.py
#  A tool to analyze and convert Apple II+ chargen ROMs
#
#  This tool can convert ROM content to adapt it for different connections usen in Apple II+ compatible boards. Further on it can clean up existing ROMs and adapt the to different ROM sizes.
import sys
import argparse
import hashlib

#Command lines for testing

#Display Info about original ROM
sys.argv = ['chargen_analyzer.py', '-i', 'APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin', '-p', 'True', '-n', 'True', '-a', 'True']

#Display Info about original Japanese j-plus ROM
#sys.argv = ['chargen_analyzer.py', '-i', 'Apple II j-plus Video ROM.bin', '-p', 'True', '-n', 'True', '-a', 'True']

#Display Info about Pigfont ROM
#sys.argv = ['chargen_analyzer.py', '-i', 'APPLE II+ - PIG FONT CHARACTER GENERATOR - 2716.bin', '-p', 'True', '-n', 'True', '-a', 'True']

#Display Info about SPACE-81 ROM
#sys.argv = ['chargen_analyzer.py', '-i', 'SPACE-81_CHRGEN.BIN', '-p', 'True', '-m', 'space', '-n', 'True', '-a', 'True']

#Display Info about Unicom ROM
#sys.argv = ['chargen_analyzer.py', '-i', 'Unicom Character.BIN', '-p', 'True', '-m', 'unicom', '-n', 'True', '-a', 'True']
#sys.argv = ['chargen_analyzer.py', '-i', 'Clone3_CHRGEN.BIN', '-p', 'True', '-m', 'unicom', '-n', 'True', '-a', 'True']

#Convert Original ROM to Space-81 with 2716 EPROM
#sys.argv = ['chargen_analyzer.py', '-e', '2716', '-i', 'APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin', '-o', 'APPLE II+ (SPACE-81) - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin', '-m', 'oem', '-g', 'space']

#Convert Original ROM to Unicom with 2732 EPROM
#sys.argv = ['chargen_analyzer.py', '-e', '2732', '-i', 'APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin', '-o', 'APPLE II+ (Unicom) - 7341-0036 - CHARACTER GENERATOR REV7+ - 2732.bin', '-m', 'oem', '-g', 'unicom']

#Display info about generated Unicom ROM
#sys.argv = ['chargen_analyzer.py', '-i', 'APPLE II+ (Unicom) - 7341-0036 - CHARACTER GENERATOR REV7+ - 2732.bin', '-p', 'True', '-m', 'unicom', '-n', 'True']

#Convert the generated Unicom ROM Back to Apple (2716)
#sys.argv = ['chargen_analyzer.py', '-i', 'APPLE II+ (Unicom) - 7341-0036 - CHARACTER GENERATOR REV7+ - 2732.bin', '-p', 'True', '-m', 'unicom', '-d', 'True', '-g', 'oem', '-e', '2716']

#Command Line Argument Parser
ArgumentsParser = argparse.ArgumentParser(description='Apple II character generator ROM conversion tool. Example: chargen_analyzer.py -i "APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin" -p True -n True -a True')
ArgumentsParser.add_argument('-i', '--infile', default='chargen_rom.bin', help='The name of the input file to use.')
ArgumentsParser.add_argument('-o', '--outfile', default='new_chargen_rom.bin', help='The name of the output file to use.')
ArgumentsParser.add_argument('-e', '--eprom', default='2716', choices=['2716','2732','2764'], help='EPROM Type to use for output generation, 2732 contains the same image as 2716 but 2x.')
ArgumentsParser.add_argument('-m', '--inmatrix', default='oem', choices=['oem', 'unicom', 'space'], help='The board type from which the input ROM is taken OEM is Apple.')
ArgumentsParser.add_argument('-g', '--outmatrix', default='oem', choices=['oem', 'unicom', 'space'], help='The board type for which the ROM image is generated OEM is Apple.')
ArgumentsParser.add_argument('-p', '--printinfo', default='False', choices=['True', 'False'], help='Print out info about the ROM.')
ArgumentsParser.add_argument('-a', '--printascii', default='False', choices=['True', 'False'], help='When printing is enabled, ASCII art for the charsets will be added.')
ArgumentsParser.add_argument('-n', '--nooutfile', default='False', choices=['True', 'False'], help='Do not write a ROM file to disk.')
ArgumentsParser.add_argument('-d', '--dl6', default='False', choices=['True', 'False'], help='Set the Flashenable for every second charset, so that DL6 is transparent to O7.')

args = ArgumentsParser.parse_args()

## Input Matrix straight, as used by Apple
#
# 0b10000000 Q7  Flash Enable From ROM
# 0b01000000 Q6 (H) Usually empty
# 0b00100000 Q5 (G) Left Dot of 5x7
# 0b00010000 Q4 (F)
# 0b00001000 Q3 (E)
# 0b00000100 Q2 (D)
# 0b00000010 Q1 (C) Right Dot of 5x7
# 0b00000001 Q0 (B) Usually empty
InputMatrixRegular =[0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

## Input Matrix for the Unicom board.
#
# 0b00000000 Q7  Flash Enable From ROM (Not used with this board)
# 0b00000010 Q1 (H) Usually empty
# 0b00001000 Q3 (G) Left Dot of 5x7
# 0b00010000 Q4 (F)
# 0b00100000 Q5 (E)
# 0b01000000 Q6 (D)
# 0b10000000 Q7 (C) Right Dot of 5x7
# 0b00000100 Q2 (B) Usually empty
InputMatrixUnicom =[0b00000100, 0b10000000, 0b01000000, 0b00100000, 0b00010000, 0b00001000, 0b00000010, 0b00000000]

## Input Matrix for the SPACE-81 board.
#
# 0b01000000 Q7  Flash Enable From ROM
# 0b10000000 Q6 (H) Usually empty
# 0b00010000 Q5 (G) Left Dot of 5x7
# 0b00001000 Q4 (F)
# 0b00000100 Q3 (E)
# 0b00000010 Q2 (D)
# 0b00000001 Q1 (C) Right Dot of 5x7
# 0b00100000 Q0 (B) Usually empty
InputMatrixSpace81 =[0b00100000, 0b00000001, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b10000000, 0b01000000]

#Input / Output filenames
InputFile  = args.infile
OutputFile = args.outfile

print ('Input File is: ', end='')
print (InputFile)


#Process Flash Flag
if (args.dl6 == 'True'):
    ProcessFlashFlag = True
    print('Seting the Flashenable for every second charset, so that DL6 is transparent to O7.')
else:
    ProcessFlashFlag = False
    print('Flashenable remains untouched.')

#Write file or not
if (args.nooutfile == 'True'):
    WriteOutputDisk = False
    print ('Not writing a ROM file to disk.')
else:
    WriteOutputDisk = True
    print ('Writing a ROM file to disk.')
    print ('Output File is: ', end='')
    print (OutputFile)

#Print out info or not
if (args.printinfo == 'True'):
    PrintROMinfo = True
else:
    PrintROMinfo = False

#Prinst charsets as ASCII art
if (args.printascii == 'True'):
    PrintASCIIart = True
    print('ASCII art for the charsets will be added.')
else:
    PrintASCIIart = False
    print('No ASCII art for the charsets will be added.')


#Conversion Matrix
print ('Input ROM image type is ', end='')
if ('oem' == args.inmatrix):
    print('Apple.')
    InputMatrix = bytearray(InputMatrixRegular)
elif ('unicom' == args.inmatrix):
    print('Unicom.')
    InputMatrix = bytearray(InputMatrixUnicom)
elif ('space' == args.inmatrix):
    print('Space-81.')
    InputMatrix = bytearray(InputMatrixSpace81)    
else:
    print('undefined.')
    InputMatrix = bytearray(InputMatrixRegular)

if (WriteOutputDisk):
    print ('Output ROM image type will be for ', end='')
    if ('oem' == args.outmatrix):
        print('Apple.')
        OutputMatrix = bytearray(InputMatrixRegular)
    elif ('unicom' == args.outmatrix):
        print('Unicom.')
        OutputMatrix = bytearray(InputMatrixUnicom)
    elif ('space' == args.outmatrix):
        print('Space-81.')
        OutputMatrix = bytearray(InputMatrixSpace81)        
    else:
        print('undefined.')
        OutputMatrix = bytearray(InputMatrixRegular)
else:
    OutputMatrix = bytearray(InputMatrixRegular)

#Output file size aka EPROM type
if (WriteOutputDisk):
    print ('Output image fits ', end='')
    if ('2716' == args.eprom):
        OutputFileSize = 2048
        print('2716', end='')
    elif('2732' == args.eprom):
        OutputFileSize = 2048 * 2
        print('2732', end='')
    elif('2764' == args.eprom):
        OutputFileSize = 2048 * 4
        print('2764', end='')
    else:
        OutputFileSize = 2048
        print('2716', end='')
    print('eprom.')
else:
    OutputFileSize = 2048

if (WriteOutputDisk):
    if (ProcessFlashFlag):
        print("DL6 will be adapted to O7.") 

#Charset MD5 hashes for identification
CharsetNames = {"0c98631668c74b15f24f010136f9448c": "regular II+ (7341-0036)",
                "4bc0aa3b9d3cfcbfecca6d94c4db4da0": "3rd party mixed case",
                "0ee3d5d4a08763577a3a5b2dc29fe921": "3rd party uppercase",
                "5262be710df23d19c7f33b632ec9a5d8": "japanese j-plus inverted",
                "31519078d343d10782c16824a0ff6b26": "3rd party uppercase",
                "2b2e231edcb4750e450864f8085c18fd": "3rd party mixed case without numbers",
                "d213ad042f6e9df89c6864c5b71811ee": "pigfont #0 uppercase",
                "9384a2ec5d4e3f03d25198d8e564a9a5": "pigfont #1 uppercase",
                "d5b637ec188daf53856387ed32cff620": "pigfont #2 mixed case without numbers",
                "6a62e905fab1d24335c92362d4fb8050": "3rd party german lower case inverted",
                "6b77b61a454a168a672c08ce03f5988b": "3rd party german mixed case without numbers",
                "c8f3ebcfb4aeb937057fee2bbad4901d": "3rd party german upper case",
                "4a1bcde4f9d86929828235ec5c7d5727": "3rd party german upper case"}

## Invert the given transformation matrix.
#
#  The given matrix is inveted for encoding a norm set.
def InvertTransMatrix(InpMatr):
    Inverted = bytearray(int(len(InpMatr)))
    BytePos = 0
    
    for Byte in InpMatr: #Iterate the Matrix
        for BitPos in range(8): # Get the Set Bit
            if (Byte & (0x01 << BitPos)):
                Inverted[BitPos] = (0x01 << BytePos)

        BytePos += 1
      
    return Inverted

## Generate ASCII Art for one Byte.
#
#  Depending on the VisibleOnly Flag, ASCII Art is created for 5 or for 7 Bits
def ByteToString(x: int, VisibleOnly: bool):

    ReturnString = ''

    DotCount = 0

    if (VisibleOnly):
        displaymatrix = bytearray([0x02, 0x04, 0x08, 0x10, 0x20])
    else:
        displaymatrix = bytearray([0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40])

    for b in reversed(displaymatrix):
        if(b & x):
            DotCount += 1
            ReturnString += "X"
        else:
            ReturnString += " "            

    return ReturnString

## Get the visible Bits.
#
#  Depending on the Extended Flag, always without flash flag either 5x7 or 7x7
def GetVisibleByte(x, Extended = False):
    if (Extended):
        return(x &(0x01 | 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40))
    
    return(x &(0x02 | 0x04 | 0x08 | 0x10 | 0x20))

## Normalize one byte.
#
#  The transformation matrix is applied to the byte.
def NormalizeByte(x, TransMatrix):
    ReturnByte = 0
    BitPos = 0
    for Byte in TransMatrix:
        if (((x & Byte) == Byte) and (Byte != 0)):
            ReturnByte |= (0x01 << BitPos)
        BitPos += 1
    return ReturnByte

## Reduce the charset to th visible bits.
#
#  Depending on the Extended Flag, always without flash flag either 5x7 or 7x7
def CleanupCharset(InputCharset, Extended = False):
    CleanCharset = bytearray(int(len(InputCharset)))
    index = 0
    for byte in InputCharset:
        CleanCharset[index] = GetVisibleByte(byte, Extended)
        index += 1
    return CleanCharset

## Normalize the given charset.
#
#  The transformation matrix is applied to the charset.
def NormalizeCharset(InputCharset, TransMatrix):
    NormCharset = bytearray(int(len(InputCharset)))
    index = 0
    for byte in InputCharset:
        NormCharset[index] = NormalizeByte(byte, TransMatrix)
        index += 1
    return NormCharset

## Print a String To the Screen and write it to a file
#
def PrintWriteString(outstring: str, SilentFlag: bool, Filehandle):
    if not SilentFlag:
        print(outstring)

    if not (None == Filehandle):
        Filehandle.write(outstring + '\n')     

## Print out one Charset as ASCII Art.
#
#  Depending on the VisibleOnly Flag either as 5x7 or 7x7x matrix.
def PrintCharset(Charset, VisibleOnly: bool, Filehandle, SilentFlag: bool):

    if VisibleOnly:
        PrintWriteString('----------------------------------------------', SilentFlag, Filehandle)
    else:
        PrintWriteString('----------------------------------------------------------------', SilentFlag, Filehandle)
        
    for chrrow in range(8):
        for row in range(8):
            OutString = ''
            for col in range(8):
                OutString = OutString + ByteToString(Charset[(chrrow * 64) + row + (col * 8)], VisibleOnly)
                OutString = OutString + '|'
            PrintWriteString(OutString, SilentFlag, Filehandle)
        if VisibleOnly:
            PrintWriteString('----------------------------------------------', SilentFlag, Filehandle)
        else:
            PrintWriteString('----------------------------------------------------------------', SilentFlag, Filehandle)
           
## Modify the Flash Enable bit.
#
#  The Flash enable Bit is set or reset for the entire charset.
def ModifyFlashEnable(InputCharset, FlashEnable = False):
    OutCharset = bytearray(int(len(InputCharset)))
    index = 0
    for ChrByte in InputCharset:
        if (FlashEnable):
            OutCharset[index] = ChrByte | 0x80 #Set Q7 Flash Enable
        else:
            OutCharset[index] = ChrByte & 0x7F #Reset Q7 Flash Enable
        index += 1
    return OutCharset

def NormalizeCharsets(Charsets, TransMatrix):
    ReturnSets = [] 
    for Charset in Charsets:
        Normset = NormalizeCharset(Charset, TransMatrix)
        ReturnSets.append(Normset)
    return ReturnSets

## Make DL6 Transparent
#
# Set the Flash Bit in every othe Charset.
def MakeDL6flash(Charsets):
    FlashSet = False
    ReturnSets = []
    for Charset in Charsets:
        ReturnSets.append(ModifyFlashEnable(Charset, FlashSet))
        if (FlashSet):
            FlashSet = False
        else:
            FlashSet = True
    return ReturnSets

## Analyze the Charset
#
# Check if it is a known charset by use of HAsh Values
def AnalyzeCharset(Charset, Filehandle, SilentFlag: bool):
    Checksum = hashlib.md5()
    Checksum.update(Charset)
    
    CleanChecksum = hashlib.md5()
    CleanChecksum.update(CleanupCharset(Charset))
    
    ExtCleanChecksum = hashlib.md5()
    ExtCleanChecksum.update(CleanupCharset(Charset, True))

    UsesBlink = False
    EveryCharBlink = True
    DotFiveMinus = False
    DotFivePlus = False

    for byte in Charset:
        if ((byte & 0x80) == 0x80): #Q7 Flash Enable
            UsesBlink = True
        else:
            EveryCharBlink = False

        if ((byte & 0x40) == 0x40): #Q6 One Left of regular Left Dot
            DotFiveMinus = True
            
        if ((byte & 0x01) == 0x01): #Q0 One Right of regular Right Dot
            DotFivePlus = True
            
    #print("                  The Charset has a hashlib.md5 of: ", end='')
    #print Checksum.hexdigest()
    #print("        The 5x7 Visible Bits have a hashlib.md5 of: ", end='')
    #print CleanChecksum.hexdigest()

    CharsetMD5Sum =  ExtCleanChecksum.hexdigest()
            
    PrintWriteString("The maximum 7x7 visible pixels have a MD5 Sum of: " + CharsetMD5Sum, SilentFlag, Filehandle)

    if CharsetMD5Sum in CharsetNames:
        PrintWriteString("This is a " + CharsetNames[CharsetMD5Sum] + " charset.", SilentFlag, Filehandle)
    else:
        PrintWriteString("This is a unnamed charset.", SilentFlag, Filehandle)

    if (UsesBlink):
        if (EveryCharBlink):
            PrintWriteString("Every Character has the Flash enable Bit set.", SilentFlag, Filehandle)
        else:
            PrintWriteString("The Flash Enable Bit is used in the Charset.", SilentFlag, Filehandle)
    else:
        PrintWriteString("The Flash Enable Bit is not used in the Charset.", SilentFlag, Filehandle)        

    if(DotFiveMinus):
        PrintWriteString("It uses pixels to the left of the regular 5x7 Matrix", SilentFlag, Filehandle) 

    if(DotFivePlus):
        PrintWriteString("It uses pixels to the right of the regular 5x7 Matrix", SilentFlag, Filehandle)    

    if DotFiveMinus or DotFivePlus:
        return False

    return True

# Read the input file
inf = open(InputFile, "rb")
try:
    CRG_ROM = bytearray(inf.read())
finally:
    inf.close()

print ("Read file: ", end='')
print (InputFile)
print ("Filesize: ", end='')
print (len(CRG_ROM), end='')
print(" bytes")

Charsets = []

for nr in range(int(len(CRG_ROM)/512)):
    Charsets.append(CRG_ROM[(nr * 512):(512 + (nr * 512))])

print ("The file contains ", end='')
print (len(Charsets), end='')
print (" charsets")

# Apply the transformation matrix to the input.
Normsets = NormalizeCharsets(Charsets, InputMatrix)

# Set the Flashenable for every second charset, so that DL6 is transparent to O7.
if (ProcessFlashFlag):
    Normsets = MakeDL6flash(Normsets)

#Prinst charsets as ASCII art
if (PrintASCIIart == True):    
    # Open a File for ASCII Art output
    AsciiArtFile = open(InputFile + '.txt', "w")

# Print out detail info about the ROM.
if (PrintROMinfo):
    print("")

CharsetCount = 0
for Charset in Normsets:
    if (PrintROMinfo):
        print ("Charset ", end='')
        print(CharsetCount, end='')
        print(" Info:")
        DisplayOnlyVisible = AnalyzeCharset(Charset, AsciiArtFile, (not PrintROMinfo))

    if(PrintASCIIart):
        #Print Out the  Charset as Ascii Art
        PrintCharset(Charset, DisplayOnlyVisible, AsciiArtFile, (not PrintROMinfo))

    if (PrintROMinfo):
        print('')
        
    CharsetCount += 1

#Prinst charsets as ASCII art
if (PrintASCIIart == True):    
    # Close  ASCII Art output File  
    AsciiArtFile.close()
  
# Apply the transformation matrix to the output.
OutSets = NormalizeCharsets(Normsets, InvertTransMatrix(OutputMatrix))

# Write the results as a ROM image.
if (WriteOutputDisk):
    print ("Write file:", end='')
    print (OutputFile)
    opf = open(OutputFile, "wb")
    bytes_out = 0
    try:
        for i in range(4):
            for Charset in OutSets:
                bytes_out += len(Charset)
                opf.write(Charset)
                if (bytes_out >= OutputFileSize):
                    break
            if (bytes_out >= OutputFileSize):
                break

    finally:
        opf.close()

    print (bytes_out, end='')
    print ("bytes filesize.")
