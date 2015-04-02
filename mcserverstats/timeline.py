import os
from urllib.request import urlopen
from mcserverstats import timeutils

try:
    import cairocffi as cairo
except ImportError:
    import cairo

########## PNG helpers ##########

def color_from_uuid(uuid, settings):
    return settings['color_%x' % (ord(uuid[0]) % 16)]

default_settings = {
    'font_name': 'sans',
    'bg_color': [0, 0, 0, 0.0],
    'border': 10,
    'line_border': 10,

    'title_border': 15,
    'title_height': 30,
    'title_color': [0, 0, 0],
    'title_shadow_color': [0, 0, 0, 0.0],
    'title_shadow_offset': [2.2, 2.2],

    'scale_line_width': 2,
    'scale_line_width_noon': 4,
    'scale_line_width_midnight': 7,
    'scale_gap': 40,
    'scale_height': 15,
    'scale_color': [0, 0, 0],
    'scale_shadow_color': [0, 0, 0, 0.0],
    'scale_shadow_offset': [1.8, 1.8],

    'name_radius': 5,
    'name_border': 5,
    'name_height': 24,
    'name_color': [1, 1, 1],
    'name_shadow_color': [0, 0, 0, 0.5],
    'name_shadow_offset': [1.8, 1.8],

    'uptimes_height': 10,
    'uptimes_color': [0, 1, 0],

    'color_0': [0.0, 0.0, 0.0],
    'color_1': [0.0, 0.0, 0.7],
    'color_2': [0.0, 0.7, 0.0],
    'color_3': [0.0, 0.7, 0.7],
    'color_4': [0.7, 0.0, 0.0],
    'color_5': [0.7, 0.0, 0.7],
    'color_6': [1.0, 0.7, 0.0],
    'color_7': [0.7, 0.7, 0.7],
    'color_8': [0.3, 0.3, 0.3],
    'color_9': [0.3, 0.3, 1.0],
    'color_a': [0.3, 1.0, 0.3],
    'color_b': [0.3, 1.0, 1.0],
    'color_c': [1.0, 0.3, 0.3],
    'color_d': [1.0, 0.3, 1.0],
    'color_e': [1.0, 1.0, 0.3],
    'color_f': [1.0, 1.0, 1.0],

    'color_from_uuid': color_from_uuid,
}

def color_from_char(color_char, settings):
    color = settings.get('color_'+color_char, [0,0,0])
    return color

# Thanks Phlip! http://stackoverflow.com/a/18792190
class SettingsDict(dict):
    def __init__(self, **kwargs):
        super(SettingsDict, self).__init__(**kwargs)
        self.__dict__ = self

LEFT = 'left'
CENTER = 'center'
RIGHT = 'right'

def fit_text(c, text, max_w):
    width = lambda: c.text_extents(text)[2]
    if not max_w or not text or width() <= max_w:
        return text  # done
    ellipsis = '~'
    text += ellipsis
    while width() > max_w and text != ellipsis:
        text = text[:-2] + ellipsis
    return text if text != ellipsis else ''

def draw_text(c, text, color, x_left, y_center, align=LEFT, max_w=None, shadow=None):
    """
    :param c: cairo drawing context
    :param text: the text to draw
    :param color: list or tuple with RGB or RGBA colors, floats from 0.0 to 1.0
    :param x_left: left end of text space
    :param y_center: vertical center of text space
    :param align: 'left', 'center', 'right'
    :param max_w: maximum width the text might use, set this to 0 for center/right alignment starting from x_left
    :param shadow: tuple of (color, (offset_x, offset_y))
    """
    text = fit_text(c, text, max_w)
    if not text:
        return  # do not draw
    x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = c.text_extents(text)
    if not max_w:  # set for centering/right aligning
        max_w = 0
    x = x_left - x_bearing
    y = y_center - y_bearing - text_height/2
    if align == CENTER:
        x += (max_w - text_width) / 2
    elif align == RIGHT:
        x += max_w - text_width
    if shadow:
        s_color, s_offset = shadow
        s_dx, s_dy = s_offset
        c.move_to(x + s_dx, y + s_dy)
        c.set_source_rgba(*s_color)
        c.show_text(text)
    c.move_to(x, y)
    c.set_source_rgba(*color)
    c.show_text(text)
    return text_width

