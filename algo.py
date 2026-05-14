# 做Pre-tokenization
def pre_tokenization(text):
    # 按照空格去掉文本中的多余空格
    vocab = text.split()
    print(vocab)
    # 按照切分后的文本做词频统计 {"word1": count1, "word2": count2, ...}
    word_freq = {}
    for word in vocab:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    return word_freq


def count_pairs(state):
    pass


def choose_best(pair_counts):
    pass


def merge_one_token_list(token_list, best_pair):
    # 合并token_list中所有的best_pair，返回一个新的token_list
    result = []
    i = 0
    while i < len(token_list):
        if i < len(token_list) - 1 and token_list[i] == best_pair[0] and token_list[i+1] == best_pair[1]:
            # 如果没走到最后一个token，并且当前token和下一个token组成了best_pair，就把它们合并成一个token
            result.append(best_pair[0] + best_pair[1])
            # 合并完之后跳过两个已经合并的token
            i = i + 2
        else:
            # 不是best_pair，把当前token加入结果列表
            result.append(token_list[i])
            # 继续下一个token
            i = i + 1
    return result


if __name__ == "__main__":
    text = "low low low low low lower lower widest widest widest newest newest newest newest newest newest"
    word_freq = pre_tokenization(text)
    print(word_freq)
