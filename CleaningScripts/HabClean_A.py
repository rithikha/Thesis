import arcpy
import os
# A1 AND A2 ZONES - DATA CLEANING


# workspace
tempgdb = r"C:\Users\rithi\Downloads\Thesis\Workspace\scratch\A2.gdb"                                                   # CHANGE
gdb = r"C:\Users\rithi\Downloads\Thesis\Workspace\BGI_invest.gdb"

arcpy.env.overwriteOutput = True
arcpy.env.workspace = gdb

# checkout spatial extension
arcpy.CheckExtension('Spatial')
arcpy.CheckOutExtension("Spatial")

habitatLayer = "A2_Supratidal"                                                                                        #  CHANGE
biobands =  ["SAMB", "DUGR"]                                                                                          # CHANGE
splashBiobands = ["BLLI", "LICH", "WHLI"]

# cleaning layers
for bioband in biobands:
    featurelyr = arcpy.MakeFeatureLayer_management(habitatLayer, habitatLayer + 'lyr')
    if bioband in splashBiobands:
        xpr1 = 'BioBand_'+ bioband + " " + "IN ('M', 'W', 'w', 'm')"
        arcpy.SelectLayerByAttribute_management(featurelyr, "NEW_SELECTION", "{}".format(xpr1))

        xpr1 = 'BioBand_'+ bioband + '_L' + " " + "IN ('5-25', '26-50')"
        arcpy.SelectLayerByAttribute_management(featurelyr, "REMOVE_FROM_SELECTION", "{}".format(xpr1))

        xpr1 = 'BioBand_'+ bioband + " " + "= 'N' AND BioBand_" + bioband + "_L = '>95'"
        arcpy.SelectLayerByAttribute_management(featurelyr, "ADD_TO_SELECTION", "{}".format(xpr1))
        arcpy.CopyFeatures_management(featurelyr, tempgdb + "\clean" + bioband)
    else:
        xpr1 = 'BioBand_'+ bioband + " " + "= 'C'"
        arcpy.SelectLayerByAttribute_management(featurelyr, "NEW_SELECTION", "{}".format(xpr1))

        xpr1 = 'BioBand_' + bioband + " " + "= 'P' AND " + "BioBand_" + bioband + "_WC" + " " + "= '>30'" "AND" + " " + "BioBand_" + bioband + "_L" + " " + "= '>95'"
        arcpy.SelectLayerByAttribute_management(featurelyr, "ADD_TO_SELECTION", "{}".format(xpr1))
        arcpy.CopyFeatures_management(featurelyr, tempgdb + "\clean" + bioband)


# setting new workspace and list variables
arcpy.env.workspace = tempgdb

shapes =  ["cleanSAMB", "cleanDUGR"]                                                                             # CHANGE
biobands =  ["LICH", "DUGR", "GRAS", "BLLI"]


# make a list of all the LEFT and RIGHT unit identifiers
fcL = r'C:\Users\rithi\Downloads\Thesis\Workspace\BGI_invest.gdb\UnitLines_LEFT'
fcR = r'C:\Users\rithi\Downloads\Thesis\Workspace\BGI_invest.gdb\UnitLines_RIGHT'
fields = ['Unit_lines_PHY_IDENT']
ids_LEFT = []
ids_RIGHT = []

with arcpy.da.SearchCursor(fcL, fields) as cursor:
    for row in cursor:
        ids_LEFT.append(row[0])

with arcpy.da.SearchCursor(fcR, fields) as cursor:
    for row in cursor:
        ids_RIGHT.append(row[0])

for shape in shapes:
    for bioband in biobands:
        arcpy.AddField_management(shape, "buffer_dist", "FLOAT", "")
        arcpy.AddField_management(shape, "buffer_dir", "TEXT", "")
        cursorCurrent = arcpy.UpdateCursor(shape)
        # add buffer distance
        for row in cursorCurrent:
            if row.getValue('BioBand_' + bioband) == 'M':
                row.setValue("buffer_dist", 3)
            elif row.getValue('BioBand_' + bioband) == 'm':
                row.setValue("buffer_dist", 3)
            elif row.getValue('BioBand_' + bioband) == 'N':
                row.setValue("buffer_dist", 0.5)
            elif row.getValue('BioBand_' + bioband) == 'n':
                row.setValue("buffer_dist", 0.5)
            elif row.getValue('BioBand_' + bioband) == 'W':
                row.setValue("buffer_dist", 7.5)
            elif row.getValue('BioBand_' + bioband) == 'w':
                row.setValue("buffer_dist", 7.5)
            elif row.getValue('BioBand_' + bioband+"_WC") == '<10':
                row.setValue("buffer_dist", 5)
            elif row.getValue('BioBand_' + bioband+"_WC") == '10-30':
                row.setValue("buffer_dist", 20)
            elif row.getValue('BioBand_' + bioband+"_WC") == '>30':
                row.setValue("buffer_dist", 35)

            if row.getValue('Unit_lines_PHY_IDENT') in ids_LEFT:
                row.setValue("buffer_dir", "LEFT")
            elif row.getValue('Unit_lines_PHY_IDENT') in ids_RIGHT:
                row.setValue("buffer_dir", "RIGHT")
            else:
                row.setValue("buffer_dir", "RIGHT")
            cursorCurrent.updateRow(row)

# delete cursor
cursorCurrent=cursorCurrent=None


# split into left buffer and right unit shapefiles

for shape in shapes:
    featurelyr = arcpy.MakeFeatureLayer_management(shape, shape + 'lyr1')
    xpr1 = "buffer_dir = 'LEFT'"
    arcpy.SelectLayerByAttribute_management(featurelyr, "NEW_SELECTION", "{}".format(xpr1))
    arcpy.CopyFeatures_management(featurelyr, shape + "LEFT")

    featurelyr = arcpy.MakeFeatureLayer_management(shape, shape + 'lyr2')
    xpr1 = "buffer_dir = 'RIGHT'"
    arcpy.SelectLayerByAttribute_management(featurelyr, "NEW_SELECTION", "{}".format(xpr1))
    arcpy.CopyFeatures_management(featurelyr, shape + "RIGHT")

# move left and right units according to Zone location



# Add buffers and merge left and right into final sub-zone polygons

for shape in shapes:
    arcpy.Buffer_analysis(shape + "LEFT", shape + "LEFT_B", "buffer_dist", "LEFT", "FLAT", "", "", "GEODESIC")
    arcpy.Buffer_analysis(shape + "RIGHT", shape + "RIGHT_B", "buffer_dist", "RIGHT", "FLAT", "", "", "GEODESIC")
    minputs = [shape + "LEFT_B", shape + "RIGHT_B"]
    arcpy.Merge_management(minputs, shape+"_A2P")                                                                   # CHANGE



arcpy.CheckInExtension("Spatial")
