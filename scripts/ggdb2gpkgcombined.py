from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsField,
    QgsFields,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsProject
)
from PyQt5.QtCore import QVariant
import warnings
from osgeo import ogr

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize the QGIS application (standalone script)
qgs = QgsApplication([], False)
qgs.initQgis()

# Define the file path for the new GeoPackage
gpk_file = r"E:\Projects\PythonProjects\fgdb-to-gpkg\file31.gpkg"

# Create an empty layer (in this case, a Point layer with the EPSG:4326 CRS)
layer = QgsVectorLayer('Point?crs=EPSG:4326', 'empty_layer', 'memory')

# Check if the layer is valid
if layer.isValid():
    # Create a fields object and add fields to it
    fields = QgsFields()

    # Adding an integer field 'id'
    fields.append(QgsField('id', QVariant.Int))  
    
    # Adding a string field 'name' with a specified length (e.g., 100 characters max)
    fields.append(QgsField('name', QVariant.String, 'String', 100))

    # Set the layer's fields
    layer.dataProvider().addAttributes(fields)
    layer.updateFields()  # Make sure the layer updates its schema

    # Use the QgsVectorFileWriter to write to GeoPackage (fixing deprecation)
    writer = QgsVectorFileWriter(gpk_file, 'UTF-8', layer.fields(), layer.wkbType(), layer.crs(), 'GPKG')

    # Check if the writing process was successful
    if writer.hasError() == QgsVectorFileWriter.NoError:
        print(f"GeoPackage created successfully at: {gpk_file}")
    else:
        print(f"Error creating GeoPackage: {writer.errorMessage()}")
else:
    print("Layer creation failed!")

# FGDB to GeoPackage conversion using OGR
fgdb = r"E:\Projects\PythonProjects\fgdb-to-gpkg\Cemetery Data Management.gdb"
outdb = gpk_file  # Output GeoPackage file path
fileEncoding = "UTF-8"

# Open the FGDB using OGR
driver = ogr.GetDriverByName("OpenFileGDB")
if not driver:
    print("FileGeodatabase driver is not available.")
    exit()

data = driver.Open(fgdb, 0)

if data is None:
    print(f"Failed to open FGDB: {fgdb}")
    exit()

# List all layers in the FGDB
feature_class_list = []
for i in range(data.GetLayerCount()):
    layer_name = data.GetLayerByIndex(i).GetName()
    feature_class_list.append(layer_name)

print(f"Layers found in FGDB: {feature_class_list}")

# Write each layer to GeoPackage
for fc in feature_class_list:
    gdbLyr = QgsVectorLayer(f"{fgdb}|layername={fc}", fc, "ogr")
    
    if gdbLyr.isValid():
        print(f'Writing: {fc}')
        
        # Debugging: Output layer geometry type and field types
        geom_type = gdbLyr.geometryType()
        print(f"Layer {fc} geometry type: {geom_type}")
        for field in gdbLyr.fields():
            print(f"Field: {field.name()} | Type: {field.typeName()}")
        
        # Setup options for writing to GeoPackage
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = fc  # Use the name of the source layer
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        options.EditionCapability = 0  # CanAddNewLayer 
        transform_context = QgsProject.instance().transformContext()

        # Writing to GeoPackage using writeAsVectorFormatV3
        error = QgsVectorFileWriter.writeAsVectorFormatV3(gdbLyr, outdb, transform_context, options)
        
        if error == QgsVectorFileWriter.NoError:
            print(f"Layer {fc} written successfully.")
        else:
            print(f"Error writing layer {fc}: {error}")
    else:
        print(f"Failed to load layer: {fc}")

# Exit QGIS application
qgs.exitQgis()
