
def build_segpal(words: list, page_dims: tuple, img_dims: tuple):

    x_tolerance = 0.02 * page_dims[1] if img_dims[1] is None else 0.02 * img_dims[1]

    pals = []
    if img_dims[0] is not None:
        for w in words:
            pals.append(
                {
                    'text': w['text'],
                    'x1': round((w['x0'] / page_dims[1]) * img_dims[1]),
                    'y1': round((w['top'] / page_dims[0]) * img_dims[0]),
                    'x2': round((w['x1'] / page_dims[1]) * img_dims[1]),
                    'y2': round((w['bottom'] / page_dims[0]) * img_dims[0])
                }
            )
    else:
        for w in words:
            pals.append(
                {
                    'text': w['text'],
                    'x1': round(w['x0']),
                    'y1': round(w['top']),
                    'x2': round(w['x1']),
                    'y2': round(w['bottom'])
                }
            )

    segments = []
    segment_words = []
    for i, p in enumerate(pals):
        if i == 0:
            segment_words.append(p)
        else:
            if p['y1'] > segment_words[-1]['y2']:   # next word is in other line
                segments.append(segment_words)
                segment_words = [p] # new segment

            elif p['x1'] - segment_words[-1]['x2'] > x_tolerance:   # next word is too far
                segments.append(segment_words)
                segment_words = [p] # new segment
            else:
                segment_words.append(p) # add word to current segment

    if bool(segment_words): # append las segment
        segments.append(segment_words)

    result = []
    for seg in segments:
        seg_x1 = min([pal['x1'] for pal in seg])
        seg_x2 = max([pal['x2'] for pal in seg])
        seg_y1 = min([pal['y1'] for pal in seg])
        seg_y2 = max([pal['y2'] for pal in seg])

        seg_pals = []
        for pal in seg:
            seg_pals.append(
                {
                    'palabra': pal['text'],
                    'bbox': f"{pal['x1']:05d} {pal['y1']:05d} {pal['x2']:05d} {pal['y2']:05d}"
                }
            )

        result.append(
            {
                'bbox': f"{seg_x1} {seg_y1} {seg_x2} {seg_y2}",
                'palabras': seg_pals
            }
        )

    return result