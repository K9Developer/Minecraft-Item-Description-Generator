import re
from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageColor


def lore_box_generator(lore, text_y_offset=0, text_x_offset=0, frame_width_right_offset=0,
                       frame_width_left_offset=0, frame_height_down_offset=0,
                       frame_height_up_offset=0, line_spacing_offset=0, char_space_offset=0):
    tmp_lore = []

    # Here we get all the images we need
    back = Image.open('LoreBoxImages/Back.png').convert('RGBA')
    side = Image.open('LoreBoxImages/sides.png').convert('RGBA')
    top_1 = Image.open('LoreBoxImages/top1.png').convert('RGBA')
    top_2 = Image.open('LoreBoxImages/top2.png').convert('RGBA')

    # A function that gives you the width in pixels of certain special chars (in width)
    def get_char_width(char):
        if char == 'i':
            return 3
        elif char == 'I':
            return 10
        elif char == 'l':
            return 5
        elif char == 't':
            return 7
        elif char == ' ':
            return 5
        elif char == '✪':
            return 20
        elif char == ',' or char == '!' or char == '.' or char == ':':
            return 3
        else:
            return 13

    # If you input an array of lore from the hypixel api it will show an
    # obtained at text so here i take the index of that text
    has_obtained_text = False
    index_of_obtained_text = 0
    for t, i in enumerate(lore):
        if 'Obtained:' in i:
            has_obtained_text = True
            index_of_obtained_text = t
            pass
        else:
            tmp_lore.append(i)
    lore = tmp_lore

    # Here we remove the obtained at text
    if has_obtained_text:
        lore.pop(index_of_obtained_text-1)

    characters_width = []

    # Here we get the longest string/value in the lore/array so we can know how big the width should be for the frame
    longest_string = max(lore, key=len)

    # Because there could be bold text we find the index of the bold text and cut the longest line at that point
    try:
        index_of_bold = (longest_string[longest_string.index('§l'):])
    except:
        index_of_bold = ''

    # Here we find the index of the end of the bold text
    index_of_end_of_bold = index_of_bold.find('§')

    # Checks if there's no end if there's not it will the index of the end of the bold text to the end of the text
    if index_of_end_of_bold == -1 or index_of_end_of_bold == 0:
        index_of_end_of_bold = len(index_of_bold)

    # Here it cuts everything between the start and the index of the end of the bold text
    bold_string = (index_of_bold[:index_of_end_of_bold])

    # Here it removes the color codes from both strings (the bold text and the longest string)
    bold_string = len(re.sub("§[0-9a-fk-or]", "", bold_string))
    longest_string = re.sub("§[0-9a-fk-or]", "", longest_string)

    # It loops through the longest string and checks if it didn't just start and there are no color codes included
    for t, i in enumerate(longest_string):
        if t != 0:
            if i != '§' or i[t - 1] != '§':

                # Here ity calls the method that gets the pixel width of the chars in the longest string
                characters_width.append(get_char_width(i)+3)

    # Here we calculate the width of the image with the longest string
    width = (round((sum(characters_width) + bold_string)/8)+18) + round(longest_string.count(':')/8) + frame_width_right_offset + frame_width_left_offset

    # Here we calculate the height of the image with the length of the lore/array
    height = round(len(lore)*18/8 + (len(lore)-1)*12/8)-3 + frame_height_down_offset + frame_height_up_offset

    # Here it resizes the background to the right size and gets it's size
    back = back.resize((round(width), height), resample=Image.NEAREST)
    back_w, back_h = back.size

    # Here we set the size of the sides of the frame to the right size and we get it's size
    side_w, side_h = side.size
    side = side.resize((side_w, height), resample=Image.NEAREST)

    # Here we set the size of the top of the frame to the right size and get it's size
    top_1 = top_1.resize((width, 3), resample=Image.NEAREST)
    top_w, top_h = top_1.size

    # Here we paste the top_2 image over the top_1 image
    top_1.paste(top_2, (0, 1))

    # Here we turn the top_2 image over
    top_2 = ImageOps.mirror(top_2)

    # Here we paste the top_2 image over the top_1 image
    top_1.paste(top_2, (top_w-2, 1))

    # Here it sets the "bottom" by flipping the top image
    bottom = ImageOps.flip(top_1)

    # Here we create a new image with the
    # sizes -> width: the with of the background  height:the height of the background
    lore_box = Image.new('RGBA', (back_w, back_h+top_h*2), (255, 255 ,255, 0))

    # Here it sets the frame to be the same as the lore_box
    frame = Image.new('RGBA', (back_w, back_h+top_h*2), (255, 255 ,255, 0))

    # Here it pastes all of the frame pieces over the frame image
    frame.paste(top_1, (0,0), top_1)
    frame.paste(side, (0, 3))
    side = ImageOps.mirror(side)
    frame.paste(side, (width-2, 3))
    frame.paste(bottom, (0, back_h+top_h), bottom)
    # Here it gets the width and height of the lore_box image
    w, h = lore_box.size

    # Sets fixed height to the height of the lore_box image times 8
    fixed_height = h * 8

    # Here we get the height multiplier
    height_percent = (fixed_height / float(lore_box.size[1]))

    # Here we set the width and height of the lore_box, frame and back images to the bigger dimensions
    width_size = int((float(lore_box.size[0]) * float(height_percent)))
    lore_box = lore_box.resize((width_size, fixed_height), Image.NEAREST)
    frame = frame.resize((width_size, fixed_height), Image.NEAREST)
    back = back.resize((width_size, fixed_height), Image.NEAREST)

    # Here we get the size of the lore_box image
    w, h = lore_box.size

    # Makes another new image that all the text would be in (dimensions: the same dimensions of the lore_box image)
    text_box = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    # Sets up the draw object to draw over the text_box image
    draw = ImageDraw.Draw(text_box)

    # Sets up the "current height" (so it would go down every line correctly)
    current_height = 0

    # This function converts the color codes to HEX and then to RGB
    def get_rgb(code):
            if code == ('§0'):
                color = '#000000'
            elif code == ('§1'):
                color = '#0000AA'
            elif code == ('§2'):
                color = '#00AA00'
            elif code == ('§3'):
                color = '#00AAAA'
            elif code == ('§4'):
                color = '#AA0000'
            elif code == ('§5'):
                color = '#AA00AA'
            elif code == ('§6'):
                color = '#FFAA00'
            elif code == ('§7'):
                color = '#AAAAAA'
            elif code == ('§8'):
                color = '#555555'
            elif code == ('§9'):
                color = '#5555FF'
            elif code == ('§a'):
                color = '#55FF55'
            elif code == ('§b'):
                color = '#55FFFF'
            elif code == ('§c'):
                color = '#FF5555'
            elif code == ('§d'):
                color = '#FF55FF'
            elif code == ('§e'):
                color = '#FFFF55'
            elif code == ('§f'):
                color = '#FFFFFF'
            elif code == ('§g'):
                color = '#DDD605'
            else:
                color = '#AAAAAA'
            return ImageColor.getcolor(color, "RGB")

    # Here it loops over the lore/array
    for t,i in enumerate(lore):

        # Makes sure that the height always changes according to the line count (so it would go down by line space)
        current_height += 29+line_spacing_offset
        
        # Sets up the stroke, space between chars and the default color
        char_counter = 0
        char_width_history = []
        stroke = 0
        space_between_chars = 3+char_space_offset
        color =(170, 170, 170)
        
        # Loops through every char in current line
        for t,o in enumerate(i):

            global font
            tmp_height = -7

            # Checks if the current char is not a color code so it wont show it on the image
            if i[t] == '§':
                stroke = 0
                if i[t+1] != 'l':
                    color = get_rgb('§'+i[t+1])
                elif i[t+1] == 'l':
                    stroke = 1
                    space_between_chars = 5
            elif i[t-1] == '§':
                continue
            else:

                # Checks if the current char is a symbol if it is it will switch to a font that has these symbols
                if o != 'α' and o != '☠' and o != '☣' and o != '♣' and o != '♪' and o != '♫' and o != '⚔' and o != '✎' and o != '✦' and o != '✪' and o != '✯' and o != '❁' and o != '❂' and o != '❈' and o != '❤' and o != '⫽' and o != '⸕'and o != '☘':
                    font = ImageFont.truetype("Minecraft.otf", 30 if stroke!=1 else 30)

                # Else it will switch to the default one
                else:
                    font = ImageFont.truetype('Minecraft_symbols.ttf', 40 if stroke!=1 else 40)

                # Sets the xy of the char according to the last char
                w = sum(char_width_history)+char_counter
                h = 20+current_height+tmp_height

                # Draws current line with the color of the color code with the stroke and the text
                draw.text((w,h),o, color,font=font, stroke_width=stroke)

                # Ups the char counter
                char_counter += 1

                # Saves the prev chars' width in pixels
                char_width_history.append(get_char_width(i[t])+1+space_between_chars)

    # Cuts the text image to the minimum size
    text_box = text_box.crop(text_box.getbbox())

    # Pastes the back over an empty image (lore_box image)
    lore_box.paste(back, (0, (3)), back)

    # Then pastes the text over that image according to the offset that was given
    lore_box.paste(text_box, (20+text_x_offset+(frame_width_left_offset*8),25+text_y_offset+(frame_height_up_offset*8)),mask=text_box)

    # Then it pastes the frame over that
    lore_box.paste(frame, (0, 0), frame)
    
    # Puts 8 pixels of transparent pixels on the corners of the image
    for i in range(8):
        for ii in range(8):
            lore_box.putpixel((ii, i), (0, 0, 0, 0))
            
        for ii in range(8):
            lore_box.putpixel((ii, i+lore_box.size[1]-8), (0, 0, 0, 0))
            
        for ii in range(8):
            lore_box.putpixel((ii+lore_box.size[0]-8, i), (0, 0, 0, 0))
            
        for ii in range(8):
            lore_box.putpixel((ii+lore_box.size[0]-8, i+lore_box.size[1]-8), (0,0,0,0))

    # Returns a PIL image
    return lore_box


lore_array = ['§aFractured Mithril Pickaxe', '§8Breaking Power 5', '', '§7Damage: §c+30', '§7Mining Speed: §a+310', '', 
        '§9Efficiency V', '§7Grants §a+110 §6⸕ Mining', '§6Speed§7.', '§9Experience II', 
        '§7Grants a §a25% §7chance for mobs', '§7and ores to drop double', '§7experience.', '§9Fortune II', 
        '§7Grants §a+20 §6☘ Mining', '§6Fortune§7, which increases your', '§7chance for multiple drops.', 
        '§9Telekinesis I', '§7Block and mob drops go directly', '§7into your inventory.', '', 
        '§6Ability: Mining Speed Boost §e§lRIGHT CLICK', '§7Grants §a+§a300%§7 §6⸕ Mining', '§6Speed §7for §a20s§7.', 
        '§8Cooldown: §a120s', '', '§7§8This item can be reforged!', '§a§lUNCOMMON PICKAXE', '', 
        '§7Obtained: §c<local-time timestamp="1628331780000"></local-time>']

lore_box_generator(lore_array).save("lore.png")
