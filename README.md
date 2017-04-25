# ctldis - Warhammer Dark Omen CTL (De)compiler

Originally developed by Rob in 2009 and extended with further opcodes over years.

CTLdis can compile and decompile the CTL-Script language that is executed on the battlefield.

For further information see the [Dark Omen Wiki](http://wiki.dark-omen.org/do/DO/CTL) article about CTL.

This program needs Python 2.7.x. Before executing the program you have to place it in a map folder (where the CTL-file is located). Create a copy of the CTL-file and add _orig to it (e.g. B101.CTL -> B101_orig.CTL). Now open ctldis.py with a text editor. Change basename to the name of the CTL-file (default is "b101") and set the MODE. 1 decompiles the CTL file and writes it in a textfile basename.txt (basename is e.g. b101). 0 converts the text file back into the CTL file.
