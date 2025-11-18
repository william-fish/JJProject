from astrbot.api.all import *
from astrbot.api.star import StarTools
from datetime import datetime, timedelta
import random
import os
import re
import json
import aiohttp
from astrbot.api.all import Image as AstrImage
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
import copy

PLUGIN_DIR = StarTools.get_data_dir("astrbot_plugin_animewifex")
CONFIG_DIR = os.path.join(PLUGIN_DIR, "config")
IMG_DIR = os.path.join(PLUGIN_DIR, "img", "wife")
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
NTR_STATUS_FILE = os.path.join(CONFIG_DIR, "ntr_status.json")
NTR_RECORDS_FILE = os.path.join(CONFIG_DIR, "ntr_records.json")
CHANGE_RECORDS_FILE = os.path.join(CONFIG_DIR, "change_records.json")
RESET_SHARED_FILE = os.path.join(CONFIG_DIR, "reset_shared_records.json")
SWAP_REQUESTS_FILE = os.path.join(CONFIG_DIR, "swap_requests.json")
SWAP_LIMIT_FILE = os.path.join(CONFIG_DIR, "swap_limit_records.json")
PRO_USER_FILE = os.path.join(CONFIG_DIR, "pro_user.json")
ITEMS_FILE = os.path.join(CONFIG_DIR, "items.json")
EFFECTS_FILE = os.path.join(CONFIG_DIR, "effects.json")
SELECT_WIFE_RECORDS_FILE = os.path.join(CONFIG_DIR, "select_wife_records.json")
BEAT_WIFE_RECORDS_FILE = os.path.join(CONFIG_DIR, "beat_wife_records.json")
SEDUCE_RECORDS_FILE = os.path.join(CONFIG_DIR, "seduce_records.json")
RESET_BLIND_BOX_RECORDS_FILE = os.path.join(CONFIG_DIR, "reset_blind_box_records.json")
MARKET_FILE = os.path.join(CONFIG_DIR, "market.json")
MARKET_PURCHASE_RECORDS_FILE = os.path.join(CONFIG_DIR, "market_purchase_records.json")
GIFT_REQUESTS_FILE = os.path.join(CONFIG_DIR, "gift_requests.json")
BLIND_BOX_PERKS_FILE = os.path.join(CONFIG_DIR, "blind_box_perks.json")
FORTUNE_FILE = os.path.join(CONFIG_DIR, "fortune.json")
ARCHIVE_FILE = os.path.join(CONFIG_DIR, "archives.json")


def get_today():
    # 获取当前上海时区日期字符串
    utc_now = datetime.utcnow()
    return (utc_now + timedelta(hours=8)).date().isoformat()


def load_json(path):
    # 安全加载 JSON 文件
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_json(path, data):
    # 保存数据到 JSON 文件
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


ntr_statuses = {}
ntr_records = {}
change_records = {}
swap_requests = {}
swap_limit_records = {}
select_wife_records = {}
beat_wife_records = {}
seduce_records = {}
reset_blind_box_records = {}
load_ntr_statuses = lambda: globals().update(ntr_statuses=load_json(NTR_STATUS_FILE))
load_ntr_records = lambda: globals().update(ntr_records=load_json(NTR_RECORDS_FILE))
load_select_wife_records = lambda: globals().update(select_wife_records=load_json(SELECT_WIFE_RECORDS_FILE))
load_beat_wife_records = lambda: globals().update(beat_wife_records=load_json(BEAT_WIFE_RECORDS_FILE))
load_seduce_records = lambda: globals().update(seduce_records=load_json(SEDUCE_RECORDS_FILE))
load_reset_blind_box_records = lambda: globals().update(reset_blind_box_records=load_json(RESET_BLIND_BOX_RECORDS_FILE))

market_data = {}
def load_market_data():
    global market_data
    market_data = load_json(MARKET_FILE)

def save_market_data():
    save_json(MARKET_FILE, market_data)

market_purchase_records = {}
def load_market_purchase_records():
    global market_purchase_records
    market_purchase_records = load_json(MARKET_PURCHASE_RECORDS_FILE)

def save_market_purchase_records():
    save_json(MARKET_PURCHASE_RECORDS_FILE, market_purchase_records)

gift_requests = {}
def load_gift_requests():
    global gift_requests
    gift_requests = load_json(GIFT_REQUESTS_FILE)

def save_gift_requests():
    save_json(GIFT_REQUESTS_FILE, gift_requests)

def cleanup_gift_requests():
    today = get_today()
    removed = False
    for day in list(gift_requests.keys()):
        if day != today:
            del gift_requests[day]
            removed = True
    if removed:
        save_gift_requests()


archives = {}


def load_archives():
    raw = load_json(ARCHIVE_FILE)
    globals()["archives"] = raw.get("archives", {})


def save_archives():
    save_json(ARCHIVE_FILE, {"archives": archives})


def load_change_records():
    raw = load_json(CHANGE_RECORDS_FILE)
    change_records.clear()
    for gid, users in raw.items():
        change_records[gid] = {}
        for uid, rec in users.items():
            if isinstance(rec, str):
                change_records[gid][uid] = {"date": rec, "count": 1}
            else:
                change_records[gid][uid] = rec


save_ntr_statuses = lambda: save_json(NTR_STATUS_FILE, ntr_statuses)
save_ntr_records = lambda: save_json(NTR_RECORDS_FILE, ntr_records)
save_change_records = lambda: save_json(CHANGE_RECORDS_FILE, change_records)
save_select_wife_records = lambda: save_json(SELECT_WIFE_RECORDS_FILE, select_wife_records)
save_beat_wife_records = lambda: save_json(BEAT_WIFE_RECORDS_FILE, beat_wife_records)
save_seduce_records = lambda: save_json(SEDUCE_RECORDS_FILE, seduce_records)
save_reset_blind_box_records = lambda: save_json(RESET_BLIND_BOX_RECORDS_FILE, reset_blind_box_records)


GLOBAL_WIFE_FILE = os.path.join(CONFIG_DIR, "wives_global.json")
RESERVED_CONFIG_FILES = {
    os.path.basename(NTR_STATUS_FILE),
    os.path.basename(NTR_RECORDS_FILE),
    os.path.basename(CHANGE_RECORDS_FILE),
    os.path.basename(RESET_SHARED_FILE),
    os.path.basename(SWAP_REQUESTS_FILE),
    os.path.basename(SWAP_LIMIT_FILE),
    os.path.basename(PRO_USER_FILE),
    os.path.basename(ITEMS_FILE),
    os.path.basename(EFFECTS_FILE),
    os.path.basename(SELECT_WIFE_RECORDS_FILE),
    os.path.basename(BEAT_WIFE_RECORDS_FILE),
    os.path.basename(SEDUCE_RECORDS_FILE),
    os.path.basename(RESET_BLIND_BOX_RECORDS_FILE),
    os.path.basename(GLOBAL_WIFE_FILE),
    os.path.basename(GIFT_REQUESTS_FILE),
    os.path.basename(ARCHIVE_FILE),
}


def clamp_probability(value) -> float:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(0.9, val))


def _normalize_user_record(uid: str, record) -> dict:
    result = {
        "nick": f"用户{uid}",
        "wives": [],
        "date": get_today(),
        "harem": False,
        "groups": [],
    }
    if isinstance(record, dict):
        if isinstance(record.get("nick"), str) and record["nick"].strip():
            result["nick"] = record["nick"]
        if isinstance(record.get("date"), str):
            result["date"] = record["date"]
        if "harem" in record:
            result["harem"] = bool(record["harem"])
        if isinstance(record.get("wives"), list):
            result["wives"] = list(dict.fromkeys([w for w in record["wives"] if isinstance(w, str)]))
        groups = record.get("groups")
        if isinstance(groups, list):
            result["groups"] = [str(g) for g in groups if g]
        elif isinstance(groups, dict):
            merged_wives = list(result["wives"])
            latest_date = result["date"]
            harem_flag = result["harem"]
            nick_value = result["nick"]
            group_ids = []
            for gid, rec in groups.items():
                group_ids.append(str(gid))
                if isinstance(rec, dict):
                    if isinstance(rec.get("wives"), list):
                        for w in rec["wives"]:
                            if isinstance(w, str) and w not in merged_wives:
                                merged_wives.append(w)
                    if isinstance(rec.get("date"), str):
                        latest_date = rec["date"]
                    if rec.get("harem"):
                        harem_flag = True
                    if isinstance(rec.get("nick"), str) and rec["nick"].strip():
                        nick_value = rec["nick"]
            if group_ids:
                result["groups"] = list(dict.fromkeys(group_ids))
            if merged_wives:
                result["wives"] = merged_wives
            result["date"] = latest_date
            result["harem"] = harem_flag
            result["nick"] = nick_value
    result["groups"] = list(dict.fromkeys([str(g) for g in result["groups"] if g]))
    result["nick"] = result["nick"] or f"用户{uid}"
    return result


def load_wife_data():
    raw = load_json(GLOBAL_WIFE_FILE)
    data = {}
    if isinstance(raw, dict):
        for uid, record in raw.items():
            data[str(uid)] = _normalize_user_record(str(uid), record)
    if not data:
        aggregated = {}
        for filename in os.listdir(CONFIG_DIR):
            if not filename.endswith(".json") or filename in RESERVED_CONFIG_FILES:
                continue
            group_id = os.path.splitext(filename)[0]
            old_cfg = load_json(os.path.join(CONFIG_DIR, filename))
            if not isinstance(old_cfg, dict):
                continue
            for uid, rec in old_cfg.items():
                uid_str = str(uid)
                info = aggregated.setdefault(
                    uid_str,
                    {
                        "nick": "",
                        "wives": [],
                        "date": get_today(),
                        "harem": False,
                        "groups": set(),
                    },
                )
                info["groups"].add(str(group_id))
                if isinstance(rec, list) and rec:
                    rec = {
                        "wives": [rec[0]],
                        "date": rec[1] if len(rec) > 1 else info["date"],
                        "nick": rec[2] if len(rec) > 2 else info["nick"],
                    }
                if not isinstance(rec, dict):
                    continue
                if isinstance(rec.get("nick"), str) and rec["nick"].strip():
                    info["nick"] = rec["nick"]
                if isinstance(rec.get("date"), str):
                    info["date"] = rec["date"]
                if rec.get("harem"):
                    info["harem"] = True
                if isinstance(rec.get("wives"), list):
                    for w in rec["wives"]:
                        if isinstance(w, str) and w not in info["wives"]:
                            info["wives"].append(w)
        if aggregated:
            for uid, info in aggregated.items():
                data[uid] = {
                    "nick": info["nick"] or f"用户{uid}",
                    "wives": info["wives"],
                    "date": info["date"],
                    "harem": info["harem"],
                    "groups": list(sorted(info["groups"])),
                }
            save_json(GLOBAL_WIFE_FILE, data)
    elif raw != data:
        save_json(GLOBAL_WIFE_FILE, data)
    return data


wives_data = load_wife_data()


def save_wife_data():
    # 保存全局老婆数据
    save_json(GLOBAL_WIFE_FILE, wives_data)


def _ensure_user_entry(uid: str, nick: str = "") -> dict:
    uid = str(uid)
    entry = wives_data.setdefault(
        uid,
        {
            "nick": nick or f"用户{uid}",
            "wives": [],
            "date": get_today(),
            "harem": False,
            "groups": [],
        },
    )
    if nick:
        entry["nick"] = nick
    entry.setdefault("wives", [])
    entry.setdefault("date", get_today())
    entry.setdefault("harem", False)
    groups = entry.get("groups")
    if not isinstance(groups, list):
        groups = []
    entry["groups"] = [str(g) for g in groups if g]
    return entry


def _ensure_group_membership(record: dict, gid: str):
    if not record:
        return
    gid_str = str(gid)
    if not gid_str:
        return
    groups = record.setdefault("groups", [])
    if gid_str not in groups:
        groups.append(gid_str)
        save_wife_data()


def get_group_record(uid: str, gid: str, attach: bool = False) -> dict | None:
    record = _ensure_user_entry(uid)
    gid_str = str(gid)
    if not gid_str:
        return record
    if gid_str in record["groups"]:
        return record
    if attach:
        _ensure_group_membership(record, gid_str)
        return record
    return None


def ensure_group_record(uid: str, gid: str, date: str, nick: str, keep_existing: bool = False) -> dict:
    record = get_group_record(uid, gid, attach=True) or _ensure_user_entry(uid, nick)
    if not keep_existing and record.get("date") != date:
        record["wives"] = []
    record["date"] = date
    if nick:
        record["nick"] = nick
    _ensure_group_membership(record, gid)
    return record


def remove_group_record(uid: str, gid: str):
    record = wives_data.get(str(uid))
    gid_str = str(gid)
    if not record or not isinstance(record, dict):
        return
    groups = record.get("groups", [])
    if gid_str in groups:
        groups.remove(gid_str)
    if not groups:
        record["harem"] = False
    save_wife_data()


def iter_group_users(gid: str):
    gid_str = str(gid)
    for uid, record in wives_data.items():
        if not isinstance(record, dict):
            continue
        groups = record.get("groups", [])
        if gid_str in groups:
            yield uid, record, record


def is_harem_user(arg1, arg2=None) -> bool:
    if isinstance(arg1, dict):
        cfg = arg1
        uid = arg2
        gid = getattr(cfg, "group_id", None)
    else:
        uid = arg1
        gid = arg2
    record = get_group_record(uid, gid, attach=True)
    return bool(record and record.get("harem"))


def get_wife_count(arg1, arg2, today: str) -> int:
    if isinstance(arg1, dict):
        cfg = arg1
        uid = arg2
        gid = getattr(cfg, "group_id", None)
    else:
        uid = arg1
        gid = arg2
    record = get_group_record(uid, gid, attach=True)
    if record and record.get("date") == today:
        return len(record.get("wives", []))
    return 0


def get_wives_list(arg1, arg2, today: str) -> list:
    if isinstance(arg1, dict):
        cfg = arg1
        uid = arg2
        gid = getattr(cfg, "group_id", None)
    else:
        uid = arg1
        gid = arg2
    record = get_group_record(uid, gid, attach=True)
    if record and record.get("date") == today:
        return list(record.get("wives", []))
    return []


def add_wife(arg1, arg2, img: str, date: str, nick: str, is_harem: bool = False, allow_shura: bool = False) -> bool:
    if isinstance(arg1, dict):
        cfg = arg1
        uid = arg2
        gid = getattr(cfg, "group_id", None)
    else:
        uid = arg1
        gid = arg2
        cfg = None
    uid_str = str(uid)
    is_shura = get_user_flag(date, uid_str, "shura")
    if is_shura and not allow_shura:
        return False
    record = ensure_group_record(uid_str, gid, date, nick, keep_existing=is_harem)
    if is_harem:
        record["harem"] = True
        if img not in record["wives"]:
            record["wives"].append(img)
    else:
        record["harem"] = False
        record["wives"] = [img]
    if is_shura and record.get("harem"):
        wives_list = record.get("wives", [])
        max_limit = 6
        while len(wives_list) > max_limit:
            if len(wives_list) <= 1:
                break
            remove_idx = random.randrange(0, len(wives_list) - 1)
            wives_list.pop(remove_idx)
        record["wives"] = wives_list
    if isinstance(cfg, dict):
        dict.__setitem__(cfg, uid_str, record)
    return True


class GroupConfigDict(dict):
    def __init__(self, gid: str):
        super().__init__()
        self.group_id = str(gid)

    def __getitem__(self, uid):
        uid_str = str(uid)
        if uid_str not in self:
            record = get_group_record(uid_str, self.group_id, attach=True)
            if record:
                dict.__setitem__(self, uid_str, record)
        return dict.__getitem__(self, uid_str)

    def get(self, uid, default=None):
        uid_str = str(uid)
        if uid_str not in self:
            record = get_group_record(uid_str, self.group_id, attach=True)
            if record:
                dict.__setitem__(self, uid_str, record)
                return record
            return default
        return dict.get(self, uid_str, default)

    def __setitem__(self, uid, value):
        uid_str = str(uid)
        record = get_group_record(uid_str, self.group_id, attach=True)
        if value and isinstance(value, dict):
            if "nick" in value and isinstance(value["nick"], str):
                record["nick"] = value["nick"]
            if "date" in value and isinstance(value["date"], str):
                record["date"] = value["date"]
            if "harem" in value:
                record["harem"] = bool(value["harem"])
            if "wives" in value and isinstance(value["wives"], list):
                record["wives"] = list(value["wives"])
        dict.__setitem__(self, uid_str, record)

    def __delitem__(self, uid):
        uid_str = str(uid)
        record = get_group_record(uid_str, self.group_id, attach=True)
        if record:
            record["wives"] = []
            record["harem"] = False
        if uid_str in self:
            dict.__delitem__(self, uid_str)


def load_group_config(group_id: str) -> GroupConfigDict:
    gid = str(group_id)
    cfg = GroupConfigDict(gid)
    for uid, record in wives_data.items():
        normalized = _ensure_user_entry(uid, record.get("nick", f"用户{uid}"))
        if gid in normalized.get("groups", []):
            dict.__setitem__(cfg, str(uid), normalized)
    return cfg


def save_group_config(cfg: GroupConfigDict | None = None):
    save_wife_data()


def load_swap_requests():
    raw = load_json(SWAP_REQUESTS_FILE)
    today = get_today()
    cleaned = {}
    for gid, reqs in raw.items():
        valid = {}
        for uid, rec in reqs.items():
            if rec.get("date") == today:
                valid[uid] = rec
        if valid:
            cleaned[gid] = valid
    globals()["swap_requests"] = cleaned
    if raw != cleaned:
        save_json(SWAP_REQUESTS_FILE, cleaned)


save_swap_requests = lambda: save_json(SWAP_REQUESTS_FILE, swap_requests)


def load_swap_limit_records():
    globals()["swap_limit_records"] = load_json(SWAP_LIMIT_FILE)


save_swap_limit_records = lambda: save_json(SWAP_LIMIT_FILE, swap_limit_records)


def load_pro_users():
    # 加载专属卡池数据并更新全局变量
    raw = load_json(PRO_USER_FILE)
    globals()["pro_users"] = raw.get("pro_users", {})


pro_users = {}
load_pro_users()

# 盲盒永久加成数据
blind_box_perks = {}

def load_blind_box_perks():
    raw = load_json(BLIND_BOX_PERKS_FILE)
    globals()["blind_box_perks"] = raw.get("perks", {})

def save_blind_box_perks():
    save_json(BLIND_BOX_PERKS_FILE, {"perks": blind_box_perks})

load_blind_box_perks()

# 运势数据
fortune_data = {}

def load_fortune_data():
    raw = load_json(FORTUNE_FILE)
    globals()["fortune_data"] = raw.get("fortunes", {})

def save_fortune_data():
    save_json(FORTUNE_FILE, {"fortunes": fortune_data})

load_fortune_data()

# 运势配置
FORTUNE_TYPES = {
    "大吉": {"stars": 7, "weight": 5},
    "吉": {"stars": 6, "weight": 15},
    "小吉": {"stars": 5, "weight": 25},
    "中平": {"stars": 4, "weight": 30},
    "小凶": {"stars": 3, "weight": 15},
    "凶": {"stars": 2, "weight": 7},
    "大凶": {"stars": 1, "weight": 3},
}

FORTUNE_ADVICE = {
    "大吉": {
        "proverbs": [
            "如龙得云,青云直上,智谋奋进,才略奏功",
            "鸿运当头,万事顺遂,把握良机,成就大业",
            "福星高照,贵人相助,事业有成,财源广进",
            "天时地利人和,运势如虹,乘风破浪,一飞冲天",
            "吉星拱照,喜事连连,机遇不断,大展宏图",
            "运势鼎盛,心想事成,百事顺遂,前程似锦",
            "龙腾虎跃,气势如虹,把握时机,成就非凡",
            "福禄双全,财运亨通,事业腾飞,名利双收",
        ],
        "dos": ["积极行动", "把握机会", "投资理财", "拓展人脉", "学习提升", "主动出击", "勇于尝试", "扩大规模", "建立合作", "创新突破"],
        "donts": ["过度自信", "忽视细节", "冲动决策", "骄傲自满", "急于求成", "忽视他人", "浪费机会"],
    },
    "吉": {
        "proverbs": [
            "春风得意,事事顺心,稳步前进,收获颇丰",
            "运势上升,机遇来临,努力奋斗,必有回报",
            "吉星高照,心想事成,稳步发展,前景光明",
            "顺风顺水,小有成就,持续努力,渐入佳境",
            "运势平稳上升,机遇渐现,把握时机,稳步发展",
            "喜事临门,好事成双,保持努力,收获在望",
            "运势向好,机遇增多,积极应对,前景可期",
            "小有收获,稳步前进,保持耐心,未来光明",
        ],
        "dos": ["制定计划", "稳步推进", "保持耐心", "维护关系", "适度投资", "积极沟通", "学习提升", "拓展视野", "建立信任", "把握时机"],
        "donts": ["急于求成", "忽视风险", "过度消费", "骄傲自满", "忽视细节", "冲动决策", "浪费资源"],
    },
    "小吉": {
        "proverbs": [
            "小有收获,稳步发展,保持努力,未来可期",
            "运势平稳,小有进步,持续努力,渐入佳境",
            "平顺安康,小有成就,保持现状,稳步前行",
            "平淡中见真章,小步前进,积累经验,等待时机",
            "运势平稳向好,小有起色,保持耐心,稳步发展",
            "无风无浪,小有收获,保持现状,稳中求进",
            "平顺安康,小有进步,持续努力,渐入佳境",
            "运势平稳,小有成就,保持努力,未来可期",
        ],
        "dos": ["保持现状", "小步前进", "维护稳定", "适度调整", "观察等待", "积累经验", "保持耐心", "维护关系", "小规模尝试"],
        "donts": ["冒险激进", "大额投资", "重大决策", "急于求成", "忽视风险", "过度消费", "冲动行事"],
    },
    "中平": {
        "proverbs": [
            "平平淡淡,无风无浪,保持现状,稳中求进",
            "运势平稳,无大喜大悲,保持平常心,稳步前行",
            "中庸之道,不偏不倚,保持平衡,等待时机",
            "平淡如水,无波无澜,保持现状,观察等待",
            "运势平平,无大起大落,保持平常心,稳步前行",
            "平淡中见真章,保持现状,等待时机,稳中求进",
            "无风无浪,平平淡淡,保持平衡,观察等待",
            "中庸之道,不偏不倚,保持现状,等待转机",
        ],
        "dos": ["保持现状", "观察等待", "维护稳定", "保持平衡", "谨慎行事", "积累经验", "保持耐心"],
        "donts": ["冒险行动", "重大改变", "过度投资", "冲动决策", "忽视风险", "急于求成", "大额支出"],
    },
    "小凶": {
        "proverbs": [
            "小有波折,需谨慎行事,保持警惕,化解危机",
            "运势下滑,遇到阻碍,冷静应对,转危为安",
            "略有不利,需多注意,小心谨慎,避免损失",
            "小有阻碍,需谨慎应对,保持冷静,化解困难",
            "运势略有下降,遇到小挫折,冷静分析,寻找转机",
            "小有波折,需格外小心,保持警惕,避免损失",
            "略有不利,需谨慎行事,冷静应对,等待转机",
            "小有困难,需小心应对,保持耐心,化解危机",
        ],
        "dos": ["谨慎行事", "保守决策", "减少风险", "保持耐心", "寻求帮助", "保持冷静", "观察等待", "避免冲突"],
        "donts": ["冒险投资", "重大决策", "忽视风险", "冲动行事", "过度消费", "急于求成", "大额支出", "冒险行动"],
    },
    "凶": {
        "proverbs": [
            "运势不佳,多有阻碍,需谨慎应对,化解困难",
            "困难重重,挑战不断,保持冷静,寻找转机",
            "不利因素增多,需格外小心,稳中求进,等待转机",
            "运势低迷,阻碍重重,需谨慎应对,寻找出路",
            "困难不断,挑战增多,保持冷静,稳中求存",
            "不利因素集中,需格外谨慎,避免损失,等待转机",
            "运势下滑,困难增多,需小心应对,化解危机",
            "阻碍重重,需谨慎行事,保持冷静,寻找转机",
        ],
        "dos": ["保守行事", "减少风险", "保持冷静", "寻求帮助", "避免冲突", "保持低调", "观察等待", "谨慎决策"],
        "donts": ["冒险行动", "重大投资", "忽视警告", "冲动决策", "过度消费", "大额支出", "冒险尝试", "忽视风险"],
    },
    "大凶": {
        "proverbs": [
            "运势极差,困难重重,需格外谨慎,等待转机",
            "危机四伏,挑战不断,保持冷静,寻找出路",
            "不利因素集中,需小心应对,稳中求存,等待时机",
            "运势极差,危机重重,需极度谨慎,避免损失",
            "困难重重,危机四伏,需格外小心,稳中求存",
            "不利因素集中,需极度谨慎,避免冒险,等待转机",
            "运势极差,困难不断,需小心应对,化解危机",
            "危机四伏,需格外谨慎,保持冷静,寻找出路",
        ],
        "dos": ["极度谨慎", "避免风险", "保持低调", "寻求支持", "保守行事", "减少活动", "保持冷静", "观察等待"],
        "donts": ["任何冒险", "重大决策", "大额投资", "忽视危险", "冲动行事", "过度消费", "冒险尝试", "忽视警告"],
    },
}

def get_user_fortune(today: str, uid: str, *, force: bool = False, favor_good: bool = False) -> dict:
    """获取用户今日运势，如果不存在（或强制刷新）则生成"""
    uid_str = str(uid)
    day_fortunes = fortune_data.setdefault(today, {})
    if force and uid_str in day_fortunes:
        del day_fortunes[uid_str]
    if uid_str not in day_fortunes:
        # 生成运势
        fortune_type = _generate_fortune(favor_good=favor_good)
        # 随机选择一张老婆图片
        image_pool = []
        try:
            if os.path.exists(IMG_DIR):
                image_pool = [
                    f for f in os.listdir(IMG_DIR)
                    if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
                ]
        except:
            pass
        wife_img = random.choice(image_pool) if image_pool else None
        
        # 从图片文件名提取老婆名称作为吉星
        lucky_star = "神秘人"
        if wife_img:
            base = os.path.splitext(os.path.basename(wife_img))[0]
            if "!" in base:
                # 形如 作品!角色名
                _, chara = base.split("!", 1)
                lucky_star = chara
            else:
                lucky_star = base
        
        # 生成建议
        advice_data = FORTUNE_ADVICE[fortune_type]
        proverb = random.choice(advice_data["proverbs"])
        # 宜XXX最多1~2个
        dos_count = random.randint(1, min(2, len(advice_data["dos"])))
        dos = random.sample(advice_data["dos"], dos_count)
        # 忌XXX最多1~2个
        donts_count = random.randint(1, min(2, len(advice_data["donts"])))
        donts = random.sample(advice_data["donts"], donts_count)
        
        day_fortunes[uid_str] = {
            "type": fortune_type,
            "stars": FORTUNE_TYPES[fortune_type]["stars"],
            "lucky_star": lucky_star,
            "wife_img": wife_img,
            "proverb": proverb,
            "dos": dos,
            "donts": donts,
        }
        save_fortune_data()
    return day_fortunes[uid_str]

def _generate_fortune(*, favor_good: bool = False) -> str:
    """根据权重随机生成运势类型，可选偏向更高运势"""
    base_types = list(FORTUNE_TYPES.keys())
    weights = []
    bias = None
    if favor_good:
        bias = {
            "大吉": 2.5,
            "吉": 2.0,
            "小吉": 1.3,
            "中平": 0.8,
            "小凶": 0.5,
            "凶": 0.4,
            "大凶": 0.3,
        }
    for ft in base_types:
        weight = FORTUNE_TYPES[ft]["weight"]
        if bias:
            weight *= bias.get(ft, 1.0)
        weights.append(weight)
    return random.choices(base_types, weights=weights)[0]

def get_blind_box_perk(uid: str, perk_type: str, default=0):
    """获取用户的盲盒永久加成"""
    user_perks = blind_box_perks.get(str(uid), {})
    return user_perks.get(perk_type, default)

def set_blind_box_perk(uid: str, perk_type: str, value):
    """设置用户的盲盒永久加成"""
    uid_str = str(uid)
    if uid_str not in blind_box_perks:
        blind_box_perks[uid_str] = {}
    blind_box_perks[uid_str][perk_type] = value
    save_blind_box_perks()

def add_blind_box_perk(uid: str, perk_type: str, delta, max_value=None):
    """增加用户的盲盒永久加成，可设置上限"""
    current = get_blind_box_perk(uid, perk_type, 0)
    new_value = current + delta
    if max_value is not None:
        new_value = min(new_value, max_value)
    set_blind_box_perk(uid, perk_type, new_value)
    return new_value


def load_item_data():
    raw = load_json(ITEMS_FILE)
    globals()["item_data"] = raw.get("item_data", {})


def save_item_data():
    save_json(ITEMS_FILE, {"item_data": item_data})


item_data = {}
load_item_data()


def get_avatar_url(user_id: str) -> str:
    # QQ 头像常用 CDN 链接方案，若平台不同可在此处调整
    return f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"


# ---------------- 道具效果状态存储：按天/按用户 ----------------
def load_effects():
    raw = load_json(EFFECTS_FILE)
    globals()["effects_data"] = raw.get("effects_data", {})


def save_effects():
    save_json(EFFECTS_FILE, {"effects_data": effects_data})


