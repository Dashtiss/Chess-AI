def check(cmd, mf):
    m = mf.findNode('pygame')
    if m is None or m.filename is None:
        return None
    return dict(
        prescripts=['py2app.recipes.pygame.preescript'],
        resources=['pygame_icon.tiff', 'pygame_icon.icns'],
    )