def draw_rounded_rect(c, color, x, y, w, h, radius=0, border=None):
    if radius == 0:
        c.rectangle(x, y, w, h)
    else:
        radius = min(radius, w / 2, h / 2)
        degrees = 3.1416 * 2 / 360
        c.new_sub_path()
        c.arc(x + w - radius, y + radius, radius, -90 * degrees, 0 * degrees)
        c.arc(x + w - radius, y + h - radius, radius, 0 * degrees, 90 * degrees)
        c.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)
        c.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        c.close_path()
    c.set_source_rgba(*color)
    if not border:
        c.fill()
    else:
        c.fill_preserve()
        border_w, *border_color = border
        c.set_line_width(border_w)
        c.set_source_rgba(*border_color)
        c.stroke()

def dark_border(width, color):
    r, g, b = map(lambda c: c / 2, color)
    return width, r, g, b

skin_cache = {}

def draw_head(c, x, y, h, name):
    if name not in skin_cache:
        skin_url = 'http://skins.minecraft.net/MinecraftSkins/%s.png' % name
        skin_cache[name] = cairo.ImageSurface.create_from_png(urlopen(skin_url))
    c.save()
    c.translate(x, y)
    c.scale(h/8, h/8)
    def copy_8x8_at(r_x, r_y=8):
        c.set_source_surface(skin_cache[name], -r_x, -r_y)
        c.get_source().set_filter(cairo.FILTER_NEAREST)
        c.rectangle(0, 0, 8, 8)
        c.fill()
    copy_8x8_at(8)  # face
    try:
        data = skin_cache[name].get_data()
    except NotImplementedError:
        print('Hat rendering disabled. Install cairocffi or check if your pycairo installation supports Surface.get_data().')
    else:
        if data[0][0] == 0:
            copy_8x8_at(40)  # hat
    c.restore()

