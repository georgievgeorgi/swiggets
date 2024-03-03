class Slider:
    def __init__(self, width):
        self.width = width

    def __call__(self, pos):
        if self.width:
            txt = [' ']*self.width
            txt[0] = '|'
            txt[-1] = '|'
            txt[round(pos*(self.width-1))] = '┃'
            return '<s><small>' + ''.join(txt) + '</small></s>'
        else:
            return ''
