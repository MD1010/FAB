from consts.prices.prices_consts import MAP_INC_DEC_PRICES


def calc_new_max_price(down_limit, up_limit, is_inc):
    if is_inc:
        return down_limit + abs(up_limit - down_limit) / 2
    else:
        return up_limit - abs(up_limit - down_limit) / 2


def get_scale_from_dict(upper_bound, lower_bound):
    possible_scales = []
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if int(values[0]) < upper_bound < int(values[1]):
            possible_scales.append(int(element[1]))
        elif int(values[0]) < lower_bound < int(values[1]):
            possible_scales.append(int(element[1]))
    return possible_scales