def draw_timeline(timeline_data, img_path, title='', im_width=None, settings=default_settings, **kwargs):
    """
    /-----border------\
    | |||||scale||||| |
    | ||line_border|| |
    | ----uptimes---- |
    | ||line_border|| |
    | /-name_border-\ |
    | | NAME ====== | |
    | \-name_border-/ |
    |   line_border   |
    | (===)    (====) |
    |   line_border   |
    | (==========)    |
    | ||line_border|| |
    |---title_border--|
    |     [TITLE]     |
    \-----border------/
    """
    for key in kwargs:
        settings[key] = kwargs[key]
    s = SettingsDict(**settings)

    t_start, t_end, lines, uptimes = timeline_data
    if not im_width:
        im_width = int((t_end - t_start) / 3600 * s.scale_gap)  # TODO

    # calculate sizes
    title_box_height = s.title_height + s.title_border \
        if len(title) > 0 and s.title_height > 0 else 0
    scale_box_height = s.scale_height + 2 * s.line_border \
        if s.scale_height > 0 else 0
    line_height = 2 * s.name_border + s.name_height
    line_box_height = s.line_border + line_height
    im_height = 2 * s.border \
                + title_box_height + scale_box_height + s.uptimes_height + s.line_border \
                + line_box_height * (len(lines) - 1) + line_height
    inner_width = im_width - 2 * s.border
    h_stretch = inner_width / (t_end - t_start)
    s.name_radius = min(s.name_radius, s.name_height / 2 + s.name_border)
    name_horiz_border = max(s.name_border, s.name_radius)

    # start drawing
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, im_width, im_height)
    c = cairo.Context(surface)
    c.select_font_face(s.font_name)
    c.set_source_rgba(*s.bg_color)
    c.paint()

    # draw title
    c.set_font_size(s.title_height)
    draw_text(c, title, s.title_color, s.border, im_height - (s.border + s.title_height / 2), CENTER,
              im_width - s.border, shadow=(s.title_shadow_color, s.title_shadow_offset))

    # draw scale
    c.set_source_rgba(*s.scale_color)
    c.set_line_width(s.scale_line_width)
    c.set_font_size(s.scale_height)
    scale_line_y = s.border + s.scale_height
    scale_line_dy = line_box_height * len(lines) + s.line_border * 2 + s.uptimes_height
    for sec in range((t_start // 3600) * 3600, t_end + 3600, 3600):
        if sec < t_start or sec > t_end:
            continue  # out of range by rounding
        hour_text = timeutils.epoch_to_date_str(sec, '%k')  # hour 0-23, space padded
        if hour_text == ' 0': c.set_line_width(s.scale_line_width_midnight)
        elif hour_text == '12': c.set_line_width(s.scale_line_width_noon)
        scale_line_x = int(s.border + (sec - t_start) * h_stretch) - c.get_line_width() / 2
        c.move_to(scale_line_x, scale_line_y)
        c.rel_line_to(0, scale_line_dy)
        c.stroke()
        if hour_text in (' 0', '12'): c.set_line_width(s.scale_line_width)
        # TODO rotate by 90 degrees
        draw_text(c, hour_text, s.scale_color, scale_line_x, s.border + s.scale_height / 2,
                  CENTER, None, shadow=(s.scale_shadow_color, s.scale_shadow_offset))

    # draw uptimes
    for t_from, t_to in uptimes:
        x = s.border + (t_from - t_start) * h_stretch
        w = (t_to - t_from) * h_stretch
        draw_rounded_rect(c, s.uptimes_color, x, scale_box_height,
                          w, s.uptimes_height,
                          s.uptimes_height, (2, 0,0,0))

    # draw sessions
    y_offset = s.border + scale_box_height + s.uptimes_height
    c.set_font_size(s.name_height)
    for i, line in enumerate(lines):
        y = i * line_box_height + y_offset
        for session in line:
            uuid, t_from, t_to, name = session
            color = s.color_from_uuid(uuid, settings)
            x = s.border + (t_from - t_start) * h_stretch
            w = (t_to - t_from) * h_stretch
            draw_rounded_rect(c, color, x, y, w, line_height, s.name_radius, dark_border(2, color))
            t_x = x + name_horiz_border
            h_y = y + s.name_border
            t_y = h_y + s.name_height / 2
            if w > s.name_height + 2 * s.name_border:
                draw_head(c, t_x, h_y, s.name_height, name)
            draw_text(c, name, s.name_color, t_x, t_y, max_w=w - 2 * name_horiz_border,
                      shadow=(s.name_shadow_color, s.name_shadow_offset))

    # save image
    surface.write_to_png(img_path)

########## HTML helpers ##########

def file_exists(path):
    os.makedirs(os.path.split(path)[0], exist_ok=True)
    return os.path.isfile(path)

image_path = 'timeline_files'

def bg_scale_path(bg_width):
    return '%s/bg_scale_%s.png' % (image_path, bg_width)

def head_path(name, height=32):
    return '%s/%s_%s.png' % (image_path, name, height)

def gen_bg_scale(bg_width):
    print('gen bg', bg_width)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, bg_width*2,1)
    c = cairo.Context(surface)
    c.set_source_rgba(0,0,0, 0.3)
    c.rectangle(0,0, bg_width,1)
    # c.set_line_width(1)
    c.stroke()
    surface.write_to_png(bg_scale_path(bg_width))

def gen_head(name, height=32):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, height, height)
    c = cairo.Context(surface)
    draw_head(c, 0, 0, height, name)
    surface.write_to_png(head_path(name, height))

