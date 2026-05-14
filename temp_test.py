from algo import merge_one_token_list


def test_merge():
    token_list = ['a', 'a', 'a', '</w>']
    best_pair = ('a', 'a')
    result = merge_one_token_list(token_list, best_pair)
    assert result == ['aa', 'a',
                      '</w>'], f"Expected ['aa','a','</w>'], but got {result}"

    token_list = ['a', 'b', 'a', 'b', '</w>']
    best_pair = ('a', 'b')
    result = merge_one_token_list(token_list, best_pair)
    assert result == ['ab', 'ab',
                      '</w>'], f"Expected ['ab','ab','</w>'], but got {result}"

    token_list = ['a', 'b', '</w>']
    best_pair = ('b', '</w>')
    result = merge_one_token_list(token_list, best_pair)
    assert result == [
        'a', 'b</w>'], f"Expected ['a','b</w>'], but got {result}"
