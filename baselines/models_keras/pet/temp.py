# import numpy as np
# import pickle 
# import json

# dataset = 'ocnli'
# data = open("output/" +  dataset + '/predict.pkl', 'rb')
# labels = pickle.load(data)
# print(len(labels), labels)

# label_des2tag ={'news_tech':'科技','news_entertainment':'娱乐','news_car':'汽车','news_travel':'旅游','news_finance':'财经',
#               'news_edu':'教育','news_world':'国际','news_house':'房产','news_game':'电竞','news_military':'军事',
#               'news_story':'故事','news_culture':'文化','news_sports':'体育','news_agriculture':'农业', 'news_stock':'股票'}
# labels={i:label_des for i, (label_des,label_tag) in enumerate(label_des2tag.items())}

# print(labels)

id2label = {0: 99, 1: 10, 2: 106, 3: 92, 4: 21, 5: 14, 6: 95, 7: 73, 8: 96, 9: 54, 10: 34, 11: 62, 12: 8, 13: 12, 14: 85, 15: 101, 16: 18, 17: 70, 18: 19, 19: 36, 20: 91, 21: 103, 22: 24, 23: 5, 24: 58, 25: 94, 26: 88, 27: 78, 28: 13, 29: 71, 30: 111, 31: 16, 32: 35, 33: 53, 34: 4, 35: 59, 36: 44, 37: 82, 38: 60, 39: 11, 40: 25, 41: 116, 42: 45, 43: 47, 44: 48, 45: 56, 46: 20, 47: 102, 48: 84, 49: 113, 50: 9, 51: 46, 52: 28, 53: 97, 54: 49, 55: 118, 56: 17, 57: 22, 58: 26, 59: 76, 60: 74, 61: 1, 62: 64, 63: 50, 64: 61, 65: 40, 66: 29, 67: 110, 68: 77, 69: 41, 70: 57, 71: 7, 72: 43, 73: 81, 74: 90, 75: 31, 76: 89, 77: 100, 78: 83, 79: 15, 80: 63, 81: 109, 82: 112, 83: 80, 84: 108, 85: 72, 86: 0, 87: 30, 88: 114, 89: 3, 90: 33, 91: 42, 92: 104, 93: 65, 94: 32, 95: 79, 96: 66, 97: 93, 98: 39, 99: 117, 100: 23, 101: 51, 102: 37, 103: 86, 104: 27, 105: 107, 106: 98, 107: 115, 108: 55, 109: 105, 110: 87, 111: 75, 112: 67, 113: 2, 114: 38, 115: 52, 116: 69, 117: 6, 118: 68}

result ={}
for id,label in id2label.items():
    result[id] = str(label)
print(result)
