"""Crop each figure (cluster of nearby embedded images, plus vector arrows/labels) from PDF pages as JPEG."""
import sys, pymupdf

pdf, first, last, outdir, prefix = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
doc = pymupdf.open(pdf)
for pno in range(first, last + 1):
    page = doc[pno - 1]
    rects = [r for img in page.get_images(full=True) for r in page.get_image_rects(img[0])
             if r.width > 60 and r.height > 60]
    clusters = []
    for r in rects:
        r = pymupdf.Rect(r)
        for c in clusters:
            if (c + (-15, -15, 15, 15)).intersects(r):
                c |= r
                break
        else:
            clusters.append(r)
    # merge clusters that grew into each other
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if (clusters[i] + (-15, -15, 15, 15)).intersects(clusters[j]):
                    clusters[i] |= clusters.pop(j); merged = True; break
            if merged: break
    for i, c in enumerate(sorted(clusters, key=lambda c: (c.y0, c.x0))):
        clip = (c + (-4, -4, 4, 4)) & page.rect
        name = f"{outdir}/{prefix}_p{pno}_{i}.jpg"
        page.get_pixmap(clip=clip, dpi=150).save(name, jpg_quality=82)
        print(name, [round(v) for v in clip])