def get_timeline_html(timeline_data, title='', bg_width=30):
    t_start, t_end, lines, uptimes = timeline_data

    sec_per_hour = 3600
    sec_to_screen = lambda t: t * bg_width / sec_per_hour

    player_colors = {
        'Gjum': '#48f',
        'HHL': '#f80',
        'Ulexos': '#0f0',
        'Offlinegott': '#f00',
    } # map of name -> color
    template_style_player = '.tl_user_%(name)s span{background-color:%(color)s}'
    html_style_players = ''.join(template_style_player % {
        'name': name, 'color': color,
    } for name, color in player_colors.items())

    template_session = '<span style="left:%(start)spx;width:%(duration)spx"></span>'
    def session_to_html(t_from, t_to):
        start = sec_to_screen(t_from - t_start)
        duration = sec_to_screen(t_to - t_from)
        return template_session % {
            'start': start, 'duration': duration - 4,
        }

    template_player_sessions = \
        '<tr><td class="tl_sessions tl_user_%(name)s">' \
        '%(sessions)s' \
        '</td><td><img height="16px" src="'+head_path('%(name)s')+'"/></td><td>%(name)s</td></tr>'
    html_all_player_sessions = ''
    for line in lines:
        last_name = line[-1][-1]
        html_sessions = ''
        for uuid, t_from, t_to, name in line:
            html_sessions += session_to_html(t_from, t_to)
        html_all_player_sessions += template_player_sessions % {
            'name':last_name, 'sessions': html_sessions
        }
        if not file_exists(head_path(last_name)):
            gen_head(last_name)

    html_uptimes = ''.join(session_to_html(t_from, t_to) for t_from, t_to in uptimes)

    html_hours = ''
    bg_offset = None
    for sec in range((t_start // sec_per_hour) * sec_per_hour,
                     t_end + sec_per_hour, sec_per_hour):
        if sec < t_start or sec >= t_end:
            continue  # out of range by rounding
        if bg_offset is None:  # first drawn hour
            bg_offset = sec_to_screen(sec - t_start)
        hour_text = timeutils.epoch_to_date_str(sec, '%k')  # hour 0-23, space padded
        html_hours += '<span>%s</span>' % hour_text
    if not file_exists(bg_scale_path(bg_width)):
        gen_bg_scale(bg_width)

    page_data = {
        'title_text': title,
        'bgwidth': bg_width,
        'bgoffset': bg_offset,
        'style_players': html_style_players,
        'hours': html_hours,
        'uptimes': html_uptimes,
        'players': html_all_player_sessions,
    }
    template_timeline = \
        '<style type="text/css">' \
        '.timeline td{margin:0px;padding:0px}' \
        '.timeline span{display:inline-block;overflow:hidden}' \
        '.tl_hours span{width:%(bgwidth)spx}' \
        '.tl_hours,.tl_uptimes,.tl_sessions{background-image:url('+bg_scale_path('%(bgwidth)s')+');background-position:%(bgoffset)spx 0px;background-repeat:repeat;position:relative;height:20px}' \
        '.tl_uptimes span,.tl_sessions span{background-color:rgba(128,128,128,0.3);border:2px solid rgba(0,0,0,0.4);height:12px;position:absolute;top:2px;' \
        'border-radius:8px;-moz-border-radius:8px}' \
        '.tl_uptimes span{background-color:#0f0;border-color:black;height:6px;top:5px}' \
        '%(style_players)s' \
        '</style><table class="timeline" style="border-collapse:collapse">' \
        '<tr><td class="tl_hours" style="padding-left:%(bgoffset)spx">' \
        '%(hours)s' \
        '</td><td colspan="2">Hours</td></tr>' \
        '<tr><td class="tl_uptimes">' \
        '%(uptimes)s' \
        '</td><td colspan="2">Server online</td></tr>' \
        '%(players)s' \
        '<tr><td colspan=3 align="center" class="tl_title" style="font-size:20px">%(title_text)s</td></tr>' \
        '</table>'
    return template_timeline % page_data

def write_timeline_html_page(timeline_data, page_path, title='', bg_width=30):
    html_page = '<html><body style="margin:0px">' \
                + get_timeline_html(timeline_data, title, bg_width) + \
                '</body></html>'
    with open(page_path, 'w') as out_file:
        out_file.write(html_page)

def get_timeline_data(logs, from_date=None, to_date=None):
    lines = list(logs.collect_user_sessions(from_date, to_date).values())
    uptimes = list(logs.collect_uptimes(from_date, to_date))
    t_start = int(min(uptimes[0][0] if uptimes else float('inf'),
                      timeutils.date_str_to_epoch(from_date) \
                      or min(s[1] for sessions in lines for s in sessions)))
    t_end = int(max(uptimes[-1][1] if uptimes else float('-inf'),
                    timeutils.date_str_to_epoch(to_date) \
                    or max(s[2] for sessions in lines for s in sessions)))
    return t_start, t_end, lines, uptimes

def main():
    from mcserverstats import logalyzer
    logs = logalyzer.LogDirectory('test_logs/')
    timeline_data = get_timeline_data(logs, None, None)
    t_start, t_end = timeline_data[:2]
    title = '%s to %s' % (timeutils.human_date_str(timeutils.epoch_to_date_str(t_start)),
                          timeutils.human_date_str(timeutils.epoch_to_date_str(t_end)) or 'last activity')

    draw_timeline(timeline_data, 'test.png', title)
    write_timeline_html_page(timeline_data, 'test.html', title)

if __name__ == '__main__':
    main()
