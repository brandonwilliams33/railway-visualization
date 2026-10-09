ordinary='京沪 陇海 京广 京九 沪昆 京哈 沈山 沈大 沈丹 沈吉 滨洲 滨绥 宝成 成渝 川黔 黔桂 湘桂 衡柳 焦柳 宁西 襄渝 沪蓉 皖赣 萧甬 宣杭 合九 兖石 胶济 胶新 新石 青盐 新长 宁启 宿淮 石太 石德 石长 太焦 太中 京包 集包 集通 包兰 宝中 包西 兰新 兰渝 青藏 京通 京承 京原 丰沙 津山 杭深 峰福 鹰厦 昌福 南昆 南广 渝怀 渝贵 阳安 西康 达成 金温 龙漳 赣龙 赣瑞龙 广深 益湛 南疆 临哈 精霍 格库 沪汉蓉 库阿 北疆 合宁 汉丹 汉宜 渝利 遂成 甬台温 温福 福厦 向莆 玉磨 昆玉 广茂 漳龙 辛泰 干武 平齐 达万 榆树 榆红 侯西 西韩 侯阎 兴泉 浦梅 南龙 邯长 哈佳 广大 楚大 滇藏 大瑞 内六 酒额 天平 天华 平汝'.split()
forbidden=['货','动车所','走行','存车','车库','检修','编组','牵出','调车','专用','厂','工程','试验','联络','上下行','疏解','南港','瓦日','浩吉','大秦','朔黄','神朔','霍日','韩原']
def approved(name):
 # Individually reviewed high-speed/conventional passenger connection.
 if name in {'大河沿联络线','沪昆铁路/内六铁路'}:return True
 if not name or any(w in name for w in forbidden):return False
 if any(w in name for w in ['高速','高铁','客专','客运专线','城际']):return True
 return any(name in [w+'线',w+'铁路',w+'鐵路',w+'下行线',w+'上行线'] for w in ordinary)
def family(name):return 'hs' if any(w in name for w in ['高速','高铁','客专','客运专线','城际']) else 'ordinary'
