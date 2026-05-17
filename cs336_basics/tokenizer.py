import regex
import re
# BPE算法实现
'''
    Byte Pair Encoding是一种基于统计的文本压缩算法，常用于自然语言处理中的词汇表构建
    BPE算法通过迭代地合并最频繁出现的字符对来构建新的词汇表，达到减少文本的表示长度的目的

    辅助函数分析：
    BPE算法基于bytes序列token，需要一个函数，完成从文本到bytes序列token的过程

    辅助函数设计：
    1. pre_tokenize(text_path, special_tokens): 输入文本文件路径和特殊token列表，输出预分词后的token列表和对应频次

    BPE算法的核心步骤包括：
    1. 统计所有相邻字符对的频次
    2. 选择频次最高的字符对进行合并
    3. 重复上述步骤，直到达到预定的合并次数或没有更多的字符对可以合并

    由上述描述可知，BPE算法的输入和输出至少需要经过以下步骤：
    输入：初始化token列表及其对应频次，通常是一个字典的kv，例如：{('a','b'): 4, ('b','a'): 2, ('a','a'): 5, ...}
    输出：合并后的token列表及其对应的频次，例如：[(['ab','ab','</w>'], 2), (['aa','aa','</w>'], 5)]

    对问题进行拆解：
    1. 合并是基于token列表中所存在的pair的，需要一个函数获取token列表中所有pair，及其频次；
    2. 获得pairs列表之后，需要选出频次最高的pair，作为本轮合并的基本对象；
    3. 获取合并的基本单位后，针对每一个token列表进行合并，得到合并后的新token列表

    对拆解后的问题进行函数设计：
    1. count_pairs(state): 输入token列表以及对应频次，输出token列表中所有pair的频次
    2. choose_best(pair_counts): 输入token列表以及频次，输出字典
    3. merge_one_token_list(token_list, best_pair): 合并token_list中所有的best_pair，返回一个新的token_list

    至此，已经可以完成一轮BPE算法的实现：
    1. 首先统计所有token列表中的pair的频次，得到pair_counts
    2. 选择频次最高的那一个pair，得到best_pair
    3. 基于best_pair合并token列表，得到新的token列表和对应频次，得到新的状态

    BPE算法基于一轮BPE算法的迭代实现，增添了一个参数num_merges，表示需要merge的次数，循环执行num_merges轮BPE算法，得到最终状态和merge规则列表

'''
def pre_tokenize(text_path, special_tokens):
    # 预分词，把文本转化为bytes序列，按照特殊token进行切分，返回切分后的token列表和对应频次
    
    # 输入：文本文件路径和特殊token列表
    # 输出：预分词后的token列表和对应频次

    # GPT-2的预分词规则，匹配类型为：
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

    #读取文本文件
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # split切分，分隔符是转义后的token
    spliter = "|".join(re.escape(token) for token in special_tokens)

    # 初始化token列表和对应频次的字典   
    token_freqs = {}

    for chunk in re.split(spliter, text):
        # 对切分后的trunk处理
        if chunk == "":
            # 跳过空trunk
            continue
        for match in regex.finditer(PAT, chunk):
            # 对trunk进行正则匹配，获取符合PAT规则的token，match.group()返回匹配到的字符串
            # 一个match形如: <regex.Match object; span=(0, 5), match='hello'>, match.group()返回'hello'

            pre_token_str = match.group()
            # 把token转化为bytes序列，hello转化为b'hello'
            pre_token_bytes = pre_token_str.encode('utf-8')
            # b'hello'转化为(b'h', b'e', b'l', b'l', b'o')
            pre_token_tuple = tuple(bytes([b]) for b in pre_token_bytes)
            # 统计频次
            if pre_token_tuple in token_freqs:
                token_freqs[pre_token_tuple] = token_freqs[pre_token_tuple] + 1
            else:
                token_freqs[pre_token_tuple] = 1
            
    # 返回列表形式的token和对应频次，例如：[(b'h', 100), (b'e', 80), (b'l', 150), (b'o', 90)]
    return [(k,v) for k,v in token_freqs.items()]
     
def count_pairs(state):
      # 输入：token列表以及对应频次，例如:['a','b','a','b',</w>'], 2
      # 输出：token列表中所有pair的频次，以及pair出现的位置，例如: [('a','b'): 2]，以及{('a','b'): [(0,1), (2,3)]}

      # 扫描token列表，建立全局频次字典，以及pair出现的位置
      pair_freqs = {}
      pair_to_locs = {}

      for state_idx, (tokens, freq) in enumerate(state):
          # 遍历每一个token列表及对应频次
          for i in range(len(tokens) - 1):
              # 拿到当前的token的每一个相邻token对，构成一个pair
              pair = (tokens[i], tokens[i+1])
              # 统计pair的频次
              if pair in pair_freqs:
                  # 已经存在这个pair，频次加上当前token列表的频次
                  pair_freqs[pair] = pair_freqs[pair] + freq
                  # 加入当前token列表中pair出现的位置
              else:
                  # 不存在这个pair，初始化频次为当前token列表的频次
                  pair_freqs[pair] = freq

              if pair not in pair_to_locs:
                  # 不存在pair，把其对应的state位置和token位置加入pair_to_locs
                  pair_to_locs[pair] = [(state_idx, i)]
              else:
                  # 已经存在这个pair，把其对应的state位置和token位置加入pair_to_locs
                  pair_to_locs[pair].append((state_idx, i))
      return pair_freqs, pair_to_locs  
                                                                                                                         
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

def update_pair_info(pair_freqs, pair_to_locs, state, new_state, best_pair):
    # 更新pair_freqs和pair_to_locs
    # 输入：原来的pair_freqs和pair_to_locs，原来的state，新的state，以及本轮合并的best_pair
    # 输出：更新后的pair_freqs和pair_to_locs

    # 给定best_pair，遍历pair_to_locs
    for loc in pair_to_locs[best_pair]:
        # 拿到(state_idx, i)
        state_idx, i = loc
        # 找到变化前后的token tuple和freq
        old_tokens, freq = state[state_idx]
        new_tokens, _ = new_state[state_idx]
        # 减掉旧tuple中i附近的pair，包括：
        # 1. best_pair本身
        # 2. old_tokens[i-1], old_tokens[i]，如果i>0
        # 3. old_tokens[i+1], old_tokens[i+2]，如果i+2<len


                    
        
        
        # 加上新tuple中i附近的pair，包括：
        # 1. (new_tokens[i-1], new_tokens[i])，如果i>0
        # 2. (new_tokens[i], new_tokens[i+1])，如果i+1<len(new_tokens)
        
         
         
        # 更新pair_to_locs对应条目


def BPE(state, num_merges):
    # BPE算法
    # 输入：初始token列表和对应频次，需要merge的次数
    # 输出：最终state和merge规则列表

    # 初始化merge规则列表和最终状态
    final_state = state.copy()
    merge_rules = []
    
    # 获取频次信息以及位置索引信息
        
        
        
        

