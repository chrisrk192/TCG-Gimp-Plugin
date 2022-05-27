#!/usr/bin/python
#
# TCG Export - GIMP plug-in that exports a template as separate images with layers' values replaced by data from a CSV file
#
# Copyright (C) 2022 christopher king <christopher@royalgoose.dev>
#
# TCG Export is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TCG Export is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TCG Export. If not, see <https://www.gnu.org/licenses/>.
import os
import csv
from gimpfu import *

def find_layer_by_name (image, name): 
    for layer in image.layers:
        if layer.name == name:
            return layer
        if(pdb.gimp_item_is_group(layer)):
            potential = find_layer_name_in_group(layer, name)
            if(potential != None):
                return potential
    return None
def find_layer_name_in_group(layerGroup, name):
    gr = layerGroup
    gr_items = pdb.gimp_item_get_children(gr)
    for index in gr_items[1]:
        item = gimp.Item.from_id(index)
        if item.name == name:
            return item
        elif(pdb.gimp_item_is_group(item)):
            potential = find_layer_name_in_group(item, name)
            if(potential != None):
                return potential
    return None

def plugin_main(timg, tdrawable, data_dir, data_out, data_csv):
    pdb.gimp_image_undo_group_start(timg)
    pdb.gimp_message(data_csv)
    with open(data_csv) as csvfile:
        header = csvfile.readline()
        #parse header row
        columns = header.strip().split(",")
        pdb.gimp_message(columns)
        
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        #for each row
        for row_index, row in enumerate(spamreader):
            #for each column
            pdb.gimp_message(row)
            name = None
            for col_index, col in enumerate(columns):
                #check if there is a layer with that header name
                layer  = find_layer_by_name(timg, col)
                if(col == "name"):
                    name = row[col_index]
                if layer != None:
                    pdb.gimp_message("Layer index " + layer.name)
                    pdb.gimp_image_set_active_layer(timg, layer)
                    path = os.path.join(data_dir, col)
                    #if there exists a folder in the directory with the same name as the column, the value is a file name
                    if os.path.exists(path):
                        pdb.gimp_message("found an asset folder for " + col)
                        img_path = os.path.join(path, row[col_index])
                        new_asset = pdb.gimp_file_load_layer(timg, img_path)
                        
                        if new_asset != None:
                            #add the new image, scaled to the right height and in the correct position and merge it down
                            new_asset.name = col
                            opacity_before = layer.opacity 
                            timg.add_layer(new_asset, -1)
                            scalefactor = new_asset.height / layer.height
                            extrawidth = ((new_asset.width / scalefactor) - layer.width) / 2
                            pdb.gimp_item_transform_scale(new_asset,  0 - extrawidth + layer.offsets[0], layer.offsets[1], layer.width + extrawidth + layer.offsets[0], layer.height + layer.offsets[1])
                            pdb.gimp_layer_resize_to_image_size(new_asset)
                            layer = pdb.gimp_image_merge_down(timg, new_asset, 2)
                            layer.opacity = opacity_before
                            
                    #if the value in the layer is a color, recolor the layer
                    elif row[col_index] != None and row[col_index].find("#") != -1:
                        pdb.gimp_message("found a color for " + col)
                        pdb.gimp_selection_none(timg)
                        pdb.gimp_image_select_item(timg, 2, layer)
                        pdb.gimp_context_set_foreground(row[col_index])
                        pdb.gimp_drawable_edit_fill(layer,FILL_FOREGROUND)
                        pdb.gimp_selection_none(timg)
                    #it is a text layer
                    else:
                        pdb.gimp_message("text layer " + col)
                        pdb.gimp_text_layer_set_text(layer, row[col_index])
            #end of each column processing, template ready for export
            if(name != None):
                new_image = pdb.gimp_image_duplicate(timg)
                layer = pdb.gimp_image_merge_visible_layers(new_image, CLIP_TO_IMAGE)
                pdb.gimp_file_save(new_image, layer, os.path.join(data_out, name + '.png'), '?')
                pdb.gimp_image_delete(new_image)
    
    
    
    pdb.gimp_image_undo_group_end(timg)



register(
        "python_fu_tcg",
        "Loads in a CSV file and a directory of art assets and exports a playing card using this template",
        "Loads in a CSV file and a directory of art assets and exports a playing card using this template",
        "Christopher King",
        "Christopher King",
        "2022",
        "<Image>/File/Export TCG files",
        "RGB*, GRAY*",
        [
                #get the project directory
                (PF_FILE, "data_dir", "Project Directory", "/"),
                #get the output directory
                (PF_FILE, "data_out", "Output Directory", "/"),
                #get the csv file
                (PF_FILE, "data_csv", "Card Data CSV", "")
        ],
        [],
        plugin_main)

main()