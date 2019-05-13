import pydotplus
import subprocess

class Morph:
    """
    1つの形態素を表すクラス
    """

    def __init__(self, surface, base, pos, pos1):
        """
        メンバ変数として表層形（surface），基本形（base），品詞（pos），品詞細分類1（pos1）を持つ.
        """
        self.surface = surface
        self.base = base
        self.pos = pos
        self.pos1 = pos1

    def is_end_of_sentence(self) -> bool: return self.pos1 == '句点'

    def __str__(self) -> str: return 'surface: {}, base: {}, pos: {}, pos1: {}'.format(self.surface, self.base, self.pos, self.pos1)


def make_morph_list(analyzed_file_name: str) -> list:
    """
    係り受け解析済みの文章ファイルを読み込んで、各文をMorphオブジェクトのリストとして表現する
    :param analyzed_file_name 係り受け解析済みの文章ファイル名
    :return list 一つの文章をMorphオブジェクトのリストとして表現したもののリスト
    """
    sentences = []
    sentence = []
    with open(analyzed_file_name, encoding='utf-8') as input_file:
        for line in input_file:
            line_list = line.split()
            if (line_list[0] == '*') | (line_list[0] == 'EOS'):
                pass
            else:
                line_list = line_list[0].split(',') + line_list[1].split(',')
                # この時点でline_listはこんな感じ
                # ['始め', '名詞', '副詞可能', '*', '*', '*', '*', '始め', 'ハジメ', 'ハジメ']
                _morph = Morph(surface=line_list[0], base=line_list[7], pos=line_list[1], pos1=line_list[2])

                sentence.append(_morph)

                if _morph.is_end_of_sentence():
                    sentences.append(sentence)
                    sentence = []

    return sentences


morphed_sentences = make_morph_list('neko.txt.cabocha')

# 3文目の形態素列を表示
for morph in morphed_sentences[2]:
    print(str(morph))

##以下41番#####################################################################################

class Chunk:
    def __init__(self, morphs: list, dst: str, srcs: str) -> None:
        """
        形態素（Morphオブジェクト）のリスト（morphs），係り先文節インデックス番号（dst），係り元文節インデックス番号のリスト（srcs）をメンバ変数に持つ
        """
        self.morphs = morphs
        self.dst = int(dst.strip("D"))
        self.srcs = int(srcs)

    # 以下は後々使うメソッドです.
    def join_morphs(self) -> str:
        return ''.join([_morph.surface for _morph in self.morphs if _morph.pos != '記号'])

    def has_noun(self) -> bool:
        return any([_morph.pos == '名詞' for _morph in self.morphs])

    def has_verb(self) -> bool:
        return any([_morph.pos == '動詞' for _morph in self.morphs])

    def has_particle(self) -> bool:
        return any([_morph.pos == '助詞' for _morph in self.morphs])

    def has_sahen_connection_noun_plus_wo(self) -> bool:
        """
        「サ変接続名詞+を（助詞）」を含むかどうかを返す.
        """
        for idx, _morph in enumerate(self.morphs):
            if _morph.pos == '名詞' and _morph.pos1 == 'サ変接続' and len(self.morphs[idx:]) > 1 and \
                            self.morphs[idx + 1].pos == '助詞' and self.morphs[idx + 1].base == 'を':
                return True

        return False

    def first_verb(self) -> Morph:
        return [_morph for _morph in self.morphs if _morph.pos == '動詞'][0]

    def last_particle(self) -> list:
        return [_morph for _morph in self.morphs if _morph.pos == '助詞'][-1]

    def pair(self, sentence: list) -> str:
        return self.join_morphs() + '\t' + sentence[self.dst].join_morphs()

    def replace_noun(self, alt: str) -> None:
        """
        名詞の表象を置換する.
        """
        for _morph in self.morphs:
            if _morph.pos == '名詞':
                _morph.surface = alt

    def __str__(self) -> str:
        return 'srcs: {}, dst: {}, morphs: ({})'.format(self.srcs, self.dst, ' / '.join([str(_morph) for _morph in self.morphs]))


def make_chunk_list(analyzed_file_name: str) -> list:
    """
    係り受け解析済みの文章ファイルを読み込んで、各文をChunkオブジェクトのリストとして表現する
    :param analyzed_file_name 係り受け解析済みの文章ファイル名
    :return list 一つの文章をChunkオブジェクトのリストとして表現したもののリスト
    """
    sentences = []
    sentence = []
    _chunk = None
    with open(analyzed_file_name, encoding='utf-8') as input_file:
        for line in input_file:
            line_list = line.split()
            if line_list[0] == '*':
                if _chunk is not None:
                    sentence.append(_chunk)
                _chunk = Chunk(morphs=[], dst=line_list[2], srcs=line_list[1])
            elif line_list[0] == 'EOS':  # End of sentence
                if _chunk is not None:
                    sentence.append(_chunk)
                if len(sentence) > 0:
                    sentences.append(sentence)
                _chunk = None
                sentence = []
            else:
                line_list = line_list[0].split(',') + line_list[1].split(',')
                # この時点でline_listはこんな感じ
                # ['始め', '名詞', '副詞可能', '*', '*', '*', '*', '始め', 'ハジメ', 'ハジメ']
                _morph = Morph(surface=line_list[0], base=line_list[7], pos=line_list[1], pos1=line_list[2])
                _chunk.morphs.append(_morph)

    return sentences


