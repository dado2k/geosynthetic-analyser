# Geosynthetic Analyser
This program lets the user input relevant parameters to calculate desing tensile strength of a variety of geogrids, conforming to BS8006.
Data for the geogrids comes from the British Board of Agrement certificates.

Converting Python to Executable (requires PyInstaller):
  - Download .py and .spec code.
  - Use cmd to reach the folder where the two files are saved
  - Insert the following code: python -m PyInstaller GeosyntheticAnalyser.spec GeosynthethicAnalyser.py
    - Tells PyInstaller to use the .spec file for the options to follow when convertin the .py file 
  - Executable will be created in the folder

How to Use:
 - When the program is run, a user interface will be created.
 - The user can define the following parameter
   - Strain (from 1 to 10% strain, using the slider. Insert 10% to see the maximum tensile strenght of all geosynthetic models)
   - Design Life (number, from the dropdown menu 'years' or 'months' can be selected. The program uses years, and will automatically convert month durations into years)
   - Soil temperature (Can be chosen out of selection, choose 20° to to calculate all geosynthetics models)
   - Soil type (Will depend on the material interfacing the geosynthethic)
   - Structure category (Used to calculate ramification of failure conforming to BS 8006-1:2010 standards)
   - Weathering (Will depend for how long the geosynthetic will be exposed to sunlight and open air)
   - Soil pH (If uknown keep within 4 and 9)
- After having chosen the appropriate inputs, press on the 'Calculate' button
   - This will output an excel file with all the calculated strengths in the same location as where the program is
  
  It is suggested that once the excel is created, it is renamed to a unique name. This will prevent the program to replace the file if other outputs want to be made.

