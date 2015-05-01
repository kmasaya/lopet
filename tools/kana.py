#!python32
#coding:utf8

# copyright: http://www.shido.info/py/python_kana.html

"""
かな変換ライブラリ

変換関数:
zj(s): s に含まれる 全角カタカナをひらがなに変換
jz(s): s に含まれる ひらがなを全角カタカナに変換
zh(s): s に含まれる 全角カタカナを半角カタカナに変換
jh(s): s に含まれる ひらがなを半角カタカナに変換
hz(s): s に含まれる 半角カタカナを全角カタカナに変換
hj(s): s に含まれる 半角カタカナをひらがなに変換

ノート
str.translate メソッドをつかって変換。
それに加えて以下の操作を行う

半角カタカナから変換する場合:
半角カタカナの濁音は2文字で表されるので、それらを正規表現を用いて制御文字1文字 (&#x80 --&#xA0)
におきかえてから translate を用いて全角の濁音に置き換える。

平仮名から変換する場合:
う゛を ヴ に置き換えてから translate で変換する。

平仮名に変換する場合
translate の結果の ヴ を う゛に置き換える。
"""

import re, functools

C_OFF = 0x80

S_HIR = '、。「」　ー０１２３４５６７８９' \
          'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん' \
            'っぁぃぅぇぉゃゅょ' \
              'がぎぐげござじずぜぞだぢづでどばびぶべぼヴ' \
                'ぱぴぷぺぽ' \

S_ZEN = '、。「」　ー０１２３４５６７８９' \
          'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン' \
            'ッァィゥェォャュョ'  \
              'ガギグゲゴザジズゼゾダヂヅデドバビブベボヴ' \
                'パピプペポ'

S_SEI = '､｡｢｣ -0123456789'  \
           'ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ' \
             'ｯｧｨｩｪｫｬｭｮ'
S_DAK ='ｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾊﾋﾌﾍﾎｳ'
S_HAT ='ﾊﾋﾌﾍﾎ'
TENN, MARU = 'ﾞ', 'ﾟ'

L_DAK = [c+TENN for c in S_DAK] + [c+MARU for c in S_HAT]
S_CCH = ''.join(chr(i+C_OFF) for i in range(len(L_DAK)))
S_HAN = S_SEI + S_CCH
L_HAN = list(S_SEI) + L_DAK
H_DAK = dict(zip(L_DAK, S_CCH))
R_DAK = re.compile('[{}]{}|[{}]{}'.format(S_DAK, TENN, S_HAT, MARU))

def comb(*fs):
    return lambda x: functools.reduce(lambda y,f:f(y), fs, x)

def trans(k,v):
    assert len(k)==len(v)
    tbl = str.maketrans(k,v) if type(v) is str else \
          str.maketrans(dict(zip(k,v)))
    return lambda s: s.translate(tbl)

def replace(c0, c1): return lambda s: s.replace(c0,c1)
subd = lambda s: R_DAK.sub(lambda m:H_DAK[m.group()], s)

zj=comb(trans(S_ZEN, S_HIR), replace('ヴ', 'う゛'))
jz=comb(replace('う゛', 'ヴ'), trans(S_HIR, S_ZEN))
zh=trans(S_ZEN, L_HAN)
jh=comb(replace('う゛', 'ヴ'), trans(S_HIR, L_HAN))
hz=comb(subd, trans(S_HAN, S_ZEN))
hj=comb(subd, trans(S_HAN, S_HIR), replace('ヴ', 'う゛'))


def test(name, fun, s):
    print(name, 'ok' if s==fun(s) else 'ng', sep=' .... ')
    
if __name__=='__main__':
    test('zen>han>zen', comb(zh, hz), S_ZEN)
    test('zen>hira>zen', comb(zj, jz), S_ZEN)
    
    s_hir = S_HIR.replace('ヴ', 'う゛')
    test('hira>zen>hira', comb(jz, zj), s_hir)
    test('hira>han>hira', comb(jh, hj), s_hir)
    
    s_han=''.join(L_HAN)
    test('han>hira>han', comb(hj, jh), s_han)
    test('han>zen>han', comb(hz, zh), s_han)
    