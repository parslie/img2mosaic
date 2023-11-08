# import random

# from arguments.parsers import Arguments
# from data.cache import load_cache, save_cache
# from data.palette import load_palette
# from utils import colors_to_closest_key, key_to_colors


# def all_single_color_keys():
#     r_values = list(range(256))
#     random.shuffle(r_values)
#     for r in r_values:
#         g_values = list(range(256))
#         random.shuffle(g_values)
#         for g in g_values:
#             b_values = list(range(256))
#             random.shuffle(b_values)
#             for b in b_values:
#                 yield f'{r} {g} {b}'


# def all_color_keys_helper(color_count: int):
#     for color_key in all_single_color_keys():
#         if color_count == 1:
#             yield f'{color_key}'
#         else:
#             for next_color_key in all_color_keys_helper(color_count - 1):
#                 yield f'{color_key} {next_color_key}'


# def all_color_keys(args: Arguments):
#     for color_key in all_color_keys_helper(args.density ** 2):
#         yield color_key


# def total_color_count(args: Arguments):
#     per_density_count = 256 * 256 * 256
#     count = 1
#     for _ in range(args.density ** 2):
#         count *= per_density_count
#     return count


# def generate_cache(args: Arguments):
#     cache = load_cache(args)
#     palette = load_palette(args)

#     color_count = total_color_count(args)
#     if len(str(color_count)) > 9:
#         color_count = f'{color_count:.3e}'
#     colors_cached = 0

#     print(f'0 / {color_count} ', end='\r')
#     for idx, color_key in enumerate(all_color_keys(args)):
#         if len(str(idx)) > 9:
#             print(f'{idx + 1:.3e} / {color_count} ', end='\r')
#         else:
#             print(f'{idx} / {color_count} ', end='\r')

#         if args.all or color_key not in cache.keys():
#             colors = key_to_colors(color_key)
#             closest_key = colors_to_closest_key(palette, colors)
#             cache[color_key] = closest_key

#             colors_cached += 1
#             if colors_cached % 10 == 0:
#                 save_cache(args, cache)
#     print()
    
#     save_cache(args, cache)