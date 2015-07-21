#Location Toolbox for ArcGIS
##Address Processing Toolbox
###1 Address Formatter
This quickly goes through an address field to make sure the directions and street abbreviations are consistent, as well as removing non alpha numeric characters from the beginning of the address (which can interfere with geocoding)
Non location specific substrings will be omitted from the address (i.e. po box, box, suite, ste)

###2 Address Finder
Oftentimes two address fields are provided, and not populated in a consistent way. This takes two address fields and determines which one is most likely the correct street address. This is better run after the address formatter, but can be run before as well.
The user has the option of deleting po boxes, removing non Iowa address, or keeping iowa + border states (This will be improved in the future to be functional for any state)

##Geocoding Toolbox
###ArcGIS Geocoder

**Necessary python library: [geocoder](https://github.com/DenisCarriere/geocoder)**

goeocder can be installed using pip:
```
$pip install geocoder
```
The ArcGIS geocoder rest API within the python geocoder library is used to find all unmatched addresses from a goeocding result. Candidate address matches are checked for state and zipcode matches, as well as location quality before updating the address, 'X', and 'Y' fields. An updated table is saved with tne naming convention 'temp_*basename*_located'. The user can simply use "Display XY data" to create a new shapefile/feature class with all located points. A new table is copied to the same working directory as the input with updated matched address, X, and Y fields to so
'Display XY Events' can be used.

**It is recommended that a local address locator built from a network dataset or street centerline file, as it will be much faster. This tool is meant as a more efficient means to located unmatched addresses (rather than manual matching)**

**Simply download the zipped folder and import into ArcGIS to use toolset**
