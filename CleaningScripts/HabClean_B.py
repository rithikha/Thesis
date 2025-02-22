import arcpy
import os
# A1 AND A2 ZONES - DATA CLEANING


# workspace
tempgdb = r"C:\Users\rithi\Downloads\Thesis\Workspace\scratch\B2.gdb"                                                   # CHANGE
gdb = r"C:\Users\rithi\Downloads\Thesis\Workspace\BGI_invest.gdb"

arcpy.env.overwriteOutput = True
arcpy.env.workspace = gdb

# checkout spatial extension
arcpy.CheckExtension('Spatial')
arcpy.CheckOutExtension("Spatial")

habitatLayer = "B1_Intertidal"                                                                                        #  CHANGE
biobands = ["BARN", "BLMU", "BIOF", "BRBA", "EELG", "FFRA", "GRAL", "ROCK", "SAMB", "SOBK"]                                           # CHANGE
splashBiobands = ["BLLI", "LICH", "WHLI"]

# cleaning layers
for bioband in biobands:
    featurelyr = arcpy.MakeFeatureLayer_management(habitatLayer, habitatLayer + 'lyr')
    xpr1 = 'BioBand_'+ bioband + " " + "= 'C'"
    arcpy.SelectLayerByAttribute_management(featurelyr, "NEW_SELECTION", "{}".format(xpr1))
    xpr1 = 'BioBand_' + bioband + " " + "= 'P' AND " + "BioBand_" + bioband + "_PCV" + " " + "= '26-50'" + " " + "AND" + " " + "BioBand_" + bioband + "_L" + " " + "= '>95'"
    print(xpr1)
    arcpy.SelectLayerByAttribute_management(featurelyr, "ADD_TO_SELECTION", "{}".format(xpr1))
    arcpy.CopyFeatures_management(featurelyr, tempgdb + "\clean" + bioband)


# setting new workspace and list variables
arcpy.env.workspace = tempgdb
print("setting up buffer workspace")

shapes = ["cleanBARN", "cleanBLMU", "cleanBIOF", "cleanBRBA", "cleanEELG", "cleanFFRA", "cleanGRAL", "cleanROCK", "cleanSAMB", "cleanSOBK"]         # CHANGE
biobands = ["BARN", "BLMU", "BIOF", "BRBA", "EELG", "FFRA", "GRAL", "ROCK", "SAMB", "SOBK"]                                                     # CHANGE


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
            elif row.getValue('BioBand_' + bioband+"_PCV") == '<5':
                row.setValue("buffer_dist", 0.05* 40)
            elif row.getValue('BioBand_' + bioband+"_PCV") == '5-25':
                row.setValue("buffer_dist", 0.15 * 40)
            elif row.getValue('BioBand_' + bioband+"_PCV") == '26-50':
                row.setValue("buffer_dist", 0.38 * 40)
            elif row.getValue('BioBand_' + bioband + "_PCV") == '51-75':
                row.setValue("buffer_dist", 0.63 * 40)
            elif row.getValue('BioBand_' + bioband + "_PCV") == '76-95':
                row.setValue("buffer_dist", 0.855 * 40)
            elif row.getValue('BioBand_' + bioband + "_PCV") == '>95':
                row.setValue("buffer_dist",  40)

            if row.getValue('Unit_lines_PHY_IDENT') in ids_LEFT:
                row.setValue("buffer_dir", "LEFT")
            elif row.getValue('Unit_lines_PHY_IDENT') in ids_RIGHT:
                row.setValue("buffer_dir", "RIGHT")
            else:
                row.setValue("buffer_dir", "RIGHT")
            cursorCurrent.updateRow(row)
print("buffer direction and distance fields set")

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

# Add buffers and merge into final sub-zone polygons

for shape in shapes:
    arcpy.Buffer_analysis(shape + "LEFT", shape + "LEFT_B", "buffer_dist", "LEFT", "FLAT", "", "", "GEODESIC")
    arcpy.Buffer_analysis(shape + "RIGHT", shape + "RIGHT_B", "buffer_dist", "RIGHT", "FLAT", "", "", "GEODESIC")


# manually move left and right units according to Zone location
# uncomment the following lines, comment everythign else above'

#
# import arcpy
# tempgdb = r"C:\Users\rithi\Downloads\Thesis\Workspace\scratch\B2.gdb"                                                   # CHANGE
# arcpy.env.overwriteOutput = True
# arcpy.env.workspace = tempgdb
# arcpy.CheckExtension('Spatial')
# arcpy.CheckOutExtension("Spatial")
#
# shapes = ["cleanBARN", "cleanBLMU", "cleanBIOF", "cleanBRBA", "cleanEELG", "cleanFFRA", "cleanGRAL", "cleanROCK", "cleanSAMB", "cleanSOBK"]         # CHANGE
# biobands = ["BARN", "BLMU", "BIOF", "BRBA", "EELG", "FFRA", "GRAL", "ROCK", "SAMB", "SOBK"]                                                     # CHANGE
#
#
# for shape in shapes:
#     minputs = [shape + "LEFT_B", shape + "RIGHT_B"]
#     arcpy.Merge_management(minputs, shape+"_B2P")                                                                   # CHANGE



arcpy.CheckInExtension("Spatial")
