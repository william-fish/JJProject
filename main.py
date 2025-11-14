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


def add_wife(arg1, arg2, img: str, date: str, nick: str, is_harem: bool = False):
    if isinstance(arg1, dict):
        cfg = arg1
        uid = arg2
        gid = getattr(cfg, "group_id", None)
    else:
        uid = arg1
        gid = arg2
        cfg = None
    record = ensure_group_record(uid, gid, date, nick, keep_existing=is_harem)
    if is_harem:
        record["harem"] = True
        if img not in record["wives"]:
            record["wives"].append(img)
    else:
        record["harem"] = False
        record["wives"] = [img]
    if isinstance(cfg, dict):
        dict.__setitem__(cfg, str(uid), record)


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
                "pachinko_777": False,  # 帕青哥：777效果
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
            },
        }
        day_map[uid] = eff
    return eff


def get_user_flag(today: str, uid: str, flag_key: str) -> bool:
    return bool(get_user_effects(today, uid)["flags"].get(flag_key, False))


def set_user_flag(today: str, uid: str, flag_key: str, value: bool):
    get_user_effects(today, uid)["flags"][flag_key] = bool(value)
    save_effects()


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
            "帕青哥",
            "苦命鸳鸯",
            "牛道具",
            "偷拍",
            "复读",
        ]
        self.items_need_target = {"雌堕", "雄竞", "勾引", "牛道具", "偷拍", "复读"}
        # 状态效果道具（不可重复获得）
        self.status_items = {
            "牛魔王",
            "开后宫",
            "贤者时间",
            "纯爱战士",
            "雄竞",
            "苦主",
            "黄毛",
            "公交车",
            "病娇",
            "熊出没",
            "龙王",
            "烧火棍",
            "未来日记",
            "爱马仕",
        }
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

    def _handle_wife_loss(self, today: str, uid: str, loss_count: int = 1):
        loss = int(loss_count or 0)
        if loss <= 0:
            return
        if not get_user_flag(today, uid, "victim_auto_ntr"):
            return
        add_user_mod(today, uid, "change_extra_uses", loss)
        penalty = int(get_user_meta(today, uid, "ntr_penalty_stack", 0) or 0)
        set_user_meta(today, uid, "ntr_penalty_stack", penalty + loss)

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
                self._handle_wife_loss(today, u, len(old_wives))
        for u, old_wives in harem_users.items():
            count = len(old_wives)
            if idx + count <= len(all_images):
                rec = ensure_group_record(u, gid, today, "", keep_existing=False)
                rec["harem"] = True
                rec["wives"] = all_images[idx:idx + count]
                idx += count
                self._handle_wife_loss(today, u, count)
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
        text = event.message_str.strip()
        for cmd, func in self.commands.items():
            if text.startswith(cmd):
                async for res in func(event):
                    yield res
                break

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
        if user_items is not None and not allow_extra_draw:
            yield event.plain_result(f"{nick}，你今天已经抽过盲盒啦，明天再来吧~")
            return
        had_items_before = user_items is not None and len(user_items) > 0
        existing_items = list(user_items or [])
        if allow_extra_draw:
            add_user_mod(today, uid, "blind_box_extra_draw", -1)
        if random.random() < 0.2:
            count = 0
        else:
            count = random.randint(1, 4)
        if count == 0:
            today_items[uid] = existing_items
            save_item_data()
            self._ensure_blind_box_group(today, uid, gid)
            if existing_items:
                yield event.plain_result(f"{nick}，这次额外的盲盒机会什么都没抽到，不过之前的道具仍然保留~")
            else:
                yield event.plain_result(f"{nick}，今天的盲盒空空如也，什么都没抽到呢~")
            return
        # 分离状态效果道具和普通道具
        status_pool = [item for item in self.item_pool if item in self.status_items]
        normal_pool = [item for item in self.item_pool if item not in self.status_items]
        drawn_items = []
        drawn_status = set()  # 已抽取的状态效果道具（不可重复）
        pending_draws = count
        crit_times = 0
        pachinko_777 = get_user_flag(today, uid, "pachinko_777")
        pachinko_777_used = False  # 777效果是否已使用
        while pending_draws > 0:
            pending_draws -= 1
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
            # 15% 暴击，额外增加一次抽取机会（777效果：必定触发一次）
            should_crit = False
            if pachinko_777 and not pachinko_777_used:
                should_crit = True
                pachinko_777_used = True
                set_user_flag(today, uid, "pachinko_777", False)  # 使用后清除777效果
            elif random.random() < 0.20:
                should_crit = True
            if should_crit:
                pending_draws += 1
                crit_times += 1
        if not drawn_items:
            today_items[uid] = existing_items
            save_item_data()
            self._ensure_blind_box_group(today, uid, gid)
            if existing_items:
                yield event.plain_result(f"{nick}，这次额外的盲盒机会什么都没抽到，不过之前的道具仍然保留~")
            else:
                yield event.plain_result(f"{nick}，今天的盲盒空空如也，什么都没抽到呢~")
            return
        existing_items.extend(drawn_items)
        today_items[uid] = existing_items
        save_item_data()
        self._ensure_blind_box_group(today, uid, gid)
        items_text = "、".join(drawn_items)
        if crit_times > 0:
            if had_items_before:
                yield event.plain_result(f"{nick}，你额外抽到了：{items_text}！触发了{crit_times}次暴击，目前共持有{len(existing_items)}张道具卡。")
            else:
                yield event.plain_result(f"{nick}，你抽到了：{items_text}！触发了{crit_times}次暴击，再接再厉~")
        else:
            if had_items_before:
                yield event.plain_result(f"{nick}，你额外抽到了：{items_text}！目前共持有{len(existing_items)}张道具卡。")
            else:
                yield event.plain_result(f"{nick}，你抽到了：{items_text}，记得善加利用哦~")

    async def reset_blind_box(self, event: AstrMessageEvent):
        today = get_today()
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        text = event.message_str.strip()
        arg = text[len("重置盲盒") :].strip()
        admin_ids = {str(a) for a in self.admins}
        today_items = item_data.setdefault(today, {})
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
        group_bonus = int(get_group_meta(today, gid, "change_extra_uses", 0))
        if group_bonus > 0:
            panel_data.append(f"群加成：+{group_bonus}次换老婆")
        
        # 收集状态数据（flags相关效果，显示完整说明）
        status_data = []
        if get_user_flag(today, uid, "protect_from_ntr"):
            status_data.append("纯爱战士：今日老婆不会被牛走和更换，也无法使用「换老婆」")
        if get_user_flag(today, uid, "ban_change"):
            status_data.append("换老婆禁用：今日无法使用「换老婆」指令")
        if get_user_flag(today, uid, "ban_items"):
            status_data.append("贤者时间：今日不受任何道具卡影响，同时也无法使用任何道具卡")
        if get_user_flag(today, uid, "harem"):
            status_data.append("开后宫：今日可以拥有多个老婆，但无法使用「换老婆」与「重置」指令")
        if get_user_flag(today, uid, "ban_ntr"):
            status_data.append("公交车：今日无法使用「牛老婆」，但可以强制交换老婆")
        if get_user_flag(today, uid, "ntr_override"):
            status_data.append("牛魔王：牛老婆和成功率提升并无视禁用效果，从其他渠道获得的牛老婆次数翻倍")
        if get_user_flag(today, uid, "force_swap"):
            status_data.append("强制交换：使用「交换老婆」指令时无需对方同意")
        if get_user_flag(today, uid, "landmine_girl"):
            status_data.append("病娇：你的老婆不会被牛走，但成功牛别人时可能遭遇惩罚")
        if get_user_flag(today, uid, "ban_reject_swap"):
            status_data.append("苦主：无法拒绝交换，请谨慎应对")
        if get_user_flag(today, uid, "victim_auto_ntr"):
            status_data.append("苦主（受害）：别人对你使用「牛老婆」必定成功，且每次失去老婆会额外获得1次「换老婆」次数")
        if get_user_flag(today, uid, "next_ntr_guarantee"):
            status_data.append("黄毛：下一次「牛老婆」必定成功")
        if get_user_flag(today, uid, "double_item_effect"):
            status_data.append("二度寝：下次使用的道具卡数值效果翻倍")
        if get_user_flag(today, uid, "stick_hero"):
            reset_extra_val = int(get_user_mod(today, uid, "reset_extra_uses", 0))
            reset_blind_box_extra_val = int(get_user_mod(today, uid, "reset_blind_box_extra", 0))
            status_data.append(f"棍勇：额外获得{reset_extra_val}次重置次数和{reset_blind_box_extra_val}次重置盲盒机会，抽老婆和换老婆有特殊效果")
        if get_user_flag(today, uid, "hermes"):
            status_data.append("爱马仕：抽老婆或换老婆只会抽到「赛马娘」")
        if get_user_flag(today, uid, "pachinko_777"):
            status_data.append("777：今日抽盲盒必定触发一次暴击")
        comp_target = get_user_meta(today, uid, "competition_target", None)
        if comp_target:
            comp_uid = str(comp_target)
            comp_record = get_group_record(comp_uid, gid) or {}
            comp_entry = wives_data.get(comp_uid, {}) if isinstance(wives_data, dict) else {}
            comp_name = comp_record.get("nick") or comp_entry.get("nick")
            status_data.append(f"雄竞：正在与{comp_name or f'用户{comp_uid}'}竞争同款老婆")
        
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
            yield event.plain_result(f"{nick}，你正处于“贤者时间”，今天无法使用任何道具卡哦~")
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
            user_items.remove(card_name)
            save_item_data()
        yield event.plain_result(message or f"{nick}，道具卡“{card_name}”已处理。")

    async def apply_item_effect(self, card_name, event, target_uid, extra_arg=""):
        # 分步实现各道具效果
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        gid = str(event.message_obj.group_id)
        cfg = load_group_config(gid)
        name = card_name
        is_sleep_effect = name == "二度寝"
        double_active = bool(get_user_flag(today, uid, "double_item_effect")) if not is_sleep_effect else False
        double_factor = 2 if double_active else 1

        def finalize(success_flag: bool, message: str | None):
            if not is_sleep_effect and double_active and success_flag:
                set_user_flag(today, uid, "double_item_effect", False)
            return success_flag, message
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
            # 将换老婆使用次数加到牛老婆的使用次数上
            change_rec = change_records.setdefault(gid, {}).get(uid, {"date": "", "count": 0})
            change_count = 0
            if change_rec.get("date") == today:
                change_count = change_rec.get("count", 0)
            bonus_count = change_count * double_factor
            # 牛魔王效果：本次累加的次数翻倍
            if get_user_flag(today, uid, "ntr_override"):
                bonus_count = bonus_count * 2
            ntr_grp = ntr_records.setdefault(gid, {})
            ntr_rec = ntr_grp.get(uid, {"date": today, "count": 0})
            if ntr_rec.get("date") != today:
                ntr_rec = {"date": today, "count": 0}
            ntr_rec["count"] += bonus_count
            ntr_grp[uid] = ntr_rec
            save_ntr_records()
            return finalize(True, f"{nick}，黄毛觉醒！下次牛老婆必定成功，已将今日已使用的「换老婆」次数累加到「牛老婆」次数，但代价是......")
        # ⑥ 雌堕：50%让@目标成为你的老婆（头像图），50%你成为对方的老婆（头像图）（贤者时间用户不受影响）
        if name == "雌堕":
            if not target_uid:
                return False, "使用「雌堕」时请@目标用户哦~"
            target_uid = str(target_uid)
            # 检查目标用户是否拥有贤者时间效果
            if get_user_flag(today, target_uid, "ban_items"):
                return False, f"{nick}，对方处于贤者时间，不受道具效果影响。"
            # 检查自己是否拥有贤者时间效果（失败分支时）
            if get_user_flag(today, uid, "ban_items"):
                return False, f"{nick}，你处于贤者时间，无法使用道具。"
            # 成功分支：对方成为你的老婆
            if random.random() < 0.5:
                img = get_avatar_url(target_uid)
                add_wife(cfg, uid, img, today, nick, False)
                save_group_config(cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，雌堕成功！对方成为你的老婆了。"
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
                add_wife(cfg, target_uid, img, today, target_nick or f"用户{target_uid}", False)
                save_group_config(cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，雌堕反噬......你成为了对方的老婆。"
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
            self._handle_wife_loss(today, uid, user_loss)
            self._handle_wife_loss(today, target_uid, target_loss)
            target_avatar = get_avatar_url(target_uid)
            user_avatar = get_avatar_url(uid)
            add_wife(cfg, uid, target_avatar, today, nick, False)
            add_wife(cfg, target_uid, user_avatar, today, target_nick, False)
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
            if get_user_flag(today, target_uid, "ban_items"):
                return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「牛道具」。")
            today_items = item_data.setdefault(today, {})
            target_items = list(today_items.get(target_uid, []))
            if not target_items:
                return finalize(False, f"{nick}，对方今天还没有道具可以被牛走。")
            steal_count = min(random.randint(0, 2), len(target_items))
            if steal_count == 0:
                return finalize(True, f"{nick}，你伸出黑手，但尴尬地牵到了对方的手，牛道具失败了......")
            stolen = random.sample(target_items, steal_count)
            for itm in stolen:
                target_items.remove(itm)
            today_items[target_uid] = target_items
            user_items = today_items.setdefault(uid, [])
            user_items.extend(stolen)
            save_item_data()
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            return finalize(True, f"{nick}，你对{target_nick}使用「牛道具」成功，掠走了：{'、'.join(stolen)}。")
        if name == "偷拍":
            if not target_uid:
                return False, "使用「偷拍」时请@目标用户哦~"
            target_uid = str(target_uid)
            if target_uid == uid:
                return False, "不能对自己使用「偷拍」哦~"
            if get_user_flag(today, target_uid, "ban_items"):
                return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「偷拍」。")
            target_wives = get_wives_list(cfg, target_uid, today)
            if not target_wives:
                return finalize(False, f"{nick}，对方今天还没有老婆可偷哦~")
            user_loss = get_wife_count(cfg, uid, today)
            if uid in cfg:
                del cfg[uid]
            self._handle_wife_loss(today, uid, user_loss)
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
            msg = f"{nick}，你付出全部老婆为代价，通过「偷拍」得到了{target_nick}的老婆阵容。"
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
            if get_user_flag(today, target_uid, "ban_items"):
                return finalize(False, f"{nick}，对方正处于贤者时间，无法对其使用「复读」。")
            today_items = item_data.setdefault(today, {})
            target_items = today_items.get(target_uid)
            if not target_items:
                return finalize(False, f"{nick}，对方今天还没有道具可以复刻。")
            today_items[uid] = list(target_items)
            save_item_data()
            target_info = cfg.get(target_uid, {})
            target_nick = target_info.get("nick", f"用户{target_uid}") if isinstance(target_info, dict) else f"用户{target_uid}"
            return finalize(True, f"{nick}，你清空了自己的道具卡，通过「复读」复制到了{target_nick}当前的全部道具：{'、'.join(target_items)}。")
        # ⑩ 何意味：随机执行一个效果（增加新效果）
        if name == "何意味":
            choice = random.choice([
                "mute_300",
                "double_counter",
                "zero_counter",
                "change_free_half",
                "change_fail_half",
                "impart",
                "do_change_once",
                "two_effects",
                "random_item",
                "draw_chance",
                "two_items",
                "ban_items",
                "lose_all_items",
                "force_use_item",
            ])
            # 被禁言300秒
            if choice == "mute_300":
                try:
                    duration = 300 * double_factor
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=int(duration))
                except:
                    pass
                return finalize(True, f"{nick}，何意味？你被禁言{duration}秒......")
            # 使今天“换老婆”/“牛老婆”随机一个指令的使用次数翻倍
            if choice == "double_counter":
                if random.random() < 0.5:
                    grp = change_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] *= (2 * double_factor)
                    grp[uid] = rec
                    save_change_records()
                    return finalize(True, f"{nick}，何意味？你今天的“换老婆”使用次数翻倍。")
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    multiplier = 2 * double_factor
                    # 牛魔王效果：本次翻倍倍数再翻倍
                    if get_user_flag(today, uid, "ntr_override"):
                        multiplier = multiplier * 2
                    rec["count"] *= multiplier
                    grp[uid] = rec
                    save_ntr_records()
                    return finalize(True, f"{nick}，何意味？你今天的「牛老婆」使用次数翻倍。")
            # 使今天“换老婆”/“牛老婆”随机一个指令的使用次数变为0
            if choice == "zero_counter":
                if random.random() < 0.5:
                    grp = change_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] = 0
                    grp[uid] = rec
                    save_change_records()
                    return finalize(True, f"{nick}，何意味？你今天的“换老婆”使用次数清零。")
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] = 0
                    grp[uid] = rec
                    save_ntr_records()
                    return finalize(True, f"{nick}，何意味？你今天的“牛老婆”使用次数清零。")
            # 今天“换老婆”有50%概率不消耗指令使用次数
            if choice == "change_free_half":
                current = clamp_probability(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_free_prob", clamp_probability(max(current, 0.5 * double_factor)))
                return finalize(True, f"{nick}，何意味？你今天“换老婆”有概率不消耗次数。")
            # 今天“换老婆”有50%概率执行失败
            if choice == "change_fail_half":
                current = clamp_probability(get_user_mod(today, uid, "change_fail_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_fail_prob", clamp_probability(max(current, 0.5 * double_factor)))
                return finalize(True, f"{nick}，何意味？你今天“换老婆”有概率执行失败。")
            # 将今天所有拥有老婆的用户的老婆重新随机分配（贤者时间用户不受影响）
            if choice == "impart":
                success, message = await self._redistribute_wives(gid, today, event, cfg)
                return finalize(success, message)
            # 执行“换老婆”指令（本次不消耗次数）
            if choice == "do_change_once":
                prev = float(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_mod(today, uid, "change_free_prob", clamp_probability(1.0))
                # 执行一次换老婆
                async for _ in self.change_wife(event):
                    pass
                # 恢复之前概率（若之前大于1.0会被限制到1.0）
                set_user_mod(today, uid, "change_free_prob", prev)
                return finalize(True, f"{nick}，何意味？你的老婆跑了......")
            # 随机生效两个效果
            if choice == "two_effects":
                effects = ["mute_300", "double_counter", "zero_counter", "change_free_half", "change_fail_half"]
                selected = random.sample(effects, min(2, len(effects)))
                msgs = []
                for eff in selected:
                    if eff == "mute_300":
                        try:
                            duration = 300 * double_factor
                            await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=duration)
                        except:
                            pass
                        msgs.append(f"被禁言{duration}秒")
                    elif eff == "double_counter":
                        if random.random() < 0.5:
                            grp = change_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] *= (2 * double_factor)
                            grp[uid] = rec
                            save_change_records()
                            msgs.append("换老婆次数翻倍")
                        else:
                            grp = ntr_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] *= (2 * double_factor)
                            grp[uid] = rec
                            save_ntr_records()
                            msgs.append("牛老婆次数翻倍")
                    elif eff == "zero_counter":
                        if random.random() < 0.5:
                            grp = change_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] = 0
                            grp[uid] = rec
                            save_change_records()
                            msgs.append("换老婆次数清零")
                        else:
                            grp = ntr_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] = 0
                            grp[uid] = rec
                            save_ntr_records()
                            msgs.append("牛老婆次数清零")
                    elif eff == "change_free_half":
                        current = clamp_probability(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
                        set_user_mod(today, uid, "change_free_prob", clamp_probability(max(current, 0.5 * double_factor)))
                        msgs.append("换老婆有概率不消耗次数")
                    elif eff == "change_fail_half":
                        current = float(get_user_mod(today, uid, "change_fail_prob", 0.0) or 0.0)
                        set_user_mod(today, uid, "change_fail_prob", max(current, min(1.0, 0.5 * double_factor)))
                        msgs.append("换老婆有概率执行失败")
                return finalize(True, f"{nick}，何意味？随机生效两个效果（{', '.join(msgs)}）。")
            # 随机获得一张道具卡
            if choice == "random_item":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                drawn = random.choices(self.item_pool, k=double_factor)
                user_items.extend(drawn)
                save_item_data()
                items_text = "、".join(drawn)
                return finalize(True, f"{nick}，何意味？你获得了道具卡「{items_text}」。")
            # 获得一次抽盲盒的机会
            if choice == "draw_chance":
                add_user_mod(today, uid, "blind_box_extra_draw", double_factor)
                return finalize(True, f"{nick}，何意味？你获得了{double_factor}次额外的抽盲盒机会。")
            # 随机获得两张道具卡
            if choice == "two_items":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                random_items = random.choices(self.item_pool, k=2 * double_factor)
                user_items.extend(random_items)
                save_item_data()
                items_text = "、".join(random_items)
                return finalize(True, f"{nick}，何意味？你获得了道具卡：{items_text}。")
            # 今日不能再使用道具卡
            if choice == "ban_items":
                set_user_flag(today, uid, "ban_items", True)
                return finalize(True, f"{nick}，何意味？你今天不能再使用道具卡了。")
            # 失去你当前所有的道具卡
            if choice == "lose_all_items":
                today_items = item_data.setdefault(today, {})
                if uid in today_items:
                    lost_count = len(today_items[uid])
                    del today_items[uid]
                    save_item_data()
                    return finalize(True, f"{nick}，何意味？你失去了所有道具卡（共{lost_count}张）。")
                return finalize(True, f"{nick}，何意味？你失去了所有道具卡（你本来就没有）。")
            if choice == "force_use_item":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.get(uid, [])
                available = [
                    card for card in user_items
                    if card not in self.items_need_target and card != "何意味"
                ]
                if not available:
                    return finalize(True, f"{nick}，何意味？你没有可以强制使用的道具卡。")
                forced_card = random.choice(available)
                user_items.remove(forced_card)
                save_item_data()
                forced_success, forced_message = await self.apply_item_effect(forced_card, event, None)
                msg_prefix = f"{nick}，何意味？强制使用了「{forced_card}」。"
                if forced_success and forced_message:
                    return finalize(True, f"{msg_prefix}\n{forced_message}")
                return finalize(True, msg_prefix)
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
            if today in item_data and uid in item_data[today]:
                del item_data[today][uid]
            # 清空老婆数据
            loss = get_wife_count(cfg, uid, today)
            if uid in cfg:
                del cfg[uid]
                save_group_config(cfg)
                self._handle_wife_loss(today, uid, loss)
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
        if name == "帕青哥":
            # 清空所有道具
            if today in item_data and uid in item_data[today]:
                del item_data[today][uid]
                save_item_data()
            # 随机触发一种效果
            choice = random.choice(["reset_and_gain", "pachinko_777", "three_states", "mute_300"])
            if choice == "reset_and_gain":
                # 用完今日所有的换老婆、牛老婆、重置、重置盲盒次数
                # 获取当前使用次数并设置为最大值
                gid = str(event.message_obj.group_id)
                # 换老婆次数
                change_recs = change_records.setdefault(gid, {})
                change_rec = change_recs.get(uid, {"date": "", "count": 0})
                if change_rec.get("date") == today:
                    max_change = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0))
                    change_rec["count"] = max_change
                    change_recs[uid] = change_rec
                # 牛老婆次数
                ntr_recs = ntr_records.setdefault(gid, {})
                ntr_rec = ntr_recs.get(uid, {"date": "", "count": 0})
                if ntr_rec.get("date") == today:
                    max_ntr = self.ntr_max + int(get_user_mod(today, uid, "ntr_extra_uses", 0))
                    ntr_rec["count"] = max_ntr
                    ntr_recs[uid] = ntr_rec
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
                add_user_mod(today, uid, "change_extra_uses", change_gain)
                add_user_mod(today, uid, "ntr_extra_uses", ntr_gain)
                add_user_mod(today, uid, "reset_extra_uses", reset_gain)
                add_user_mod(today, uid, "reset_blind_box_extra", reset_blind_box_gain)
                save_change_records()
                save_ntr_records()
                return finalize(True, f"{nick}，帕青哥！你已用完今日所有次数，并获得{change_gain}次换老婆、{ntr_gain}次牛老婆、{reset_gain}次重置、{reset_blind_box_gain}次重置盲盒机会。")
            elif choice == "pachinko_777":
                # 获得"777"效果
                set_user_flag(today, uid, "pachinko_777", True)
                add_user_mod(today, uid, "blind_box_extra_draw", 1)
                return finalize(True, f"{nick}，帕青哥！你获得了「777」效果：获得1次额外抽盲盒次数，且今日抽盲盒必定触发一次暴击。")
            elif choice == "three_states":
                # 随机获得三个状态（flags）效果（不能重复获得已有的状态）
                available_states = [
                    "牛魔王", "开后宫", "纯爱战士", "苦主", "黄毛", "公交车", "病娇", "熊出没", "龙王", "二度寝", "爱马仕"
                ]
                eff = get_user_effects(today, uid)
                current_flags = eff["flags"]
                # 获取当前已有的状态道具
                current_states = []
                if current_flags.get("ntr_override"): current_states.append("牛魔王")
                if current_flags.get("harem"): current_states.append("开后宫")
                if current_flags.get("protect_from_ntr"): current_states.append("纯爱战士")
                if current_flags.get("victim_auto_ntr") or current_flags.get("ban_reject_swap"): current_states.append("苦主")
                if current_flags.get("next_ntr_guarantee"): current_states.append("黄毛")
                if current_flags.get("ban_ntr") or current_flags.get("force_swap"): current_states.append("公交车")
                if current_flags.get("landmine_girl"): current_states.append("病娇")
                if current_flags.get("seduce_uses") == -1: current_states.append("熊出没")
                # 这里需要检查龙王状态，但龙王需要特殊条件，暂时跳过
                if current_flags.get("double_item_effect"): current_states.append("二度寝")
                if current_flags.get("hermes"): current_states.append("爱马仕")
                # 过滤掉已有的状态
                available_states = [s for s in available_states if s not in current_states]
                if len(available_states) < 3:
                    available_states = available_states * 3  # 如果不够3个，允许重复
                selected = random.sample(available_states, min(3, len(available_states)))
                # 应用选中的状态
                for state in selected:
                    if state == "牛魔王":
                        atk_now = float(get_user_mod(today, uid, "ntr_attack_bonus", 0.0))
                        def_now = float(get_user_mod(today, uid, "ntr_defense_bonus", 0.0))
                        set_user_mod(today, uid, "ntr_attack_bonus", max(atk_now, 0.3))
                        set_user_mod(today, uid, "ntr_defense_bonus", max(def_now, 0.3))
                        set_user_flag(today, uid, "ntr_override", True)
                    elif state == "开后宫":
                        set_user_flag(today, uid, "harem", True)
                        set_user_flag(today, uid, "ban_change", True)
                    elif state == "纯爱战士":
                        set_user_flag(today, uid, "protect_from_ntr", True)
                        set_user_flag(today, uid, "ban_change", True)
                    elif state == "苦主":
                        set_user_flag(today, uid, "victim_auto_ntr", True)
                        set_user_flag(today, uid, "ban_reject_swap", True)
                    elif state == "黄毛":
                        set_user_flag(today, uid, "next_ntr_guarantee", True)
                        set_user_flag(today, uid, "ban_change", True)
                    elif state == "公交车":
                        set_user_flag(today, uid, "force_swap", True)
                        set_user_flag(today, uid, "ban_ntr", True)
                    elif state == "病娇":
                        set_user_flag(today, uid, "landmine_girl", True)
                    elif state == "熊出没":
                        set_user_mod(today, uid, "seduce_uses", -1)
                    elif state == "二度寝":
                        set_user_flag(today, uid, "double_item_effect", True)
                    elif state == "爱马仕":
                        set_user_flag(today, uid, "hermes", True)
                return finalize(True, f"{nick}，帕青哥！你随机获得了三个状态效果：{', '.join(selected)}。")
            elif choice == "mute_300":
                # 被禁言300秒
                try:
                    duration = 300
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=int(duration))
                except:
                    pass
                return finalize(True, f"{nick}，帕青哥！你被禁言300秒......")
        # 其他未实现
        return finalize(False, f"道具卡「{card_name}」的效果正在开发中，敬请期待~")

    async def animewife(self, event: AstrMessageEvent):
        # 抽老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
        cfg = load_group_config(gid)
        is_harem = get_user_flag(today, uid, "harem")
        # 检查是否今天已抽（普通用户）或是否达到次数限制（开后宫用户）
        if is_harem:
            # 开后宫：抽老婆次数 = 换老婆次数
            change_recs = change_records.setdefault(gid, {})
            change_rec = change_recs.get(uid, {"date": "", "count": 0})
            max_draw = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0))
            if change_rec.get("date") == today and change_rec.get("count", 0) >= max_draw:
                yield event.plain_result(f"{nick}，你今天已经抽了{max_draw}次老婆啦（开后宫模式下抽老婆次数=换老婆次数），明天再来吧~")
                return
            # 检查是否已有老婆（开后宫可以继续抽）
            wife_count = get_wife_count(cfg, uid, today)
            if wife_count > 0:
                # 检查修罗场触发：5% * 1.35^老婆数量
                chaos_multiplier = float(get_user_meta(today, uid, "harem_chaos_multiplier", 1.0) or 1.0)
                prob = 0.05 * (1.35 ** wife_count) * chaos_multiplier
                prob = min(prob, 0.9)
                if random.random() < prob:
                    # 触发修罗场，失去所有老婆
                    if uid in cfg:
                        loss = wife_count
                        del cfg[uid]
                        save_group_config(cfg)
                        self._handle_wife_loss(today, uid, loss)
                    yield event.plain_result(f"{nick}，修罗场爆发！你失去了所有老婆......")
                    return
        else:
            # 普通用户：今天已抽则直接返回
            wives = get_wives_list(cfg, uid, today)
            if wives:
                img = wives[0]  # 普通用户只有一个老婆
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
            if target_wives and random.random() < competition_prob:
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
        if stick_hero and random.random() < 0.35:
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
        add_wife(cfg, uid, img, today, nick, is_harem)
        save_group_config(cfg)
        if is_harem:
            # 增加抽老婆次数（使用换老婆记录）
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
        # 目标不可被牛（纯爱战士等保护）
        if get_user_flag(today, tid, "protect_from_ntr"):
            yield event.plain_result("对方今天誓死守护纯爱，无法牛走对方的老婆哦~")
            return
        # 目标不可被牛（病娇效果）
        if get_user_flag(today, tid, "landmine_girl"):
            yield event.plain_result("对方的老婆是病娇，无法牛走对方的老婆哦~")
            return
        rec["count"] += 1
        grp[uid] = rec
        save_ntr_records()
        # 计算经由效果修正后的成功概率
        attack_bonus = float(get_user_mod(today, uid, "ntr_attack_bonus", 0.0))
        defense_bonus = float(get_user_mod(today, tid, "ntr_defense_bonus", 0.0))
        final_prob = max(0.0, min(0.9, (self.ntr_possibility or 0.0) + attack_bonus + defense_bonus))
        forced_success = False
        if get_user_flag(today, uid, "next_ntr_guarantee"):
            forced_success = True
            set_user_flag(today, uid, "next_ntr_guarantee", False)
        if get_user_flag(today, tid, "victim_auto_ntr"):
            forced_success = True
        if forced_success or random.random() < final_prob:
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
            self._handle_wife_loss(today, tid, 1)
            # 检查攻击者是否有病娇效果（在有老婆的情况下成功牛别人时触发事件）
            attacker_has_wife = get_wife_count(cfg, uid, today) > 0
            landmine_girl = get_user_flag(today, uid, "landmine_girl")
            if landmine_girl and attacker_has_wife:
                # 病娇效果：随机触发事件
                event_choice = random.choice([
                    "kill_wife",
                    "mute_300",
                    "suicide",
                    "get_item",
                ])
                if event_choice == "kill_wife":
                    # 从wives列表里随机挑选一个老婆
                    murdered_wife = random.choice(cfg[uid]["wives"])
                    # 你原本的老婆将你牛到的老婆"杀"了（即本次牛老婆不会替换你原本的老婆或增加你的老婆）
                    yield event.plain_result(f"{nick}，你的老婆{murdered_wife}不小心把{os.path.splitext(wife)[0]}杀了......")
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
                    self._handle_wife_loss(today, uid, loss)
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
            add_wife(cfg, uid, wife, today, nick, is_attacker_harem)
            save_group_config(cfg)
            # 检查并取消相关交换请求
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, tid])
            yield event.plain_result(f"{nick}，牛老婆成功！老婆已归你所有，恭喜恭喜~")
            if cancel_msg:
                yield event.plain_result(cancel_msg)
            # 立即展示新老婆
            async for res in self.animewife(event):
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
        self._handle_wife_loss(today, uid, lost_count)
        fail_prob = float(get_user_mod(today, uid, "change_fail_prob", 0.0) or 0.0)
        if fail_prob > 0 and random.random() < fail_prob:
            rec["count"] += 1
            recs[uid] = rec
            save_change_records()
            yield event.plain_result(f"{nick}，换老婆失败了，真可惜......")
            return
        consume = True
        free_prob = clamp_probability(get_user_mod(today, uid, "change_free_prob", 0.0) or 0.0)
        if free_prob > 0 and random.random() < free_prob:
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
        if free_msg:
            yield event.plain_result(f"{nick}{free_msg}")

    async def reset_ntr(self, event: AstrMessageEvent):
        # 重置牛老婆主逻辑
        gid = str(event.message_obj.group_id)
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today = get_today()
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
        if random.random() < self.reset_success_rate:
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
        if random.random() < self.reset_success_rate:
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
        # 检查目标是否拥有开后宫效果
        if get_user_flag(today, tid, "harem"):
            yield event.plain_result(f"{nick}，无法对开后宫状态的用户使用「交换老婆」指令哦~")
            return
        # 检查目标是否拥有纯爱战士效果
        if get_user_flag(today, tid, "protect_from_ntr"):
            yield event.plain_result(f"{nick}，无法对纯爱战士使用「交换老婆」指令哦~")
            return
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
        # 检查同意者是否拥有开后宫效果
        if get_user_flag(today, tid, "harem"):
            yield event.plain_result(f"{nick}，开后宫状态下无法使用「同意交换」指令哦~")
            return
        # 检查同意者是否拥有纯爱战士效果
        if get_user_flag(today, tid, "protect_from_ntr"):
            yield event.plain_result(f"{nick}，纯爱战士不会使用「同意交换」指令哦~")
            return
        grp = swap_requests.get(gid, {})
        rec = grp.get(uid)
        if not rec or rec.get("target") != tid:
            yield event.plain_result(
                f"{nick}，请在命令后@发起者，或用「查看交换请求」命令查看当前请求哦~"
            )
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
        if get_user_flag(today, tid, "ban_reject_swap"):
            yield event.plain_result(f"{nick}，苦主无法使用「拒绝交换」指令哦~")
            return
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
        add_wife(cfg, uid, img, today, nick, is_harem)
        save_group_config(cfg)
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
        if not has_landmine and random.random() < 0.3:
            if uid in cfg:
                del cfg[uid]
                save_group_config(cfg)
                self._handle_wife_loss(today, uid, wife_count)
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
            yield event.plain_result(f"{nick}，病娇效果发动！\n{text}")
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
        # 检查使用次数（-1表示无限）
        uses = int(get_user_mod(today, uid, "seduce_uses", 0))
        if uses == 0:
            yield event.plain_result(f"{nick}，你今天还没有「勾引」的使用次数，快去使用道具卡获得吧~")
            return
        # 检查是否无限使用（熊出没效果）
        is_unlimited = (uses == -1)
        if not is_unlimited:
            # 消耗使用次数
            add_user_mod(today, uid, "seduce_uses", -1)
        # 解析目标
        target_uid = self.parse_at_target(event)
        if not target_uid or target_uid == uid:
            msg = "请@你想勾引的对象哦~" if not target_uid else "不能勾引自己呀，换个人试试吧~"
            yield event.plain_result(f"{nick}，{msg}")
            return
        target_uid = str(target_uid)
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
        # 熊出没效果：25%概率被禁言120秒
        if is_unlimited:
            if random.random() < 0.25:
                try:
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=120)
                except:
                    pass
                yield event.plain_result(f"{nick}，勾引失败！你被禁言120秒......")
                return
        # 30%概率成功
        if random.random() < 0.3:
            cfg = load_group_config(gid)
            img = get_avatar_url(target_uid)
            is_harem = get_user_flag(today, uid, "harem")
            add_wife(cfg, uid, img, today, nick, is_harem)
            save_group_config(cfg)
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
            del item_data[today][target_uid]
        # 清空老婆数据
        cfg = load_group_config(gid)
        loss = get_wife_count(cfg, target_uid, today)
        if target_uid in cfg:
            del cfg[target_uid]
            save_group_config(cfg)
            self._handle_wife_loss(today, target_uid, loss)
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