def get_user_effects(today: str, uid: str) -> dict:
    day_map = effects_data.setdefault(today, {})
    eff = day_map.get(uid)
    if eff is None:
        eff = {
            "mods": {
                "ntr_attack_bonus": 0.0,  # 进攻方牛成功率增幅，叠加到基础概率
                "ntr_defense_bonus": 0.0,  # 防守方被牛成功率增幅（对方受益，自己受损）
                "change_extra_uses": 0,  # 额外换老婆次数
                "ntr_extra_uses": 0,  # 额外牛老婆次数
                "select_wife_uses": 0,  # 选老婆使用次数
                "beat_wife_uses": 0,  # 打老婆使用次数
                "seduce_uses": 0,  # 勾引使用次数（-1表示无限）
                "blind_box_extra_draw": 0,  # 额外抽盲盒机会次数
                "reset_extra_uses": 0,  # 额外的重置次数
                "reset_blind_box_extra": 0,  # 额外的重置盲盒机会
                "change_free_prob": 0.0,  # 何意味：换老婆免消耗概率
                "change_fail_prob": 0.0,  # 何意味：换老婆失败概率
                "market_extra_purchases": 0,  # 额外老婆集市购买次数
                "market_wife_extra_purchases": 0,  # 额外老婆集市购买老婆次数
            },
            "flags": {
                "protect_from_ntr": False,  # 不可被牛走
                "ban_change": False,  # 禁止使用换老婆
                "ban_items": False,  # 禁止使用道具（贤者时间）
                "harem": False,  # 开后宫（多老婆支持将在后续实现）
                "ban_ntr": False,  # 禁止使用牛老婆（公交车）
                "ntr_override": False,  # 无视牛老婆禁用（牛魔王）
                "force_swap": False,  # 强制交换（公交车）
                "landmine_girl": False,  # 病娇效果
                "ban_reject_swap": False,  # 禁止使用拒绝交换（苦主）
                "next_ntr_guarantee": False,  # 黄毛：下次牛必定成功
                "victim_auto_ntr": False,  # 苦主：被牛必定成功
                "double_item_effect": False,  # 二度寝：下次道具效果翻倍
                "stick_hero": False,  # 棍勇状态
                "hermes": False,  # 爱马仕状态
                "yuanpi": False,  # 原批状态
                "pachinko_777": False,  # 柏青哥：777效果
                "light_fingers": False,  # 顺手的事
                "rich_bro": False,  # 富哥
                "share_bonus": False,  # 见者有份
                "learned": False,  # 长一智
                "lightbulb": False,  # 电灯泡
                "lucky_e": False,  # 幸运E
                "shura": False,  # 修罗
                "super_lucky": False,  # 超吉
                "extreme_evil": False,  # 穷凶极恶
                "equal_rights": False,  # 众生平等
            },
            "meta": {
                "ntr_penalty_stack": 0,  # 苦主：失去老婆次数增量 -> 换老婆额外次数
                "competition_target": None,  # 雄竞目标
                "blind_box_groups": [],  # 今日已抽盲盒的群列表
                "competition_prob": 0.3,  # 雄竞概率
                "harem_chaos_multiplier": 1.0,  # 开后宫修罗场概率倍数
                "lost_wives": [],  # 今日被牛走的老婆
                "stick_hero_wives": [],  # 棍勇已获得的老婆列表（用于不重复获得）
                "future_diary_target": None,  # 未来日记：下次抽老婆或换老婆的目标关键词
                "lightbulb_group": None,  # 电灯泡监听群
            },
        }
        day_map[uid] = eff
    return eff


def get_user_flag(today: str, uid: str, flag_key: str) -> bool:
    return bool(get_user_effects(today, uid)["flags"].get(flag_key, False))


def set_user_flag(today: str, uid: str, flag_key: str, value: bool, *, propagate: bool = True):
    uid = str(uid)
    eff = get_user_effects(today, uid)
    flags = eff["flags"]
    new_value = bool(value)
    changed = flags.get(flag_key) != new_value
    flags[flag_key] = new_value
    save_effects()
    if propagate and changed:
        _propagate_brother_flag(today, uid, flag_key, new_value)


def _get_brother_partner(today: str, uid: str) -> str | None:
    partner = get_user_meta(today, uid, "brother_partner")
    if not partner:
        return None
    partner_str = str(partner)
    return partner_str or None


def _propagate_brother_flag(today: str, uid: str, flag_key: str, value: bool):
    partner_uid = _get_brother_partner(today, uid)
    if not partner_uid or partner_uid == uid:
        return
    partner_flags = get_user_effects(today, partner_uid)["flags"]
    if partner_flags.get(flag_key) == bool(value):
        return
    set_user_flag(today, partner_uid, flag_key, value, propagate=False)


def _sync_brother_statuses(today: str, uid_a: str, uid_b: str):
    uid_a = str(uid_a)
    uid_b = str(uid_b)
    if uid_a == uid_b:
        return
    flags_a = get_user_effects(today, uid_a)["flags"]
    flags_b = get_user_effects(today, uid_b)["flags"]
    all_keys = set(flags_a.keys()) | set(flags_b.keys())
    changed = False
    for key in all_keys:
        combined = bool(flags_a.get(key, False) or flags_b.get(key, False))
        if flags_a.get(key, False) != combined:
            flags_a[key] = combined
            changed = True
        if flags_b.get(key, False) != combined:
            flags_b[key] = combined
            changed = True
    if changed:
        save_effects()


def _clear_brother_link(today: str, uid: str):
    uid = str(uid)
    eff = get_user_effects(today, uid)
    meta = eff["meta"]
    partner = meta.pop("brother_partner", None)
    meta.pop("brother_label", None)
    partner_uid = str(partner) if partner is not None else None
    partner_changed = False
    if partner_uid:
        partner_eff = get_user_effects(today, partner_uid)
        partner_meta = partner_eff["meta"]
        if partner_meta.get("brother_partner") == uid:
            partner_meta.pop("brother_partner", None)
            partner_meta.pop("brother_label", None)
            partner_changed = True
    if partner is not None or partner_changed:
        save_effects()
    set_user_flag(today, uid, "brother_bond", False, propagate=False)
    if partner_uid:
        set_user_flag(today, partner_uid, "brother_bond", False, propagate=False)


def get_user_mod(today: str, uid: str, mod_key: str, default=0):
    return get_user_effects(today, uid)["mods"].get(mod_key, default)


def add_user_mod(today: str, uid: str, mod_key: str, delta):
    eff = get_user_effects(today, uid)
    eff["mods"][mod_key] = eff["mods"].get(mod_key, 0) + delta
    save_effects()


def set_user_mod(today: str, uid: str, mod_key: str, value):
    eff = get_user_effects(today, uid)
    eff["mods"][mod_key] = value
    save_effects()


def get_user_meta(today: str, uid: str, key: str, default=None):
    return get_user_effects(today, uid)["meta"].get(key, default)


def set_user_meta(today: str, uid: str, key: str, value):
    get_user_effects(today, uid)["meta"][key] = value
    save_effects()


def get_group_meta(today: str, gid: str, key: str, default=0):
    day_map = effects_data.setdefault(today, {})
    group_map = day_map.setdefault("__groups__", {})
    group_state = group_map.get(gid, {})
    return group_state.get(key, default)


def add_group_meta(today: str, gid: str, key: str, delta):
    day_map = effects_data.setdefault(today, {})
    group_map = day_map.setdefault("__groups__", {})
    group_state = group_map.setdefault(gid, {})
    group_state[key] = group_state.get(key, 0) + delta
    save_effects()


def set_group_meta(today: str, gid: str, key: str, value):
    day_map = effects_data.setdefault(today, {})
    group_map = day_map.setdefault("__groups__", {})
    group_state = group_map.setdefault(gid, {})
    group_state[key] = value
    save_effects()


effects_data = {}
load_effects()
load_ntr_statuses()
load_ntr_records()
load_change_records()
load_swap_requests()
load_swap_limit_records()
load_select_wife_records()
load_beat_wife_records()
load_seduce_records()
load_reset_blind_box_records()
load_market_data()
load_market_purchase_records()
load_gift_requests()
cleanup_gift_requests()
load_archives()


