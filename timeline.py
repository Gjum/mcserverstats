import cairo
import logalyzer

"""
/-----border------\
|     [TITLE]     |
|---title_border--|
| /-name_border-\ |
| | NAME ====== | |
| \-name_border-/ |
|   line_border   |
| (===)    (====) |
|   line_border   |
| (==========)    |
\-----border-----/
"""

default_settings = {
    'font_name': 'sans',
    'bg_color': [0.6, 0.6, 0.6, 0.2],
    'border': 10,
    'line_border': 10,

    'title_height': 30,
    'title_border': 15,
    'title_color': [0.2, 0.2, 0.2],
    'title_shadow_color': [0, 0, 0, 0.0],
    'title_shadow_offset': [1.5, 1.5],

    'time_height': 20,
    'time_color': [0.2, 0.2, 0.2],
    'time_shadow_color': [0, 0, 0, 0.0],
    'time_shadow_offset': [1.5, 1.5],

    'name_height': 20,
    'name_border': 5,
    'name_radius': 0,  # TODO 5
    'name_color': [1, 1, 1],
    'name_shadow_color': [0, 0, 0, 0.5],
    'name_shadow_offset': [1.5, 1.5],

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
}

color_by_uuid = {
    '1234-1234': '1',
    '1234-4321': '3',
}

def get_color(color_char, settings):
    color = settings.get('color_'+color_char, [0,0,0])
    return color

def draw_text(c, color, text, x_left, y_center, align=0, shadow=None):
    """
    x: left end of text space
    y: vertical center of text space
    align:
        positive: center between x and x+align
        0: left-aligned
        negative: right-aligned
    """
    x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = c.text_extents(text)
    x = x_left - x_bearing
    y = y_center - y_bearing - text_height/2
    if align > 0:
        x += (align - text_width) / 2
    elif align < 0:
        raise NotImplementedError()
    if shadow:
        s_color, s_offset = shadow
        s_dx, s_dy = s_offset
        c.move_to(x + s_dx, y + s_dy)
        c.set_source_rgba(*s_color)
        c.show_text(text)
    c.move_to(x, y)
    c.set_source_rgba(*color)
    c.show_text(text)

def draw_rounded_rect(c, color, x, y, w, h, radius=0):
    c.set_source_rgba(*color)
    if radius == 0:
        print('rect %s:%s %sx%s' % (x,y, w,h))
        c.rectangle(x, y, w, h)
    else:
        print('AAA')
        c.move_to(x, y)
        c.rel_line_to(w, 0)
        c.rel_line_to(0, h)
        c.rel_line_to(-w, 0)
        c.close_path()
    c.fill()

def draw_timeline(path, im_width, title='', settings=default_settings, **kwargs):
    for key in kwargs:
        settings[key] = kwargs[key]

    # TODO get sessions
    t_start, t_end, lines = 100, 130, (
        (
            ('1234-1234', 100, 107, 'name'),
            ('1234-1234', 112, 120, '...'),
        ),
        (
            ('1234-4321', 105, 115, 'fghij'),
            ('1234-4321', 118, 130, 'foo'),
        ),
    )

    # calculate sizes
    s = settings
    title_box_height = s['title_height'] + s['title_border'] \
        if len(title) > 0 else 0
    line_height = 2 * s['name_border'] + s['name_height']
    line_box_height = s['line_border'] + line_height
    im_height = 2 * s['border'] \
             + title_box_height \
             + line_box_height * (len(lines) - 1) + line_height
    h_scale = (im_width - 2 * s['border']) / (t_end - t_start)

    # draw image
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, im_width, im_height)
    c = cairo.Context(surface)
    c.select_font_face(s['font_name'])
    c.set_source_rgba(*s['bg_color'])
    c.paint()

    # TODO draw title
    c.set_font_size(s['title_height'])
    draw_text(c, s['title_color'], title,
              s['border'], im_height - (s['border'] + s['title_height'] / 2),
              im_width - s['border'],
              shadow=(s['title_shadow_color'], s['title_shadow_offset']))

    # TODO draw timeline
    c.set_font_size(s['time_height'])

    # draw lines
    c.set_font_size(s['name_height'])
    radius = s['name_radius']
    for i, line in enumerate(lines):
        y = i * line_box_height + s['border']
        for session in line:
            uuid, t_from, t_to, name = session
            color = get_color(color_by_uuid[uuid], s)
            x = s['border'] + (t_from - t_start) * h_scale
            w = (t_to - t_from) * h_scale
            draw_rounded_rect(c, color, x, y, w, line_height, radius)
            t_x = x + s['name_border']
            t_y = y + s['name_border'] + s['name_height'] / 2
            draw_text(c, s['name_color'], name, t_x, t_y,
                      shadow=(s['name_shadow_color'], s['name_shadow_offset']))

    # save image
    surface.write_to_png(path)

if __name__ == '__main__':
    draw_timeline('test.png', 610, 'Title! Yey!')