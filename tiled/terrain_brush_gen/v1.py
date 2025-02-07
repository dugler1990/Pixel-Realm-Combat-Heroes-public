from PIL import Image, ImageDraw, ImageFilter
import os



#### Ok, so next step is to divide the tile in 4 , create the subtiles in the correct place

#### so each tile will be drawn on either tl,tr,bl,br

#### I'm not sure how much we care in general tbh.

###### we want the corresponding tiles, always from both layers

######

########## Actually, i think the issue might be simpler, if i just fivide the tile in 4 to have 4 of the terrain brush
#          tile, it might work.



def create_masked_tile(tex_a, tex_b, mask_func, tile_size):
    tile = Image.new("RGBA", (tile_size, tile_size))
    mask = Image.new("L", (tile_size, tile_size))
    draw = ImageDraw.Draw(mask)
    
    for y in range(tile_size):
        for x in range(tile_size):
            draw.point((x, y), fill=255 if mask_func(x, y) else 0)
    
    # Apply Gaussian blur for smooth transitions
    mask = mask.filter(ImageFilter.GaussianBlur(5))
    blended = Image.composite(tex_a, tex_b, mask)
    tile.paste(blended, (0, 0))
    return tile

def generate_terrain_tileset(texture_a, texture_b, tile_size=1100, output_path="tileset.png"):
    # Load textures
    tex_a = Image.open(texture_a).resize((tile_size, tile_size))
    tex_b = Image.open(texture_b).resize((tile_size, tile_size))
    
    half_size = tile_size // 2
        
    tex_a_tl = tex_a.crop((0, 0, half_size, half_size))  # Top-left
    tex_a_tr = tex_a.crop((half_size, 0, tile_size, half_size))  # Top-right
    tex_a_bl = tex_a.crop((0, half_size, half_size, tile_size))  # Bottom-left
    tex_a_br = tex_a.crop((half_size, half_size, tile_size, tile_size))  # Bottom-right
    
    tex_b_tl = tex_b.crop((0, 0, half_size, half_size))  # Top-left
    tex_b_tr = tex_b.crop((half_size, 0, tile_size, half_size))  # Top-right
    tex_b_bl = tex_b.crop((0, half_size, half_size, tile_size))  # Bottom-left
    tex_b_br = tex_b.crop((half_size, half_size, tile_size, tile_size))  # Bottom-right

    
    
    patterns = {
        #"full_a": lambda x, y: True,
       # "full_b": lambda x, y: False,
        # Horizontal Splits
        "edge_top_1_3": lambda x, y: y > half_size // 3,  # Bottom 2/3 remains
        "edge_top_2_3": lambda x, y: y > 2 * half_size // 3,  # Bottom 1/3 remains
        "edge_bottom_1_3": lambda x, y: y < 2 * half_size // 3,  # Top 2/3 remains
        "edge_bottom_2_3": lambda x, y: y < half_size // 3,  # Top 1/3 remains
        
        # Vertical Splits
        "edge_left_1_3": lambda x, y: x > half_size // 3,  # Right 2/3 remains
        "edge_left_2_3": lambda x, y: x > 2 * half_size // 3,  # Right 1/3 remains
        "edge_right_1_3": lambda x, y: x < 2 * half_size // 3,  # Left 2/3 remains
        "edge_right_2_3": lambda x, y: x < half_size // 3,  # Left 1/3 remains
        "corner_outer_large_tl": lambda x, y: not (x**2 + y**2 < (half_size *2//3)**2),
        "corner_outer_large_tr": lambda x, y: not ((x - half_size)**2 + y**2 < (half_size *2//3)**2),
        "corner_outer_large_bl": lambda x, y: not (x**2 + (y - half_size)**2 < (half_size *2//3 )**2),
        "corner_outer_large_br": lambda x, y: not ((x - half_size)**2 + (y - half_size)**2 < (half_size *2//3 )**2),
        "corner_inner_large_tl": lambda x, y: x**2 + y**2 < (half_size *2//3 )**2,
        "corner_inner_large_tr": lambda x, y: (x - half_size)**2 + y**2 < (half_size *2//3 )**2,
        "corner_inner_large_bl": lambda x, y: x**2 + (y - half_size)**2 < (half_size *2//3 )**2,
        "corner_inner_large_br": lambda x, y: (x - half_size)**2 + (y - half_size)**2 < (half_size *2//3 )**2,
         # Outer Small Corners (Remove the correct quadrant)
          # Outer Small Corners (Remove the correct quadrant)
        "corner_outer_small_tl": lambda x, y: not (x**2 + y**2 < (half_size // 3)**2),
        "corner_outer_small_tr": lambda x, y: not ((x - half_size)**2 + y**2 < (half_size // 3)**2),
        "corner_outer_small_bl": lambda x, y: not (x**2 + (y - half_size)**2 < (half_size // 3)**2),
        "corner_outer_small_br": lambda x, y: not ((x - half_size)**2 + (y - half_size)**2 < (half_size // 3)**2),
        
        # Inner Small Corners (Keep only the correct quadrant)
        "corner_inner_small_tl": lambda x, y: x**2 + y**2 < (half_size // 3)**2,
        "corner_inner_small_tr": lambda x, y: (x - half_size)**2 + y**2 < (half_size // 3)**2,
        "corner_inner_small_bl": lambda x, y: x**2 + (y - half_size)**2 < (half_size // 3)**2,
        "corner_inner_small_br": lambda x, y: (x - half_size)**2 + (y - half_size)**2 < (half_size // 3)**2,

     "t_top": lambda x, y:  
# Draw a properly sized, THICKER T shape with 1/4 tile height  
(y < half_size // 2 or (x > half_size // 4 and x < 3 * half_size // 4))  

# Carve out TWO smooth curves at the bottom corners of the horizontal bar  
and not ((x - half_size // 8)**2 + (y - half_size*3 // 8)**2 < (half_size // 8)**2)  
and not ((x - 7 * half_size // 8)**2 + (y - half_size*3 // 8)**2 < (half_size // 8)**2)  

# Remove three quadrants from the left circle  
and not (  
    (x >= half_size // 8 - (half_size // 8) and x <= half_size // 8 and  
     y >= half_size *3// 8 - (half_size // 8) and y <= half_size *3// 8)  # Top-left of left circle  
    or  
    (x >= half_size // 8 - (half_size // 8) and x <= half_size // 8 and  
     y >= half_size *3// 8 and y <= half_size *3// 8 + (half_size // 8))  # Bottom-left of left circle  
    or  
    (x >= half_size // 8 and x <= half_size // 8 + (half_size // 8) and  
     y >= half_size *3// 8 and y <= half_size *3// 8 + (half_size // 8))  # Bottom-right of left circle  
)  

# Remove three quadrants from the right circle, keeping the top-right  
and not (  
    (x >= 7 * half_size // 8 and x <= 7 * half_size // 8 + (half_size // 8) and  
     y >= half_size *3// 8 - (half_size // 8) and y <= half_size *3// 8)  # Top-right of right circle  
    or  
    (x >= 7 * half_size // 8 - (half_size // 8) and x <= 7 * half_size // 8 and  
     y >= half_size *3 // 8 and y <= half_size * 3 // 8 + (half_size // 8))  # Bottom-left of right circle  
    or  
    (x >= 7 * half_size // 8 and x <= 7 * half_size // 8 + (half_size // 8) and  
     y >= half_size *3// 8 and y <= half_size * 3 // 8 + (half_size // 8))  # Bottom-right of right circle  
)
,
        "t_left": lambda x, y:  
# Draw a properly sized, THICKER T shape with 1/4 tile width  
(x > half_size // 2 or (y > half_size // 4 and y < 3 * half_size // 4))  

# Carve out TWO smooth curves at the bottom corners of the horizontal bar  
and not ((y - half_size // 8)**2 + (x - half_size * 3 // 8)**2 < (half_size // 8)**2)  
and not ((y - 7 * half_size // 8)**2 + (x - half_size * 3 // 8)**2 < (half_size // 8)**2)  

# Remove three quadrants from the top circle  
and not (  
    (y >= half_size // 8 - (half_size // 8) and y <= half_size // 8 and  
     x >= half_size * 3 // 8 - (half_size // 8) and x <= half_size * 3 // 8)  # Top-left of top circle  
    or  
    (y >= half_size // 8 - (half_size // 8) and y <= half_size // 8 and  
     x >= half_size * 3 // 8 and x <= half_size * 3 // 8 + (half_size // 8))  # Bottom-left of top circle  
    or  
    (y >= half_size // 8 and y <= half_size // 8 + (half_size // 8) and  
     x >= half_size * 3 // 8 and x <= half_size * 3 // 8 + (half_size // 8))  # Bottom-right of top circle  
)  

# Remove three quadrants from the bottom circle, keeping the top-right  
and not (  
    (y >= 7 * half_size // 8 and y <= 7 * half_size // 8 + (half_size // 8) and  
     x >= half_size * 3 // 8 - (half_size // 8) and x <= half_size * 3 // 8)  # Top-right of bottom circle  
    or  
    (y >= 7 * half_size // 8 - (half_size // 8) and y <= 7 * half_size // 8 and  
     x >= half_size * 3 // 8 and x <= half_size * 3 // 8 + (half_size // 8))  # Bottom-left of bottom circle  
    or  
    (y >= 7 * half_size // 8 and y <= 7 * half_size // 8 + (half_size // 8) and  
     x >= half_size * 3 // 8 and x <= half_size * 3 // 8 + (half_size // 8))  # Bottom-right of bottom circle  
)
,
        "t_right": lambda x, y:  
# Draw a properly sized, THICKER T shape with 1/4 tile width  
(x < tile_size // 2 or (y > tile_size // 4 and y < 3 * tile_size // 4))  

# Carve out TWO smooth curves at the bottom corners of the horizontal bar  
and not ((y - tile_size // 8)**2 + (x - tile_size * 3 // 8)**2 < (tile_size // 8)**2)  
and not ((y - 7 * tile_size // 8)**2 + (x - tile_size * 3 // 8)**2 < (tile_size // 8)**2)  

# Remove three quadrants from the top circle  
and not (  
    (y >= tile_size // 8 - (tile_size // 8) and y <= tile_size // 8 and  
     x >= tile_size * 3 // 8 - (tile_size // 8) and x <= tile_size * 3 // 8)  # Top-left of top circle  
    or  
    (y >= tile_size // 8 - (tile_size // 8) and y <= tile_size // 8 and  
     x >= tile_size * 3 // 8 and x <= tile_size * 3 // 8 + (tile_size // 8))  # Bottom-left of top circle  
    or  
    (y >= tile_size // 8 and y <= tile_size // 8 + (tile_size // 8) and  
     x >= tile_size * 3 // 8 and x <= tile_size * 3 // 8 + (tile_size // 8))  # Bottom-right of top circle  
)  

# Remove three quadrants from the bottom circle, keeping the top-right  
and not (  
    (y >= 7 * tile_size // 8 and y <= 7 * tile_size // 8 + (tile_size // 8) and  
     x >= tile_size * 3 // 8 - (tile_size // 8) and x <= tile_size * 3 // 8)  # Top-right of bottom circle  
    or  
    (y >= 7 * tile_size // 8 - (tile_size // 8) and y <= 7 * tile_size // 8 and  
     x >= tile_size * 3 // 8 and x <= tile_size * 3 // 8 + (tile_size // 8))  # Bottom-left of bottom circle  
    or  
    (y >= 7 * tile_size // 8 and y <= 7 * tile_size // 8 + (tile_size // 8) and  
     x >= tile_size * 3 // 8 and x <= tile_size * 3 // 8 + (tile_size // 8))  # Bottom-right of bottom circle  
),
       # "x_cross": lambda x, y: (x > tile_size // 4 and x < 3 * tile_size // 4) or (y > tile_size // 4 and y < 3 * tile_size // 4)
    }
    
    num_patterns = len(patterns)
    raw_tile_chunks = [tex_a_tl,tex_a_tr,tex_a_bl,tex_a_br,tex_b_tl,tex_b_tr,tex_b_bl,tex_b_br] 
    tileset_width = (tile_size * num_patterns) + len(raw_tile_chunks)
    tileset = Image.new("RGBA", (tileset_width, tile_size))
    
    # raw tiles : 
   
    i = 0
    for tile in raw_tile_chunks:
        tileset.paste( tile, (i*tile_size//2,0))
        i += 1
    for j, (pattern_name, mask_func) in enumerate(patterns.items()):
        print(j+i)
        tile = create_masked_tile(tex_a_tr, tex_b_tr, mask_func, tile_size//2)
        tileset.paste(tile, ((j+i) * (tile_size//2), 0))# j+i to keep pos of raw_tile_chunks accounted for , bit dirty
        #tileset.show(j+1)
    
    
    tileset.save(output_path)
    print(f"Generated tileset saved as '{output_path}'")

# Example usage
generate_terrain_tileset("Ice 5.jpg", "Snow 5.jpg")
