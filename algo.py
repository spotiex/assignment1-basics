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
    # 输入：token列表以及对应频次，例如:['a','b','a','b',</w>'], 2
    # 输出：token列表中所有pair的频次，例如{('a','b'): 4, ('b','a'): 2, ('a','a'): 5, ...}

    # 初始化列表和频次的映射
    pair_counts = {}
    for tokens, freq in state:
        # 针对每一个token列表和频次
        if len(tokens) < 2:
            # token列表长度小于2，直接跳过
            continue
        else:
            for i in range(len(tokens)-1):
                # 遍历token列表
                pair = (tokens[i], tokens[i+1])
                # 如果在序列内，次数加上当前词频，否则把次数置为第一次的词频
                if pair in pair_counts:
                    pair_counts[pair] = pair_counts[pair] + freq
                else:
                    pair_counts[pair] = freq
    return pair_counts


def choose_best(pair_counts):
    # 输入token列表以及频次，输出字典序最大的那一个best_pair

    # 初始化best_pair和best_count
    best_pair = ()
    best_count = 0

    if len(pair_counts) == 0:
        # 没有候选项的时候，返回空
        return best_pair

    for pair, count in pair_counts.items():
        # 遍历每一个计算好的候选pair
        if count > best_count:
            # 首先按频次比较
            best_count = count
            best_pair = pair
        elif best_count == count:
            # 统计次数相等，比较首字符排序
            if pair > best_pair:
                best_pair = pair
            else:
                continue
    return best_pair


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


def one_bpe_step(state):
    # 一轮BPE算法，输入token列表和对应频次，输出合并后的token列表和对应频次
    # 输入：当前token列表及其频次，例如：[(['a','b','a','b','</w>'], 2), (['a','a','a','a','</w>'], 5)]
    # 输出：合并后的token列表及其频次，例如：[(['ab','ab','</w>'], 2), (['aa','aa','</w>'], 5)]

    # 统计所有token列表中的pair的频次
    pair_counts = count_pairs(state)

    # 选择频次最高的那一个pair
    best_pair = choose_best(pair_counts)

    if best_pair == ():
        # 如果best_pair为空，直接返回当前状态，不需要merge了
        return state, best_pair

    # 进行merge操作
    new_state = []
    for tokens, freq in state:
        # 遍历每一个token列表和对应频次
        new_tokens = merge_one_token_list(tokens, best_pair)
        # 基于best_pair合并token列表，得到新的token列表
        new_state.append((new_tokens, freq))
        # 把新的token列表和对应频次加入新的状态列表
    return new_state, best_pair


def BPE(state, num_merges):
    # BPE算法
    # 输入：初始token列表和对应频次，需要merge的次数
    # 输出：最终state和merge规则列表

    # 初始化merge规则列表和最终状态
    final_state = state
    merge_rules = []
    for i in range(num_merges):
        # 做num_merges轮BPE算法
        final_state, best_pair = one_bpe_step(final_state)
        if best_pair == ():
            # 没有best_pair，提前结束BPE
            return final_state, merge_rules
        merge_rules.append(best_pair)
    # 循环结束，返回最终状态和merge规则列表
    return final_state, merge_rules


if __name__ == "__main__":
    text = "low low low low low lower lower widest widest widest newest newest newest newest newest newest"
    word_freq = pre_tokenization(text)
    print(word_freq)
