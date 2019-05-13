import CaboCha
import pydotplus
import subprocess
def make_analyzed_file(input_file_name: str, output_file_name: str) -> None:
    """
    プレーンな日本語の文章ファイルを係り受け解析してファイルに保存する.
    (空白は削除します.)
    :param input_file_name プレーンな日本語の文章ファイル名
    :param output_file_name 係り受け解析済みの文章ファイル名
    """
    c = CaboCha.Parser()
    with open(input_file_name, encoding='utf-8') as input_file:
        with open(output_file_name, mode='w', encoding='utf-8') as output_file:
            for line in input_file:
                tree = c.parse(line.lstrip())
                output_file.write(tree.toString(CaboCha.FORMAT_LATTICE))


make_analyzed_file('neko.txt', 'neko.txt.cabocha')
