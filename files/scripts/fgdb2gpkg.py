from osgeo import ogr

fgdb = r"E:\Projects\PythonProjects\fgdb-to-gpkg\Tax Parcel Data Management.gdb"
outdb = r"E:\Projects\PythonProjects\fgdb-to-gpkg\Tax Parcel Data Management2.gpkg" #Has to be created in advance
fileEncoding = "UTF-8"

driver = ogr.GetDriverByName("OpenFileGDB")
data = driver.Open(fgdb, 0)

#List all layers in the file geodatabase
feature_class_list = []
for i in data:
    foo = i.GetName()
    feature_class_list.append(foo)
    
#Write to geopackage
for fc in feature_class_list:
    gdbLyr = QgsVectorLayer("{0}|layername={1}".format(fgdb, fc), fc, "ogr")
    print('Writing: ', fc)
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = fc
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
    options.EditionCapability = 0 #CanAddNewLayer 
    transform_context = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(gdbLyr, outdb, transform_context, options)