chunked_sentences = make_chunk_list('neko.txt.cabocha')

# 3文目の形態素列を表示
for chunk in chunked_sentences[2]:
    print(str(chunk))

##以下42番#####################################################################################

def is_valid_chunk(_chunk, sentence):
    return _chunk.join_morphs() != '' and _chunk.dst > -1 and sentence[_chunk.dst].join_morphs() != ''


paired_sentences = [[chunk.pair(sentence) for chunk in sentence if is_valid_chunk(chunk, sentence)] for sentence in chunked_sentences if len(sentence) > 1]
print(paired_sentences[0:100])

##以下43番#####################################################################################

for sentence in chunked_sentences:
    for chunk in sentence:
        if chunk.has_noun() and chunk.dst > -1 and sentence[chunk.dst].has_verb():
            print(chunk.pair(sentence))


##以下45番#####################################################################################

def case_patterns(_chunked_sentences: list) -> list:
    """
    動詞の格のパターン(動詞と助詞の組み合わせ)のリストを返します.(「格」は英語で"Case"というらしい.)
    :param _chunked_sentences チャンク化された形態素を文章ごとにリスト化したもののリスト
    :return 格のパターン(例えば['与える', ['に', 'を']])のリスト
    """
    _case_pattern = []
    for sentence in _chunked_sentences:
        for _chunk in sentence:
            if not _chunk.has_verb():
                continue

            particles = [c.last_particle().base for c in sentence if c.dst == _chunk.srcs and c.has_particle()]

            if len(particles) > 0:
                _case_pattern.append([_chunk.first_verb().base, sorted(particles)])

    return _case_pattern


def save_case_patterns(_case_patterns: list, file_name: str) -> None:
    """
    動詞の格のパターン(動詞と助詞の組み合わせ)のリストをファイルに保存します.
    :param _case_patterns 格のパターン(例えば['与える', ['に', 'を']])のリスト
    :param file_name 保存先のファイル名
    """
    with open(file_name, mode='w', encoding='utf-8') as output_file:
        for _case in _case_patterns:
            output_file.write('{}\t{}\n'.format(_case[0], ' '.join(_case[1])))


save_case_patterns(case_patterns(chunked_sentences), 'case_patterns.txt')


def print_case_pattern_ranking(_grep_str: str) -> None:
    """
    コーパス(case_pattern.txt)中で出現頻度の高い順に上位20件をUNIXコマンドを用いてを表示する.
    `cat case_patterns.txt | grep '^する\t' | sort | uniq -c | sort -r | head -20`のようなUnixコマンドを実行してprintしている.
    grepの部分は引数`_grep_str`に応じて付加される.
    :param _grep_str 検索条件となる動詞
    """
    _grep_str = '' if _grep_str == '' else '| grep \'^{}\t\''.format(_grep_str)
    print(subprocess.run('cat case_patterns.txt {} | sort | uniq -c | sort -r | head -10'.format(_grep_str), shell=True))


# コーパス中で頻出する述語と格パターンの組み合わせ（上位10件）
# 「する」「見る」「与える」という動詞の格パターン（コーパス中で出現頻度の高い順に上位10件）
for grep_str in ['', 'する', '見る', '与える']:
    print_case_pattern_ranking(grep_str)

##以下44番#####################################################################################

def sentence_to_dot(idx: int, sentence: list) -> str:
    head = "digraph sentence{} ".format(idx)
    body_head = "{ graph [rankdir = LR]; "
    body_list = ['"{}"->"{}"; '.format(*chunk_pair.split()) for chunk_pair in sentence]

    return head + body_head + ''.join(body_list) + '}'


def sentences_to_dots(sentences: list) -> list:
    _dots = []
    for idx, sentence in enumerate(sentences):
        _dots.append(sentence_to_dot(idx, sentence))
    return _dots


def save_graph(dot: str, file_name: str) -> None:
    g = pydotplus.graph_from_dot_data(dot)
    g.write_jpeg(file_name, prog='dot')


dots = sentences_to_dots(paired_sentences)
for idx in range(101, 104):
    save_graph(dots[idx], 'graph{}.jpg'.format(idx))
