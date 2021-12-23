import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Color code map, Source - https://www.digminecraft.com/lists/color_list_pc.php
color_code_map = {
    "§4": "#AA0000",
    "§c": "#FF5555",
    "§6": "#FFAA00",
    "§e": "#FFFF55",
    "§2": "#00AA00",
    "§a": "#55FF55",
    "§b": "#55FFFF",
    "§3": "#00AAAA",
    "§1": "#0000AA",
    "§9": "#5555FF",
    "§d": "#FF55FF",
    "§5": "#AA00AA",
    "§f": "#FFFFFF",
    "§7": "#AAAAAA",
    "§8": "#555555",
    "§0": "#000000",
    "§l": "bold",
    "§o": "italic",
    "§r": "reset"}

font_path = 'assets/fonts/Full_Minecraft-R.ttf'
offset = 60


def draw_description(desc, text_size=100, line_spacing=10, char_spacing=5, draw_text_start_offset_w=0,
                     draw_text_start_offset_h=0):
    """
    A function that generates an image out of a list of text.

    :param desc: The full description as a list containing each line as a string
    :type desc: list[str,]
    :param text_size: The font size of the text
    :type text_size: int
    :param line_spacing: The spacing of each written line
    :type line_spacing: int
    :param char_spacing: The spacing of each written char
    :type char_spacing: int
    :param draw_text_start_offset_w: The offset the text would start writing from the right
    :type draw_text_start_offset_w: int
    :param draw_text_start_offset_h: The offset the text would start writing from the top
    :type draw_text_start_offset_h: int
    :return: The description box
    :rtype: PIL.Image
    """

    # Creates an image that is bigger than the text itself so we can crop it later to the exact size of the text
    template_image = Image.new('RGBA',
                               (ImageFont.truetype(font_path,
                                                   text_size).getsize(max(desc, key=len))[
                                    0] * char_spacing // 5 + offset * 2,
                                len(desc) * line_spacing * 10 + offset * 2), (0, 0, 0, 0))

    # Initializes some variables
    template_image_draw = ImageDraw.Draw(template_image)
    current_color = color_code_map['§7']
    current_line_height = 30 + draw_text_start_offset_h
    font = ImageFont.truetype(font_path, size=text_size)
    bold = 0

    # Loops through every line
    for line_counter, line in enumerate(desc):

        # Checks if we've reached the end, skip the data line and break out of the loop
        if line_counter != len(desc) - 1:
            if '§7Obtained' in desc[line_counter + 1]:
                break

        # Resets the current_line_width so it can start writing again from the start
        current_line_width = 30 + draw_text_start_offset_w

        # Loops through every char in the line
        for char_counter, char in enumerate(line):
            if char == '§':

                # If the char is not at the end
                if char_counter != len(line) - 1:

                    # Set a temp variable to have the current color if that current color is NOT
                    # bold or reset then continue and set the actual variable to the color so it won't set
                    # The color to be bold or reset which are not valid colors but if they come out it will
                    # Make the text stroke width higher or if it's reset it will reset the font, the boldness and the
                    # color. After that it skips so it wont write the color code chars
                    tmp_current_color = color_code_map[f'§{line[char_counter + 1]}']
                    if tmp_current_color not in ['bold', 'reset']:
                        current_color = tmp_current_color
                    else:
                        if tmp_current_color == 'bold':
                            bold = 1
                        else:
                            font = ImageFont.truetype(font_path, size=text_size)
                            current_color = color_code_map['§7']
                            bold = 0
                    continue

            # If the char before the current char is § then skip writing this char because it means it is part
            # of the color coding
            if line[char_counter - 1] == '§':
                continue

            # Draws the char with the right color, font and stroke width and then ups the value of the variable
            # current_line_width With the current char width in pixels and with the
            # char_spacing var so the chars wont overlap.
            # Im drawing each char at a time so i can color each one.
            template_image_draw.text((current_line_width, current_line_height), char, fill=current_color, font=font,
                                     stroke_width=bold)
            current_line_width += font.getsize(char)[0] + char_spacing

        # After each line it will up the value of the variable current_line_height with the height of the last drawn
        # Char in pixels plus the line spacing so the lines wont overlap.
        current_line_height += font.getsize(char)[1] + line_spacing

    tmp_offset = offset // 2

    # After all the text was drawn on the big image it will crop the image to the minimum size possible while
    # keeping the text and then making it a bit larger so we would be able to put the frame in
    bbox = template_image.getbbox()
    template_image = template_image.crop((bbox[0] - tmp_offset, bbox[1] - tmp_offset,
                                          bbox[2] + tmp_offset + tmp_offset // 2,
                                          bbox[3] + tmp_offset + tmp_offset // 2))

    # Changes the original image's size and rotation to fit on all sides of the frame and background
    frame_image = Image.new('RGBA', template_image.size, (0, 0, 0, 0))
    left_frame = Image.open('assets/images/frame.png').resize((tmp_offset, frame_image.size[1] - tmp_offset))
    right_frame = ImageOps.mirror(
        Image.open('assets/images/frame.png').resize((tmp_offset, frame_image.size[1] - tmp_offset)))
    top_frame = Image.open('assets/images/frame.png').rotate(-90, Image.NEAREST, 1).resize(
        (frame_image.size[0] - tmp_offset, tmp_offset))
    bottom_frame = Image.open('assets/images/frame.png').rotate(90, Image.NEAREST, 1).resize(
        (frame_image.size[0] - tmp_offset, tmp_offset))
    background = Image.open('assets/images/background.png').resize(
        (frame_image.size[0] - offset, frame_image.size[1] - offset))

    # Pastes every frame, background and the text to the original image
    frame_image.paste(background, (tmp_offset, tmp_offset), background)
    frame_image.paste(left_frame, (0, tmp_offset // 2), left_frame)
    frame_image.paste(right_frame, (frame_image.size[0] - tmp_offset, tmp_offset // 2), right_frame)
    frame_image.paste(top_frame, (tmp_offset // 2, 0), top_frame)
    frame_image.paste(bottom_frame, (tmp_offset // 2, frame_image.size[1] - tmp_offset), bottom_frame)
    frame_image.paste(template_image, (10 + draw_text_start_offset_w, 10 + draw_text_start_offset_h), template_image)
    return frame_image

    
draw_description(['§6Heroic Flower of Truth §6✪§6✪§6✪', '§7Gear Score: §d726 §8(953)', '§7Damage: §c+180 §e(+20) §8(+248.4)', '§7Strength: §c+360 §e(+20) §9(+40) §8(+496.8)', '§7Bonus Attack Speed: §c+5% §9(+5%) §8(+6.5%)', '§7Intelligence: §a+100 §9(+100) §8(+138)', ' §8[§7❁§8]', '', '§7§lUltimate Wise III§9, §7Cleave V§9, §7Critical V', '§7Cubism V§9, §7Ender Slayer V§9, §7Execute V', '§9Experience III§9, §7First Strike IV§9, §7Giant Killer V', '§7Impaling III§9, §7Lethality V§9, §7Life Steal III', '§9Looting III§9, §7Luck V§9, §9Scavenger III', '§9Sharpness V§9, §9Telekinesis I§9, §7Thunderbolt V', '§7Vampirism V§9, §7Venomous V', '', '§7§cYou do not have a high enough', '§cEnchanting level to use some of', '§cthe enchantments on this item!', '', '§6Ability: Heat-Seeking Rose §e§lRIGHT CLICK', '§7Shoots a rose that ricochets', '§7between enemies, damaging up to', '§7§a3 §7of your foes! Damage', '§7multiplies as more enemies are', '§7hit.', '§8Mana Cost: §37', '§8Cooldown: §a1s', '§7§7The mana cost of this item is', '§7§a10.0% §7of your maximum mana.', '', '§aPerfect 70000 / 70000', '§6§lLEGENDARY DUNGEON SWORD', '', '§7Obtained: §c<local-time timestamp="1627124400000"></local-time>']).save('test.png')