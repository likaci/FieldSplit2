# -*-coding:utf-8-*-
import os

__author__ = 'Administrator'
import arcpy
import time

layerFieldDict = {
    u"��բ": "RICKE",
    u"������": "SSDLX",
    u"��ѹ��": "RICKE",
    u"����": "RICKE",
    u"����ָʾ��": "RICKE",
    u"���": "RICKE",
    u"����": "RICKE",
    u"������": "RICKE",
    u"��ѹ����": "RICKE",
    u"������": "?XLMC",
    u"��ѹ����": "?XLMC",
    u"�˺�": "?SSDLX",
}

arcpy.AddMessage(u"���ű��������������ԣ���ȷ�Ը��������к˶�")
arcpy.AddMessage("----------")

mxd = arcpy.mapping.MapDocument("current")
layers = arcpy.mapping.ListLayers(mxd)

toSplitLayer = []
unSplitLayer = []
lineNames = set()
beforeCount = 0
afterCount = 0
nowTimeStr = time.strftime("%Y%m%d-%H%M%S", time.localtime())

for layer in layers:
    if layer.name not in layerFieldDict.keys():
        unSplitLayer.append(layer)
    else:
        toSplitLayer.append(layer)
        fieldName = layerFieldDict.get(layer.name)
        rows = arcpy.SearchCursor(layer)
        for row in rows:
            beforeCount += 1
            if "?" in fieldName:
                continue
            else:
                try:
                    lineNames.add(row.getValue(fieldName))
                except:
                    arcpy.AddMessage(u"����:" + layer.name + "," + fieldName)
    if len(unSplitLayer) > 0:
        arcpy.AddMessage(u"����ͼ�㲻��ָ�: " + ",".join(l.name for l in unSplitLayer))
        arcpy.AddMessage("----------")
arcpy.AddMessage(u"���ҵ� %d ������:\n" % len(lineNames) + ",".join(lineNames))
arcpy.AddMessage("----------")

for lineName in lineNames:
    if lineName == " ":
        lineName = u"0δ����"
    if not os.path.exists("c:/" + nowTimeStr + "/" + lineName):
        try:
            os.makedirs("c:/" + nowTimeStr + "/" + lineName)
        except:
            arcpy.AddMessage(u"���� mkdir @ " + "c:/" + nowTimeStr + "/" + lineName)
            pass

for layer in toSplitLayer:
    fieldName = layerFieldDict.get(layer.name)
    if "?" in fieldName:
        fieldName = fieldName.replace("?", "")

    rows = arcpy.SearchCursor(layer)
    rowNumber = 1
    for row in rows:
        rowNumber += 1
        for lineName in lineNames:
            value = row.getValue(fieldName)
            valueInLineNames = False
            if lineName in value:
                valueInLineNames = True
                if lineName == " ":
                    lineName = u"0δ����"

                outShpPath = "c:/" + nowTimeStr + "/" + lineName + "/" + layer.name + "_" + lineName + ".shp"
                if not os.path.exists(outShpPath):
                    describe = arcpy.Describe(layer)
                    featureType = describe.featureClass.shapeType
                    spatialReference = describe.spatialReference
                    arcpy.CreateFeatureclass_management("c:/" + nowTimeStr + "/" + lineName,
                                                        layer.name + "_" + lineName, featureType,
                                                        layer,
                                                        spatial_reference=spatialReference)

                curName = "cur" + lineName + layer.name
                if curName not in locals():
                    locals()[curName] = arcpy.InsertCursor(outShpPath)
                cur = locals()[curName]
                cur.insertRow(row)
                afterCount += 1
                break
        if not valueInLineNames:
            lineName = u"0δ����"
            outShpPath = "c:/" + nowTimeStr + "/" + lineName + "/" + layer.name + "_" + lineName + ".shp"
            if not os.path.exists(outShpPath):
                    describe = arcpy.Describe(layer)
                    featureType = describe.featureClass.shapeType
                    spatialReference = describe.spatialReference
                    arcpy.CreateFeatureclass_management("c:/" + nowTimeStr + "/" + lineName,
                                                    layer.name + "_" + lineName, featureType,
                                                    layer,
                                                    spatial_reference=spatialReference)

            curName = "cur" + lineName + layer.name
            if curName not in locals():
                locals()[curName] = arcpy.InsertCursor(outShpPath)
            cur = locals()[curName]
            cur.insertRow(row)
            afterCount += 1

arcpy.AddMessage("----------")
arcpy.AddMessage(u"����ǰ��������: %d" % beforeCount)
arcpy.AddMessage(u"�������������: %d" % afterCount)
arcpy.AddMessage("----------")
arcpy.AddMessage(u"���Ŀ¼: c:/" + nowTimeStr + "/")
arcpy.AddMessage(u"���ű��������������ԣ���ȷ�Ը��������к˶�")
