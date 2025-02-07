# resizing object images 


import os
import PIL
import math
PIL.Image.new

pic_folder_dir = "./objects/" 
pic_dirs = os.listdir( pic_folder_dir )

tile_size = 550
tiles_per_width = 5

tile_set_width = tiles_per_width * tile_size

additional_rows = 0
if len(pic_dirs)%tiles_per_width != 0:
    additional_rows = 1

tile_set_height = ( math.floor( len(pic_dirs)/5 ) + additional_rows ) * tile_size

tile_set = PIL.Image.new(mode = "RGBA", size = ( tile_set_height, tile_set_width ))
counter = 0
for pic_dir in pic_dirs:
    pic = PIL.Image.open(  pic_folder_dir + pic_dir).resize((tile_size,tile_size))
    height_start = math.floor(counter/5) * tile_size
    width_start = (counter % tiles_per_width) * tile_size
    
    tile_set.paste( pic, (height_start,width_start) )
    counter += 1
    
tile_set.save("object_tileset.png")