@register(
    "astrbot_plugin_animewifex",
    "monbed",
    "群二次元老婆插件修改版",
    "1.6.2",
    "https://github.com/monbed/astrbot_plugin_animewifex",
)
class WifePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        # 配置参数初始化
        self.ntr_max = config.get("ntr_max")
        self.ntr_possibility = config.get("ntr_possibility")
        self.change_max_per_day = config.get("change_max_per_day")
        self.reset_max_uses_per_day = config.get("reset_max_uses_per_day")
        self.reset_success_rate = config.get("reset_success_rate")
        self.reset_mute_duration = config.get("reset_mute_duration")
        self.image_base_url = config.get("image_base_url")
        self.swap_max_per_day = config.get("swap_max_per_day")
        self.market_max_wives = 16
        self.market_max_items = 8
        self.item_pool = [
            "牛魔王",
            "开后宫",
            "贤者时间",
            "开impart",
            "纯爱战士",
            "雌堕",
            "雄竞",
            "苦主",
            "黄毛",
            "吃一堑",
            "何意味",
            "白月光",
            "公交车",
            "病娇",
            "儒夫",
            "熊出没",
            "宝刀未老",
            "鹿鹿时间到了",
            "开明盒",
            "龙王",
            "二度寝",
            "烧火棍",
            "未来日记",
            "爱马仕",
            "柏青哥",
            "苦命鸳鸯",
            "牛道具",
            "偷拍",
            "复读",
            "囤囤鼠",
            "露出癖",
            "会员制餐厅",
            "偷外卖",
            "富哥",
            "疯狂星期四",
            "赠人玫瑰",
            "南北西",
            "城管",
            "仓管",
            "电灯泡",
            "枪兵",
            "修罗",
            "吉星如意",
            "穷凶极恶",
            "缘分",
            "55开",
            "洗牌",
            "塞翁失马",
            "斗转星移",
            "好兄弟",
            "存档",
        ]
        self.items_need_target = {"雌堕", "雄竞", "勾引", "牛道具", "偷拍", "复读", "会员制餐厅", "好兄弟"}
        # 状态效果判定工具
        def flag_checker(flag_key: str):
            return lambda eff, key=flag_key: eff["flags"].get(key, False)

        def any_flag_checker(*flag_keys: str):
            return lambda eff, keys=flag_keys: any(eff["flags"].get(k, False) for k in keys)

        def mod_equals_checker(mod_key: str, expected):
            return lambda eff, mod=mod_key, val=expected: eff["mods"].get(mod) == val

        def meta_exists_checker(meta_key: str):
            return lambda eff, meta=meta_key: bool(eff["meta"].get(meta))

        def meta_equals_checker(meta_key: str, expected):
            return lambda eff, meta=meta_key, val=expected: eff["meta"].get(meta) == val

        self.status_effect_specs = [
            {
                "id": "harem",
                "label": "开后宫",
                "desc": "开后宫：今日可以拥有多个老婆，使用「牛老婆」后会追加一次不消耗次数的「抽老婆」，但无法使用「换老婆」与「重置」指令",
                "item_name": "开后宫",
                "checker": flag_checker("harem"),
            },
            {
                "id": "protect_from_ntr",
                "label": "纯爱战士",
                "desc": "纯爱战士：今日老婆不会被牛走，也无法使用「换老婆」",
                "item_name": "纯爱战士",
                "checker": flag_checker("protect_from_ntr"),
            },
            {
                "id": "ban_change",
                "label": "换老婆禁用",
                "desc": "换老婆禁用：今日无法使用「换老婆」指令",
                "checker": flag_checker("ban_change"),
            },
            {
                "id": "ban_items",
                "label": "贤者时间",
                "desc": "贤者时间：今日不受任何道具影响，也无法使用道具",
                "item_name": "贤者时间",
                "checker": flag_checker("ban_items"),
            },
            {
                "id": "ban_ntr",
                "label": "公交车",
                "desc": "公交车：今日无法使用「牛老婆」，但可以强制交换老婆",
                "item_name": "公交车",
                "checker": any_flag_checker("ban_ntr", "force_swap"),
            },
            {
                "id": "ntr_override",
                "label": "牛魔王",
                "desc": "牛魔王：牛老婆成功率提升并无视禁用效果，从其它渠道获得次数翻倍",
                "item_name": "牛魔王",
                "checker": flag_checker("ntr_override"),
            },
            {
                "id": "landmine_girl",
                "label": "病娇",
                "desc": "病娇：你的老婆不会被牛走，但成功牛别人时可能遭遇惩罚",
                "item_name": "病娇",
                "checker": flag_checker("landmine_girl"),
            },
            {
                "id": "victim_auto_ntr",
                "label": "苦主",
                "desc": "苦主：别人牛你必定成功，且每次失去老婆会额外获得1次「换老婆」次数，同时无法拒绝交换",
                "item_name": "苦主",
                "checker": any_flag_checker("victim_auto_ntr", "ban_reject_swap"),
            },
            {
                "id": "next_ntr_guarantee",
                "label": "黄毛",
                "desc": "黄毛：下一次「牛老婆」必定成功，今日无法再使用「换老婆」",
                "item_name": "黄毛",
                "checker": flag_checker("next_ntr_guarantee"),
            },
            {
                "id": "double_item_effect",
                "label": "二度寝",
                "desc": "二度寝：下次使用的道具卡数值效果翻倍",
                "item_name": "二度寝",
                "checker": flag_checker("double_item_effect"),
            },
            {
                "id": "stick_hero",
                "label": "棍勇",
                "desc": "棍勇：获得额外的重置次数与特殊抽换老婆效果",
                "item_name": "烧火棍",
                "checker": flag_checker("stick_hero"),
                "desc_generator": lambda today, uid, gid: (
                    f"棍勇：额外获得{int(get_user_mod(today, uid, 'reset_extra_uses', 0))}次重置次数和{int(get_user_mod(today, uid, 'reset_blind_box_extra', 0))}次重置盲盒机会，抽老婆和换老婆有特殊效果"
                ),
            },
            {
                "id": "light_fingers",
                "label": "顺手的事",
                "desc": "顺手的事：牛成功或在集市购物时，有50%概率顺手牵羊/被抓",
                "item_name": "偷外卖",
                "checker": flag_checker("light_fingers"),
            },
            {
                "id": "rich_bro",
                "label": "富哥",
                "desc": "富哥：今日额外获得2次老婆集市购买机会，并随机让一位群友见者有份",
                "item_name": "富哥",
                "checker": flag_checker("rich_bro"),
            },
            {
                "id": "share_bonus",
                "label": "见者有份",
                "desc": "见者有份：今日额外获得1次老婆集市购买机会",
                "checker": flag_checker("share_bonus"),
            },
            {
                "id": "learned",
                "label": "长一智",
                "desc": "长一智：当别人对你使用道具卡时你会获得对方使用的那张道具卡",
                "item_name": "吃一堑",
                "checker": flag_checker("learned"),
            },
            {
                "id": "hand_scent",
                "label": "手留余香",
                "desc": "手留余香：你赠送道具时会随机获得一张新的道具卡",
                "item_name": "赠人玫瑰",
                "checker": flag_checker("hand_scent"),
            },
            {
                "id": "blind_box_enthusiast",
                "label": "盲盒爱好者",
                "desc": "盲盒爱好者：今日每4小时可免费抽一次盲盒，每1小时仅能使用一个道具",
                "item_name": "囤囤鼠",
                "checker": flag_checker("blind_box_enthusiast"),
            },
            {
                "id": "exhibitionist",
                "label": "露出癖",
                "desc": "露出癖：今日使用任何指令和道具都会额外执行一次「查老婆」指令",
                "item_name": "露出癖",
                "checker": flag_checker("exhibitionist"),
            },
            {
                "id": "hermes",
                "label": "爱马仕",
                "desc": "爱马仕：抽老婆或换老婆只会抽到「赛马娘」的角色",
                "item_name": "爱马仕",
                "checker": flag_checker("hermes"),
            },
            {
                "id": "yuanpi",
                "label": "原批",
                "desc": "原批：今日抽老婆和换老婆只会抽到「原神」的角色",
                "item_name": "缘分",
                "checker": flag_checker("yuanpi"),
            },
            {
                "id": "equal_rights",
                "label": "众生平等",
                "desc": "众生平等：你对其他人使用指令或道具时可无视对方的状态，但其他人对你使用道具时也会无视你的状态",
                "item_name": "55开",
                "checker": flag_checker("equal_rights"),
            },
            {
                "id": "fortune_linked",
                "label": "福祸相依",
                "desc": "福祸相依：今日失去老婆时会获得同数量的随机道具卡，失去道具卡时会获得同数量的新老婆（使用道具或换老婆不视为失去）",
                "item_name": "塞翁失马",
                "checker": flag_checker("fortune_linked"),
            },
            {
                "id": "brother_bond",
                "label": "同甘共苦",
                "desc": "同甘共苦：今日与你绑定的好兄弟将与你共享全部状态",
                "desc_generator": lambda today, uid, gid: (
                    f"与{get_user_meta(today, uid, 'brother_label') or '好兄弟'}同甘共苦：任意一方获得的新状态都会立即共享"
                ),
                "checker": flag_checker("brother_bond"),
            },
            {
                "id": "lucky_e",
                "label": "幸运E",
                "desc": "幸运E：所有概率减半但不会低于20%",
                "item_name": "枪兵",
                "checker": flag_checker("lucky_e"),
            },
            {
                "id": "shura",
                "label": "修罗",
                "desc": "修罗：你今天不再触发修罗场且最多拥有6位老婆，但仅能通过「牛老婆」获得新老婆",
                "item_name": "修罗",
                "checker": flag_checker("shura"),
            },
            {
                "id": "pachinko_777",
                "label": "777",
                "desc": "777：今日抽盲盒必定触发一次暴击，并获得额外抽盲盒机会",
                "checker": flag_checker("pachinko_777"),
            },
            {
                "id": "competition_target",
                "label": "雄竞",
                "desc": "雄竞：今日抽老婆有概率抽到与目标相同的老婆",
                "item_name": "雄竞",
                "checker": meta_exists_checker("competition_target"),
                "desc_generator": lambda today, uid, gid: (
                    (lambda comp_target: (
                        (lambda comp_uid: (
                            f"雄竞：正在与{((get_group_record(comp_uid, gid) or {}).get('nick') or (wives_data.get(comp_uid, {}) if isinstance(wives_data, dict) else {}).get('nick') or f'用户{comp_uid}')}竞争同款老婆"
                        ))(str(comp_target)) if comp_target else "雄竞：今日抽老婆有概率抽到与目标相同的老婆"
                    ))(get_user_meta(today, uid, "competition_target", None))
                ),
            },
            {
                "id": "seduce_unlimited",
                "label": "熊出没",
                "desc": "熊出没：今日可无限次使用「勾引」，但每次有被禁言的风险",
                "item_name": "熊出没",
                "checker": mod_equals_checker("seduce_uses", -1),
            },
            {
                "id": "future_diary_target",
                "label": "未来日记",
                "desc": "未来日记：下次抽老婆或换老婆将指向特定角色",
                "item_name": "未来日记",
                "checker": meta_equals_checker("future_diary_target", "我妻由乃"),
            },
            {
                "id": "lightbulb",
                "label": "电灯泡",
                "desc": "电灯泡：监听指定群的换/牛老婆动向获取额外次数，并禁止重置",
                "item_name": "电灯泡",
                "checker": flag_checker("lightbulb"),
                "desc_generator": lambda today, uid, gid: (
                    f"电灯泡：监听群{get_user_meta(today, uid, 'lightbulb_group', None) or '指定'}的换/牛老婆动向获取额外次数，无法使用各类重置指令"
                ),
            },
            {
                "id": "super_lucky",
                "label": "超吉",
                "desc": "超吉：若你的老婆为今日吉星，则今日运势加成变为120%，不再会触发修罗场事件，且你的抽盲盒必定触发幸运事件",
                "item_name": "吉星如意",
                "checker": flag_checker("super_lucky"),
            },
            {
                "id": "extreme_evil",
                "label": "穷凶极恶",
                "desc": "穷凶极恶：今日你的所有需要@目标的指令或道具的作恶概率加成变为125%",
                "item_name": "穷凶极恶",
                "checker": flag_checker("extreme_evil"),
            },
        ]
        self.status_item_specs = {
            spec["item_name"]: spec
            for spec in self.status_effect_specs
            if spec.get("item_name")
        }
        # 状态效果道具（不可重复获得）
        self.status_items = set(self.status_item_specs.keys())
        # 柏青哥三状态随机池配置（道具名称, 是否已拥有检查器）
        pachinko_state_order = [
            "牛魔王",
            "开后宫",
            "纯爱战士",
            "苦主",
            "黄毛",
            "公交车",
            "病娇",
            "熊出没",
            "二度寝",
            "爱马仕",
            "囤囤鼠",
            "露出癖",
            "偷外卖",
            "富哥",
            "吃一堑",
            "电灯泡",
            "枪兵",
            "修罗",
        ]
        self.pachinko_state_specs = [
            (item_name, self.status_item_specs[item_name]["checker"])
            for item_name in pachinko_state_order
            if item_name in self.status_item_specs
        ]
        # 命令与处理函数映射
        self.commands = {
            "抽老婆": self.animewife,
            "牛老婆": self.ntr_wife,
            "查老婆": self.search_wife,
            "查状态": self.view_status,
            "老婆插件帮助": self.show_wife_help,
            "切换ntr开关状态": self.switch_ntr,
            "换老婆": self.change_wife,
            "重置牛": self.reset_ntr,
            "老婆集市": self.show_market,
            "购买": self.purchase_from_market,
            "重置换": self.reset_change_wife,
            "交换老婆": self.swap_wife,
            "同意交换": self.agree_swap_wife,
            "拒绝交换": self.reject_swap_wife,
            "查看交换请求": self.view_swap_requests,
            "抽盲盒": self.draw_item,
            "重置盲盒": self.reset_blind_box,
            "使用": self.use_item,
            "查道具": self.view_items,
            "选老婆": self.select_wife,
            "打老婆": self.beat_wife,
            "勾引": self.seduce,
            "重开": self.reset_basics,
            "赠送": self.gift_item,
            "索取": self.request_item,
            "同意赠送": self.accept_gift,
            "同意索取": self.accept_request,
            "查看道具请求": self.view_item_requests,
            "今日运势": self.show_fortune,
        }
        self.admins = self.load_admins()

    def load_admins(self):
        # 加载管理员列表
        path = os.path.join("data", "cmd_config.json")
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                cfg = json.load(f)
                return cfg.get("admins_id", [])
        except:
            return []

    def parse_at_target(self, event):
        # 解析@目标用户
        for comp in event.message_obj.message:
            if isinstance(comp, At):
                return str(comp.qq)
        return None

    def parse_target(self, event):
        # 解析命令目标用户
        target = self.parse_at_target(event)
        if target:
            return target
        msg = event.message_str.strip()
        if msg.startswith("牛老婆") or msg.startswith("查老婆"):
            name = msg.split(maxsplit=1)[-1]
            if name:
                group_id = str(event.message_obj.group_id)
                for uid, record, entry in iter_group_users(group_id):
                    nick = entry.get("nick") or record.get("nick")
                    if nick and re.search(re.escape(name), nick, re.IGNORECASE):
                        return uid
        return None

    def _build_image_component(self, img: str):
        if not img:
            return None
        if img.startswith("http"):
            return AstrImage.fromURL(img)
        path = os.path.join(IMG_DIR, img)
        if os.path.exists(path):
            return AstrImage.fromFileSystem(path)
        if self.image_base_url and isinstance(self.image_base_url, str) and self.image_base_url.startswith(("http://", "https://")):
            join_url = self.image_base_url.rstrip("/") + "/" + img.lstrip("/")
            return AstrImage.fromURL(join_url)
        return None

    def _ensure_blind_box_group(self, today: str, uid: str, gid: str):
        groups = get_user_meta(today, uid, "blind_box_groups", [])
        if not isinstance(groups, list):
            groups = []
        if gid not in groups:
            new_groups = list(groups)
            new_groups.append(gid)
            set_user_meta(today, uid, "blind_box_groups", new_groups)

    def _resolve_avatar_nick(self, cfg: dict, img: str) -> str:
        match = re.search(r"nk=([0-9]+)", img)
        if not match:
            return "神秘人"
        target_uid = match.group(1)
        data = cfg.get(target_uid, {})
        if isinstance(data, dict):
            nick = data.get("nick")
            if nick:
                return nick
        return f"用户{target_uid}"

    def _get_wife_display_name(self, cfg: dict, img: str) -> str:
        """根据图片路径或QQ头像URL，提取用于文案的老婆名字"""
        if not img:
            return "神秘人"
        if img.startswith("http"):
            # QQ 头像：用群配置里的昵称
            return self._resolve_avatar_nick(cfg, img)
        base = os.path.splitext(os.path.basename(img))[0]
        if "!" in base:
            # 形如 作品!角色名
            _, chara = base.split("!", 1)
            return chara
        return base

    async def _trigger_exhibitionist_search(self, event: AstrMessageEvent, text: str = ""):
        """露出效果：额外执行一次查老婆"""
        if getattr(event, "_exhibitionist_extra_done", False):
            return
        today = get_today()
        uid = str(event.get_sender_id())
        if not get_user_flag(today, uid, "exhibitionist"):
            return
        if text.startswith("查老婆") or text.startswith("换老婆"):
            return
        setattr(event, "_exhibitionist_extra_done", True)
        async for res in self.search_wife(event):
            yield res

    def _ensure_market_history(self, today: str, uid: str) -> list:
        purchase_records = market_purchase_records.setdefault(today, {})
        history = purchase_records.get(uid)
        if isinstance(history, dict):
            history = [history]
        if not isinstance(history, list):
            history = []
        purchase_records[uid] = history
        return history

    def _collect_user_archive_payload(self, today: str, uid: str) -> dict:
        uid = str(uid)
        payload = {}
        day_effects = effects_data.get(today, {}).get(uid)
        if day_effects is not None:
            payload["effects"] = copy.deepcopy(day_effects)
        record = wives_data.get(uid)
        if record:
            payload["wife_record"] = copy.deepcopy(record)
        return payload

    def _apply_user_archive_payload(self, today: str, uid: str, payload: dict):
        uid = str(uid)
        if "effects" in payload:
            effects_data.setdefault(today, {})[uid] = copy.deepcopy(payload["effects"])
            save_effects()
        if "wife_record" in payload:
            record = copy.deepcopy(payload["wife_record"])
            record["date"] = today
            record.setdefault("nick", record.get("nick", f"用户{uid}"))
            record.setdefault("wives", record.get("wives", []))
            record.setdefault("groups", record.get("groups", []))
            wives_data[uid] = record
            save_wife_data()

    def _restore_archive_if_needed(self, today: str, uid: str) -> str | None:
        uid = str(uid)
        archive = archives.get(uid)
        if not archive:
            return None
        saved_on = archive.get("saved_on")
        data = archive.get("data")
        if not data:
            del archives[uid]
            save_archives()
            return None
        if saved_on == today:
            return None
        self._apply_user_archive_payload(today, uid, data)
        del archives[uid]
        save_archives()
        return f"已为你加载{saved_on}的存档，今日数据沿用当日状态。"

    def _consume_market_purchase_quota(self, today: str, uid: str, purchase_type: str, history_len: int) -> bool:
        base_limit = 1
        if history_len < base_limit:
            return True
        extra_general = int(get_user_mod(today, uid, "market_extra_purchases", 0))
        if extra_general > 0:
            add_user_mod(today, uid, "market_extra_purchases", -1)
            return True
        extra_wife = int(get_user_mod(today, uid, "market_wife_extra_purchases", 0))
        if purchase_type == "wife" and extra_wife > 0:
            add_user_mod(today, uid, "market_wife_extra_purchases", -1)
            return True
        return False

    def _handle_wife_loss(self, today: str, uid: str, loss_count: int = 1, gid: str = None):
        loss = int(loss_count or 0)
        if loss <= 0:
            return
        if get_user_flag(today, uid, "fortune_linked"):
            self._grant_fortune_bond_item_reward(today, uid, loss)
        if not get_user_flag(today, uid, "victim_auto_ntr"):
            return
        # 开后宫用户：换老婆次数转换为抽老婆次数
        is_harem = get_user_flag(today, uid, "harem")
        if is_harem and gid:
            # 如果有gid且是开后宫用户，直接转换为抽老婆次数
            self._convert_change_to_draw_for_harem(today, uid, gid, loss)
        else:
            # 否则增加change_extra_uses（普通用户或没有gid的情况）
            add_user_mod(today, uid, "change_extra_uses", loss)
        penalty = int(get_user_meta(today, uid, "ntr_penalty_stack", 0) or 0)
        set_user_meta(today, uid, "ntr_penalty_stack", penalty + loss)

    def _grant_fortune_bond_item_reward(self, today: str, uid: str, count: int):
        reward_count = int(count or 0)
        if reward_count <= 0:
            return
        today_items = item_data.setdefault(today, {})
        user_items = today_items.setdefault(uid, [])
        rewards = random.choices(self.item_pool, k=reward_count)
        user_items.extend(rewards)
        save_item_data()

    def _choose_random_wife_image(self):
        try:
            candidates = [
                f for f in os.listdir(IMG_DIR)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
            ]
        except Exception:
            candidates = []
        if not candidates:
            return None
        return random.choice(candidates)

    def _grant_fortune_bond_wife_reward(self, today: str, uid: str, count: int, gid: str = None):
        reward_count = int(count or 0)
        if reward_count <= 0 or not gid:
            return
        cfg = load_group_config(gid)
        user_entry = cfg.get(uid)
        if isinstance(user_entry, dict):
            nick = user_entry.get("nick", f"用户{uid}")
        else:
            nick = f"用户{uid}"
        is_harem = get_user_flag(today, uid, "harem")
        granted = 0
        for _ in range(reward_count):
            img = self._choose_random_wife_image()
            if not img:
                break
            if add_wife(cfg, uid, img, today, nick, is_harem):
                granted += 1
        if granted:
            save_group_config(cfg)

    def _handle_item_loss(self, today: str, uid: str, loss_count: int = 1, gid: str = None):
        loss = int(loss_count or 0)
        if loss <= 0:
            return
        if get_user_flag(today, uid, "fortune_linked"):
            self._grant_fortune_bond_wife_reward(today, uid, loss, gid)
    
    def _convert_change_to_draw_for_harem(self, today: str, uid: str, gid: str, amount: int):
        """
        开后宫用户获得换老婆次数时，转换为抽老婆次数
        通过增加change_extra_uses来增加可用次数，不修改records的count
        """
        is_harem = get_user_flag(today, uid, "harem")
        if is_harem and amount > 0:
            # 增加额外使用次数，而不是修改records的count
            add_user_mod(today, uid, "change_extra_uses", amount)
    
    def _check_exhibitionist_chaos(self, today: str, uid: str, gid: str, cfg: dict) -> tuple[bool, int]:
        """
        检查露出状态的修罗场触发（超吉状态不会触发）
        返回: (是否触发, 老婆数量)
        """
        # 超吉状态：不再触发修罗场
        if get_user_flag(today, uid, "super_lucky"):
            return False, get_wife_count(cfg, uid, today)
        if get_user_flag(today, uid, "shura"):
            return False, get_wife_count(cfg, uid, today)
        is_exhibitionist = get_user_flag(today, uid, "exhibitionist")
        is_harem = get_user_flag(today, uid, "harem")
        if not is_exhibitionist or not is_harem:
            return False, 0
        wife_count = get_wife_count(cfg, uid, today)
        if wife_count >= 2:
            # 触发修罗场，失去所有老婆
            if uid in cfg:
                loss = wife_count
                del cfg[uid]
                save_group_config(cfg)
                self._handle_wife_loss(today, uid, loss, gid)
            return True, wife_count
        return False, wife_count

    async def _handle_light_fingers_on_ntr(self, today: str, uid: str, target_uid: str, event: AstrMessageEvent, cfg: dict):
        if not get_user_flag(today, uid, "light_fingers"):
            return
        gid = str(event.message_obj.group_id)
        nick = event.get_sender_name()
        today_items = item_data.setdefault(today, {})
        user_items = today_items.setdefault(uid, [])
        steal = self._probability_check(0.5, today, uid)
        if steal:
            target_items = today_items.get(target_uid, [])
            if target_items:
                stolen = random.choice(target_items)
                target_items.remove(stolen)
                user_items.append(stolen)
                save_item_data()
                self._handle_item_loss(today, target_uid, 1, gid)
                target_info = cfg.get(target_uid, {})
                target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
                yield event.plain_result(f"{nick}，顺手牵羊成功，从{target_nick}那里偷到了「{stolen}」！")
            else:
                yield event.plain_result(f"{nick}，你想顺手牵羊，但对方没有道具可偷。")
        else:
            if user_items:
                lost = random.choice(user_items)
                user_items.remove(lost)
                save_item_data()
                self._handle_item_loss(today, uid, 1, gid)
                yield event.plain_result(f"{nick}，被抓个正着，失去了自己的「{lost}」。")
            else:
                yield event.plain_result(f"{nick}，被抓个正着，但你身上没有道具。")

    async def _handle_light_fingers_on_market(self, today: str, uid: str, event: AstrMessageEvent, market: dict):
        if not get_user_flag(today, uid, "light_fingers"):
            return
        gid = str(event.message_obj.group_id)
        nick = event.get_sender_name()
        today_items = item_data.setdefault(today, {})
        user_items = today_items.setdefault(uid, [])
        steal = self._probability_check(0.5, today, uid)
        if steal:
            market_items = market.get("items", [])
            if market_items:
                stolen = random.choice(market_items)
                market_items.remove(stolen)
                user_items.append(stolen)
                save_market_data()
                save_item_data()
                yield event.plain_result(f"{nick}，顺手牵羊成功，从集市额外偷到了「{stolen}」！")
            else:
                yield event.plain_result(f"{nick}，你想顺手牵羊，但集市里已经没有道具卡可偷。")
        else:
            if user_items:
                lost = random.choice(user_items)
                user_items.remove(lost)
                save_item_data()
                self._handle_item_loss(today, uid, 1, gid)
                yield event.plain_result(f"{nick}，被抓个正着，集市管理员没收了你的「{lost}」。")
            else:
                yield event.plain_result(f"{nick}，被抓个正着，但你身上没有道具卡可没收。")

    async def _redistribute_wives(self, gid: str, today: str, event: AstrMessageEvent, cfg: dict):
        today_users = []
        harem_users = {}
        all_images = []
        protected_users = set()
        for u, rec, _ in iter_group_users(gid):
            if rec.get("date") != today:
                continue
            if get_user_flag(today, u, "ban_items"):
                protected_users.add(u)
                continue
            wives = list(rec.get("wives", []))
            if not wives:
                continue
            if rec.get("harem"):
                harem_users[u] = list(wives)
                all_images.extend(wives)
            else:
                today_users.append((u, list(wives)))
                all_images.append(wives[0])
        if len(today_users) + len(harem_users) < 2:
            return False, "当前持有老婆的用户不足以进行重新分配~"
        random.shuffle(all_images)
        idx = 0
        for u, old_wives in today_users:
            if idx < len(all_images):
                rec = ensure_group_record(u, gid, today, "", keep_existing=False)
                rec["wives"] = [all_images[idx]]
                rec["harem"] = False
                idx += 1
                self._handle_wife_loss(today, u, len(old_wives), gid)
        for u, old_wives in harem_users.items():
            count = len(old_wives)
            if idx + count <= len(all_images):
                rec = ensure_group_record(u, gid, today, "", keep_existing=False)
                rec["harem"] = True
                rec["wives"] = all_images[idx:idx + count]
                idx += count
                self._handle_wife_loss(today, u, count, gid)
        save_group_config(cfg)
        all_owners = [u for u, _ in today_users] + list(harem_users.keys())
        cancel_msg = await self.cancel_swap_on_wife_change(gid, all_owners)
        msg = "已将所有今日拥有老婆的用户进行随机分配！"
        if protected_users:
            msg += "（拥有贤者时间的人不受影响）"
        if cancel_msg:
            msg += f"\n{cancel_msg}"
        return True, msg

    @event_message_type(EventMessageType.ALL)
    async def on_all_messages(self, event: AstrMessageEvent):
        # 消息分发，根据命令调用对应方法
        if not hasattr(event.message_obj, "group_id"):
            return
        today = get_today()
        uid = str(event.get_sender_id())
        restored_msg = self._restore_archive_if_needed(today, uid)
        if restored_msg:
            yield event.plain_result(restored_msg)
        text = event.message_str.strip()
        cmd_executed = False
        for cmd, func in self.commands.items():
            if text.startswith(cmd):
                async for res in func(event):
                    yield res
                cmd_executed = True
                break
        
        # 检查露出效果：使用任何指令后额外执行一次查老婆
        if cmd_executed:
            async for res in self._trigger_exhibitionist_search(event, text):
                yield res

    async def draw_item(self, event: AstrMessageEvent):
        # 抽盲盒主逻辑
        today = get_today()
        gid = str(event.message_obj.group_id)
        cfg = load_group_config(gid)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today_items = item_data.setdefault(today, {})
        user_items = today_items.get(uid)
        extra_draws = int(get_user_mod(today, uid, "blind_box_extra_draw", 0) or 0)
        allow_extra_draw = extra_draws > 0
        
        # 检查盲盒爱好者状态：每4小时可以免费抽一次盲盒
        is_blind_box_enthusiast = get_user_flag(today, uid, "blind_box_enthusiast")
        if is_blind_box_enthusiast:
            now = datetime.utcnow().timestamp()
            last_free_draw = get_user_meta(today, uid, "last_free_blind_box_draw", 0)
            four_hours_ago = now - 14400  # 4小时 = 14400秒
            
            if last_free_draw > four_hours_ago:
                # 距离上次免费抽盲盒不足4小时
                wait_seconds = int(14400 - (now - last_free_draw))
                wait_hours = wait_seconds // 3600
                wait_mins = (wait_seconds % 3600) // 60
                if wait_hours > 0:
                    wait_text = f"{wait_hours}小时{wait_mins}分钟"
                else:
                    wait_text = f"{wait_mins}分钟"
                yield event.plain_result(f"{nick}，你作为盲盒爱好者，每4小时可以免费抽一次盲盒，请等待{wait_text}后再试~")
                return
            
            # 可以免费抽盲盒，记录本次时间
            set_user_meta(today, uid, "last_free_blind_box_draw", now)
            # 继续执行抽盲盒逻辑，不消耗正常次数
        elif user_items is not None and not allow_extra_draw:
            yield event.plain_result(f"{nick}，你今天已经抽过盲盒啦，明天再来吧~")
            return
        had_items_before = user_items is not None and len(user_items) > 0
        existing_items = list(user_items or [])
        if allow_extra_draw:
            add_user_mod(today, uid, "blind_box_extra_draw", -1)
        # 检查5%概率触发永久加成效果（超吉状态必定触发，但今日最多触发一次）
        perk_triggered = False
        perk_message = ""
        is_super_lucky = get_user_flag(today, uid, "super_lucky")
        super_lucky_perk_used = get_user_meta(today, uid, "super_lucky_perk_used", False)
        
        # 超吉状态：必定触发幸运事件（今日最多一次）
        if is_super_lucky and not super_lucky_perk_used:
            perk_triggered = True
            set_user_meta(today, uid, "super_lucky_perk_used", True)
            perk_type = random.choice(["item_count", "crit_rate", "empty_reduction"])
            if perk_type == "item_count":
                new_value = add_blind_box_perk(uid, "item_count_bonus", 1, max_value=5)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒可能获得的道具数量+1（当前+{new_value}，最多+5）"
            elif perk_type == "crit_rate":
                new_value = add_blind_box_perk(uid, "crit_rate_bonus", 0.02, max_value=0.10)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒暴击率+2%（当前+{int(new_value * 100)}%，最多+10%）"
            else:  # empty_reduction
                new_value = add_blind_box_perk(uid, "empty_reduction_bonus", 0.04, max_value=0.20)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒抽不到道具卡的概率-4%（当前-{int(new_value * 100)}%，最多-20%）"
        elif not is_super_lucky and self._probability_check(0.05, today, uid):
            perk_triggered = True
            perk_type = random.choice(["item_count", "crit_rate", "empty_reduction"])
            if perk_type == "item_count":
                new_value = add_blind_box_perk(uid, "item_count_bonus", 1, max_value=5)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒可能获得的道具数量+1（当前+{new_value}，最多+5）"
            elif perk_type == "crit_rate":
                new_value = add_blind_box_perk(uid, "crit_rate_bonus", 0.02, max_value=0.10)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒暴击率+2%（当前+{int(new_value * 100)}%，最多+10%）"
            else:  # empty_reduction
                new_value = add_blind_box_perk(uid, "empty_reduction_bonus", 0.04, max_value=0.20)
                perk_message = f"🎁 幸运事件！你获得了永久加成：抽盲盒抽不到道具卡的概率-4%（当前-{int(new_value * 100)}%，最多-20%）"
        
        # 获取永久加成值
        item_count_bonus = get_blind_box_perk(uid, "item_count_bonus", 0)
        crit_rate_bonus = get_blind_box_perk(uid, "crit_rate_bonus", 0.0)
        empty_reduction_bonus = get_blind_box_perk(uid, "empty_reduction_bonus", 0.0)
        
        # 分离状态效果道具和普通道具
        status_pool = [item for item in self.item_pool if item in self.status_items]
        normal_pool = [item for item in self.item_pool if item not in self.status_items]
        drawn_items = []
        drawn_status = set()  # 已抽取的状态效果道具（不可重复）
        # 抽盲盒按"批次"进行：每一批都有 0~5 张道具卡（可受永久加成影响）
        # 暴击时增加一整批额外抽取机会（再次抽 0~5 张）
        pending_batches = 1
        crit_times = 0
        pachinko_777 = get_user_flag(today, uid, "pachinko_777")
        pachinko_777_used = False  # 777效果是否已使用
        while pending_batches > 0:
            pending_batches -= 1
            # 本批次决定抽取的道具数量（应用永久加成）
            base_empty_prob = 0.2 - empty_reduction_bonus  # 空抽概率，最低为0
            base_empty_prob = max(0.0, min(1.0, base_empty_prob))
            if self._probability_check(base_empty_prob, today, uid):
                batch_count = 0
            else:
                max_count = 5 + item_count_bonus
                batch_count = random.randint(1, max_count)
            for _ in range(batch_count):
                available_pools = []
                if len(drawn_status) < len(status_pool):
                    available_pools.append("status")
                if normal_pool:
                    available_pools.append("normal")
                if not available_pools:
                    break  # 没有可抽取的道具了
                pool_type = random.choice(available_pools)
                if pool_type == "status":
                    available_status = [item for item in status_pool if item not in drawn_status]
                    if not available_status:
                        continue
                    item = random.choice(available_status)
                    drawn_status.add(item)
                else:
                    item = random.choice(normal_pool)
                drawn_items.append(item)
            # 暴击检查（应用永久加成，777效果：必定触发一次）
            base_crit_rate = 0.20 + crit_rate_bonus
            base_crit_rate = min(1.0, base_crit_rate)  # 暴击率最高100%
            should_crit = False
            if pachinko_777 and not pachinko_777_used:
                should_crit = True
                pachinko_777_used = True
                set_user_flag(today, uid, "pachinko_777", False)  # 使用后清除777效果
            elif self._probability_check(base_crit_rate, today, uid):
                should_crit = True
            if should_crit:
                pending_batches += 1
                crit_times += 1
        if not drawn_items:
            today_items[uid] = existing_items
            save_item_data()
            self._ensure_blind_box_group(today, uid, gid)
            result_parts = []
            if perk_triggered:
                result_parts.append(perk_message)
            if existing_items:
                result_parts.append(f"{nick}，这次额外的盲盒机会什么都没抽到，不过之前的道具仍然保留~")
            else:
                result_parts.append(f"{nick}，今天的盲盒空空如也，什么都没抽到呢~")
            yield event.plain_result("\n".join(result_parts))
            return
        existing_items.extend(drawn_items)
        today_items[uid] = existing_items
        save_item_data()
        self._ensure_blind_box_group(today, uid, gid)
        items_text = "、".join(drawn_items)
        
        # 构建返回消息
        result_parts = []
        if perk_triggered:
            result_parts.append(perk_message)
        if crit_times > 0:
            if had_items_before:
                result_parts.append(f"{nick}，你额外抽到了：{items_text}！触发了{crit_times}次暴击，目前共持有{len(existing_items)}张道具卡。")
            else:
                result_parts.append(f"{nick}，你抽到了：{items_text}！触发了{crit_times}次暴击，再接再厉~")
        else:
            if had_items_before:
                result_parts.append(f"{nick}，你额外抽到了：{items_text}！目前共持有{len(existing_items)}张道具卡。")
            else:
                result_parts.append(f"{nick}，你抽到了：{items_text}，记得善加利用哦~")
        
        yield event.plain_result("\n".join(result_parts))

    async def reset_blind_box(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        text = event.message_str.strip()
        arg = text[len("重置盲盒") :].strip()
        admin_ids = {str(a) for a in self.admins}
        today_items = item_data.setdefault(today, {})
        if get_user_flag(today, uid, "lightbulb"):
            yield event.plain_result(f"{nick}，电灯泡状态下无法使用「重置盲盒」指令哦~")
            return
        # 自己重置
        if not arg:
            day_record = reset_blind_box_records.setdefault(today, {})
            used = int(day_record.get(uid, 0))
            reset_blind_box_extra = int(get_user_mod(today, uid, "reset_blind_box_extra", 0))
            max_reset_blind_box = 1 + reset_blind_box_extra
            if used >= max_reset_blind_box:
                yield event.plain_result(f"{nick}，你今天已经使用过「重置盲盒」{max_reset_blind_box}次啦~")
                return
            if uid not in today_items:
                yield event.plain_result(f"{nick}，你今天还没有抽过盲盒，无需重置哦~")
                return
            del today_items[uid]
            save_item_data()
            day_record[uid] = used + 1
            save_reset_blind_box_records()
            add_user_mod(today, uid, "blind_box_extra_draw", -get_user_mod(today, uid, "blind_box_extra_draw", 0))
            groups = list(get_user_meta(today, uid, "blind_box_groups", []) or [])
            if gid in groups:
                groups.remove(gid)
                set_user_meta(today, uid, "blind_box_groups", groups)
            yield event.plain_result(f"{nick}，你的盲盒次数已重置，当前道具已清空，可以重新抽取啦！")
            return
        # 重置指定目标
        if arg == "所有人":
            if uid not in admin_ids:
                yield event.plain_result(f"{nick}，仅管理员才能重置所有人的盲盒次数哦~")
                return
            affected = 0
            for target_uid in list(today_items.keys()):
                groups = get_user_meta(today, target_uid, "blind_box_groups", [])
                valid_groups = groups if isinstance(groups, list) else []
                if gid in valid_groups:
                    add_user_mod(today, target_uid, "blind_box_extra_draw", 1)
                    affected += 1
            if affected == 0:
                yield event.plain_result(f"{nick}，今天还没有需要重置盲盒的群成员哦~")
            else:
                yield event.plain_result(f"{nick}，已为本群{affected}位成员重置盲盒次数，已保留他们现有的道具卡。")
            return
        target_uid = self.parse_at_target(event)
        if not target_uid:
            yield event.plain_result(f"{nick}，请在“重置盲盒”后@需要重置的目标用户哦~")
            return
        if uid not in admin_ids:
            yield event.plain_result(f"{nick}，仅管理员才能为他人重置盲盒次数哦~")
            return
        target_uid = str(target_uid)
        if target_uid not in today_items:
            yield event.plain_result(f"{nick}，对方今天还没有抽过盲盒，无需重置哦~")
            return
        del today_items[target_uid]
        save_item_data()
        add_user_mod(today, target_uid, "blind_box_extra_draw", -get_user_mod(today, target_uid, "blind_box_extra_draw", 0))
        groups = list(get_user_meta(today, target_uid, "blind_box_groups", []) or [])
        if gid in groups:
            groups.remove(gid)
            set_user_meta(today, target_uid, "blind_box_groups", groups)
        target_record = get_group_record(target_uid, gid)
        entry = wives_data.get(target_uid, {}) if isinstance(wives_data, dict) else {}
        target_nick = (
            (target_record or {}).get("nick")
            or entry.get("nick")
            or f"用户{target_uid}"
        )
        yield event.plain_result(f"{nick}，已为 {target_nick} 重置盲盒次数并清空其今日道具。")

    async def view_items(self, event: AstrMessageEvent):
        # 查看道具卡主逻辑
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today_items = item_data.get(today, {})
        user_items = today_items.get(uid)
        if user_items is None or len(user_items) == 0:
            yield event.plain_result(f"{nick}，你今天还没有道具卡，快去抽盲盒吧~")
            return
        items_text = "、".join(user_items)
        yield event.plain_result(f"{nick}，你当前拥有的道具卡：{items_text}")

    async def gift_item(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        if get_user_flag(today, uid, "ban_items"):
            yield event.plain_result(f"{nick}，你处于贤者时间，无法使用「赠送」指令哦~")
            return
        target_uid = self.parse_at_target(event)
        if not target_uid:
            yield event.plain_result(f"{nick}，使用「赠送」时请@目标用户哦~")
            return
        target_uid = str(target_uid)
        if target_uid == uid:
            yield event.plain_result(f"{nick}，不能把道具送给自己哦~")
            return
        text = event.message_str.strip()
        item_name = text[len("赠送"):].strip()
        if "@" in item_name:
            item_name = item_name.split("@", 1)[0].strip()
        item_name = item_name.strip("【】「」『』\"'“” ")
        if not item_name:
            yield event.plain_result(f"{nick}，请写明要赠送的道具卡名称哦~")
            return
        today_items = item_data.setdefault(today, {})
        user_items = today_items.get(uid, [])
        if item_name not in user_items:
            yield event.plain_result(f"{nick}，你的道具卡里没有「{item_name}」哦~")
            return
        entry = self._get_gift_group_entry(today, gid)
        donations = entry.setdefault("donations", {})
        target_bucket = donations.setdefault(target_uid, {})
        target_bucket[uid] = {
            "item": item_name,
            "time": datetime.utcnow().timestamp(),
        }
        save_gift_requests()
        cfg = load_group_config(gid)
        target_info = cfg.get(target_uid, {})
        target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
        yield event.plain_result(
            f"{nick}，已申请将「{item_name}」赠送给{target_nick}，请TA发送“同意赠送 @{nick}”确认领取。"
        )

    async def accept_gift(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        receiver_uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        if get_user_flag(today, receiver_uid, "ban_items"):
            yield event.plain_result(f"{nick}，你目前无法使用道具指令，无法接受赠送哦~")
            return
        sender_uid = self.parse_at_target(event)
        if not sender_uid:
            yield event.plain_result(f"{nick}，请在“同意赠送”后@发起赠送的人哦~")
            return
        sender_uid = str(sender_uid)
        entry = self._get_gift_group_entry(today, gid)
        donations = entry.get("donations", {})
        target_bucket = donations.get(receiver_uid, {})
        record = target_bucket.get(sender_uid)
        if not record:
            yield event.plain_result(f"{nick}，当前没有来自该用户的赠送请求哦~")
            return
        item_name = record["item"]
        today_items = item_data.setdefault(today, {})
        sender_items = today_items.get(sender_uid, [])
        if item_name not in sender_items:
            del target_bucket[sender_uid]
            if not target_bucket:
                donations.pop(receiver_uid, None)
            self._cleanup_gift_entry(today, gid)
            yield event.plain_result(f"{nick}，对方已经没有「{item_name}」了，赠送请求失效啦~")
            return
        sender_items.remove(item_name)
        self._handle_item_loss(today, sender_uid, 1, gid)
        receiver_items = today_items.setdefault(receiver_uid, [])
        receiver_items.append(item_name)
        cfg = load_group_config(gid)
        sender_info = cfg.get(sender_uid, {})
        sender_nick = sender_info.get("nick", f"用户{sender_uid}") if isinstance(sender_info, dict) else f"用户{sender_uid}"
        bonus_msg = ""
        if get_user_flag(today, sender_uid, "hand_scent") and self.item_pool:
            reward_card = random.choice(self.item_pool)
            sender_items.append(reward_card)
            bonus_msg = f"\n（{sender_nick}的手留余香触发，获得「{reward_card}」）"
        save_item_data()
        del target_bucket[sender_uid]
        if not target_bucket:
            donations.pop(receiver_uid, None)
        self._cleanup_gift_entry(today, gid)
        yield event.plain_result(f"{nick}，已成功领取{sender_nick}赠送的「{item_name}」！{bonus_msg}")

    async def request_item(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        if get_user_flag(today, uid, "ban_items"):
            yield event.plain_result(f"{nick}，你处于贤者时间，无法使用「索取」指令哦~")
            return
        target_uid = self.parse_at_target(event)
        if not target_uid:
            yield event.plain_result(f"{nick}，使用「索取」时请@目标用户哦~")
            return
        target_uid = str(target_uid)
        if target_uid == uid:
            yield event.plain_result(f"{nick}，不能向自己索取道具哦~")
            return
        text = event.message_str.strip()
        item_name = text[len("索取"):].strip()
        if "@" in item_name:
            item_name = item_name.split("@", 1)[0].strip()
        item_name = item_name.strip("【】「」『』\"'“” ")
        if not item_name:
            yield event.plain_result(f"{nick}，请写明要索取的道具卡名称哦~")
            return
        today_items = item_data.setdefault(today, {})
        target_items = today_items.get(target_uid, [])
        if item_name not in target_items:
            yield event.plain_result(f"{nick}，对方当前没有「{item_name}」，无法索取哦~")
            return
        entry = self._get_gift_group_entry(today, gid)
        demands = entry.setdefault("demands", {})
        sender_bucket = demands.setdefault(target_uid, {})
        sender_bucket[uid] = {
            "item": item_name,
            "time": datetime.utcnow().timestamp(),
        }
        save_gift_requests()
        cfg = load_group_config(gid)
        target_info = cfg.get(target_uid, {})
        target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
        yield event.plain_result(
            f"{nick}，已向{target_nick}发起索取「{item_name}」的请求，请TA发送“同意索取 @{nick}”确认。"
        )

    async def accept_request(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        giver_uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        if get_user_flag(today, giver_uid, "ban_items"):
            yield event.plain_result(f"{nick}，你处于贤者时间，无法执行「同意索取」哦~")
            return
        requester_uid = self.parse_at_target(event)
        if not requester_uid:
            yield event.plain_result(f"{nick}，请在“同意索取”后@请求道具的用户哦~")
            return
        requester_uid = str(requester_uid)
        entry = self._get_gift_group_entry(today, gid)
        demands = entry.get("demands", {})
        giver_bucket = demands.get(giver_uid, {})
        record = giver_bucket.get(requester_uid)
        if not record:
            yield event.plain_result(f"{nick}，没有来自该用户的索取请求哦~")
            return
        item_name = record["item"]
        today_items = item_data.setdefault(today, {})
        giver_items = today_items.get(giver_uid, [])
        if item_name not in giver_items:
            del giver_bucket[requester_uid]
            if not giver_bucket:
                demands.pop(giver_uid, None)
            self._cleanup_gift_entry(today, gid)
            yield event.plain_result(f"{nick}，你已经没有「{item_name}」了，此次索取请求自动失效~")
            return
        giver_items.remove(item_name)
        self._handle_item_loss(today, giver_uid, 1, gid)
        requester_items = today_items.setdefault(requester_uid, [])
        requester_items.append(item_name)
        bonus_msg = ""
        if get_user_flag(today, giver_uid, "hand_scent") and self.item_pool:
            reward_card = random.choice(self.item_pool)
            giver_items.append(reward_card)
            bonus_msg = f"\n（手留余香触发，你额外获得「{reward_card}」）"
        save_item_data()
        del giver_bucket[requester_uid]
        if not giver_bucket:
            demands.pop(giver_uid, None)
        self._cleanup_gift_entry(today, gid)
        cfg = load_group_config(gid)
        requester_info = cfg.get(requester_uid, {})
        requester_nick = requester_info.get("nick", f"用户{requester_uid}") if isinstance(requester_info, dict) else f"用户{requester_uid}"
        yield event.plain_result(f"{nick}，已同意索取请求，「{item_name}」已交给{requester_nick}。{bonus_msg}")

    async def view_item_requests(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        cleanup_gift_requests()
        day_entry = gift_requests.get(today, {})
        group_entry = day_entry.get(gid, {})
        donations = group_entry.get("donations", {})
        demands = group_entry.get("demands", {})
        cfg = load_group_config(gid)
        lines = []
        incoming = donations.get(uid, {})
        if incoming:
            lines.append("【待你确认的赠送】")
            for sender_uid, info in incoming.items():
                item_name = info.get("item", "未知道具")
                sender_info = cfg.get(sender_uid, {})
                sender_nick = sender_info.get("nick", f"用户{sender_uid}") if isinstance(sender_info, dict) else f"用户{sender_uid}"
                lines.append(f"- {sender_nick} 赠送 「{item_name}」")
        outgoing = demands.get(uid, {})
        if outgoing:
            lines.append("【待你确认的索取】")
            for requester_uid, info in outgoing.items():
                item_name = info.get("item", "未知道具")
                requester_info = cfg.get(requester_uid, {})
                requester_nick = requester_info.get("nick", f"用户{requester_uid}") if isinstance(requester_info, dict) else f"用户{requester_uid}"
                lines.append(f"- {requester_nick} 索取 「{item_name}」")
        if not lines:
            yield event.plain_result(f"{nick}，目前没有待你处理的道具赠送或索取请求。")
            return
        lines.insert(0, f"{nick}，当前待你处理的道具请求如下：")
        yield event.plain_result("\n".join(lines))

    async def view_status(self, event: AstrMessageEvent):
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        gid = str(event.message_obj.group_id)
        
        # 收集面板数据（mods相关数值）
        panel_data = []
        change_extra = int(get_user_mod(today, uid, "change_extra_uses", 0))
        if change_extra > 0:
            panel_data.append(f"额外换老婆次数：+{change_extra}")
        ntr_extra = int(get_user_mod(today, uid, "ntr_extra_uses", 0))
        if ntr_extra > 0:
            panel_data.append(f"额外牛老婆次数：+{ntr_extra}")
        blind_box_extra = int(get_user_mod(today, uid, "blind_box_extra_draw", 0))
        if blind_box_extra > 0:
            panel_data.append(f"额外抽盲盒机会：+{blind_box_extra}")
        reset_extra = int(get_user_mod(today, uid, "reset_extra_uses", 0))
        if reset_extra > 0:
            panel_data.append(f"额外重置次数：+{reset_extra}")
        reset_blind_box_extra = int(get_user_mod(today, uid, "reset_blind_box_extra", 0))
        if reset_blind_box_extra > 0:
            panel_data.append(f"额外重置盲盒机会：+{reset_blind_box_extra}")
        change_free_prob = float(get_user_mod(today, uid, "change_free_prob", 0.0))
        if change_free_prob > 0:
            panel_data.append(f"换老婆免消耗概率：{int(change_free_prob * 100)}%")
        change_fail_prob = float(get_user_mod(today, uid, "change_fail_prob", 0.0))
        if change_fail_prob > 0:
            panel_data.append(f"换老婆失败概率：{int(change_fail_prob * 100)}%")
        market_extra_purchases = int(get_user_mod(today, uid, "market_extra_purchases", 0))
        if market_extra_purchases > 0:
            panel_data.append(f"集市额外购买次数（剩余）：{market_extra_purchases}")
        market_wife_extra = int(get_user_mod(today, uid, "market_wife_extra_purchases", 0))
        if market_wife_extra > 0:
            panel_data.append(f"集市额外购买老婆次数（剩余）：{market_wife_extra}")
        group_bonus = int(get_group_meta(today, gid, "change_extra_uses", 0))
        if group_bonus > 0:
            panel_data.append(f"群加成：+{group_bonus}次换老婆")
        
        # 收集状态数据（flags相关效果，显示完整说明）
        status_data = []
        eff_snapshot = get_user_effects(today, uid)
        if not isinstance(eff_snapshot, dict):
            eff_snapshot = {"flags": {}, "mods": {}, "meta": {}}
        eff_snapshot.setdefault("flags", {})
        eff_snapshot.setdefault("mods", {})
        eff_snapshot.setdefault("meta", {})
        for spec in self.status_effect_specs:
            checker = spec.get("checker")
            active = False
            if checker:
                try:
                    active = bool(checker(eff_snapshot))
                except:
                    active = False
            if not active:
                continue
            desc = spec.get("desc_generator")(today, uid, gid) if spec.get("desc_generator") else spec["desc"]
            status_data.append(desc)
        
        # 如果没有数据，返回文字提示
        if not panel_data and not status_data:
            yield event.plain_result(f"{nick}，你目前没有任何状态效果，安心抽老婆吧~")
            return
        
        # 生成图片
        try:
            img = self._generate_status_image(nick, panel_data, status_data)
            # 保存临时图片
            temp_path = os.path.join(PLUGIN_DIR, f"status_{uid}_{today}.png")
            img.save(temp_path)
            # 发送图片
            yield event.chain_result([Plain(f"{nick}，你当前的状态效果："), AstrImage.fromFileSystem(temp_path)])
            # 删除临时文件
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception as e:
            # 如果生成图片失败，回退到文字形式
            all_texts = []
            if panel_data:
                all_texts.append("【面板】")
                all_texts.extend(panel_data)
            if status_data:
                all_texts.append("【状态】")
                all_texts.extend(status_data)
            msg = f"{nick}，你当前的状态效果：\n" + "\n".join(f"- {text}" for text in all_texts)
            yield event.plain_result(msg)
    
    def _generate_status_image(self, nick: str, panel_data: list, status_data: list):
        """生成状态图片"""
        # 图片尺寸
        width = 1000
        padding = 30
        line_height = 30
        title_height = 60
        section_gap = 20
        column_width = (width - padding * 2 - 20) // 2  # 每栏宽度，减去中间分隔线
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            # 尝试使用系统字体
            title_font = ImageFont.truetype("msyh.ttc", 28)  # 微软雅黑
            text_font = ImageFont.truetype("msyh.ttc", 18)
        except:
            try:
                title_font = ImageFont.truetype("arial.ttf", 28)
                text_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
        
        # 计算文本换行后的行数
        def calculate_lines(text, max_width, font):
            """计算文本换行后的行数，支持中文无空格换行"""
            if not text:
                return [""]
            lines = []
            current_line = ""
            for ch in text:
                if ch == "\n":
                    lines.append(current_line)
                    current_line = ""
                    continue
                test_line = current_line + ch
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = ch
            if current_line:
                lines.append(current_line)
            return lines if lines else [text]
        
        # 创建临时draw对象用于计算
        temp_img = PILImage.new('RGB', (width, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(temp_img)
        
        # 计算面板部分所需行数
        panel_total_lines = 0
        if panel_data:
            panel_total_lines += 1  # 标题行
            for item in panel_data:
                lines = calculate_lines(f"• {item}", column_width - 20, text_font)
                panel_total_lines += len(lines)
        else:
            panel_total_lines = 2  # 标题 + "无"
        
        # 计算状态部分所需行数
        status_total_lines = 0
        if status_data:
            status_total_lines += 1  # 标题行
            for item in status_data:
                lines = calculate_lines(f"• {item}", column_width - 20, text_font)
                status_total_lines += len(lines)
        else:
            status_total_lines = 2  # 标题 + "无"
        
        # 计算总高度
        max_lines = max(panel_total_lines, status_total_lines)
        height = title_height + max_lines * line_height + padding * 2 + section_gap
        
        # 创建实际图片
        img = PILImage.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制标题
        title_text = f"{nick} 的状态面板"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, padding), title_text, fill=(0, 0, 0), font=title_font)
        
        # 绘制分隔线
        line_y = title_height + padding
        draw.line([(padding, line_y), (width - padding, line_y)], fill=(200, 200, 200), width=2)
        
        # 计算左右两栏的位置
        left_x = padding + 20
        right_x = width // 2 + 20
        start_y = line_y + section_gap
        
        # 绘制面板部分（左侧）
        y_offset = start_y
        if panel_data:
            panel_title = "【面板】"
            draw.text((left_x, y_offset), panel_title, fill=(70, 130, 180), font=text_font)
            y_offset += line_height
            for item in panel_data:
                lines = calculate_lines(f"• {item}", column_width - 20, text_font)
                for line in lines:
                    draw.text((left_x, y_offset), line, fill=(50, 50, 50), font=text_font)
                    y_offset += line_height
        else:
            draw.text((left_x, y_offset), "【面板】", fill=(200, 200, 200), font=text_font)
            y_offset += line_height
            draw.text((left_x, y_offset), "• 无", fill=(150, 150, 150), font=text_font)
        
        # 绘制状态部分（右侧）
        y_offset = start_y
        if status_data:
            status_title = "【状态】"
            draw.text((right_x, y_offset), status_title, fill=(70, 130, 180), font=text_font)
            y_offset += line_height
            for item in status_data:
                lines = calculate_lines(f"• {item}", column_width - 20, text_font)
                for line in lines:
                    draw.text((right_x, y_offset), line, fill=(50, 50, 50), font=text_font)
                    y_offset += line_height
        else:
            draw.text((right_x, y_offset), "【状态】", fill=(200, 200, 200), font=text_font)
            y_offset += line_height
            draw.text((right_x, y_offset), "• 无", fill=(150, 150, 150), font=text_font)
        
        # 绘制中间分隔线
        mid_x = width // 2
        draw.line([(mid_x, line_y + section_gap), (mid_x, height - padding)], fill=(230, 230, 230), width=1)
        
        return img

    def _generate_help_image(self, nick: str, sections: list, item_list: list):
        """生成帮助图片"""
        width = 1000
        padding = 30
        line_height = 28
        title_height = 60
        section_gap = 16

        # 尝试加载字体
        try:
            title_font = ImageFont.truetype("msyh.ttc", 28)
            text_font = ImageFont.truetype("msyh.ttc", 18)
        except:
            try:
                title_font = ImageFont.truetype("arial.ttf", 28)
                text_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

        temp_img = PILImage.new("RGB", (width, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(temp_img)

        def calc_lines(text: str, max_width: int) -> list[str]:
            if not text:
                return [""]
            lines = []
            cur = ""
            for ch in text:
                if ch == "\n":
                    lines.append(cur)
                    cur = ""
                    continue
                test = cur + ch
                bbox = draw.textbbox((0, 0), test, font=text_font)
                if bbox[2] - bbox[0] <= max_width:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = ch
            if cur:
                lines.append(cur)
            return lines or [text]

        max_text_width = width - padding * 2

        total_lines = 0
        # 标题行
        total_lines += 1
        # 各 section
        for title, items in sections:
            total_lines += 1  # section 标题
            for item in items:
                total_lines += len(calc_lines(f"- {item}", max_text_width))
            total_lines += 1  # section 间距
        # 道具列表标题 + 内容
        total_lines += 1  # 道具卡标题
        if item_list:
            items_text = "、".join(item_list)
            total_lines += len(calc_lines(items_text, max_text_width))

        height = padding + title_height + total_lines * line_height + padding
        img = PILImage.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 标题
        title_text = f"老婆插件帮助"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_w) // 2, padding), title_text, fill=(0, 0, 0), font=title_font)

        y = padding + title_height
        for title, items in sections:
            draw.text((padding, y), f"【{title}】", fill=(70, 130, 180), font=text_font)
            y += line_height
            for item in items:
                for line in calc_lines(f"- {item}", max_text_width):
                    draw.text((padding, y), line, fill=(50, 50, 50), font=text_font)
                    y += line_height
            y += section_gap

        # 道具卡列表
        draw.text((padding, y), "【道具卡列表】", fill=(70, 130, 180), font=text_font)
        y += line_height
        if item_list:
            items_text = "、".join(item_list)
            for line in calc_lines(items_text, max_text_width):
                draw.text((padding, y), line, fill=(50, 50, 50), font=text_font)
                y += line_height

        return img

    async def show_wife_help(self, event: AstrMessageEvent):
        nick = event.get_sender_name()
        sections = [
            (
                "基础玩法",
                [
                    "抽老婆：获取今日老婆；普通用户每日一次，开后宫可多抽但有修罗场风险",
                    "查老婆[@目标/昵称]：查看自己或指定对象今日老婆，支持@或昵称关键词",
                    "查状态：生成状态面板图片，面板展示数值，状态展示已激活效果",
                    "老婆插件帮助：查看本说明",
                ],
            ),
            (
                "互动与挑战",
                [
                    "牛老婆 @目标：尝试牛走目标当天老婆，需@目标，概率受状态影响",
                    "换老婆：消耗换老婆次数重新抽取（开后宫无法使用）",
                    "重置牛：消耗「重置」次数，恢复今天的牛老婆次数上限",
                    "重置换：消耗「重置」次数，恢复今天的换老婆次数上限",
                    "选老婆 关键词：消耗专用次数，按关键词从卡池中定向抽老婆",
                    "打老婆：消耗专用次数触发事件，可能失去老婆或获得特殊反馈",
                    "勾引 @目标：消耗或无限使用次数（熊出没）来勾引目标，30%成功，需@目标",
                ],
            ),
            (
                "交换系统",
                [
                    "交换老婆 @目标：发起交换请求，双方各消耗1次交换机会",
                    "同意交换 @目标：同意对方请求并立即交换老婆",
                    "拒绝交换 @目标：拒绝请求（部分状态可能无法拒绝）",
                    "查看交换请求：查看尚未处理的交换请求列表",
                ],
            ),
            (
                "道具与盲盒",
                [
                    "抽盲盒：消耗今日盲盒次数抽取随机道具卡，有概率触发暴击",
                    "重置盲盒：消耗「重置盲盒」次数，恢复抽盲盒机会并可能获得额外奖励",
                    "查道具：查看今日持有的道具卡名称",
                    "使用道具名 [@目标]：使用指定道具，部分道具需要@目标",
                    "老婆集市：查看今日老婆集市的商品列表",
                    "购买 名称：在老婆集市中购买指定老婆或道具卡",
                    "赠送 道具名 @目标：向他人赠送当前持有的道具卡，等待对方确认",
                    "同意赠送 @目标：接受指定用户的赠送请求，立即获得其道具",
                    "索取 道具名 @目标：主动向别人索取指定道具，等待对方同意",
                    "同意索取 @目标：同意他人的索取请求，将道具交给对方",
                    "查看道具请求：查看当前待处理的赠送/索取请求列表",
                ],
            ),
            (
                "管理员指令",
                [
                    "切换ntr开关状态：管理员开/关当前群的牛老婆功能",
                    "重开 @目标：管理员清空目标今日所有数据（老婆、记录、道具、状态等）",
                ],
            ),
        ]
        # 生成图片，与查状态/老婆集市风格一致
        try:
            img = self._generate_help_image(nick, sections, sorted(self.item_pool))
            today = get_today()
            uid = str(event.get_sender_id())
            temp_path = os.path.join(PLUGIN_DIR, f"help_{uid}_{today}.png")
            img.save(temp_path)
            yield event.chain_result([Plain(f"{nick}，老婆插件使用说明："), AstrImage.fromFileSystem(temp_path)])
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception:
            # 回退到文字形式
            lines = [f"{nick}，老婆插件使用说明如下："]
            for title, items in sections:
                lines.append(f"【{title}】")
                lines.extend(f"- {item}" for item in items)
            item_list = "、".join(sorted(self.item_pool))
            lines.append(f"道具卡列表：{item_list}")
            yield event.plain_result("\n".join(lines))

    async def use_item(self, event: AstrMessageEvent):
        # 使用道具卡主逻辑（效果待实现）
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        # 贤者时间：禁止使用任何道具
        if get_user_flag(today, uid, "ban_items"):
            yield event.plain_result(f"{nick}，你正处于「贤者时间」，今天无法使用任何道具卡哦~")
            return
        
        # 检查盲盒爱好者状态：每1小时只能使用一个道具
        is_blind_box_enthusiast = get_user_flag(today, uid, "blind_box_enthusiast")
        if is_blind_box_enthusiast:
            now = datetime.utcnow().timestamp()
            last_item_use = get_user_meta(today, uid, "last_item_use_time", 0)
            one_hour_ago = now - 3600  # 1小时 = 3600秒
            
            if last_item_use > one_hour_ago:
                # 距离上次使用道具不足1小时
                wait_seconds = int(3600 - (now - last_item_use))
                wait_mins = wait_seconds // 60
                wait_secs = wait_seconds % 60
                if wait_mins > 0:
                    wait_text = f"{wait_mins}分{wait_secs}秒"
                else:
                    wait_text = f"{wait_secs}秒"
                yield event.plain_result(f"{nick}，你作为盲盒爱好者，每1小时只能使用一个道具，请等待{wait_text}后再试~")
                return
        text = event.message_str.strip()
        content = text[len("使用") :].strip()
        if not content:
            yield event.plain_result(f"{nick}，请在“使用”后跟上道具名称哦~")
            return
        parts = re.split(r"\s+|@", content, maxsplit=1)
        card_name = parts[0] if parts else ""
        if not card_name:
            yield event.plain_result(f"{nick}，请明确要使用的道具名称哦~")
            return
        if card_name not in self.item_pool:
            yield event.plain_result(f"{nick}，暂未识别到名为“{card_name}”的道具卡~")
            return
        extra_arg = content[len(card_name) :].strip()
        target_uid = self.parse_at_target(event)
        if card_name in self.items_need_target and not target_uid:
            yield event.plain_result(f"{nick}，使用“{card_name}”时请@目标哦~")
            return
        today_items = item_data.get(today, {})
        user_items = today_items.get(uid)
        if user_items is None:
            yield event.plain_result(f"{nick}，你今天还没有抽盲盒，暂时没有可用的道具卡~")
            return
        if card_name not in user_items:
            yield event.plain_result(f"{nick}，你今天的道具卡里没有“{card_name}”哦~")
            return
        success, message = await self.apply_item_effect(card_name, event, target_uid, extra_arg)
        if success:
            # 洗牌道具已经在apply_item_effect中清空了所有道具，不需要再次移除
            if card_name != "洗牌" and card_name in user_items:
                user_items.remove(card_name)
                save_item_data()
            # 吃一堑：若目标拥有长一智，则目标也获得一张同名道具卡
            if target_uid is not None:
                target_str = str(target_uid)
                if target_str != uid and get_user_flag(today, target_str, "learned"):
                    target_items = today_items.setdefault(target_str, [])
                    target_items.append(card_name)
                    save_item_data()
            # 记录道具使用时间（盲盒爱好者状态）
            if is_blind_box_enthusiast:
                now = datetime.utcnow().timestamp()
                set_user_meta(today, uid, "last_item_use_time", now)
        yield event.plain_result(message or f"{nick}，道具卡「{card_name}」已处理。")

    async def apply_item_effect(
        self,
        card_name,
        event,
        target_uid,
        extra_arg="",
        caller_uid=None,
        *,
        use_double_effect: bool = True,
        consume_double_effect: bool = True,
    ):
        # 分步实现各道具效果
        # caller_uid: 可选，如果提供则使用该uid作为使用者（用于会员制餐厅等道具）
        today = get_today()
        if caller_uid is not None:
            uid = str(caller_uid)
            # 获取目标用户昵称
            target_cfg = load_group_config(str(event.message_obj.group_id))
            target_info = target_cfg.get(uid, {})
            nick = target_info.get("nick", f"用户{uid}") if isinstance(target_info, dict) else f"用户{uid}"
        else:
            uid = str(event.get_sender_id())
            nick = event.get_sender_name()
        gid = str(event.message_obj.group_id)
        cfg = load_group_config(gid)
        name = card_name
        is_sleep_effect = name == "二度寝"
        double_active = (
            bool(get_user_flag(today, uid, "double_item_effect"))
            if (use_double_effect and not is_sleep_effect)
            else False
        )
        double_factor = 2 if double_active else 1

        def finalize(success_flag: bool, message: str | None):
            if (
                consume_double_effect
                and use_double_effect
                and not is_sleep_effect
                and double_active
                and success_flag
            ):
                set_user_flag(today, uid, "double_item_effect", False)
            return success_flag, message
        # 长一智被动效果：如果本次道具有明确目标，且目标拥有长一智，则目标在生效后获得同名道具卡
        learned_target_uid = None
        if target_uid is not None:
            target_uid_str = str(target_uid)
            if target_uid_str != uid and get_user_flag(today, target_uid_str, "learned"):
                learned_target_uid = target_uid_str

        # ① 牛魔王：进攻+30%，自身被牛也+30%（不叠加 -> 取更大值）
        if name == "牛魔王":
            atk_now = float(get_user_mod(today, uid, "ntr_attack_bonus", 0.0))
            def_now = float(get_user_mod(today, uid, "ntr_defense_bonus", 0.0))
            base_bonus = min(1.0, 0.3 * double_factor)
            target_atk = max(atk_now, base_bonus)
            target_def = max(def_now, base_bonus)
            eff = get_user_effects(today, uid)
            eff["mods"]["ntr_attack_bonus"] = target_atk
            eff["mods"]["ntr_defense_bonus"] = target_def
            set_user_flag(today, uid, "ntr_override", True)
            base_total = (self.ntr_max or 0) + int(get_user_mod(today, uid, "ntr_extra_uses", 0))
            if base_total > 0:
                add_user_mod(today, uid, "ntr_extra_uses", base_total)
            save_effects()
            result = f"{nick}，牛魔王发动！今日牛成功率UP，牛老婆次数翻倍，但你的老婆也更容易被牛走......"
            return finalize(True, result)
        # ② 开后宫：无法使用换老婆和重置指令，支持多老婆，有修罗场风险
        if name == "开后宫":
            set_user_flag(today, uid, "harem", True)
            rec = ensure_group_record(uid, gid, today, nick, keep_existing=True)
            rec["harem"] = True
            rec.setdefault("wives", [])
            set_user_meta(today, uid, "harem_chaos_multiplier", float(double_factor))
            save_group_config(cfg)
            # 检查露出状态：如果用户有露出状态，触发修罗场
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                # 触发修罗场后获得一次抽老婆（换老婆）机会
                add_user_mod(today, uid, "change_extra_uses", 1)
                return finalize(True, f"{nick}，你开启了后宫模式！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
            result = f"{nick}，你开启了后宫模式！今日无法使用换老婆和重置指令，可同时拥有多个老婆，但小心修罗场哦~"
            return finalize(True, result)
        # ③ 贤者时间：清空当日前已生效效果，并禁止使用道具
        if name == "贤者时间":
            eff = get_user_effects(today, uid)
            eff["mods"] = {
                "ntr_attack_bonus": 0.0,
                "ntr_defense_bonus": 0.0,
                "change_extra_uses": 0,
            }
            eff["flags"] = {
                "protect_from_ntr": False,
                "ban_change": False,
                "ban_items": True,
                "harem": False,
                "ban_ntr": False,
                "ntr_override": False,
                "force_swap": False,
                "landmine_girl": False,
                "ban_reject_swap": False,
            }
            meta = eff["meta"]
            meta["competition_prob"] = 0.3
            meta["harem_chaos_multiplier"] = 1.0
            meta["double_item_effect"] = False
            meta["lost_wives"] = []
            save_effects()
            result = f"{nick}，你进入了贤者时间......"
            return finalize(True, result)
        # ④ 开impart：将今天所有拥有老婆的用户的老婆重新随机分配（开后宫用户保持原有数量，贤者时间用户不受影响）
        if name == "开impart":
            success, message = await self._redistribute_wives(gid, today, event, cfg)
            return finalize(success, message)
        # ⑤ 纯爱战士：今日不可被牛走，且无法使用换老婆
        if name == "纯爱战士":
            set_user_flag(today, uid, "protect_from_ntr", True)
            set_user_flag(today, uid, "ban_change", True)
            return finalize(True, f"{nick}，你成为了纯爱战士！")
        if name == "雄竞":
            if not target_uid:
                return False, "使用“雄竞”时请@目标用户哦~"
            set_user_meta(today, uid, "competition_target", target_uid)
            set_user_meta(today, uid, "competition_prob", clamp_probability(0.35 * double_factor))
            result = f"{nick}，你向对方发起了雄竞！今日抽老婆有概率抽到与其相同的老婆。"
            return finalize(True, result)
        if name == "苦主":
            set_user_flag(today, uid, "victim_auto_ntr", True)
            set_user_meta(today, uid, "ntr_penalty_stack", 0)
            set_user_flag(today, uid, "ban_reject_swap", True)
            return finalize(True, f"{nick}，你成为了苦主：别人牛你必定成功，且每次失去老婆都会额外补偿1次「换老婆」次数......")
        if name == "黄毛":
            set_user_flag(today, uid, "next_ntr_guarantee", True)
            set_user_flag(today, uid, "ban_change", True)
            # 将换老婆使用次数转换为牛老婆的额外使用次数（增加ntr_extra_uses，不修改records的count）
            change_rec = change_records.setdefault(gid, {}).get(uid, {"date": "", "count": 0})
            change_count = 0
            if change_rec.get("date") == today:
                change_count = change_rec.get("count", 0)
            bonus_count = change_count * double_factor
            # 牛魔王效果：本次累加的次数翻倍
            if get_user_flag(today, uid, "ntr_override"):
                bonus_count = bonus_count * 2
            # 增加牛老婆的额外使用次数，而不是修改records的count
            add_user_mod(today, uid, "ntr_extra_uses", bonus_count)
            return finalize(True, f"{nick}，黄毛觉醒！下次牛老婆必定成功，已将今日已使用的「换老婆」次数累加到「牛老婆」次数，但代价是......")
        if name == "吃一堑":
            set_user_flag(today, uid, "learned", True)
            return finalize(True, f"{nick}，吃一堑长一智：你变得聪明了。")
        if name == "偷外卖":
            set_user_flag(today, uid, "light_fingers", True)
            return finalize(True, f"{nick}，你学会了顺手的事：牛成功或在集市购物时，有50%概率顺手牵羊一张道具卡，50%概率被抓失去自己的道具卡。")
        if name == "富哥":
            # 自己获得2次额外集市购买次数
            add_user_mod(today, uid, "market_extra_purchases", 2 * double_factor)
            set_user_flag(today, uid, "rich_bro", True)
            # 群里随机一人获得见者有份
            others = [u for u in cfg.keys() if u != uid]
            target_nick_info = ""
            if others:
                target_uid = random.choice(others)
                set_user_flag(today, target_uid, "share_bonus", True)
                add_user_mod(today, target_uid, "market_extra_purchases", 1)
                target_info = cfg.get(target_uid, {})
                target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
                target_nick_info = f"，{target_nick}获得了「见者有份」效果"
            return finalize(True, f"{nick}，你成为了富哥，今日额外获得2次老婆集市购买机会{target_nick_info}。")
        if name == "疯狂星期四":
            # 额外获得一次只能购买老婆的集市次数
            add_user_mod(today, uid, "market_wife_extra_purchases", 1 * double_factor)
            return finalize(True, f"{nick}，疯狂星期四来啦！你额外获得1次只能购买老婆的集市机会。")
        if name == "赠人玫瑰":
            set_user_flag(today, uid, "hand_scent", True)
            return finalize(True, f"{nick}，赠人玫瑰，手留余香！你赠送道具时会随机获得新的道具卡。")
        if name == "南北西":
            keyword = "禁寄交流群!阿东"
            local_imgs = []
            try:
                if os.path.exists(IMG_DIR):
                    local_imgs = [
                        f for f in os.listdir(IMG_DIR)
                        if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")) and keyword in f
                    ]
            except:
                local_imgs = []
            if not local_imgs:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.image_base_url) as resp:
                            text = await resp.text()
                        all_imgs = text.splitlines()
                        local_imgs = [img for img in all_imgs if keyword in img]
                except:
                    local_imgs = []
            if not local_imgs:
                return finalize(False, f"{nick}，未找到包含“{keyword}”的老婆素材，稍后再试吧~")
            img = random.choice(local_imgs)
            cfg = load_group_config(gid)
            is_harem = get_user_flag(today, uid, "harem")
            if not add_wife(cfg, uid, img, today, nick, is_harem):
                return finalize(False, f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
            save_group_config(cfg)
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                add_user_mod(today, uid, "change_extra_uses", 1)
                return finalize(True, f"{nick}，阿东降临！但你处于露出状态，修罗场爆发，获得一次抽老婆的机会。")
            if img.startswith("http"):
                display_name = self._resolve_avatar_nick(cfg, img)
                text = f"{nick}，你得到了{display_name}，请好好珍惜哦~"
            else:
                name = os.path.splitext(img)[0]
                if "!" in name:
                    source, chara = name.split("!", 1)
                    text = f"{nick}，你得到了来自《{source}》的{chara}，请好好珍惜哦~"
                else:
                    text = f"{nick}，你得到了{name}，请好好珍惜哦~"
            return finalize(True, text)
        if name == "城管":
            if not self._ensure_market_available(today):
                return finalize(False, f"{nick}，城管出动失败，今日集市暂无法刷新，请稍后再试~")
            market = market_data[today]
            current_wives = len(market.get("wives", []))
            current_items = len(market.get("items", []))
            market["wives"] = self._generate_market_wives(current_wives)
            market["items"] = self._generate_market_items(current_items)
            save_market_data()
            return finalize(True, f"{nick}，城管出动！集市已重新整顿，刷新了{len(market['wives'])}位老婆与{len(market['items'])}件道具。")
        if name == "仓管":
            if not self._ensure_market_available(today):
                return finalize(False, f"{nick}，仓管暂无法补货，今日集市未能刷新，请稍后再试~")
            market = market_data[today]
            added_wives = []
            added_items = []
            market_wives = market.setdefault("wives", [])
            market_items = market.setdefault("items", [])
            missing_wives = max(0, self.market_max_wives - len(market_wives))
            if missing_wives > 0:
                existing_names = {w.get("name") for w in market_wives}
                existing_imgs = {w.get("img") for w in market_wives}
                new_wives = self._generate_market_wives(missing_wives, existing_names, existing_imgs)
                market_wives.extend(new_wives)
                added_wives = new_wives
            missing_items = max(0, self.market_max_items - len(market_items))
            if missing_items > 0:
                new_items = self._generate_market_items(missing_items, set(market_items))
                market_items.extend(new_items)
                added_items = new_items
            save_market_data()
            if not added_wives and not added_items:
                return finalize(True, f"{nick}，仓管盘点完成，当前集市已经满员。")
            return finalize(True, f"{nick}，仓管补货完成，新增{len(added_wives)}位老婆、{len(added_items)}件道具。")
        if name == "电灯泡":
            change_recs = change_records.setdefault(gid, {})
            change_rec = change_recs.get(uid, {"date": today, "count": 0})
            if change_rec.get("date") == today:
                change_rec["count"] = 0
                change_recs[uid] = change_rec
                save_change_records()
            ntr_recs = ntr_records.setdefault(gid, {})
            ntr_rec = ntr_recs.get(uid, {"date": today, "count": 0})
            if ntr_rec.get("date") == today:
                ntr_rec["count"] = 0
                ntr_recs[uid] = ntr_rec
                save_ntr_records()
            set_user_mod(today, uid, "change_extra_uses", 0)
            set_user_mod(today, uid, "ntr_extra_uses", 0)
            set_user_flag(today, uid, "lightbulb", True)
            set_user_meta(today, uid, "lightbulb_group", gid)
            return finalize(True, f"{nick}，电灯泡上线！你将实时掌控本群的换牛动向")
        if name == "枪兵":
            set_user_flag(today, uid, "lucky_e", True)
            return finalize(True, f"{nick}，枪兵出击！但自古枪兵幸运E...")
        if name == "修罗":
            set_user_flag(today, uid, "shura", True)
            return finalize(True, f"{nick}，你踏入修罗之路......")
        if name == "吉星如意":
            set_user_flag(today, uid, "super_lucky", True)
            return finalize(True, f"{nick}，你的吉星温柔地注视着你")
        if name == "穷凶极恶":
            # 检查今日运势是否为小凶、凶、大凶（1~3颗星）
            fortune = get_user_fortune(today, uid)
            stars = fortune.get("stars", 4)
            if stars >= 1 and stars <= 3:
                set_user_flag(today, uid, "extreme_evil", True)
                return finalize(True, f"{nick}，穷凶极恶！你的厄运化为了力量，尽情作恶吧")
            else:
                return finalize(True, f"{nick}，你的好运庇护了你，穷凶极恶无法生效。")
        # ⑥ 雌堕：50%让@目标成为你的老婆（头像图），50%你成为对方的老婆（头像图）（贤者时间用户不受影响）
        if name == "雌堕":
            if not target_uid:
                return False, "使用「雌堕」时请@目标用户哦~"
            target_uid = str(target_uid)
            # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
            user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
            target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
            equal_rights_msg = ""  # 保存众生平等提示语
            if not user_has_equal_rights and not target_has_equal_rights:
                # 检查目标用户是否拥有贤者时间效果
                if get_user_flag(today, target_uid, "ban_items"):
                    return False, f"{nick}，对方处于贤者时间，不受道具效果影响。"
            else:
                # 众生平等状态：豁免保护，显示特殊提示语
                if get_user_flag(today, target_uid, "ban_items"):
                    if user_has_equal_rights:
                        equal_rights_msg = "众生平等！你无视了对方的贤者时间，"
                    elif target_has_equal_rights:
                        equal_rights_msg = "众生平等！对方的状态无法保护自己，"
            # 检查自己是否拥有贤者时间效果（失败分支时）
            if get_user_flag(today, uid, "ban_items"):
                return False, f"{nick}，你处于贤者时间，无法使用道具。"
            # 成功分支：对方成为你的老婆
            # 穷凶极恶效果：正面概率加成变为125%
            base_prob = 0.5
            if get_user_flag(today, uid, "extreme_evil"):
                base_prob = base_prob * 1.25
                base_prob = min(0.9, base_prob)  # 概率上限为90%
            if self._probability_check(base_prob, today, uid):
                img = get_avatar_url(target_uid)
                if not add_wife(cfg, uid, img, today, nick, False):
                    return finalize(False, f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
                save_group_config(cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，{equal_rights_msg}雌堕成功！对方成为你的老婆了。"
                if cancel_msg:
                    msg += f"\n{cancel_msg}"
                return finalize(True, msg)
            # 失败分支：你成为对方的老婆
            else:
                img = get_avatar_url(uid)
                # 获取对方昵称
                target_nick = None
                try:
                    target_nick = event.get_sender_name() if str(event.get_sender_id()) == target_uid else None
                except:
                    target_nick = None
                if not add_wife(cfg, target_uid, img, today, target_nick or f"用户{target_uid}", False):
                    return finalize(False, f"{nick}，对方处于修罗状态，只能通过「牛老婆」获得新老婆。")
                save_group_config(cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，{equal_rights_msg}雌堕反噬......你成为了对方的老婆。"
                if cancel_msg:
                    msg += f"\n{cancel_msg}"
                return finalize(True, msg)
        if name == "苦命鸳鸯":
            candidates = []
            for target_id, rec, _ in iter_group_users(gid):
                tid = str(target_id)
                if tid == uid:
                    continue
                if get_wife_count(cfg, tid, today) > 0:
                    candidates.append(tid)
            if not candidates:
                return finalize(False, "当前群友里暂时没有拥有老婆的对象，无法发动「苦命鸳鸯」~")
            target_uid = random.choice(candidates)
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            user_loss = get_wife_count(cfg, uid, today)
            target_loss = get_wife_count(cfg, target_uid, today)
            if uid in cfg:
                del cfg[uid]
            if target_uid in cfg:
                del cfg[target_uid]
            self._handle_wife_loss(today, uid, user_loss, gid)
            self._handle_wife_loss(today, target_uid, target_loss, gid)
            target_avatar = get_avatar_url(target_uid)
            user_avatar = get_avatar_url(uid)
            if not add_wife(cfg, uid, target_avatar, today, nick, False):
                return finalize(False, f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
            if not add_wife(cfg, target_uid, user_avatar, today, target_nick, False):
                return finalize(False, f"{nick}，{target_nick}处于修罗状态，无法获得新的老婆。")
            save_group_config(cfg)
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
            msg = f"{nick}，真是一对苦命鸳鸯......你与{target_nick}失去了所有老婆，并互相成为了对方的老婆。你可有何话说？"
            if cancel_msg:
                msg += f"\n{cancel_msg}"
            return finalize(True, msg)
        if name == "牛道具":
            if not target_uid:
                return False, "使用「牛道具」时请@目标用户哦~"
            target_uid = str(target_uid)
            if target_uid == uid:
                return False, "不能对自己使用「牛道具」哦~"
            # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
            user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
            target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
            equal_rights_msg = ""  # 保存众生平等提示语
            if not user_has_equal_rights and not target_has_equal_rights:
                if get_user_flag(today, target_uid, "ban_items"):
                    return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「牛道具」。")
            else:
                # 众生平等状态：豁免保护，显示特殊提示语
                if get_user_flag(today, target_uid, "ban_items"):
                    if user_has_equal_rights:
                        equal_rights_msg = "众生平等！你无视了对方的贤者时间，"
                    elif target_has_equal_rights:
                        equal_rights_msg = "众生平等！对方的状态无法保护自己，"
            today_items = item_data.setdefault(today, {})
            target_items = list(today_items.get(target_uid, []))
            if not target_items:
                return finalize(False, f"{nick}，对方今天还没有道具可以被牛走。")
            steal_count = min(random.randint(0, 2), len(target_items))
            if steal_count == 0:
                return finalize(True, f"{nick}，{equal_rights_msg}你伸出黑手，但尴尬地牵到了对方的手，牛道具失败了......")
            stolen = random.sample(target_items, steal_count)
            for itm in stolen:
                target_items.remove(itm)
            today_items[target_uid] = target_items
            if steal_count > 0:
                self._handle_item_loss(today, target_uid, steal_count, gid)
            user_items = today_items.setdefault(uid, [])
            user_items.extend(stolen)
            save_item_data()
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            return finalize(True, f"{nick}，{equal_rights_msg}你对{target_nick}使用「牛道具」成功，掠走了：{'、'.join(stolen)}。")
        if name == "偷拍":
            if not target_uid:
                return False, "使用「偷拍」时请@目标用户哦~"
            target_uid = str(target_uid)
            if target_uid == uid:
                return False, "不能对自己使用「偷拍」哦~"
            # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
            user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
            target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
            equal_rights_msg = ""  # 保存众生平等提示语
            if not user_has_equal_rights and not target_has_equal_rights:
                if get_user_flag(today, target_uid, "ban_items"):
                    return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「偷拍」。")
            else:
                # 众生平等状态：豁免保护，显示特殊提示语
                if get_user_flag(today, target_uid, "ban_items"):
                    if user_has_equal_rights:
                        equal_rights_msg = "众生平等！你无视了对方的贤者时间，"
                    elif target_has_equal_rights:
                        equal_rights_msg = "众生平等！对方的状态无法保护自己，"
            target_wives = get_wives_list(cfg, target_uid, today)
            if not target_wives:
                return finalize(False, f"{nick}，对方今天还没有老婆可偷哦~")
            user_loss = get_wife_count(cfg, uid, today)
            if uid in cfg:
                del cfg[uid]
            self._handle_wife_loss(today, uid, user_loss, gid)
            rec = ensure_group_record(uid, gid, today, nick, keep_existing=False)
            if get_user_flag(today, uid, "harem"):
                rec["harem"] = True
                rec["wives"] = list(target_wives)
            else:
                rec["harem"] = False
                rec["wives"] = [target_wives[0]]
            save_group_config(cfg)
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid])
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            msg = f"{nick}，{equal_rights_msg}通过「偷拍」得到了{target_nick}的老婆并回家意淫了"
            if not get_user_flag(today, uid, "harem") and len(target_wives) > 1:
                msg += "（未开后宫，仅获得其中一位）"
            if cancel_msg:
                msg += f"\n{cancel_msg}"
            return finalize(True, msg)
        if name == "复读":
            if not target_uid:
                return False, "使用「复读」时请@目标用户哦~"
            target_uid = str(target_uid)
            if target_uid == uid:
                return False, "不能对自己使用「复读」哦~"
            # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
            user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
            target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
            equal_rights_msg = ""  # 保存众生平等提示语
            if not user_has_equal_rights and not target_has_equal_rights:
                if get_user_flag(today, target_uid, "ban_items"):
                    return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「复读」。")
            else:
                # 众生平等状态：豁免保护，显示特殊提示语
                if get_user_flag(today, target_uid, "ban_items"):
                    if user_has_equal_rights:
                        equal_rights_msg = "众生平等！你无视了对方的贤者时间，"
                    elif target_has_equal_rights:
                        equal_rights_msg = "众生平等！对方的状态无法保护自己，"
            today_items = item_data.setdefault(today, {})
            target_items = today_items.get(target_uid)
            if not target_items:
                return finalize(False, f"{nick}，对方今天还没有道具可以复刻。")
            today_items[uid] = list(target_items)
            save_item_data()
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            return finalize(True, f"{nick}，{equal_rights_msg}你清空了自己的道具卡，通过「复读」复制到了{target_nick}当前的全部道具：{'、'.join(target_items)}。")
        # ⑩ 何意味：随机执行一个效果（增加新效果）
        if name == "何意味":
            two_effect_candidates = [
                "mute_300",
                "double_counter",
                "zero_counter",
                "change_free_half",
                "change_fail_half",
            ]

            async def effect_mute_300():
                duration = 300 * double_factor
                try:
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=int(duration))
                except:
                    pass
                msg = f"{nick}，何意味？你被禁言{duration}秒......"
                return True, msg, f"被禁言{duration}秒"

            async def effect_double_counter():
                if self._probability_check(0.5, today, uid):
                    grp = change_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] *= (2 * double_factor)
                    grp[uid] = rec
                    save_change_records()
                    msg = f"{nick}，何意味？你今天的“换老婆”使用次数翻倍。"
                    return True, msg, "换老婆次数翻倍"
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    multiplier = 2 * double_factor
                    if get_user_flag(today, uid, "ntr_override"):
                        multiplier = multiplier * 2
                    rec["count"] *= multiplier
                    grp[uid] = rec
                    save_ntr_records()
                    msg = f"{nick}，何意味？你今天的「牛老婆」使用次数翻倍。"
                    return True, msg, "牛老婆次数翻倍"

            async def effect_zero_counter():
                if self._probability_check(0.5, today, uid):
                    grp = change_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] = 0
                    grp[uid] = rec
                    save_change_records()
                    msg = f"{nick}，何意味？你今天的“换老婆”使用次数清零。"
                    return True, msg, "换老婆次数清零"
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] = 0
                    grp[uid] = rec
                    save_ntr_records()
                    msg = f"{nick}，何意味？你今天的“牛老婆”使用次数清零。"
                    return True, msg, "牛老婆次数清零"

            async def effect_change_free_half():
                current = clamp_probability(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_free_prob", clamp_probability(max(current, 0.5 * double_factor)))
                msg = f"{nick}，何意味？你今天“换老婆”有概率不消耗次数。"
                return True, msg, "换老婆有概率不消耗次数"

            async def effect_change_fail_half():
                current = clamp_probability(get_user_mod(today, uid, "change_fail_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_fail_prob", clamp_probability(max(current, 0.5 * double_factor)))
                msg = f"{nick}，何意味？你今天“换老婆”有概率执行失败。"
                return True, msg, "换老婆有概率执行失败"

            async def effect_impart():
                success, message = await self._redistribute_wives(gid, today, event, cfg)
                return success, message, message

            async def effect_do_change_once():
                prev = float(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_free_prob", clamp_probability(1.0))
                async for _ in self.change_wife(event):
                    pass
                set_user_mod(today, uid, "change_free_prob", prev)
                msg = f"{nick}，何意味？你的老婆跑了......"
                return True, msg, "强制执行一次换老婆"

            async def effect_two_effects():
                candidates = [c for c in two_effect_candidates if c in heyimi_effects]
                if not candidates:
                    return True, f"{nick}，何意味？随机效果失效了。", "随机两个效果（无效）"
                selected = random.sample(candidates, min(2, len(candidates)))
                summaries = []
                for eff_key in selected:
                    eff_success, _, eff_summary = await heyimi_effects[eff_key]()
                    if eff_success:
                        summaries.append(eff_summary or eff_key)
                summary_text = "、".join(summaries) if summaries else "无效果"
                msg = f"{nick}，何意味？随机生效两个效果（{summary_text}）。"
                return True, msg, f"随机两个效果（{summary_text}）"

            async def effect_random_item():
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                drawn = random.choices(self.item_pool, k=double_factor)
                user_items.extend(drawn)
                save_item_data()
                items_text = "、".join(drawn)
                msg = f"{nick}，何意味？你获得了道具卡「{items_text}」。"
                return True, msg, f"获得道具卡「{items_text}」"

            async def effect_draw_chance():
                add_user_mod(today, uid, "blind_box_extra_draw", double_factor)
                msg = f"{nick}，何意味？你获得了{double_factor}次额外的抽盲盒机会。"
                return True, msg, f"额外抽盲盒{double_factor}次"

            async def effect_two_items():
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                random_items = random.choices(self.item_pool, k=2 * double_factor)
                user_items.extend(random_items)
                save_item_data()
                items_text = "、".join(random_items)
                msg = f"{nick}，何意味？你获得了道具卡：{items_text}。"
                return True, msg, f"获得道具卡：{items_text}"

            async def effect_ban_items():
                set_user_flag(today, uid, "ban_items", True)
                msg = f"{nick}，何意味？你今天不能再使用道具卡了。"
                return True, msg, "今日禁用道具卡"

            async def effect_lose_all_items():
                today_items = item_data.setdefault(today, {})
                if uid in today_items:
                    lost_count = len(today_items[uid])
                    del today_items[uid]
                    save_item_data()
                    self._handle_item_loss(today, uid, lost_count, gid)
                    msg = f"{nick}，何意味？你失去了所有道具卡（共{lost_count}张）。"
                else:
                    msg = f"{nick}，何意味？你失去了所有道具卡（你本来就没有）。"
                return True, msg, "失去所有道具卡"

            async def effect_force_use_item():
                today_items = item_data.setdefault(today, {})
                user_items = today_items.get(uid, [])
                available = [
                    card for card in user_items
                    if card not in self.items_need_target and card != "何意味"
                ]
                if not available:
                    msg = f"{nick}，何意味？你没有可以强制使用的道具卡。"
                    return True, msg, "没有可强制使用的道具"
                forced_card = random.choice(available)
                user_items.remove(forced_card)
                save_item_data()
                forced_success, forced_message = await self.apply_item_effect(forced_card, event, None)
                msg_prefix = f"{nick}，何意味？强制使用了「{forced_card}」。"
                if forced_success and forced_message:
                    return True, f"{msg_prefix}\n{forced_message}", f"强制使用「{forced_card}」"
                return True, msg_prefix, f"强制使用「{forced_card}」"

            heyimi_effects = {
                "mute_300": effect_mute_300,
                "double_counter": effect_double_counter,
                "zero_counter": effect_zero_counter,
                "change_free_half": effect_change_free_half,
                "change_fail_half": effect_change_fail_half,
                "impart": effect_impart,
                "do_change_once": effect_do_change_once,
                "two_effects": effect_two_effects,
                "random_item": effect_random_item,
                "draw_chance": effect_draw_chance,
                "two_items": effect_two_items,
                "ban_items": effect_ban_items,
                "lose_all_items": effect_lose_all_items,
                "force_use_item": effect_force_use_item,
            }

            effect_key = random.choice(list(heyimi_effects.keys()))
            success, message, _ = await heyimi_effects[effect_key]()
            return finalize(success, message)
        # 新增道具卡效果
        if name == "二度寝":
            set_user_flag(today, uid, "double_item_effect", True)
            return True, f"{nick}，二度寝成功！你的下一张道具卡效果将翻倍。"
        # ① 白月光：今天获得一次"选老婆"的使用次数
        if name == "白月光":
            add_user_mod(today, uid, "select_wife_uses", 1 * double_factor)
            return finalize(True, f"{nick}，你获得了{1 * double_factor}次「选老婆」的使用次数。")
        # ② 公交车：今天你对其他人使用"交换老婆"指令时无需经过对方同意，强制交换，但你今天无法使用"牛老婆"指令
        if name == "公交车":
            set_user_flag(today, uid, "force_swap", True)
            set_user_flag(today, uid, "ban_ntr", True)
            return finalize(True, f"{nick}，公交车已发车！你今天可以与别人强制交换老婆！但代价是......")
        # ③ 病娇：今天你的老婆不会被别人使用"牛老婆"牛走，但当你在有老婆的情况下成功使用"牛老婆"指令牛走别人的老婆时，随机触发事件
        if name == "病娇":
            set_user_flag(today, uid, "landmine_girl", True)
            return finalize(True, f"{nick}，你的老婆变成了病娇...")
        # ④ 儒夫：今天你获得10次"打老婆"使用次数
        if name == "儒夫":
            add_user_mod(today, uid, "beat_wife_uses", 10 * double_factor)
            return finalize(True, f"{nick}，儒家思想已融入你的血液，你今天获得了{10 * double_factor}次「打老婆」的使用次数。")
        # ⑤ 熊出没：今天你可以使用"勾引"指令无数次，但每次使用有25%概率被禁言120秒
        if name == "熊出没":
            add_user_mod(today, uid, "seduce_uses", -1)  # -1表示无限
            return finalize(True, f"{nick}，熊出没已上线！你今天可以无限使用「勾引」指令")
        if name == "宝刀未老":
            grp = ntr_records.setdefault(gid, {})
            rec = grp.get(uid, {"date": today, "count": 0})
            if rec.get("date") != today:
                rec = {"date": today, "count": 0}
            if rec.get("count", 0) < self.ntr_max:
                return finalize(False, f"{nick}，只有今天已经用完全部「牛老婆」次数时才能使用「宝刀未老」哦~")
            bonus_uses = 4 * double_factor
            # 牛魔王效果：本次获得的次数翻倍
            if get_user_flag(today, uid, "ntr_override"):
                bonus_uses = bonus_uses * 2
            add_user_mod(today, uid, "ntr_extra_uses", bonus_uses)
            return finalize(True, f"{nick}，宝刀未老！你今天额外获得{bonus_uses}次「牛老婆」机会。")
        if name == "龙王":
            lost_wives = get_user_meta(today, uid, "lost_wives", [])
            if not isinstance(lost_wives, list) or len(lost_wives) < 1:
                return finalize(False, "隐忍，还未到使用的时候......")
            set_user_flag(today, uid, "harem", True)
            set_user_meta(today, uid, "harem_chaos_multiplier", float(double_factor))
            rec = ensure_group_record(uid, gid, today, nick, keep_existing=True)
            rec["harem"] = True
            for w in lost_wives:
                if isinstance(w, str) and w not in rec["wives"]:
                    rec["wives"].append(w)
            set_user_meta(today, uid, "lost_wives", [])
            save_group_config(cfg)
            # 检查露出状态：如果用户有露出状态，触发修罗场
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                # 触发修罗场后获得一次抽老婆（换老婆）机会
                add_user_mod(today, uid, "change_extra_uses", 1)
                return finalize(True, f"{nick}，龙王降临！你开启了后宫模式，但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
            return finalize(True, f"{nick}，龙王降临！你开启了后宫模式，并取回了所有被牛走的老婆。")
        if name == "鹿鹿时间到了":
            add_group_meta(today, gid, "change_extra_uses", 1 * double_factor)
            return finalize(True, f"{nick}，「鹿鹿时间到了」为本群所有人增加了{1 * double_factor}次「换老婆」机会！")
        if name == "开明盒":
            desired = extra_arg.strip()
            if not desired:
                return finalize(False, f"{nick}，请在“使用开明盒”后写上想要的道具卡名称哦~")
            if desired not in self.item_pool:
                return finalize(False, f"{nick}，暂未识别到名为“{desired}”的道具卡，请重新选择~")
            today_items = item_data.setdefault(today, {})
            user_items = today_items.setdefault(uid, [])
            user_items.append(desired)
            save_item_data()
            return finalize(True, f"{nick}，你打开了开明盒，获得了自选道具卡「{desired}」！")
        if name == "烧火棍":
            # 清空今日所有数据
            # 清空今日效果数据（但保留棍勇状态）
            eff = get_user_effects(today, uid)
            # 保存棍勇相关数据
            stick_hero = eff["meta"].get("stick_hero", False)
            stick_hero_wives = eff["meta"].get("stick_hero_wives", [])
            reset_extra_uses = eff["meta"].get("reset_extra_uses", 0)
            reset_blind_box_extra = eff["meta"].get("reset_blind_box_extra", 0)
            # 清空效果数据
            if today in effects_data and uid in effects_data[today]:
                del effects_data[today][uid]
            # 清空今日道具数据
            lost_items = 0
            if today in item_data and uid in item_data[today]:
                lost_items = len(item_data[today][uid])
                del item_data[today][uid]
                if lost_items:
                    self._handle_item_loss(today, uid, lost_items, gid)
            # 清空老婆数据
            loss = get_wife_count(cfg, uid, today)
            if uid in cfg:
                del cfg[uid]
                save_group_config(cfg)
                self._handle_wife_loss(today, uid, loss, gid)
            # 清空牛老婆记录（如果日期是今天）
            if gid in ntr_records and uid in ntr_records[gid]:
                rec = ntr_records[gid][uid]
                if rec.get("date") == today:
                    del ntr_records[gid][uid]
            # 清空换老婆记录（如果日期是今天）
            if gid in change_records and uid in change_records[gid]:
                rec = change_records[gid][uid]
                if rec.get("date") == today:
                    del change_records[gid][uid]
            # 清空交换请求
            if gid in swap_requests and uid in swap_requests[gid]:
                del swap_requests[gid][uid]
            # 清空选老婆记录
            if today in select_wife_records and uid in select_wife_records[today]:
                del select_wife_records[today][uid]
            # 清空打老婆记录
            if today in beat_wife_records and uid in beat_wife_records[today]:
                del beat_wife_records[today][uid]
            # 清空重置盲盒记录（如果日期是今天）
            if today in reset_blind_box_records and uid in reset_blind_box_records[today]:
                del reset_blind_box_records[today][uid]
            # 清空交换限制记录（如果日期是今天）
            if gid in swap_limit_records and uid in swap_limit_records[gid]:
                rec_lim = swap_limit_records[gid][uid]
                if rec_lim.get("date") == today:
                    del swap_limit_records[gid][uid]
            # 保存所有修改
            save_ntr_records()
            save_change_records()
            save_swap_requests()
            save_select_wife_records()
            save_beat_wife_records()
            save_reset_blind_box_records()
            save_swap_limit_records()
            # 设置棍勇状态
            set_user_flag(today, uid, "stick_hero", True)
            set_user_meta(today, uid, "stick_hero_wives", stick_hero_wives)
            add_user_mod(today, uid, "reset_extra_uses", 1)
            add_user_mod(today, uid, "reset_blind_box_extra", 1)
            return finalize(True, f"{nick}，你成为了棍勇......已清空今日所有数据")
        if name == "未来日记":
            # 设置下次抽老婆或换老婆的目标关键词
            set_user_meta(today, uid, "future_diary_target", "我妻由乃")
            # 获得病娇效果
            set_user_flag(today, uid, "landmine_girl", True)
            return finalize(True, f"{nick}，你已预见未来......")
        if name == "爱马仕":
            # 设置爱马仕状态
            set_user_flag(today, uid, "hermes", True)
            return finalize(True, f"{nick}，你成为了爱马仕")
        if name == "缘分":
            # 设置原批状态
            set_user_flag(today, uid, "yuanpi", True)
            return finalize(True, f"{nick}，原来你也......")
        if name == "存档":
            # 先确保今日效果已初始化，避免遗漏信息
            get_user_effects(today, uid)
            snapshot = self._collect_user_archive_payload(today, uid)
            archives[uid] = {
                "saved_on": today,
                "data": snapshot,
            }
            save_archives()
            return finalize(True, f"{nick}，存档完成！下次开启新的一天时会自动继承当前数据。")
        if name == "55开":
            # 设置众生平等状态
            set_user_flag(today, uid, "equal_rights", True)
            return finalize(True, f"{nick}，众生平等！你对其他人使用指令或道具时可无视对方的状态，但其他人对你使用道具时也会无视你的状态。")
        if name == "囤囤鼠":
            # 设置盲盒爱好者状态
            set_user_flag(today, uid, "blind_box_enthusiast", True)
            return finalize(True, f"{nick}，你成为了盲盒爱好者！今日每4小时可以免费抽一次盲盒，但每1小时只能使用一个道具。")
        if name == "露出癖":
            # 设置露出状态
            set_user_flag(today, uid, "exhibitionist", True)
            # 检查是否处于开后宫状态，如果是且拥有2个及以上老婆则触发修罗场
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                # 触发修罗场后获得一次抽老婆（换老婆）机会
                add_user_mod(today, uid, "change_extra_uses", 1)
                return finalize(True, f"{nick}，你获得了「露出」效果！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
            return finalize(True, f"{nick}，你获得了「露出」效果！今日使用任何指令和道具都会额外使用一次「查老婆」指令。")
        if name == "会员制餐厅":
            # 使用方法：使用会员制餐厅 XXX @目标
            # 赠送当前背包的一张道具卡给目标，并立即使用（视为目标使用该道具）
            if not target_uid:
                return finalize(False, f"{nick}，使用「会员制餐厅」时请@目标用户哦~ 使用方法：使用会员制餐厅 「道具卡名称」 @目标用户")
            target_uid = str(target_uid)
            if target_uid == uid:
                return finalize(False, f"{nick}，不能对自己使用「会员制餐厅」哦~")
            # 从extra_arg中解析要赠送的道具名称（去掉@目标部分）
            gift_card_name = extra_arg.strip()
            # 移除可能包含的@目标部分
            if "@" in gift_card_name:
                gift_card_name = gift_card_name.split("@")[0].strip()
            if not gift_card_name:
                return finalize(False, f"{nick}，请在「使用会员制餐厅」后写上要赠送的道具卡名称哦~ 使用方法：使用会员制餐厅 「道具卡名称」 @目标用户")
            if gift_card_name not in self.item_pool:
                return finalize(False, f"{nick}，暂未识别到名为「{gift_card_name}」的道具卡，请重新选择~")
            # 检查用户是否有该道具
            today_items = item_data.get(today, {})
            user_items = today_items.get(uid, [])
            if gift_card_name not in user_items:
                return finalize(False, f"{nick}，你的道具卡里没有「{gift_card_name}」哦~")
            # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
            user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
            target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
            equal_rights_msg = ""  # 保存众生平等提示语
            if not user_has_equal_rights and not target_has_equal_rights:
                # 检查目标是否处于贤者时间
                if get_user_flag(today, target_uid, "ban_items"):
                    return finalize(False, f"{nick}，对方正处于贤者时间，无法接收道具。")
            else:
                # 众生平等状态：豁免保护，显示特殊提示语
                if get_user_flag(today, target_uid, "ban_items"):
                    if user_has_equal_rights:
                        equal_rights_msg = "众生平等！你无视了对方的贤者时间，"
                    elif target_has_equal_rights:
                        equal_rights_msg = "众生平等！对方的状态无法保护自己，"
            # 从用户背包中移除道具
            user_items.remove(gift_card_name)
            self._handle_item_loss(today, uid, 1, gid)
            save_item_data()
            # 将道具添加到目标背包
            target_items = today_items.setdefault(target_uid, [])
            target_items.append(gift_card_name)
            save_item_data()
            # 立即为目标使用该道具（视为目标使用）
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            # 调用apply_item_effect，但使用target_uid作为caller_uid
            success, message = await self.apply_item_effect(gift_card_name, event, None, "", caller_uid=target_uid)
            if success:
                # 从目标背包移除道具（因为已经使用了）
                if gift_card_name in target_items:
                    target_items.remove(gift_card_name)
                    save_item_data()
            return finalize(True, f"{nick}，{equal_rights_msg}吃完有奖励，吃不完有惩罚......你通过「会员制餐厅」将「{gift_card_name}」赠送给了{target_nick}，并立即为其使用。\n{message or ''}")
        if name == "柏青哥":
            # 清空所有道具
            if today in item_data and uid in item_data[today]:
                lost_items = len(item_data[today][uid])
                del item_data[today][uid]
                save_item_data()
                if lost_items:
                    self._handle_item_loss(today, uid, lost_items, gid)
            # 随机触发一种效果
            choice = random.choice(["reset_and_gain", "pachinko_777", "three_states", "mute_300"])
            if choice == "reset_and_gain":
                # 用完今日所有的换老婆、牛老婆、重置、重置盲盒次数
                # 将当前使用次数设置为最大值（表示已用完），但不修改额外次数
                gid = str(event.message_obj.group_id)
                # 换老婆次数：设置为最大值表示已用完
                change_recs = change_records.setdefault(gid, {})
                change_rec = change_recs.get(uid, {"date": "", "count": 0})
                if change_rec.get("date") == today:
                    max_change = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0))
                    change_rec["count"] = max_change
                    change_recs[uid] = change_rec
                    save_change_records()
                # 牛老婆次数：设置为最大值表示已用完
                ntr_recs = ntr_records.setdefault(gid, {})
                ntr_rec = ntr_recs.get(uid, {"date": "", "count": 0})
                if ntr_rec.get("date") == today:
                    max_ntr = (self.ntr_max or 0) + int(get_user_mod(today, uid, "ntr_extra_uses", 0))
                    ntr_rec["count"] = max_ntr
                    ntr_recs[uid] = ntr_rec
                    save_ntr_records()
                # 重置次数
                reset_records = load_json(RESET_SHARED_FILE)
                grp = reset_records.setdefault(gid, {})
                rec = grp.get(uid, {"date": today, "count": 0})
                if rec.get("date") == today:
                    reset_extra_uses = int(get_user_mod(today, uid, "reset_extra_uses", 0))
                    max_reset = (self.reset_max_uses_per_day or 0) + reset_extra_uses
                    rec["count"] = max_reset
                    grp[uid] = rec
                    save_json(RESET_SHARED_FILE, reset_records)
                # 重置盲盒次数
                day_record = reset_blind_box_records.setdefault(today, {})
                used = int(day_record.get(uid, 0))
                reset_blind_box_extra = int(get_user_mod(today, uid, "reset_blind_box_extra", 0))
                max_reset_blind_box = 1 + reset_blind_box_extra
                day_record[uid] = max_reset_blind_box
                save_reset_blind_box_records()
                # 随机获得1~6次换老婆的次数、1~6次牛老婆的次数、0~3次重置次数、0~3次重置盲盒次数
                change_gain = random.randint(1, 6)
                ntr_gain = random.randint(1, 6)
                reset_gain = random.randint(0, 3)
                reset_blind_box_gain = random.randint(0, 3)
                # 开后宫用户：换老婆次数转换为抽老婆次数
                is_harem = get_user_flag(today, uid, "harem")
                if is_harem:
                    self._convert_change_to_draw_for_harem(today, uid, gid, change_gain)
                else:
                    add_user_mod(today, uid, "change_extra_uses", change_gain)
                add_user_mod(today, uid, "ntr_extra_uses", ntr_gain)
                add_user_mod(today, uid, "reset_extra_uses", reset_gain)
                add_user_mod(today, uid, "reset_blind_box_extra", reset_blind_box_gain)
                save_change_records()
                save_ntr_records()
                return finalize(True, f"{nick}，666！你已用完今日所有次数，并获得{change_gain}次换老婆、{ntr_gain}次牛老婆、{reset_gain}次重置、{reset_blind_box_gain}次重置盲盒机会。")
            elif choice == "pachinko_777":
                # 获得"777"效果
                set_user_flag(today, uid, "pachinko_777", True)
                add_user_mod(today, uid, "blind_box_extra_draw", 2)
                return finalize(True, f"{nick}，777！你获得2次额外抽盲盒次数，且今日抽盲盒必定触发一次暴击。")
            elif choice == "three_states":
                eff = get_user_effects(today, uid)
                state_pool = []
                for state_name, checker in self.pachinko_state_specs:
                    has_state = False
                    try:
                        has_state = bool(checker(eff))
                    except:
                        has_state = False
                    if not has_state:
                        state_pool.append(state_name)
                if not state_pool:
                    state_pool = [state_name for state_name, _ in self.pachinko_state_specs]
                if not state_pool:
                    return finalize(False, f"{nick}，暂无可用的状态效果，柏青哥罢工了。")
                while len(state_pool) < 3:
                    state_pool.extend(state_pool)
                selected = random.sample(state_pool, min(3, len(state_pool)))
                applied_states = []
                for state in selected:
                    success, _ = await self.apply_item_effect(
                        state,
                        event,
                        None,
                        caller_uid=uid,
                        use_double_effect=False,
                        consume_double_effect=False,
                    )
                    if success:
                        applied_states.append(state)
                if not applied_states:
                    return finalize(False, f"{nick}，柏青哥抽取状态失败了，请稍后再试。")
                return finalize(True, f"{nick}，111！你随机获得了三个状态效果：{', '.join(applied_states)}。")
            elif choice == "mute_300":
                # 被禁言300秒
                try:
                    duration = 300
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=int(duration))
                except:
                    pass
                return finalize(True, f"{nick}，438！你被禁言300秒......")
        if name == "洗牌":
            # 失去你所有道具卡，再获得同等数量的道具卡（此道具也将计入数量）
            today_items = item_data.setdefault(today, {})
            user_items = today_items.get(uid, [])
            if not user_items:
                return finalize(False, f"{nick}，你当前没有道具卡，无法使用「洗牌」。")
            # 获取当前道具数量（包括"洗牌"本身）
            item_count = len(user_items)
            # 清空所有道具
            today_items[uid] = []
            save_item_data()
            # 从道具池中随机抽取同等数量的道具
            new_items = random.choices(self.item_pool, k=item_count)
            today_items[uid] = new_items
            save_item_data()
            items_text = "、".join(new_items)
            return finalize(True, f"{nick}，洗牌完成！你失去了所有道具卡，重新获得了{item_count}张道具卡：{items_text}。")
        if name == "塞翁失马":
            set_user_flag(today, uid, "fortune_linked", True)
            return finalize(True, f"{nick}，塞翁失马焉知非福？")
        if name == "好兄弟":
            if not target_uid:
                return finalize(False, f"{nick}，使用「好兄弟」时请@目标用户哦~")
            target_uid = str(target_uid)
            if target_uid == uid:
                return finalize(False, f"{nick}，不能对自己使用「好兄弟」哦~")
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            _clear_brother_link(today, uid)
            _clear_brother_link(today, target_uid)
            self_eff = get_user_effects(today, uid)
            target_eff = get_user_effects(today, target_uid)
            self_eff["meta"]["brother_partner"] = target_uid
            self_eff["meta"]["brother_label"] = target_nick
            target_eff["meta"]["brother_partner"] = uid
            target_eff["meta"]["brother_label"] = nick
            save_effects()
            _sync_brother_statuses(today, uid, target_uid)
            set_user_flag(today, uid, "brother_bond", True)
            return finalize(True, f"{nick}，你与{target_nick}结为好兄弟！今日双方同甘共苦，获得的状态将实时共享。")
        if name == "斗转星移":
            new_fortune = get_user_fortune(today, uid, force=True, favor_good=True)
            fortune_type = new_fortune.get("type", "未知")
            stars = new_fortune.get("stars", "?")
            lucky_star = new_fortune.get("lucky_star", "神秘人")
            fortune_texts = []
            fortune_texts.append(f"{nick}，斗转星移！你的今日运势被重新占卜为「{fortune_type}」（{stars}星），幸运吉星是「{lucky_star}」。")
            # 复用今日运势指令输出
            fortune = get_user_fortune(today, uid)
            proverb = fortune.get("proverb", "……")
            lucky = fortune.get("lucky_star", "神秘人")
            dos = "、".join(fortune.get("dos", [])) or "暂无"
            donts = "、".join(fortune.get("donts", [])) or "暂无"
            fortune_texts.append(f"今日箴言：{proverb}")
            fortune_texts.append(f"宜：{dos}")
            fortune_texts.append(f"忌：{donts}")
            return finalize(True, "\n".join(fortune_texts))
        # 其他未实现
        return finalize(False, f"道具卡「{card_name}」的效果正在开发中，敬请期待~")

    async def animewife(self, event: AstrMessageEvent, free_draw: bool = False):
        # 抽老婆主逻辑
        # free_draw: 是否免费抽（不消耗次数），用于牛成功后的追加抽老婆流程
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        if get_user_flag(today, uid, "shura"):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
            return
        cfg = load_group_config(gid)
        is_harem = get_user_flag(today, uid, "harem")
        # 检查是否今天已抽（普通用户）或是否达到次数限制（开后宫用户）
        if is_harem:
            # 免费抽跳过次数检查
            if not free_draw:
                # 开后宫：抽老婆次数 = 换老婆次数
                change_recs = change_records.setdefault(gid, {})
                change_rec = change_recs.get(uid, {"date": "", "count": 0})
                if change_rec.get("date") != today:
                    change_rec = {"date": today, "count": 0}
                # 检查群加成，如果是开后宫用户，将群加成转换为抽老婆次数（增加额外使用次数）
                group_bonus = int(get_group_meta(today, gid, "change_extra_uses", 0))
                if group_bonus > 0:
                    # 检查已转换的群加成数量
                    converted_amount = int(get_user_meta(today, uid, "group_bonus_converted", 0))
                    remaining_bonus = group_bonus - converted_amount
                    if remaining_bonus > 0:
                        # 将剩余的群加成转换为抽老婆次数（增加额外使用次数，不修改records的count）
                        add_user_mod(today, uid, "change_extra_uses", remaining_bonus)
                        # 更新已转换的群加成数量
                        set_user_meta(today, uid, "group_bonus_converted", group_bonus)
                max_draw = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0))
                if change_rec.get("count", 0) >= max_draw:
                    yield event.plain_result(f"{nick}，你今天已经抽了{max_draw}次老婆啦（开后宫模式下抽老婆次数=换老婆次数），明天再来吧~")
                    return
            # 检查是否已有老婆（开后宫可以继续抽）
            wife_count = get_wife_count(cfg, uid, today)
            if wife_count > 0:
                # 超吉状态：不再触发修罗场
                if not get_user_flag(today, uid, "super_lucky"):
                    # 检查修罗场触发：5% * 1.33^老婆数量
                    chaos_multiplier = float(get_user_meta(today, uid, "harem_chaos_multiplier", 1.0) or 1.0)
                    prob = 0.05 * (1.33 ** wife_count) * chaos_multiplier
                    prob = min(prob, 0.9)
                    if self._probability_check(prob, today, uid):
                        # 触发修罗场，失去所有老婆
                        if uid in cfg:
                            loss = wife_count
                            del cfg[uid]
                            save_group_config(cfg)
                            self._handle_wife_loss(today, uid, loss, gid)
                        # 触发修罗场后获得一次抽老婆（换老婆）机会
                        add_user_mod(today, uid, "change_extra_uses", 1)
                        yield event.plain_result(f"{nick}，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
                        return
        else:
            # 普通用户：今天已抽则直接返回
            wives = get_wives_list(cfg, uid, today)
            if wives:
                img = wives[0]  # 普通用户只有一个老婆
                if img.startswith("http"):
                    display_name = self._resolve_avatar_nick(cfg, img)
                    text = f"{nick}，你今天的老婆是{display_name}，请好好珍惜哦~"
                else:
                    name = os.path.splitext(img)[0]
                    if "!" in name:
                        source, chara = name.split("!", 1)
                        text = f"{nick}，你今天的老婆是来自《{source}》的{chara}，请好好珍惜哦~"
                    else:
                        text = f"{nick}，你今天的老婆是{name}，请好好珍惜哦~"
                image_component = self._build_image_component(img)
                if image_component:
                    yield event.chain_result([Plain(text), image_component])
                else:
                    yield event.plain_result(text)
                return
        # 开始抽取新老婆
        user_keywords = pro_users.get(uid, [])
        hermes = get_user_flag(today, uid, "hermes")
        yuanpi = get_user_flag(today, uid, "yuanpi")

        image_pool = []
        try:
            if os.path.exists(IMG_DIR):
                image_pool = [f for f in os.listdir(IMG_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))]
        except:
            image_pool = []

        if not image_pool:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.image_base_url) as resp:
                        text = await resp.text()
                        image_pool = text.splitlines()
            except:
                yield event.plain_result("抱歉，今天的老婆获取失败了，请稍后再试~")
                return

        if hermes:
            image_pool = [img_name for img_name in image_pool if "赛马娘" in img_name]
            if not image_pool:
                yield event.plain_result("抱歉，没有找到包含「赛马娘」关键词的角色，请稍后再试~")
                return
        
        if yuanpi:
            image_pool = [img_name for img_name in image_pool if "原神" in img_name]
            if not image_pool:
                yield event.plain_result("抱歉，没有找到包含「原神」关键词的角色，请稍后再试~")
                return

        if user_keywords:
            keywords_lower = [kw.lower() for kw in user_keywords]
            filtered_imgs = [
                img_name for img_name in image_pool
                if any(kw in img_name.lower() for kw in keywords_lower)
            ]
            if filtered_imgs:
                image_pool = filtered_imgs

        img = random.choice(image_pool)
        comp_target = get_user_meta(today, uid, "competition_target", None)
        if comp_target:
            target_wives = get_wives_list(cfg, comp_target, today)
            competition_prob = clamp_probability(get_user_meta(today, uid, "competition_prob", 0.35) or 0.35)
            # 穷凶极恶效果：正面概率加成变为125%
            if get_user_flag(today, uid, "extreme_evil"):
                competition_prob = competition_prob * 1.25
                competition_prob = min(0.9, competition_prob)  # 概率上限为90%
            if target_wives and self._probability_check(competition_prob, today, uid):
                img = random.choice(target_wives)
                # 抽到与目标相同的老婆后，退出雄竞状态
                eff = get_user_effects(today, uid)
                if "competition_target" in eff["meta"]:
                    del eff["meta"]["competition_target"]
                if "competition_prob" in eff["meta"]:
                    del eff["meta"]["competition_prob"]
                save_effects()
        # 检查棍勇状态：35%概率抽到关键词包含"回复术士的重启人生"的老婆
        stick_hero = get_user_flag(today, uid, "stick_hero")
        if stick_hero and self._probability_check(0.35, today, uid):
            stick_hero_wives = get_user_meta(today, uid, "stick_hero_wives", [])
            if not isinstance(stick_hero_wives, list):
                stick_hero_wives = []
            # 获取所有图片列表
            try:
                if os.path.exists(IMG_DIR):
                    local_imgs = [f for f in os.listdir(IMG_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))]
                else:
                    local_imgs = []
            except:
                local_imgs = []
            if not local_imgs:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.image_base_url) as resp:
                            text = await resp.text()
                        local_imgs = text.splitlines()
                except:
                    local_imgs = []
            # 筛选包含"回复术士的重启人生"关键词的图片，排除已获得的
            keyword = "回复术士的重启人生"
            filtered_imgs = [
                img_name for img_name in local_imgs
                if keyword in img_name and img_name not in stick_hero_wives
            ]
            if filtered_imgs:
                img = random.choice(filtered_imgs)
                # 记录已获得的老婆
                stick_hero_wives.append(img)
                set_user_meta(today, uid, "stick_hero_wives", stick_hero_wives)
        # 检查未来日记：强制抽到指定关键词的老婆
        future_diary_target = get_user_meta(today, uid, "future_diary_target", None)
        if future_diary_target:
            # 获取所有图片列表
            try:
                if os.path.exists(IMG_DIR):
                    local_imgs = [f for f in os.listdir(IMG_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))]
                else:
                    local_imgs = []
            except:
                local_imgs = []
            if not local_imgs:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.image_base_url) as resp:
                            text = await resp.text()
                        local_imgs = text.splitlines()
                except:
                    local_imgs = []
            # 筛选包含目标关键词的图片
            filtered_imgs = [
                img_name for img_name in local_imgs
                if future_diary_target in img_name
            ]
            if filtered_imgs:
                img = random.choice(filtered_imgs)
                # 清除未来日记标记（只生效一次）
                eff = get_user_effects(today, uid)
                if "future_diary_target" in eff["meta"]:
                    del eff["meta"]["future_diary_target"]
                save_effects()
        # 统一使用add_wife函数添加老婆
        if not add_wife(cfg, uid, img, today, nick, is_harem):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
            return
        save_group_config(cfg)
        # 检查露出状态：如果用户有露出状态且处于开后宫状态，当老婆数量达到2个及以上时触发修罗场
        triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
        if triggered:
            # 触发修罗场后获得一次抽老婆（换老婆）机会
            add_user_mod(today, uid, "change_extra_uses", 1)
            yield event.plain_result(f"{nick}，你抽到了新老婆！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
            return
        if is_harem:
            # 增加抽老婆次数（使用换老婆记录），但免费抽不消耗次数
            if not free_draw:
                change_recs = change_records.setdefault(gid, {})
                change_rec = change_recs.get(uid, {"date": today, "count": 0})
                if change_rec.get("date") != today:
                    change_rec = {"date": today, "count": 0}
                change_rec["count"] = change_rec.get("count", 0) + 1
                change_recs[uid] = change_rec
                save_change_records()
            wife_count = get_wife_count(cfg, uid, today)
            text = f"{nick}，你抽到了新老婆！当前共有{wife_count}个老婆。"
        else:
            text = ""
        # 解析出处和角色名，分隔符为!
        if img.startswith("http"):
            display_name = self._resolve_avatar_nick(cfg, img)
            if not text:
                text = f"{nick}，你今天的老婆是{display_name}，请好好珍惜哦~"
            else:
                text += display_name
        else:
            name = os.path.splitext(img)[0]
            if "!" in name:
                source, chara = name.split("!", 1)
                if not text:
                    text = f"{nick}，你今天的老婆是来自《{source}》的{chara}，请好好珍惜哦~"
                else:
                    text += f"来自《{source}》的{chara}"
            else:
                if not text:
                    text = f"{nick}，你今天的老婆是{name}，请好好珍惜哦~"
                else:
                    text += name
        image_component = self._build_image_component(img)
        if image_component:
            yield event.chain_result([Plain(text), image_component])
        else:
            yield event.plain_result(text)

    async def ntr_wife(self, event: AstrMessageEvent):
        # 牛老婆主逻辑
        gid = str(event.message_obj.group_id)
        if not ntr_statuses.get(gid, True):
            yield event.plain_result("牛老婆功能还没开启哦，请联系管理员开启~")
            return
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        # 检查使用者是否拥有纯爱战士效果
        if get_user_flag(today, uid, "protect_from_ntr") and not get_user_flag(today, uid, "ntr_override"):
            yield event.plain_result(f"{nick}，纯爱战士不会使用「牛老婆」指令哦~")
            return
        # 检查使用者是否拥有公交车效果（无法使用牛老婆）
        if get_user_flag(today, uid, "ban_ntr") and not get_user_flag(today, uid, "ntr_override"):
            yield event.plain_result(f"{nick}，公交车效果：你今天无法使用「牛老婆」指令哦~")
            return
        grp = ntr_records.setdefault(gid, {})
        rec = grp.get(uid, {"date": today, "count": 0})
        if rec["date"] != today:
            rec = {"date": today, "count": 0}
        extra_ntr = int(get_user_mod(today, uid, "ntr_extra_uses", 0))
        max_ntr = (self.ntr_max or 0) + extra_ntr
        if rec["count"] >= max_ntr:
            yield event.plain_result(
                f"{nick}，你今天已经牛了{max_ntr}次啦，明天再来吧~"
            )
            return
        tid = self.parse_target(event)
        if not tid or tid == uid:
            msg = "请@你想牛的对象哦~" if not tid else "不能牛自己呀，换个人试试吧~"
            yield event.plain_result(f"{nick}，{msg}")
            return
        cfg = load_group_config(gid)
        # 检查目标是否有老婆（支持开后宫用户）
        target_wife_count = get_wife_count(cfg, tid, today)
        if target_wife_count == 0:
            yield event.plain_result("对方今天还没有老婆可牛哦~")
            return
        # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
        user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
        target_has_equal_rights = get_user_flag(today, tid, "equal_rights")
        if not user_has_equal_rights and not target_has_equal_rights:
            # 目标不可被牛（纯爱战士等保护）
            if get_user_flag(today, tid, "protect_from_ntr"):
                yield event.plain_result("对方今天誓死守护纯爱，无法牛走对方的老婆哦~")
                return
            # 目标不可被牛（病娇效果）
            if get_user_flag(today, tid, "landmine_girl"):
                yield event.plain_result("对方的老婆是病娇，无法牛走对方的老婆哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语
            if get_user_flag(today, tid, "protect_from_ntr"):
                if user_has_equal_rights:
                    yield event.plain_result("众生平等！你无视了对方的纯爱守护，继续执行牛老婆~")
                elif target_has_equal_rights:
                    yield event.plain_result("众生平等！对方的状态无法保护自己，继续执行牛老婆~")
            if get_user_flag(today, tid, "landmine_girl"):
                if user_has_equal_rights:
                    yield event.plain_result("众生平等！你无视了对方的病娇保护，继续执行牛老婆~")
                elif target_has_equal_rights:
                    yield event.plain_result("众生平等！对方的状态无法保护自己，继续执行牛老婆~")
        rec["count"] += 1
        grp[uid] = rec
        save_ntr_records()
        # 计算经由效果修正后的成功概率
        attack_bonus = float(get_user_mod(today, uid, "ntr_attack_bonus", 0.0))
        defense_bonus = float(get_user_mod(today, tid, "ntr_defense_bonus", 0.0))
        final_prob = max(0.0, min(0.9, (self.ntr_possibility or 0.0) + attack_bonus + defense_bonus))
        # 穷凶极恶效果：正面概率加成变为125%
        if get_user_flag(today, uid, "extreme_evil"):
            final_prob = final_prob * 1.25
            final_prob = min(0.9, final_prob)  # 保持原有上限
        forced_success = False
        if get_user_flag(today, uid, "next_ntr_guarantee"):
            forced_success = True
            set_user_flag(today, uid, "next_ntr_guarantee", False)
        if get_user_flag(today, tid, "victim_auto_ntr"):
            forced_success = True
        if forced_success or self._probability_check(final_prob, today, uid):
            # 获取目标的老婆（支持开后宫用户）
            target_wives = get_wives_list(cfg, tid, today)
            if not target_wives:
                yield event.plain_result("对方今天还没有老婆可牛哦~")
                return
            wife = random.choice(target_wives)
            if get_user_flag(today, uid, "protect_from_ntr"):
                yield event.plain_result("坚守纯爱的你拒绝了牛来的老婆，不要违背自己的内心哦")
                return
            lost_wives = get_user_meta(today, tid, "lost_wives", [])
            if not isinstance(lost_wives, list):
                lost_wives = []
            if wife not in lost_wives:
                lost_wives.append(wife)
            set_user_meta(today, tid, "lost_wives", lost_wives)
            # 从目标处移除老婆
            if is_harem_user(cfg, tid):
                cfg[tid]["wives"].remove(wife)
                if len(cfg[tid]["wives"]) == 0:
                    del cfg[tid]
            else:
                del cfg[tid]
            self._handle_wife_loss(today, tid, 1, gid)
            # 检查攻击者是否有病娇效果（在有老婆的情况下成功牛别人时触发事件）
            attacker_has_wife = get_wife_count(cfg, uid, today) > 0
            landmine_girl = get_user_flag(today, uid, "landmine_girl")
            if landmine_girl and attacker_has_wife:
                # 病娇效果：随机触发事件
                # 25% kill_wife, 15% mute_300, 10% suicide, 50% get_item
                event_choice = random.choices(
                    ["kill_wife", "mute_300", "suicide", "get_item"],
                    weights=[25, 15, 10, 50],
                    k=1
                )[0]
                if event_choice == "kill_wife":
                    # 从wives列表里随机挑选一个老婆
                    murdered_wife = random.choice(cfg[uid]["wives"])
                    # 文案中使用人物名而不是文件名/URL
                    murderer_name = self._get_wife_display_name(cfg, murdered_wife)
                    victim_name = self._get_wife_display_name(cfg, wife)
                    # 你原本的老婆将你牛到的老婆"杀"了（即本次牛老婆不会替换你原本的老婆或增加你的老婆）
                    yield event.plain_result(f"{nick}，你的老婆{murderer_name}不小心把{victim_name}杀了......")
                    return
                elif event_choice == "mute_300":
                    # 你被禁言300秒
                    try:
                        await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=300)
                    except:
                        pass
                    yield event.plain_result(f"{nick}，你被你的老婆打晕了......但好消息是，你还活着")
                    return
                elif event_choice == "suicide":
                    # 你原本的老婆自杀了（即原本的老婆将消失，你牛到的老婆也不会添加到你的wives列表）
                    loss = get_wife_count(cfg, uid, today)
                    if uid in cfg:
                        del cfg[uid]
                    save_group_config(cfg)
                    self._handle_wife_loss(today, uid, loss, gid)
                    yield event.plain_result(f"{nick}，你的老婆自杀了......你失去了所有老婆。")
                    return
                elif event_choice == "get_item":
                    # 获得一张何意味道具卡
                    today_items = item_data.setdefault(today, {})
                    user_items = today_items.setdefault(uid, [])
                    user_items.append("何意味")
                    save_item_data()
                    # 继续执行牛老婆逻辑
                    pass
            # 给攻击者添加老婆
            is_attacker_harem = is_harem_user(cfg, uid)
            add_wife(cfg, uid, wife, today, nick, is_attacker_harem, allow_shura=True)
            save_group_config(cfg)
            # 检查露出状态：如果用户有露出状态且处于开后宫状态，当老婆数量达到2个及以上时触发修罗场
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                # 触发修罗场后获得一次抽老婆（换老婆）机会
                add_user_mod(today, uid, "change_extra_uses", 1)
                yield event.plain_result(f"{nick}，牛老婆成功！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
                return
            # 检查并取消相关交换请求
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, tid])
            yield event.plain_result(f"{nick}，牛老婆成功！老婆已归你所有，恭喜恭喜~")
            if cancel_msg:
                yield event.plain_result(cancel_msg)
            async for res in self._handle_light_fingers_on_ntr(today, uid, tid, event, cfg):
                yield res
            self._grant_lightbulb_bonus(today, gid, "ntr")
            if not get_user_flag(today, uid, "shura"):
                # 立即展示新老婆（免费抽，不消耗次数）
                async for res in self.animewife(event, free_draw=True):
                    yield res
        else:
            rem = max_ntr - rec["count"]
            yield event.plain_result(
                f"{nick}，很遗憾，牛失败了！你今天还可以再试{rem}次~"
            )

    async def search_wife(self, event: AstrMessageEvent):
        # 查老婆主逻辑
        gid = str(event.message_obj.group_id)
        tid = self.parse_target(event) or str(event.get_sender_id())
        today = get_today()
        cfg = load_group_config(gid)
        # 检查是否有老婆
        wife_count = get_wife_count(cfg, tid, today)
        if wife_count == 0:
            yield event.plain_result("没有发现老婆的踪迹，快去抽一个试试吧~")
            return
        # 获取用户信息
        data = cfg.get(tid, {})
        owner = data.get("nick", f"用户{tid}") if isinstance(data, dict) else f"用户{tid}"
        # 开后宫用户：显示所有老婆
        if is_harem_user(cfg, tid):
            wives = get_wives_list(cfg, tid, today)
            if not wives:
                yield event.plain_result("没有发现老婆的踪迹，快去抽一个试试吧~")
                return
            # 显示所有老婆
            for idx, img in enumerate(wives, 1):
                if img.startswith("http"):
                    display_name = self._resolve_avatar_nick(cfg, img)
                    text = f"{owner}的第{idx}个老婆是{display_name}"
                else:
                    name = os.path.splitext(img)[0]
                    if "!" in name:
                        source, chara = name.split("!", 1)
                        text = f"{owner}的第{idx}个老婆是来自《{source}》的{chara}"
                    else:
                        text = f"{owner}的第{idx}个老婆是{name}"
                if idx == len(wives):
                    text += f"，共有{len(wives)}个老婆，羡慕吗？"
                else:
                    text += "，"
                image_component = self._build_image_component(img)
                if image_component:
                    yield event.chain_result([Plain(text), image_component])
                else:
                    yield event.plain_result(text)
        else:
            # 普通用户：显示单个老婆
            wives = get_wives_list(cfg, tid, today)
            if not wives:
                yield event.plain_result(f"{owner}今天还没有老婆哦~")
                return
            img = wives[0]  # 普通用户只有一个老婆
            if img.startswith("http"):
                display_name = self._resolve_avatar_nick(cfg, img)
                text = f"{owner}的老婆是{display_name}，羡慕吗？"
            else:
                name = os.path.splitext(img)[0]
                if "!" in name:
                    source, chara = name.split("!", 1)
                    text = f"{owner}的老婆是来自《{source}》的{chara}，羡慕吗？"
                else:
                    text = f"{owner}的老婆是{name}，羡慕吗？"
            image_component = self._build_image_component(img)
            if image_component:
                yield event.chain_result([Plain(text), image_component])
            else:
                yield event.plain_result(text)
        # # 解析出处和角色名，分隔符为!
        # if "!" in name:
        #     source, chara = name.split("!", 1)
        #     text = f"{owner}的老婆是来自《{source}》的{chara}，羡慕吗？"
        # else:
        #     text = f"{owner}的老婆是{name}，羡慕吗？"
        # path = os.path.join(IMG_DIR, img)
        # chain = [
        #     Plain(text),
        #         (Image.fromURL(img) if img.startswith("http")
        #          else (Image.fromFileSystem(path) if os.path.exists(path) else Image.fromURL(self.image_base_url + img))),
        # ]
        # try:
        #     yield event.chain_result(chain)
        # except:
        #     yield event.plain_result(text)

    async def switch_ntr(self, event: AstrMessageEvent):
        # 切换NTR开关，仅管理员可用
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        if uid not in self.admins:
            yield event.plain_result(f"{nick}，你没有权限操作哦~")
            return
        ntr_statuses[gid] = not ntr_statuses.get(gid, False)
        save_ntr_statuses()
        load_ntr_statuses()
        state = "开启" if ntr_statuses[gid] else "关闭"
        yield event.plain_result(f"{nick}，NTR已{state}")

    async def change_wife(self, event: AstrMessageEvent):
        # 换老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        cfg = load_group_config(gid)
        recs = change_records.setdefault(gid, {})
        rec = recs.get(uid, {"date": "", "count": 0})
        if get_user_flag(today, uid, "shura"):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法使用「换老婆」。")
            return
        # 禁止换老婆标记
        if get_user_flag(today, uid, "ban_change"):
            yield event.plain_result(f"{nick}，你今天无法使用“换老婆”哦~")
            return
        # 开后宫模式：无法使用换老婆指令
        is_harem = get_user_flag(today, uid, "harem")
        if is_harem:
            yield event.plain_result(f"{nick}，开后宫状态下无法使用“换老婆”指令哦~")
            return
        if rec.get("date") != today:
            rec = {"date": today, "count": 0}
            recs[uid] = rec
        # 普通用户：额外可用次数修正
        group_bonus = int(get_group_meta(today, gid, "change_extra_uses", 0))
        max_change = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0)) + group_bonus
        if rec["count"] >= max_change:
            yield event.plain_result(
                f"{nick}，你今天已经换了{max_change}次老婆啦，明天再来吧~"
            )
            return
        wives = get_wives_list(cfg, uid, today)
        if not wives:
            yield event.plain_result(f"{nick}，你今天还没有老婆，先去抽一个再来换吧~")
            return
        lost_count = len(wives)
        # 删除旧老婆数据
        if uid in cfg:
            del cfg[uid]
        self._handle_wife_loss(today, uid, lost_count, gid)
        fail_prob = float(get_user_mod(today, uid, "change_fail_prob", 0.0) or 0.0)
        if fail_prob > 0 and self._probability_check(fail_prob, today, uid):
            rec["count"] += 1
            recs[uid] = rec
            save_change_records()
            yield event.plain_result(f"{nick}，换老婆失败了，真可惜......")
            return
        consume = True
        free_prob = clamp_probability(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
        if free_prob > 0 and self._probability_check(free_prob, today, uid):
            consume = False
        free_msg = ""
        if not consume and free_prob > 0:
            free_msg = "（本次未消耗次数）"
        if not is_harem:
            # 普通用户已在上面的else分支删除
            save_group_config(cfg)
        if consume:
            rec["count"] += 1
        recs[uid] = rec
        save_change_records()
        # 检查并取消相关交换请求
        cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid])
        if cancel_msg:
            yield event.plain_result(cancel_msg)
        # 立即展示新老婆
        async for res in self.animewife(event):
            yield res
        if consume:
            self._grant_lightbulb_bonus(today, gid, "change")
        if free_msg:
            yield event.plain_result(f"{nick}{free_msg}")

    async def reset_ntr(self, event: AstrMessageEvent):
        # 重置牛老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        if get_user_flag(today, uid, "lightbulb"):
            yield event.plain_result(f"{nick}，电灯泡状态下无法使用「重置牛」指令哦~")
            return
        # 开后宫用户无法使用重置指令
        if get_user_flag(today, uid, "harem"):
            yield event.plain_result(f"{nick}，开后宫状态下无法使用“重置牛”指令哦~")
            return
        if uid in self.admins:
            tid = self.parse_at_target(event) or uid
            if gid in ntr_records and tid in ntr_records[gid]:
                del ntr_records[gid][tid]
                save_ntr_records()
            chain = [
                Plain("管理员操作：已重置"),
                At(qq=int(tid)),
                Plain("的牛老婆次数。"),
            ]
            yield event.chain_result(chain)
            return
        reset_records = load_json(RESET_SHARED_FILE)
        grp = reset_records.setdefault(gid, {})
        rec = grp.get(uid, {"date": today, "count": 0})
        if rec.get("date") != today:
            rec = {"date": today, "count": 0}
        reset_extra_uses = int(get_user_mod(today, uid, "reset_extra_uses", 0))
        max_reset = (self.reset_max_uses_per_day or 0) + reset_extra_uses
        if rec["count"] >= max_reset:
            yield event.plain_result(
                f"{nick}，你今天已经用完{max_reset}次重置机会啦，明天再来吧~"
            )
            return
        rec["count"] += 1
        grp[uid] = rec
        save_json(RESET_SHARED_FILE, reset_records)
        tid = self.parse_at_target(event) or uid
        if self._probability_check(self.reset_success_rate, today, uid):
            if gid in ntr_records and tid in ntr_records[gid]:
                del ntr_records[gid][tid]
                save_ntr_records()
            chain = [Plain("已重置"), At(qq=int(tid)), Plain("的牛老婆次数。")]
            yield event.chain_result(chain)
        else:
            try:
                await event.bot.set_group_ban(
                    group_id=int(gid),
                    user_id=int(uid),
                    duration=self.reset_mute_duration,
                )
            except:
                pass
            yield event.plain_result(
                f"{nick}，重置牛失败，被禁言{self.reset_mute_duration}秒，下次记得再接再厉哦~"
            )

    async def reset_change_wife(self, event: AstrMessageEvent):
        # 重置换老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        if get_user_flag(today, uid, "lightbulb"):
            yield event.plain_result(f"{nick}，电灯泡状态下无法使用「重置换」指令哦~")
            return
        # 开后宫用户无法使用重置指令
        if get_user_flag(today, uid, "harem"):
            yield event.plain_result(f"{nick}，开后宫状态下无法使用“重置换”指令哦~")
            return
        if uid in self.admins:
            tid = self.parse_at_target(event) or uid
            grp = change_records.setdefault(gid, {})
            if tid in grp:
                del grp[tid]
                if not grp:
                    del change_records[gid]
                save_change_records()
            chain = [
                Plain("管理员操作：已重置"),
                At(qq=int(tid)),
                Plain("的换老婆次数。"),
            ]
            yield event.chain_result(chain)
            return
        reset_records = load_json(RESET_SHARED_FILE)
        grp = reset_records.setdefault(gid, {})
        rec = grp.get(uid, {"date": today, "count": 0})
        if rec.get("date") != today:
            rec = {"date": today, "count": 0}
        if rec["count"] >= self.reset_max_uses_per_day:
            yield event.plain_result(
                f"{nick}，你今天已经用完{self.reset_max_uses_per_day}次重置机会啦，明天再来吧~"
            )
            return
        rec["count"] += 1
        grp[uid] = rec
        save_json(RESET_SHARED_FILE, reset_records)
        tid = self.parse_at_target(event) or uid
        if self._probability_check(self.reset_success_rate, today, uid):
            grp2 = change_records.setdefault(gid, {})
            if tid in grp2:
                del grp2[tid]
                if not grp2:
                    del change_records[gid]
                save_change_records()
            chain = [Plain("已重置"), At(qq=int(tid)), Plain("的换老婆次数。")]
            yield event.chain_result(chain)
        else:
            try:
                await event.bot.set_group_ban(
                    group_id=int(gid),
                    user_id=int(uid),
                    duration=self.reset_mute_duration,
                )
            except:
                pass
            yield event.plain_result(
                f"{nick}，重置换失败，被禁言{self.reset_mute_duration}秒，下次记得再接再厉哦~"
            )

    async def swap_wife(self, event: AstrMessageEvent):
        # 发起交换老婆请求
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        tid = self.parse_at_target(event)
        nick = event.get_sender_name()
        today = get_today()
        if get_user_flag(today, uid, "shura"):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法使用「交换老婆」。")
            return
        # 检查发起者是否拥有开后宫效果
        if get_user_flag(today, uid, "harem"):
            yield event.plain_result(f"{nick}，开后宫状态下无法使用「交换老婆」指令哦~")
            return
        # 检查发起者是否拥有纯爱战士效果
        if get_user_flag(today, uid, "protect_from_ntr"):
            yield event.plain_result(f"{nick}，纯爱战士不会使用「交换老婆」指令哦~")
            return
        grp_limit = swap_limit_records.setdefault(gid, {})
        rec_lim = grp_limit.get(uid, {"date": "", "count": 0})
        if rec_lim["date"] != today:
            rec_lim = {"date": today, "count": 0}
        if rec_lim["count"] >= self.swap_max_per_day:
            yield event.plain_result(
                f"{nick}，你今天已经发起了{self.swap_max_per_day}次交换请求啦，明天再来吧~"
            )
            return
        if not tid or tid == uid:
            yield event.plain_result(f"{nick}，请在命令后@你想交换的对象哦~")
            return
        # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
        user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
        target_has_equal_rights = get_user_flag(today, tid, "equal_rights")
        if not user_has_equal_rights and not target_has_equal_rights:
            if get_user_flag(today, tid, "shura"):
                yield event.plain_result(f"{nick}，对方处于修罗状态，只能通过「牛老婆」获得新老婆，无法参与交换。")
                return
            # 检查目标是否拥有开后宫效果
            if get_user_flag(today, tid, "harem"):
                yield event.plain_result(f"{nick}，无法对开后宫状态的用户使用「交换老婆」指令哦~")
                return
            # 检查目标是否拥有纯爱战士效果
            if get_user_flag(today, tid, "protect_from_ntr"):
                yield event.plain_result(f"{nick}，无法对纯爱战士使用「交换老婆」指令哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语
            if get_user_flag(today, tid, "shura"):
                if user_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！你无视了对方的修罗状态，继续执行交换~")
                elif target_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
            if get_user_flag(today, tid, "harem"):
                if user_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！你无视了对方的开后宫状态，继续执行交换~")
                elif target_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
            if get_user_flag(today, tid, "protect_from_ntr"):
                if user_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！你无视了对方的纯爱守护，继续执行交换~")
                elif target_has_equal_rights:
                    yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
        cfg = load_group_config(gid)
        for x in (uid, tid):
            wife_count = get_wife_count(cfg, x, today)
            if wife_count == 0:
                who = nick if x == uid else "对方"
                yield event.plain_result(f"{who}，今天还没有老婆，无法进行交换哦~")
                return
        # 检查是否有公交车效果（强制交换）
        force_swap = get_user_flag(today, uid, "force_swap")
        if force_swap:
            # 强制交换，直接执行
            cfg = load_group_config(gid)
            wives_u = get_wives_list(cfg, uid, today)
            wives_t = get_wives_list(cfg, tid, today)
            if wives_u and wives_t:
                # 获取用户信息
                data_u = cfg.get(uid, {})
                data_t = cfg.get(tid, {})
                nick_u = data_u.get("nick", f"用户{uid}") if isinstance(data_u, dict) else f"用户{uid}"
                nick_t = data_t.get("nick", f"用户{tid}") if isinstance(data_t, dict) else f"用户{tid}"
                # 交换老婆
                cfg[uid] = {"wives": [wives_t[0]], "date": today, "nick": nick_u}
                cfg[tid] = {"wives": [wives_u[0]], "date": today, "nick": nick_t}
                save_group_config(cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, tid])
                yield event.plain_result(f"{nick}，公交车效果发动！强制交换成功！")
                if cancel_msg:
                    yield event.plain_result(cancel_msg)
                return
        rec_lim["count"] += 1
        grp_limit[uid] = rec_lim
        save_swap_limit_records()
        grp = swap_requests.setdefault(gid, {})
        grp[uid] = {"target": tid, "date": today}
        save_swap_requests()
        yield event.chain_result(
            [
                Plain(f"{nick} 想和 "),
                At(qq=int(tid)),
                Plain(
                    " 交换老婆啦！请对方用「同意交换 @发起者」或「拒绝交换 @发起者」来回应~"
                ),
            ]
        )

    async def agree_swap_wife(self, event: AstrMessageEvent):
        # 同意交换老婆
        gid = str(event.message_obj.group_id)
        tid = str(event.get_sender_id())
        uid = self.parse_at_target(event)
        nick = event.get_sender_name()
        today = get_today()
        # 众生平等：如果发起者有众生平等，则无视发起者状态；如果同意者有众生平等，则无视同意者状态
        agreeing_has_equal_rights = get_user_flag(today, tid, "equal_rights")
        if not agreeing_has_equal_rights:
            if get_user_flag(today, tid, "shura"):
                yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法使用「同意交换」。")
                return
            # 检查同意者是否拥有开后宫效果
            if get_user_flag(today, tid, "harem"):
                yield event.plain_result(f"{nick}，开后宫状态下无法使用「同意交换」指令哦~")
                return
            # 检查同意者是否拥有纯爱战士效果
            if get_user_flag(today, tid, "protect_from_ntr"):
                yield event.plain_result(f"{nick}，纯爱战士不会使用「同意交换」指令哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语（同意者）
            if get_user_flag(today, tid, "shura"):
                yield event.plain_result(f"{nick}，众生平等！你的状态无法保护自己，继续执行同意交换~")
            if get_user_flag(today, tid, "harem"):
                yield event.plain_result(f"{nick}，众生平等！你的状态无法保护自己，继续执行同意交换~")
            if get_user_flag(today, tid, "protect_from_ntr"):
                yield event.plain_result(f"{nick}，众生平等！你的状态无法保护自己，继续执行同意交换~")
        grp = swap_requests.get(gid, {})
        rec = grp.get(uid)
        if not rec or rec.get("target") != tid:
            yield event.plain_result(
                f"{nick}，请在命令后@发起者，或用「查看交换请求」命令查看当前请求哦~"
            )
            return
        # 众生平等：如果发起者有众生平等，则无视发起者状态
        initiator_has_equal_rights = get_user_flag(today, uid, "equal_rights")
        if not initiator_has_equal_rights:
            if get_user_flag(today, uid, "shura"):
                del grp[uid]
                save_swap_requests()
                yield event.plain_result(f"{nick}，对方处于修罗状态，只能通过「牛老婆」获得新老婆，无法参与交换。")
                return
            # 检查发起者是否拥有开后宫效果（可能在发起后使用了开后宫道具）
            if get_user_flag(today, uid, "harem"):
                del grp[uid]
                save_swap_requests()
                yield event.plain_result(f"{nick}，对方已开启后宫状态，无法进行交换哦~")
                return
            # 检查发起者是否拥有纯爱战士效果（可能在发起后使用了纯爱战士道具）
            if get_user_flag(today, uid, "protect_from_ntr"):
                del grp[uid]
                save_swap_requests()
                yield event.plain_result(f"{nick}，对方已成为纯爱战士，无法进行交换哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语（发起者）
            if get_user_flag(today, uid, "shura"):
                yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
            if get_user_flag(today, uid, "harem"):
                yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
            if get_user_flag(today, uid, "protect_from_ntr"):
                yield event.plain_result(f"{nick}，众生平等！对方的状态无法保护自己，继续执行交换~")
        cfg = load_group_config(gid)
        # 检查双方是否都有老婆（支持普通用户）
        for x in (uid, tid):
            wife_count = get_wife_count(cfg, x, today)
            if wife_count == 0:
                who = nick if x == tid else "对方"
                del grp[uid]
                save_swap_requests()
                yield event.plain_result(f"{who}，今天还没有老婆，无法进行交换哦~")
                return
        # 交换老婆（只支持普通用户，因为开后宫用户已被禁止）
        wives_u = get_wives_list(cfg, uid, today)
        wives_t = get_wives_list(cfg, tid, today)
        if wives_u and wives_t:
            # 获取用户信息
            data_u = cfg.get(uid, {})
            data_t = cfg.get(tid, {})
            nick_u = data_u.get("nick", f"用户{uid}") if isinstance(data_u, dict) else f"用户{uid}"
            nick_t = data_t.get("nick", f"用户{tid}") if isinstance(data_t, dict) else f"用户{tid}"
            # 交换老婆
            cfg[uid] = {"wives": [wives_t[0]], "date": today, "nick": nick_u}
            cfg[tid] = {"wives": [wives_u[0]], "date": today, "nick": nick_t}
        save_group_config(cfg)
        del grp[uid]
        save_swap_requests()
        # 检查并取消相关交换请求
        cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, tid])
        yield event.plain_result("交换成功！你们的老婆已经互换啦，祝幸福~")
        if cancel_msg:
            yield event.plain_result(cancel_msg)

    async def reject_swap_wife(self, event: AstrMessageEvent):
        # 拒绝交换老婆
        gid = str(event.message_obj.group_id)
        tid = str(event.get_sender_id())
        uid = self.parse_at_target(event)
        nick = event.get_sender_name()
        today = get_today()
        # 检查是否拥有苦主效果（无法拒绝）
        # 众生平等：如果拒绝者有众生平等，则无视自己的状态
        rejecting_has_equal_rights = get_user_flag(today, tid, "equal_rights")
        if not rejecting_has_equal_rights:
            if get_user_flag(today, tid, "ban_reject_swap"):
                yield event.plain_result(f"{nick}，苦主无法使用「拒绝交换」指令哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语
            if get_user_flag(today, tid, "ban_reject_swap"):
                yield event.plain_result(f"{nick}，众生平等！你的状态无法保护自己，继续执行拒绝交换~")
        grp = swap_requests.get(gid, {})
        rec = grp.get(uid)
        if not rec or rec.get("target") != tid:
            yield event.plain_result(
                f"{nick}，请在命令后@发起者，或用「查看交换请求」命令查看当前请求哦~"
            )
            return
        del grp[uid]
        save_swap_requests()
        yield event.chain_result(
            [At(qq=int(uid)), Plain("，对方婉拒了你的交换请求，下次加油吧~")]
        )

    async def view_swap_requests(self, event: AstrMessageEvent):
        # 查看当前用户发起或@到自己的交换请求
        gid = str(event.message_obj.group_id)
        me = str(event.get_sender_id())
        today = get_today()
        grp = swap_requests.get(gid, {})
        cfg = load_group_config(gid)
        sent_targets = [rec["target"] for uid, rec in grp.items() if uid == me]
        received_from = [uid for uid, rec in grp.items() if rec.get("target") == me]
        if not sent_targets and not received_from:
            yield event.plain_result("你当前没有任何交换请求哦~")
            return
        parts = []
        for tid in sent_targets:
            data = cfg.get(tid, {})
            name = data.get("nick", "未知用户") if isinstance(data, dict) else "未知用户"
            parts.append(f"→ 你发起给 {name} 的交换请求")
        for uid in received_from:
            data = cfg.get(uid, {})
            name = data.get("nick", "未知用户") if isinstance(data, dict) else "未知用户"
            parts.append(f"→ {name} 发起给你的交换请求")
        text = (
            "当前交换请求如下：\n"
            + "\n".join(parts)
            + "\n请在“同意交换”或“拒绝交换”命令后@发起者进行操作~"
        )
        yield event.plain_result(text)

    async def cancel_swap_on_wife_change(self, gid, user_ids):
        # 检查并取消与user_ids相关的交换请求，返还交换次数，并返回提示文本（如有）。
        changed = False
        today = get_today()
        grp = swap_requests.get(gid, {})
        grp_limit = swap_limit_records.setdefault(gid, {})
        to_cancel = []
        for req_uid, req in grp.items():
            if req_uid in user_ids or req.get("target") in user_ids:
                to_cancel.append(req_uid)
        for req_uid in to_cancel:
            # 返还次数
            rec_lim = grp_limit.get(req_uid, {"date": "", "count": 0})
            if rec_lim.get("date") == today and rec_lim.get("count", 0) > 0:
                rec_lim["count"] = max(0, rec_lim["count"] - 1)
                grp_limit[req_uid] = rec_lim
                changed = True
            del grp[req_uid]
        if to_cancel:
            save_swap_requests()
        if changed:
            save_swap_limit_records()
        if to_cancel:
            return "检测到老婆变更，已自动取消相关交换请求并返还次数~"
        return None

    async def select_wife(self, event: AstrMessageEvent):
        # 选老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        # 检查使用次数
        uses = int(get_user_mod(today, uid, "select_wife_uses", 0))
        if uses <= 0:
            yield event.plain_result(f"{nick}，你今天还没有「选老婆」的使用次数，快去使用道具卡获得吧~")
            return
        if get_user_flag(today, uid, "shura"):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法使用「选老婆」。")
            return
        # 解析关键词
        msg = event.message_str.strip()
        parts = msg.split(maxsplit=1)
        if len(parts) < 2:
            yield event.plain_result(f"{nick}，请发送「选老婆 XXX」格式，XXX为关键词哦~")
            return
        keyword = parts[1].strip()
        if not keyword:
            yield event.plain_result(f"{nick}，关键词不能为空哦~")
            return
        # 消耗使用次数
        add_user_mod(today, uid, "select_wife_uses", -1)
        # 筛选卡池
        cfg = load_group_config(gid)
        local_imgs = os.listdir(IMG_DIR)
        filtered_imgs = []
        if local_imgs:
            keyword_lower = keyword.lower()
            filtered_imgs = [
                img_name for img_name in local_imgs
                if keyword_lower in img_name.lower()
            ]
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.image_base_url) as resp:
                        text = await resp.text()
                        all_imgs = text.splitlines()
                        keyword_lower = keyword.lower()
                        filtered_imgs = [
                            img_name for img_name in all_imgs
                            if keyword_lower in img_name.lower()
                        ]
            except:
                yield event.plain_result("抱歉，今天的老婆获取失败了，请稍后再试~")
                return
        if not filtered_imgs:
            yield event.plain_result(f"{nick}，没有找到包含「{keyword}」的老婆，换个关键词试试吧~")
            return
        # 随机选择一个
        img = random.choice(filtered_imgs)
        # 检查是否开后宫
        is_harem = get_user_flag(today, uid, "harem")
        if not add_wife(cfg, uid, img, today, nick, is_harem):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
            return
        save_group_config(cfg)
        # 检查露出状态：如果用户有露出状态且处于开后宫状态，当老婆数量达到2个及以上时触发修罗场
        triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
        if triggered:
            # 触发修罗场后获得一次抽老婆（换老婆）机会
            add_user_mod(today, uid, "change_extra_uses", 1)
            yield event.plain_result(f"{nick}，你选择了新老婆！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
            return
        # 解析出处和角色名
        name = os.path.splitext(img)[0]
        if "!" in name:
            source, chara = name.split("!", 1)
            text = f"{nick}，你选择了来自《{source}》的{chara}作为你的老婆，请好好珍惜哦~"
        else:
            text = f"{nick}，你选择了{name}作为你的老婆，请好好珍惜哦~"
        image_component = self._build_image_component(img)
        if image_component:
            yield event.chain_result([Plain(text), image_component])
        else:
            yield event.plain_result(text)

    async def beat_wife(self, event: AstrMessageEvent):
        # 打老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        # 检查使用次数
        uses = int(get_user_mod(today, uid, "beat_wife_uses", 0))
        if uses <= 0:
            yield event.plain_result(f"{nick}，你今天还没有「打老婆」的使用次数，快去使用道具卡获得吧~")
            return
        # 检查是否有老婆
        cfg = load_group_config(gid)
        wife_count = get_wife_count(cfg, uid, today)
        if wife_count == 0:
            yield event.plain_result(f"{nick}，你还没有老婆，无法使用「打老婆」指令哦~")
            return
        # 消耗使用次数
        add_user_mod(today, uid, "beat_wife_uses", -1)
        has_landmine = get_user_flag(today, uid, "landmine_girl")
        # 30% 概率失去所有老婆（病娇效果免疫）
        if not has_landmine and self._probability_check(0.3, today, uid):
            if uid in cfg:
                del cfg[uid]
                save_group_config(cfg)
                self._handle_wife_loss(today, uid, wife_count, gid)
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid])
            yield event.plain_result(f"{nick}，你下手太狠了，老婆伤心地离开了你......你失去了所有老婆。")
            if cancel_msg:
                yield event.plain_result(cancel_msg)
            return
        # 根据是否拥有病娇效果选择不同的事件
        if has_landmine:
            joy_lines = [
                "她甜甜地笑着说：“就喜欢你这种坏坏的温柔~”",
                "老婆眯起眼靠在你怀里：“再打一点点，我好开心！”",
                "她轻声耳语：“被你疼爱的时候，心里像开了花一样。”",
                "老婆握住你的手：“病娇上线！奖励亲亲三十秒~”",
                "她娇羞地说道：“太舒服了，再来一次嘛~”",
                "老婆欢快地转圈：“被你打的感觉，好像恋爱升级了！”",
                "她眼里泛着星光：“再多一点力气，我还想要！”",
                "老婆抱着你大笑：“今天的我，是你的快乐小抱枕！”",
                "她俏皮地眨眼：“嗯哼，惩罚就是享受哦！”",
                "老婆踮脚亲你：“奖励你今晚独享我的撒娇时间！”",
            ]
            text = random.choice(joy_lines)
            yield event.plain_result(f"{nick}，你打了老婆...\n{text}")
        else:
            pain_lines = [
                "呜呜呜...为什么要这样对我...",
                "好痛...但是...如果是你的话...",
                "不要...求求你...",
                "为什么...为什么要伤害我...",
                "我...我做错了什么吗...",
                "好痛...但是...我不会离开你的...",
                "为什么...为什么要这样...",
                "我...我到底做错了什么...",
                "不要...求求你不要这样...",
                "好痛...但是...如果是你的话...我愿意...",
                "为什么...为什么要伤害我...我明明那么爱你...",
                "我...我做错了什么吗...为什么要这样对我...",
                "不要...求求你...我真的好痛...",
                "为什么...为什么要这样对我...我明明那么爱你...",
                "好痛...但是...如果是你的话...我愿意承受...",
                "我...我到底做错了什么...为什么要这样...",
                "不要...求求你不要这样...我真的好痛...",
                "为什么...为什么要伤害我...我明明那么爱你...",
                "好痛...但是...如果是你的话...我愿意承受这一切...",
                "我...我做错了什么吗...为什么要这样对我...我真的好痛...",
            ]
            pain_text = random.choice(pain_lines)
            yield event.plain_result(f"{nick}，你打了老婆...\n{pain_text}")

    async def seduce(self, event: AstrMessageEvent):
        # 勾引主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        if get_user_flag(today, uid, "shura"):
            yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法使用「勾引」。")
            return
        # 检查使用次数（-1表示无限）
        uses = int(get_user_mod(today, uid, "seduce_uses", 0))
        if uses == 0:
            yield event.plain_result(f"{nick}，你今天还没有「勾引」的使用次数，快去使用道具卡获得吧~")
            return
        # 检查是否无限使用（熊出没效果）
        is_unlimited = (uses == -1)
        
        # 解析目标
        target_uid = self.parse_at_target(event)
        if not target_uid or target_uid == uid:
            msg = "请@你想勾引的对象哦~" if not target_uid else "不能勾引自己呀，换个人试试吧~"
            yield event.plain_result(f"{nick}，{msg}")
            return
        target_uid = str(target_uid)
        # 众生平等：无视目标状态（使用者有众生平等 或 目标有众生平等）
        user_has_equal_rights = get_user_flag(today, uid, "equal_rights")
        target_has_equal_rights = get_user_flag(today, target_uid, "equal_rights")
        if not user_has_equal_rights and not target_has_equal_rights:
            # 检查目标是否受保护（纯爱战士、贤者时间、雄竞效果）
            if get_user_flag(today, target_uid, "protect_from_ntr"):
                yield event.plain_result("对方是纯爱战士，不受勾引影响哦~")
                return
            if get_user_flag(today, target_uid, "ban_items"):
                yield event.plain_result("对方处于贤者时间，不受勾引影响哦~")
                return
            if get_user_meta(today, target_uid, "competition_target", None):
                yield event.plain_result("对方处于雄竞状态，不受勾引影响哦~")
                return
        else:
            # 众生平等状态：豁免保护，显示特殊提示语
            if get_user_flag(today, target_uid, "protect_from_ntr"):
                if user_has_equal_rights:
                    yield event.plain_result("众生平等！你无视了对方的纯爱守护，继续执行勾引~")
                elif target_has_equal_rights:
                    yield event.plain_result("众生平等！对方的状态无法保护自己，继续执行勾引~")
            if get_user_flag(today, target_uid, "ban_items"):
                if user_has_equal_rights:
                    yield event.plain_result("众生平等！你无视了对方的贤者时间，继续执行勾引~")
                elif target_has_equal_rights:
                    yield event.plain_result("众生平等！对方的状态无法保护自己，继续执行勾引~")
            if get_user_meta(today, target_uid, "competition_target", None):
                if user_has_equal_rights:
                    yield event.plain_result("众生平等！你无视了对方的雄竞状态，继续执行勾引~")
                elif target_has_equal_rights:
                    yield event.plain_result("众生平等！对方的状态无法保护自己，继续执行勾引~")
        
        # 检查每10分钟最多使用3次的限制（在通过所有基本检查后）
        now = datetime.utcnow().timestamp()
        ten_minutes_ago = now - 600  # 10分钟 = 600秒
        user_records = seduce_records.setdefault(uid, [])
        # 清理10分钟之前的时间戳
        user_records = [ts for ts in user_records if ts > ten_minutes_ago]
        seduce_records[uid] = user_records
        
        # 检查最近10分钟内的使用次数
        if len(user_records) >= 3:
            # 计算还需要等待的时间
            oldest_record = min(user_records)
            wait_seconds = int(600 - (now - oldest_record))
            wait_minutes = wait_seconds // 60
            wait_secs = wait_seconds % 60
            if wait_minutes > 0:
                wait_text = f"{wait_minutes}分{wait_secs}秒"
            else:
                wait_text = f"{wait_secs}秒"
            yield event.plain_result(f"{nick}，你已力竭！请等待{wait_text}后再试~")
            return
        
        # 记录本次使用时间（在通过所有检查后）
        user_records.append(now)
        seduce_records[uid] = user_records
        save_seduce_records()
        
        if not is_unlimited:
            # 消耗使用次数
            add_user_mod(today, uid, "seduce_uses", -1)
        # 熊出没效果：25%概率被禁言120秒
        if is_unlimited:
            if self._probability_check(0.25, today, uid):
                try:
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=120)
                except:
                    pass
                yield event.plain_result(f"{nick}，勾引失败！你被禁言120秒......")
                return
        # 30%概率成功（穷凶极恶效果：正面概率加成变为125%）
        base_prob = 0.3
        if get_user_flag(today, uid, "extreme_evil"):
            base_prob = base_prob * 1.25
            base_prob = min(0.9, base_prob)  # 概率上限为90%
        if self._probability_check(base_prob, today, uid):
            cfg = load_group_config(gid)
            img = get_avatar_url(target_uid)
            is_harem = get_user_flag(today, uid, "harem")
            if not add_wife(cfg, uid, img, today, nick, is_harem):
                yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
                return
            save_group_config(cfg)
            # 检查露出状态：如果用户有露出状态且处于开后宫状态，当老婆数量达到2个及以上时触发修罗场
            triggered, wife_count = self._check_exhibitionist_chaos(today, uid, gid, cfg)
            if triggered:
                # 触发修罗场后获得一次抽老婆（换老婆）机会
                add_user_mod(today, uid, "change_extra_uses", 1)
                yield event.plain_result(f"{nick}，勾引成功！但因为你处于露出状态，修罗场爆发！你失去了所有老婆......但获得了一次抽老婆的机会。")
                return
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
            msg = f"{nick}，勾引成功！对方已经拜倒在你的脂包肌下了。"
            if cancel_msg:
                msg += f"\n{cancel_msg}"
            yield event.plain_result(msg)
        else:
            yield event.plain_result(f"{nick}，勾引失败！对方没有注意到你，下次再试试吧~")

    async def reset_basics(self, event: AstrMessageEvent):
        # 重开：清空目标今日的所有数据，仅管理员可用
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        # 检查管理员权限
        if uid not in self.admins:
            yield event.plain_result(f"{nick}，仅管理员才能使用「重开」指令哦~")
            return
        # 解析目标
        target_uid = self.parse_at_target(event)
        if not target_uid:
            yield event.plain_result(f"{nick}，请@你想清空数据的目标用户哦~")
            return
        target_uid = str(target_uid)
        # 先获取目标用户昵称（在清空数据之前）
        target_nick = "目标用户"
        try:
            target_cfg = load_group_config(gid)
            if target_uid in target_cfg:
                target_nick = target_cfg[target_uid].get("nick", "目标用户")
        except:
            pass
        # 清空今日效果数据
        if today in effects_data and target_uid in effects_data[today]:
            del effects_data[today][target_uid]
        # 清空今日道具数据
        if today in item_data and target_uid in item_data[today]:
            lost_items = len(item_data[today][target_uid])
            del item_data[today][target_uid]
            if lost_items:
                self._handle_item_loss(today, target_uid, lost_items, gid)
        # 清空老婆数据
        cfg = load_group_config(gid)
        loss = get_wife_count(cfg, target_uid, today)
        if target_uid in cfg:
            del cfg[target_uid]
            save_group_config(cfg)
            self._handle_wife_loss(today, target_uid, loss, gid)
        # 清空牛老婆记录（如果日期是今天）
        if gid in ntr_records and target_uid in ntr_records[gid]:
            rec = ntr_records[gid][target_uid]
            if rec.get("date") == today:
                del ntr_records[gid][target_uid]
        # 清空换老婆记录（如果日期是今天）
        if gid in change_records and target_uid in change_records[gid]:
            rec = change_records[gid][target_uid]
            if rec.get("date") == today:
                del change_records[gid][target_uid]
        # 清空交换请求
        if gid in swap_requests and target_uid in swap_requests[gid]:
            del swap_requests[gid][target_uid]
        # 清空选老婆记录
        if today in select_wife_records and target_uid in select_wife_records[today]:
            del select_wife_records[today][target_uid]
        # 清空打老婆记录
        if today in beat_wife_records and target_uid in beat_wife_records[today]:
            del beat_wife_records[today][target_uid]
        # 清空重置盲盒记录（如果日期是今天）
        if today in reset_blind_box_records and target_uid in reset_blind_box_records[today]:
            del reset_blind_box_records[today][target_uid]
        # 清空交换限制记录（如果日期是今天）
        if gid in swap_limit_records and target_uid in swap_limit_records[gid]:
            rec_lim = swap_limit_records[gid][target_uid]
            if rec_lim.get("date") == today:
                del swap_limit_records[gid][target_uid]
        # 保存所有修改
        save_effects()
        save_item_data()
        save_ntr_records()
        save_change_records()
        save_swap_requests()
        save_select_wife_records()
        save_beat_wife_records()
        save_reset_blind_box_records()
        save_swap_limit_records()
        yield event.plain_result(f"{nick}，已清空{target_nick}今日的所有数据（效果、道具、老婆、记录等）")

    def _load_image_pool(self):
        image_pool = []
        try:
            if os.path.exists(IMG_DIR):
                image_pool = [
                    f
                    for f in os.listdir(IMG_DIR)
                    if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
                ]
        except:
            image_pool = []
        return image_pool

    def _ensure_unique_wife_name(self, base_name, used_names):
        if base_name not in used_names:
            used_names.add(base_name)
            return base_name
        idx = 1
        while True:
            candidate = f"{base_name}({idx})"
            if candidate not in used_names:
                used_names.add(candidate)
                return candidate
            idx += 1

    def _generate_market_wives(self, count, existing_names=None, exclude_images=None):
        if count <= 0:
            return []
        used_names = set(existing_names or [])
        excluded = set(exclude_images or [])
        image_pool = self._load_image_pool()
        available = [img for img in image_pool if img not in excluded]
        if not available:
            available = list(image_pool)
        if not available:
            return []
        if len(available) >= count:
            selection = random.sample(available, count)
        else:
            selection = available[:]
            while len(selection) < count and image_pool:
                selection.append(random.choice(image_pool))
        processed = []
        for wife_img in selection:
            name = os.path.splitext(wife_img)[0]
            if "!" in name:
                _, chara = name.split("!", 1)
                base_name = chara
            else:
                base_name = name
            display_name = self._ensure_unique_wife_name(base_name, used_names)
            processed.append({"img": wife_img, "name": display_name})
        return processed

    def _generate_market_items(self, count, exclude_items=None):
        if count <= 0:
            return []
        excluded = set(exclude_items or [])
        available = [item for item in self.item_pool if item not in excluded]
        if not available:
            available = list(self.item_pool)
        if not available:
            return []
        if len(available) >= count:
            return random.sample(available, count)
        selection = available[:]
        while len(selection) < count and self.item_pool:
            selection.append(random.choice(self.item_pool))
        return selection

    def _ensure_market_available(self, today: str) -> bool:
        if today not in market_data or not market_data[today]:
            return self._refresh_market(today)
        return True
    
    def _get_gift_group_entry(self, today: str, gid: str):
        cleanup_gift_requests()
        day_entry = gift_requests.setdefault(today, {})
        group_entry = day_entry.setdefault(gid, {"donations": {}, "demands": {}})
        return group_entry
    
    def _cleanup_gift_entry(self, today: str, gid: str):
        day_entry = gift_requests.get(today)
        if not day_entry:
            save_gift_requests()
            return
        group_entry = day_entry.get(gid)
        if group_entry:
            if not group_entry.get("donations") and not group_entry.get("demands"):
                del day_entry[gid]
        if not day_entry:
            gift_requests.pop(today, None)
        save_gift_requests()

    def _grant_lightbulb_bonus(self, today: str, gid: str, action: str):
        day_effects = effects_data.get(today, {})
        if not day_effects:
            return
        bonus_key = "change_extra_uses" if action == "change" else "ntr_extra_uses"
        for lamp_uid, eff in day_effects.items():
            if lamp_uid == "__groups__":
                continue
            flags = eff.get("flags", {})
            if not flags.get("lightbulb"):
                continue
            meta = eff.get("meta", {})
            if meta.get("lightbulb_group") != gid:
                continue
            add_user_mod(today, lamp_uid, bonus_key, 1)

    def _adjust_probability(self, prob: float, today: str, uid: str) -> float:
        adjusted = clamp_probability(prob)
        # 幸运E效果：概率减半但不低于20%
        if get_user_flag(today, uid, "lucky_e"):
            adjusted = max(0.2, adjusted * 0.5)
        
        # 超吉效果：若用户有超吉状态且老婆中有今日吉星，概率加成变为120%
        if get_user_flag(today, uid, "super_lucky"):
            # 从全局老婆数据获取用户的老婆列表
            user_record = wives_data.get(uid, {})
            wives = user_record.get("wives", []) if isinstance(user_record, dict) else []
            fortune = get_user_fortune(today, uid)
            lucky_star = fortune.get("lucky_star", "")
            # 检查老婆中是否有今日吉星
            has_lucky_star_wife = False
            for wife_img in wives:
                if wife_img.startswith("http"):
                    continue  # QQ头像跳过
                base = os.path.splitext(os.path.basename(wife_img))[0]
                if "!" in base:
                    _, chara = base.split("!", 1)
                    if chara == lucky_star:
                        has_lucky_star_wife = True
                        break
                else:
                    if base == lucky_star:
                        has_lucky_star_wife = True
                        break
            
            if has_lucky_star_wife:
                # 概率加成变为120%
                adjusted = adjusted * 1.20
                # 如果用户有幸运E，确保最低20%
                if get_user_flag(today, uid, "lucky_e"):
                    adjusted = max(0.2, adjusted)
                return clamp_probability(adjusted)
        
        # 运势影响：在所有计算之后，以4颗星（中平）为基准，每多/少一颗星，概率乘以1±0.05
        # 但幸运E需保证最低20%
        fortune = get_user_fortune(today, uid)
        stars = fortune.get("stars", 4)
        star_diff = stars - 4  # 与中平的差值
        fortune_multiplier = 1.0 + (star_diff * 0.05)
        adjusted = adjusted * fortune_multiplier
        # 如果用户有幸运E，确保最低20%
        if get_user_flag(today, uid, "lucky_e"):
            adjusted = max(0.2, adjusted)
        return clamp_probability(adjusted)

    def _probability_check(self, prob: float, today: str, uid: str) -> bool:
        adjusted = self._adjust_probability(prob, today, uid)
        return random.random() < adjusted

    def _refresh_market(self, today: str):
        """刷新当日集市数据"""
        selected_wives = self._generate_market_wives(self.market_max_wives)
        if self.market_max_wives > 0 and not selected_wives:
            return False
        selected_items = self._generate_market_items(self.market_max_items)
        
        # 保存集市数据
        market_data[today] = {
            "wives": selected_wives,
            "items": selected_items
        }
        save_market_data()
        return True

    async def show_market(self, event: AstrMessageEvent):
        """显示老婆集市"""
        today = get_today()
        nick = event.get_sender_name()
        
        # 检查是否有当日数据，如果没有则刷新
        if today not in market_data or not market_data[today]:
            if not self._refresh_market(today):
                yield event.plain_result(f"{nick}，集市暂时无法打开，请稍后再试~")
                return
        
        market = market_data[today]
        wives = market.get("wives", [])
        items = market.get("items", [])
        
        if not wives and not items:
            if not self._refresh_market(today):
                yield event.plain_result(f"{nick}，集市暂时无法打开，请稍后再试~")
                return
            market = market_data[today]
            wives = market.get("wives", [])
            items = market.get("items", [])
        
        # 生成集市图片
        try:
            img = self._generate_market_image(wives, items)
            temp_path = os.path.join(PLUGIN_DIR, f"market_{today}.png")
            img.save(temp_path)
            yield event.chain_result([Plain(f"{nick}，今日老婆集市："), AstrImage.fromFileSystem(temp_path)])
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception as e:
            # 如果生成图片失败，回退到文字形式
            lines = ["【老婆集市】"]
            if wives:
                lines.append("【老婆】")
                for i, wife in enumerate(wives, 1):
                    lines.append(f"{i}. {wife['name']}")
            if items:
                lines.append("【道具卡】")
                for i, item in enumerate(items, 1):
                    lines.append(f"{i}. {item}")
            msg = f"{nick}，今日老婆集市：\n" + "\n".join(lines)
            yield event.plain_result(msg)

    def _generate_market_image(self, wives: list, items: list):
        """生成集市图片"""
        width = 1200
        padding = 20
        slot_cols = 8
        slot_gap = 20
        slot_width = (width - padding * 2 - slot_gap * (slot_cols - 1)) // slot_cols
        slot_height = max(180, int(slot_width * 1.25))
        max_wife_display = slot_cols * 2
        display_wives = wives[:max_wife_display]
        display_items = items[:slot_cols]
        wife_rows = (len(display_wives) + slot_cols - 1) // slot_cols if display_wives else 0
        item_rows = (len(display_items) + slot_cols - 1) // slot_cols if display_items else 0
        gap = 30
        
        # 尝试加载字体
        try:
            title_font = ImageFont.truetype("msyh.ttc", 24)
            text_font = ImageFont.truetype("msyh.ttc", 16)
        except:
            try:
                title_font = ImageFont.truetype("arial.ttf", 24)
                text_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
        wife_row_gap = 30
        item_row_gap = 20

        def _calc_line_height(font: ImageFont.ImageFont) -> int:
            try:
                bbox = font.getbbox("字")
                return max(18, (bbox[3] - bbox[1]) + 4)
            except:
                try:
                    size = font.getsize("字")
                    return max(18, size[1] + 4)
                except:
                    return 20

        line_height = _calc_line_height(text_font)
        max_wife_lines = 2
        max_item_lines = 2
        wife_text_height = line_height * max_wife_lines
        item_text_height = line_height * max_item_lines
        wife_section_height = 0 if wife_rows == 0 else wife_rows * (slot_height + wife_text_height) + max(0, wife_rows - 1) * wife_row_gap
        item_section_height = 0 if item_rows == 0 else item_rows * item_text_height + max(0, item_rows - 1) * item_row_gap
        
        # 计算总高度
        title_height = 40
        wife_title_height = 30
        item_title_height = 30
        total_height = (
            padding
            + title_height
            + (wife_title_height + wife_section_height if wife_rows else 0)
            + (gap if wife_rows and item_rows else 0)
            + (item_title_height + item_section_height if item_rows else 0)
            + padding
        )
        
        # 创建图片
        img = PILImage.new('RGB', (width, total_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        def _measure_text_width(text: str) -> int:
            if not text:
                return 0
            try:
                bbox = text_font.getbbox(text)
                return bbox[2] - bbox[0]
            except:
                try:
                        return text_font.getsize(text)[0]
                except:
                        return len(text) * 10

        def _wrap_text(text: str, max_width: int, max_lines: int) -> list[str]:
            if not text:
                return [""]
            lines: list[str] = []
            idx = 0
            length = len(text)
            while idx < length and len(lines) < max_lines:
                end = idx + 1
                last_valid = idx
                while end <= length:
                    segment = text[idx:end]
                    if _measure_text_width(segment) <= max_width:
                        last_valid = end
                        end += 1
                        continue
                    break
                if last_valid == idx:
                    last_valid = min(idx + 1, length)
                lines.append(text[idx:last_valid])
                idx = last_valid
            if idx < length and lines:
                ellipsis = "..."
                truncated = lines[-1]
                while truncated and _measure_text_width(truncated + ellipsis) > max_width:
                    truncated = truncated[:-1]
                lines[-1] = (truncated + ellipsis) if truncated else ellipsis
            return lines or [text]
        
        # 绘制标题
        title_text = "老婆集市"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, padding), title_text, fill=(0, 0, 0), font=title_font)
        
        # 绘制老婆部分
        current_y = padding + 40
        if wife_rows:
            draw.text((padding, current_y), "【老婆】", fill=(70, 130, 180), font=text_font)
            current_y += wife_title_height
            for idx, wife in enumerate(display_wives):
                row = idx // slot_cols
                col = idx % slot_cols
                x = padding + col * (slot_width + slot_gap)
                y = current_y + row * (slot_height + wife_text_height + wife_row_gap)
                wife_img_path = os.path.join(IMG_DIR, wife["img"])
                try:
                    if os.path.exists(wife_img_path):
                        wife_img = PILImage.open(wife_img_path)
                        wife_img = wife_img.resize((slot_width, slot_height), PILImage.Resampling.LANCZOS)
                        img.paste(wife_img, (x, y))
                except:
                    pass
                name_lines = _wrap_text(wife["name"], slot_width, max_wife_lines)
                for line_idx, text_line in enumerate(name_lines):
                    line_width = _measure_text_width(text_line)
                    text_x = x + (slot_width - line_width) // 2
                    text_y = y + slot_height + 5 + line_idx * line_height
                    draw.text((text_x, text_y), text_line, fill=(50, 50, 50), font=text_font)
            current_y += wife_section_height
        
        # 绘制道具卡部分
        if item_rows:
            if wife_rows:
                current_y += gap
            draw.text((padding, current_y), "【道具卡】", fill=(70, 130, 180), font=text_font)
            current_y += item_title_height
            for idx, item in enumerate(display_items):
                row = idx // slot_cols
                col = idx % slot_cols
                x = padding + col * (slot_width + slot_gap)
                y = current_y + row * (item_text_height + item_row_gap)
                item_lines = _wrap_text(item, slot_width, max_item_lines)
                for line_idx, text_line in enumerate(item_lines):
                    line_width = _measure_text_width(text_line)
                    text_x = x + (slot_width - line_width) // 2
                    text_y = y + line_idx * line_height
                    draw.text((text_x, text_y), text_line, fill=(50, 50, 50), font=text_font)
        
        return img

    async def purchase_from_market(self, event: AstrMessageEvent):
        """从集市购买"""
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        gid = str(event.message_obj.group_id)
        
        # 检查是否有当日集市数据
        if today not in market_data or not market_data[today]:
            if not self._refresh_market(today):
                yield event.plain_result(f"{nick}，集市暂时无法打开，请稍后再试~")
                return
        
        # 解析购买内容
        text = event.message_str.strip()
        content = text[len("购买"):].strip()
        if not content:
            yield event.plain_result(f"{nick}，请在「购买」后写上要购买的老婆名或道具名哦~")
            return
        
        market = market_data[today]
        wives = market.get("wives", [])
        items = market.get("items", [])
        user_history = self._ensure_market_history(today, uid)
        
        # 查找匹配的老婆或道具
        purchased = None
        purchase_type = None
        
        # 先查找老婆（支持部分匹配）
        for wife in wives:
            if content in wife["name"] or wife["name"] in content:
                purchased = wife
                purchase_type = "wife"
                break
        
        # 如果没找到老婆，查找道具
        if not purchased:
            for item in items:
                if content == item or content in item:
                    purchased = item
                    purchase_type = "item"
                    break
        
        if not purchased:
            yield event.plain_result(f"{nick}，集市中没有找到「{content}」，请检查名称是否正确~")
            return

        if not self._consume_market_purchase_quota(today, uid, purchase_type, len(user_history)):
            yield event.plain_result(f"{nick}，你今天的集市购买次数已经用完啦，明天再来吧~")
            return
        
        # 执行购买
        cfg = load_group_config(gid)
        if purchase_type == "wife":
            if get_user_flag(today, uid, "shura"):
                yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆，无法在集市购买老婆。")
                return
            # 购买老婆
            wife_img = purchased["img"]
            is_harem = get_user_flag(today, uid, "harem")
            if not add_wife(cfg, uid, wife_img, today, nick, is_harem):
                yield event.plain_result(f"{nick}，修罗状态下只能通过「牛老婆」获得新老婆。")
                return
            save_group_config(cfg)
            
            # 从集市下架该老婆
            try:
                market["wives"].remove(purchased)
            except ValueError:
                market["wives"] = [w for w in market.get("wives", []) if w.get("img") != wife_img]
            save_market_data()
            
            # 记录购买
            entry = {
                "type": "wife",
                "name": purchased["name"],
                "img": wife_img
            }
            user_history.append(entry)
            save_market_purchase_records()
            
            # 显示结果
            name = purchased["name"]
            image_component = self._build_image_component(wife_img)
            if image_component:
                yield event.chain_result([Plain(f"{nick}，购买成功！你获得了老婆：{name}"), image_component])
            else:
                yield event.plain_result(f"{nick}，购买成功！你获得了老婆：{name}")
        else:
            # 购买道具
            item_name = purchased
            today_items = item_data.setdefault(today, {})
            user_items = today_items.setdefault(uid, [])
            user_items.append(item_name)
            save_item_data()
            
            # 从集市下架该道具
            if item_name in market.get("items", []):
                market["items"].remove(item_name)
                save_market_data()
            
            # 记录购买
            entry = {
                "type": "item",
                "name": item_name
            }
            user_history.append(entry)
            save_market_purchase_records()
            
            yield event.plain_result(f"{nick}，购买成功！你获得了道具卡：{item_name}")
        
        # 顺手的事：购买后触发
        async for res in self._handle_light_fingers_on_market(today, uid, event, market):
            yield res

    async def show_fortune(self, event: AstrMessageEvent):
        """显示今日运势"""
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        
        # 获取运势（如果不存在会自动生成）
        fortune = get_user_fortune(today, uid)
        
        # 生成运势图片
        try:
            img = self._generate_fortune_image(fortune)
            temp_path = os.path.join(PLUGIN_DIR, f"fortune_{today}_{uid}.png")
            img.save(temp_path)
            yield event.chain_result([AstrImage.fromFileSystem(temp_path)])
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception as e:
            # 如果生成图片失败，回退到文字形式
            fortune_type = fortune.get("type", "中平")
            stars = fortune.get("stars", 4)
            proverb = fortune.get("proverb", "")
            dos = fortune.get("dos", [])
            donts = fortune.get("donts", [])
            
            star_text = "★" * stars + "☆" * (7 - stars)
            lines = [
                f"{nick}，您的今日运势为：{fortune_type}+{star_text}",
                f"{proverb}",
                "",
                "宜：" + "、".join(dos) if dos else "宜：保持现状",
                "忌：" + "、".join(donts) if donts else "忌：无",
            ]
            yield event.plain_result("\n".join(lines))

    def _generate_fortune_image(self, fortune: dict) -> PILImage.Image:
        """生成运势图片"""
        width = 800
        padding = 30
        
        # 尝试加载字体（增大字体以增加内容占比）
        try:
            title_font = ImageFont.truetype("msyh.ttc", 40)
            large_font = ImageFont.truetype("msyh.ttc", 32)
            text_font = ImageFont.truetype("msyh.ttc", 24)
            small_font = ImageFont.truetype("msyh.ttc", 18)
        except:
            try:
                title_font = ImageFont.truetype("arial.ttf", 40)
                large_font = ImageFont.truetype("arial.ttf", 32)
                text_font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                large_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
        
        # 先计算所有内容的高度
        current_y = padding
        
        # 标题高度
        current_y += 60
        
        # 运势类型高度
        current_y += 60
        
        # 星级高度
        current_y += 70
        
        # 谚语高度（估算，因为此时draw对象还未创建）
        proverb = fortune.get("proverb", "")
        if proverb:
            max_width = width - padding * 2
            words = proverb.split(",")
            lines = []
            current_line = ""
            # 使用临时字体对象估算文本宽度
            try:
                temp_font = ImageFont.truetype("msyh.ttc", 24)
            except:
                try:
                    temp_font = ImageFont.truetype("arial.ttf", 24)
                except:
                    temp_font = ImageFont.load_default()
            
            for word in words:
                test_line = current_line + ("," if current_line else "") + word
                try:
                    test_bbox = temp_font.getbbox(test_line) if hasattr(temp_font, 'getbbox') else temp_font.getsize(test_line)
                    if hasattr(temp_font, 'getbbox'):
                        test_width = test_bbox[2] - test_bbox[0]
                    else:
                        test_width = test_bbox[0]
                except:
                    # 估算：每个字符约14像素（24号字体）
                    test_width = len(test_line) * 14
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            current_y += len(lines) * 40 + 30
        else:
            current_y += 30
        
        # 老婆图片高度
        wife_img_name = fortune.get("wife_img")
        wife_img_height = 0
        if wife_img_name:
            wife_img_path = os.path.join(IMG_DIR, wife_img_name)
            if os.path.exists(wife_img_path):
                try:
                    temp_img = PILImage.open(wife_img_path)
                    max_img_height = 320  # 稍微增大图片
                    img_width, img_height = temp_img.size
                    scale = min(1.0, max_img_height / img_height, (width - padding * 2) / img_width)
                    wife_img_height = int(img_height * scale)
                    current_y += wife_img_height + 30
                except:
                    pass
        
        # 吉星文字高度
        if wife_img_height > 0:
            current_y += 45
        
        # 建议高度
        dos = fortune.get("dos", [])
        donts = fortune.get("donts", [])
        if dos:
            current_y += 45
        if donts:
            current_y += 45
        
        current_y += 30
        
        # 免责声明高度
        current_y += 30
        current_y += 30
        
        # 按钮高度
        button_height = 45
        current_y += button_height + padding
        
        # 根据内容高度创建图片
        height = current_y
        
        # 创建图片
        img = PILImage.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        current_y = padding
        
        # 绘制标题
        title_text = "您的今日运势为:"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, current_y), title_text, fill=(0, 0, 0), font=title_font)
        current_y += 60
        
        # 绘制运势类型
        fortune_type = fortune.get("type", "中平")
        fortune_text = fortune_type
        # 添加额外标签（如果有）
        stars = fortune.get("stars", 4)
        if stars >= 6:
            fortune_text += "+官运+财运+才艺"
        elif stars >= 5:
            fortune_text += "+财运"
        elif stars <= 2:
            fortune_text += "+破财+阻碍"
        
        fortune_bbox = draw.textbbox((0, 0), fortune_text, font=large_font)
        fortune_width = fortune_bbox[2] - fortune_bbox[0]
        draw.text(((width - fortune_width) // 2, current_y), fortune_text, fill=(0, 0, 0), font=large_font)
        current_y += 60
        
        # 绘制星级
        star_count = stars
        star_text = "★" * star_count + "☆" * (7 - star_count)
        star_bbox = draw.textbbox((0, 0), star_text, font=large_font)
        star_width = star_bbox[2] - star_bbox[0]
        draw.text(((width - star_width) // 2, current_y), star_text, fill=(0, 0, 0), font=large_font)
        current_y += 70
        
        # 绘制谚语
        proverb = fortune.get("proverb", "")
        if proverb:
            # 计算文本宽度，如果太宽则换行
            max_width = width - padding * 2
            words = proverb.split(",")
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + ("," if current_line else "") + word
                test_bbox = draw.textbbox((0, 0), test_line, font=text_font)
                test_width = test_bbox[2] - test_bbox[0]
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=text_font)
                line_width = line_bbox[2] - line_bbox[0]
                draw.text(((width - line_width) // 2, current_y), line, fill=(50, 50, 50), font=text_font)
                current_y += 40
        current_y += 30
        
        # 绘制老婆图片（缩小图片占比，增加内容占比）
        wife_img_path = None
        wife_img_name = fortune.get("wife_img")
        if wife_img_name:
            wife_img_path = os.path.join(IMG_DIR, wife_img_name)
        
        if wife_img_path and os.path.exists(wife_img_path):
            try:
                wife_img = PILImage.open(wife_img_path)
                # 计算图片尺寸（居中，最大高度320，稍微增大图片）
                max_img_height = 320
                img_width, img_height = wife_img.size
                scale = min(1.0, max_img_height / img_height, (width - padding * 2) / img_width)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                wife_img = wife_img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                
                img_x = (width - new_width) // 2
                img_y = current_y
                img.paste(wife_img, (img_x, img_y))
                current_y += new_height + 30
                
                # 在老婆图片下方显示"今日吉星：【老婆名】"
                # 从fortune数据获取，如果没有则从图片文件名提取
                lucky_star = fortune.get("lucky_star")
                if not lucky_star and wife_img_name:
                    # 从图片文件名提取老婆名称
                    base = os.path.splitext(os.path.basename(wife_img_name))[0]
                    if "!" in base:
                        # 形如 作品!角色名
                        _, chara = base.split("!", 1)
                        lucky_star = chara
                    else:
                        lucky_star = base
                if not lucky_star:
                    lucky_star = "神秘人"
                lucky_star_text = f"今日吉星：【{lucky_star}】"
                lucky_star_bbox = draw.textbbox((0, 0), lucky_star_text, font=text_font)
                lucky_star_width = lucky_star_bbox[2] - lucky_star_bbox[0]
                draw.text(((width - lucky_star_width) // 2, current_y), lucky_star_text, fill=(70, 130, 180), font=text_font)
                current_y += 45
            except:
                pass
        
        # 绘制建议（增加字体大小和间距）
        dos = fortune.get("dos", [])
        donts = fortune.get("donts", [])
        
        if dos:
            dos_text = "宜：" + "、".join(dos)
            dos_bbox = draw.textbbox((0, 0), dos_text, font=text_font)
            dos_width = dos_bbox[2] - dos_bbox[0]
            draw.text(((width - dos_width) // 2, current_y), dos_text, fill=(0, 100, 0), font=text_font)
            current_y += 45
        
        if donts:
            donts_text = "忌：" + "、".join(donts)
            donts_bbox = draw.textbbox((0, 0), donts_text, font=text_font)
            donts_width = donts_bbox[2] - donts_bbox[0]
            draw.text(((width - donts_width) // 2, current_y), donts_text, fill=(150, 0, 0), font=text_font)
            current_y += 45
        
        current_y += 30
        
        # 绘制免责声明
        disclaimer1 = "图片源自网络|如有侵权请反馈删除"
        disclaimer2 = "仅供娱乐|相信科学|请勿迷信"
        disclaimer_bbox1 = draw.textbbox((0, 0), disclaimer1, font=small_font)
        disclaimer_width1 = disclaimer_bbox1[2] - disclaimer_bbox1[0]
        draw.text(((width - disclaimer_width1) // 2, current_y), disclaimer1, fill=(150, 150, 150), font=small_font)
        current_y += 30
        
        disclaimer_bbox2 = draw.textbbox((0, 0), disclaimer2, font=small_font)
        disclaimer_width2 = disclaimer_bbox2[2] - disclaimer_bbox2[0]
        draw.text(((width - disclaimer_width2) // 2, current_y), disclaimer2, fill=(150, 150, 150), font=small_font)
        current_y += 30
        
        # 绘制按钮（模拟）
        button_y = current_y
        button_height = 45
        button_rect = [padding, button_y, width - padding, button_y + button_height]
        draw.rectangle(button_rect, fill=(70, 130, 180), outline=(50, 100, 150), width=2)
        button_text = "今日运势"
        button_bbox = draw.textbbox((0, 0), button_text, font=text_font)
        button_text_width = button_bbox[2] - button_bbox[0]
        button_text_x = (width - button_text_width) // 2
        button_text_y = button_y + (button_height - (button_bbox[3] - button_bbox[1])) // 2
        draw.text((button_text_x, button_text_y), button_text, fill=(255, 255, 255), font=text_font)
        
        return img
