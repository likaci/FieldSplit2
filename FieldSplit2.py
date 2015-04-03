# -*-coding:utf-8-*-
import os

__author__ = 'Administrator'
import arcpy
import time

layerFieldDict = {
    u"刀闸": "RICKE",
    u"分线箱": "SSDLX",
    u"变压器": "RICKE",
    u"开关": "RICKE",
    u"故障指示器": "RICKE",
    u"灵克": "RICKE",
    u"电容": "RICKE",
    u"避雷器": "RICKE",
    u"高压计量": "RICKE",
    u"电力线": "?XLMC",
    u"高压电缆": "?XLMC",
    u"杆号": "?SSDLX",
}

arcpy.AddMessage(u"本脚本不对数据完整性，正确性负责，请自行核对")
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
                    arcpy.AddMessage(u"错误:" + layer.name + "," + fieldName)
    if len(unSplitLayer) > 0:
        arcpy.AddMessage(u"以下图层不会分割: " + ",".join(l.name for l in unSplitLayer))
        arcpy.AddMessage("----------")
arcpy.AddMessage(u"共找到 %d 个干线:\n" % len(lineNames) + ",".join(lineNames))
arcpy.AddMessage("----------")

for lineName in lineNames:
    if lineName == " ":
        lineName = u"0未分类"
    if not os.path.exists("c:/" + nowTimeStr + "/" + lineName):
        try:
            os.makedirs("c:/" + nowTimeStr + "/" + lineName)
        except:
            arcpy.AddMessage(u"错误 mkdir @ " + "c:/" + nowTimeStr + "/" + lineName)
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
                    lineName = u"0未分类"

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
            lineName = u"0未分类"
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
arcpy.AddMessage(u"处理前数据条数: %d" % beforeCount)
arcpy.AddMessage(u"处理后数据条数: %d" % afterCount)
arcpy.AddMessage("----------")
arcpy.AddMessage(u"输出目录: c:/" + nowTimeStr + "/")
arcpy.AddMessage(u"本脚本不对数据完整性，正确性负责，请自行核对")
