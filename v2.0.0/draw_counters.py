import badger2040

def draw_counters(espresso_count, cappuccino_count, other_count):
    display = badger2040.Badger2040()
    WIDTH = 296
    HEIGHT = 128

    term_espresso = "ESPRESSO"
    term_cappu = "CAPPU"
    term_other = "OTHER"
    
    term_y = HEIGHT - 20
    count_y = HEIGHT - 40

    x_espresso = 41
    x_cappu = 147
    x_other = 253

    display.set_pen(0)
    espresso_text_width = display.measure_text(str(espresso_count), 1)
    term_espresso_width = display.measure_text(term_espresso, 1)
    display.text(str(espresso_count), x_espresso - espresso_text_width // 2, count_y, 1)
    display.text(term_espresso, x_espresso - term_espresso_width // 2, term_y, 1)

    cappuccino_text_width = display.measure_text(str(cappuccino_count), 1)
    term_cappu_width = display.measure_text(term_cappu, 1)
    display.text(str(cappuccino_count), x_cappu - cappuccino_text_width // 2, count_y, 1)
    display.text(term_cappu, x_cappu - term_cappu_width // 2, term_y, 1)

    other_text_width = display.measure_text(str(other_count), 1)
    term_other_width = display.measure_text(term_other, 1)
    display.text(str(other_count), x_other - other_text_width // 2, count_y, 1)
    display.text(term_other, x_other - term_other_width // 2, term_y, 1)