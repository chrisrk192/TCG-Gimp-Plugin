#!/usr/bin/python
#
# Image Pack - GIMP plug-in combines all the files in a directory into a single image
#
# Copyright (C) 2022 christopher king <christopher@royalgoose.dev>
#
# Image Pack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Image Pack is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Image Pack. If not, see <https://www.gnu.org/licenses/>.
import os
import csv
from gimpfu import *



def plugin_main(timg, tdrawable, data_dir, data_width, data_height, data_img_w, data_img_h):
    pdb.gimp_image_undo_group_start(timg)
    originalWidth = data_img_w#timg.width
    originalHeight = data_img_h#timg.height
    pdb.gimp_image_resize(timg,data_img_w*data_width,data_img_h*data_height,0,0)
    #get a list of all the files in the directory
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    #for each location in the packed image, try to load the file and place it in the correct position
    i = 0
    for y in range(0, data_height):
        for x in range(0, data_width):
            if i < len(files):
                file = files[i]
                img_path = os.path.join(data_dir, file)
                new_asset = pdb.gimp_file_load_layer(timg, img_path)
                #if the asset is not null, transform it to the correct position
                if new_asset != None:
                    new_asset.name = file
                    timg.add_layer(new_asset, -1)
                    pdb.gimp_item_transform_scale(new_asset, x * originalWidth, y * originalHeight, (x+1) * originalWidth, (y+1) * originalHeight)
            i+=1;
    
    if(i < len(files):
        pdb.gimp_message("Only fit " + str(i) + " files out of " + str(len(files)))
    
    pdb.gimp_image_undo_group_end(timg)



register(
        "python_fu_img_pack",
        "Packs all images in a directory into a single image",
        "Packs all images in a directory into a single image",
        "Christopher King",
        "Christopher King",
        "2022",
        "<Image>/File/Pack Images",
        "RGB*, GRAY*",
        [
                #get the project directory
                (PF_DIRNAME, "data_dir", "Input Directory", "."),
                #get the number of images per row
                (PF_INT, "data_width", "Number of Columns", 10),
				#get the number of columns
                (PF_INT, "data_height", "Number of Rows", 7),
                (PF_INT, "data_img_w", "Individual Image Width", 816),
                (PF_INT, "data_img_h", "Individual Image Height", 1110),
        ],
        [],
        plugin_main)

main()