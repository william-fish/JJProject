from astrbot.api.all import *
from astrbot.api.star import StarTools
from datetime import datetime, timedelta
import random
import os
import re
import json
import aiohttp

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


def load_group_config(group_id: str) -> dict:
    path = os.path.join(CONFIG_DIR, f"{group_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_group_config(
    group_id: str, user_id: str, wife_name: str, date: str, nickname: str, config: dict
):
    # 统一使用 {"wives": [...], "date": ..., "nick": ...} 格式
    config[user_id] = {"wives": [wife_name], "date": date, "nick": nickname}
    path = os.path.join(CONFIG_DIR, f"{group_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def is_harem_user(cfg: dict, uid: str) -> bool:
    """检查用户是否开启了后宫模式"""
    data = cfg.get(uid)
    if not data or not isinstance(data, dict):
        return False
    return data.get("harem") is True


def get_wife_count(cfg: dict, uid: str, today: str) -> int:
    """获取用户今天的老婆数量"""
    data = cfg.get(uid)
    if not data or not isinstance(data, dict):
        return 0
    if data.get("date") == today:
        return len(data.get("wives", []))
    return 0


def get_wives_list(cfg: dict, uid: str, today: str) -> list:
    """获取用户今天的老婆列表（图片名列表）"""
    data = cfg.get(uid)
    if not data or not isinstance(data, dict):
        return []
    if data.get("date") == today:
        return data.get("wives", [])
    return []


def add_wife(cfg: dict, uid: str, img: str, date: str, nick: str, is_harem: bool = False):
    """添加一个老婆到用户列表（统一格式：{"wives": [...], "date": ..., "nick": ...}）"""
    if uid not in cfg:
        cfg[uid] = {"wives": [], "date": date, "nick": nick}
        if is_harem:
            cfg[uid]["harem"] = True
    data = cfg[uid]
    # 兼容旧格式：如果是列表格式，转换为新格式
    if isinstance(data, list) and len(data) >= 1:
        old_img = data[0]
        cfg[uid] = {"wives": [old_img], "date": data[1] if len(data) > 1 else date, "nick": data[2] if len(data) > 2 else nick}
        if is_harem:
            cfg[uid]["harem"] = True
        data = cfg[uid]
    # 确保是字典格式
    if not isinstance(data, dict):
        cfg[uid] = {"wives": [img], "date": date, "nick": nick}
        if is_harem:
            cfg[uid]["harem"] = True
        data = cfg[uid]
    # 更新日期和昵称
    if data.get("date") != date:
        data["wives"] = []
        data["date"] = date
        data["nick"] = nick
    # 更新harem标记
    if is_harem:
        data["harem"] = True
    # 添加老婆
    if img not in data["wives"]:
        data["wives"].append(img)


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
                "select_wife_uses": 0,  # 选老婆使用次数
                "beat_wife_uses": 0,  # 打老婆使用次数
                "seduce_uses": 0,  # 勾引使用次数（-1表示无限）
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
            },
            "meta": {
                "next_ntr_guarantee": False,  # 黄毛：下次牛必定成功
                "ntr_penalty_stack": 0,  # 苦主：被牛次数增量 -> 换老婆额外次数
                "competition_target": None,  # 雄竞目标
                "victim_auto_ntr": False,  # 苦主：被牛必定成功
                "change_free_prob": 0.0,  # 何意味：换老婆免消耗概率
                "change_fail_prob": 0.0,  # 何意味：换老婆失败概率
                "blind_box_extra_draw": False,  # 额外抽盲盒机会
                "blind_box_groups": [],  # 今日已抽盲盒的群列表
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


def get_user_meta(today: str, uid: str, key: str, default=None):
    return get_user_effects(today, uid)["meta"].get(key, default)


def set_user_meta(today: str, uid: str, key: str, value):
    get_user_effects(today, uid)["meta"][key] = value
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
        ]
        self.items_need_target = {"雌堕", "雄竞", "勾引"}
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
        }
        # 命令与处理函数映射
        self.commands = {
            "抽老婆": self.animewife,
            "牛老婆": self.ntr_wife,
            "查老婆": self.search_wife,
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
                cfg = load_group_config(group_id)
                for uid, data in cfg.items():
                    nick = event.get_sender_name()
                    if nick and re.search(re.escape(name), nick, re.IGNORECASE):
                        return uid
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
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        today_items = item_data.setdefault(today, {})
        user_items = today_items.get(uid)
        allow_extra_draw = bool(get_user_meta(today, uid, "blind_box_extra_draw", False))
        if user_items is not None and not allow_extra_draw:
            yield event.plain_result(f"{nick}，你今天已经抽过盲盒啦，明天再来吧~")
            return
        had_items_before = user_items is not None and len(user_items) > 0
        existing_items = list(user_items or [])
        if allow_extra_draw:
            set_user_meta(today, uid, "blind_box_extra_draw", False)
        count = random.randint(0, 3)
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
            # 15% 暴击，额外增加一次抽取机会
            if random.random() < 0.15:
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
            if used >= 1:
                yield event.plain_result(f"{nick}，你今天已经使用过「重置盲盒」啦~")
                return
            if uid not in today_items:
                yield event.plain_result(f"{nick}，你今天还没有抽过盲盒，无需重置哦~")
                return
            del today_items[uid]
            save_item_data()
            day_record[uid] = used + 1
            save_reset_blind_box_records()
            set_user_meta(today, uid, "blind_box_extra_draw", False)
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
                    set_user_meta(today, target_uid, "blind_box_extra_draw", True)
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
        set_user_meta(today, target_uid, "blind_box_extra_draw", False)
        groups = list(get_user_meta(today, target_uid, "blind_box_groups", []) or [])
        if gid in groups:
            groups.remove(gid)
            set_user_meta(today, target_uid, "blind_box_groups", groups)
        cfg = load_group_config(gid)
        target_data = cfg.get(target_uid, {}) if isinstance(cfg, dict) else {}
        target_nick = target_data.get("nick", f"用户{target_uid}") if isinstance(target_data, dict) else f"用户{target_uid}"
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
        card_name = re.split(r"\s+|@", content, maxsplit=1)[0]
        if not card_name:
            yield event.plain_result(f"{nick}，请明确要使用的道具名称哦~")
            return
        if card_name not in self.item_pool:
            yield event.plain_result(f"{nick}，暂未识别到名为“{card_name}”的道具卡~")
            return
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
        success, message = await self.apply_item_effect(card_name, event, target_uid)
        if success:
            user_items.remove(card_name)
            save_item_data()
        yield event.plain_result(message or f"{nick}，道具卡“{card_name}”已处理。")

    async def apply_item_effect(self, card_name, event, target_uid):
        # 分步实现各道具效果
        today = get_today()
        uid = str(event.get_sender_id())
        nick = event.get_sender_name()
        gid = str(event.message_obj.group_id)
        cfg = load_group_config(gid)
        name = card_name
        # ① 牛魔王：进攻+30%，自身被牛也+30%（不叠加 -> 取更大值）
        if name == "牛魔王":
            atk_now = float(get_user_mod(today, uid, "ntr_attack_bonus", 0.0))
            def_now = float(get_user_mod(today, uid, "ntr_defense_bonus", 0.0))
            target_atk = max(atk_now, 0.3)
            target_def = max(def_now, 0.3)
            # 直接写入（使用 add_user_mod 的相对加法会叠加，这里用设置）
            eff = get_user_effects(today, uid)
            eff["mods"]["ntr_attack_bonus"] = target_atk
            eff["mods"]["ntr_defense_bonus"] = target_def
            set_user_flag(today, uid, "ntr_override", True)
            save_effects()
            return True, f"{nick}，牛魔王发动！今日牛成功率UP，但你的老婆也更容易被牛走......"
        # ② 开后宫：无法使用换老婆和重置指令，支持多老婆，有修罗场风险
        if name == "开后宫":
            set_user_flag(today, uid, "harem", True)
            # 将现有老婆转换为后宫格式（如果还没有）
            if uid in cfg:
                data = cfg[uid]
                if isinstance(data, list) and len(data) >= 2 and data[1] == today:
                    cfg[uid] = {"harem": True, "wives": [data[0]], "date": today, "nick": nick}
                    save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
            return True, f"{nick}，你开启了后宫模式！今日无法使用换老婆和重置指令，可同时拥有多个老婆，但小心修罗场哦~"
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
            save_effects()
            return True, f"{nick}，你进入了贤者时间......"
        # ④ 开impart：将今天所有拥有老婆的用户的老婆重新随机分配（开后宫用户保持原有数量，贤者时间用户不受影响）
        if name == "开impart":
            today_users = []
            harem_users = {}  # {uid: wife_count}
            all_images = []
            protected_users = set()  # 拥有贤者时间的用户
            for u, rec in cfg.items():
                # 检查是否拥有贤者时间效果
                if get_user_flag(today, u, "ban_items"):
                    protected_users.add(u)
                    continue
                if isinstance(rec, dict) and rec.get("harem") and rec.get("date") == today:
                    wives = rec.get("wives", [])
                    if wives:
                        harem_users[u] = len(wives)
                        all_images.extend(wives)
                elif isinstance(rec, dict) and rec.get("date") == today:
                    wives = rec.get("wives", [])
                    if wives:
                        today_users.append((u, wives[0]))  # 普通用户只有一个老婆
                        all_images.append(wives[0])
            if len(today_users) + len(harem_users) < 2:
                return False, "当前持有老婆的用户不足以进行重新分配~"
            # 随机打乱所有图片
            random.shuffle(all_images)
            idx = 0
            # 先分配给普通用户
            for u, _ in today_users:
                if idx < len(all_images):
                    # 获取用户信息
                    user_data = cfg.get(u, {})
                    user_nick = user_data.get("nick", f"用户{u}") if isinstance(user_data, dict) else f"用户{u}"
                    cfg[u] = {"wives": [all_images[idx]], "date": today, "nick": user_nick}
                    idx += 1
            # 再分配给开后宫用户，保持原有数量
            for u, count in harem_users.items():
                if idx + count <= len(all_images):
                    user_data = cfg.get(u, {})
                    user_nick = user_data.get("nick", f"用户{u}") if isinstance(user_data, dict) else f"用户{u}"
                    cfg[u] = {"harem": True, "wives": all_images[idx:idx+count], "date": today, "nick": user_nick}
                    idx += count
            save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
            # 取消与变更相关的交换请求（不包括贤者时间用户）
            all_owners = [u for u, _ in today_users] + list(harem_users.keys())
            cancel_msg = await self.cancel_swap_on_wife_change(gid, all_owners)
            msg = "已将所有今日拥有老婆的用户进行随机分配！"
            if protected_users:
                msg += f"（拥有贤者时间的人不受影响）"
            if cancel_msg:
                msg += f"\n{cancel_msg}"
            return True, msg
        # ⑤ 纯爱战士：今日不可被牛走，且无法使用换老婆
        if name == "纯爱战士":
            set_user_flag(today, uid, "protect_from_ntr", True)
            set_user_flag(today, uid, "ban_change", True)
            return True, f"{nick}，你成为了纯爱战士！"
        if name == "雄竞":
            if not target_uid:
                return False, "使用“雄竞”时请@目标用户哦~"
            set_user_meta(today, uid, "competition_target", target_uid)
            return True, f"{nick}，你向对方发起了雄竞！今日抽老婆有概率抽到与其相同的老婆。"
        if name == "苦主":
            set_user_meta(today, uid, "victim_auto_ntr", True)
            set_user_meta(today, uid, "ntr_penalty_stack", 0)
            set_user_flag(today, uid, "ban_reject_swap", True)
            return True, f"{nick}，你成为了苦主......"
        if name == "黄毛":
            set_user_meta(today, uid, "next_ntr_guarantee", True)
            set_user_flag(today, uid, "ban_change", True)
            # 将换老婆使用次数加到牛老婆的使用次数上
            change_rec = change_records.setdefault(gid, {}).get(uid, {"date": "", "count": 0})
            change_count = 0
            if change_rec.get("date") == today:
                change_count = change_rec.get("count", 0)
            ntr_grp = ntr_records.setdefault(gid, {})
            ntr_rec = ntr_grp.get(uid, {"date": today, "count": 0})
            if ntr_rec.get("date") != today:
                ntr_rec = {"date": today, "count": 0}
            ntr_rec["count"] += change_count
            ntr_grp[uid] = ntr_rec
            save_ntr_records()
            return True, f"{nick}，黄毛觉醒！下次牛老婆必定成功，但代价是......"
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
                save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，雌堕成功！对方成为你的老婆了。"
                if cancel_msg:
                    msg += f"\n{cancel_msg}"
                return True, msg
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
                save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
                cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
                msg = f"{nick}，雌堕反噬......你成为了对方的老婆。"
                if cancel_msg:
                    msg += f"\n{cancel_msg}"
                return True, msg
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
                    await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=300)
                except:
                    pass
                return True, f"{nick}，何意味？你被禁言300秒......"
            # 使今天“换老婆”/“牛老婆”随机一个指令的使用次数翻倍
            if choice == "double_counter":
                if random.random() < 0.5:
                    grp = change_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] *= 2
                    grp[uid] = rec
                    save_change_records()
                    return True, f"{nick}，何意味？你今天的“换老婆”使用次数翻倍。"
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] *= 2
                    grp[uid] = rec
                    save_ntr_records()
                    return True, f"{nick}，何意味？你今天的“牛老婆”使用次数翻倍。"
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
                    return True, f"{nick}，何意味？你今天的“换老婆”使用次数清零。"
                else:
                    grp = ntr_records.setdefault(gid, {})
                    rec = grp.get(uid, {"date": today, "count": 0})
                    if rec.get("date") != today:
                        rec = {"date": today, "count": 0}
                    rec["count"] = 0
                    grp[uid] = rec
                    save_ntr_records()
                    return True, f"{nick}，何意味？你今天的“牛老婆”使用次数清零。"
            # 今天“换老婆”有50%概率不消耗指令使用次数
            if choice == "change_free_half":
                current = float(get_user_meta(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_meta(today, uid, "change_free_prob", max(current, 0.5))
                return True, f"{nick}，何意味？你今天“换老婆”有概率不消耗次数。"
            # 今天“换老婆”有50%概率执行失败
            if choice == "change_fail_half":
                current = float(get_user_meta(today, uid, "change_fail_prob", 0.0) or 0.0)
                set_user_meta(today, uid, "change_fail_prob", max(current, 0.5))
                return True, f"{nick}，何意味？你今天“换老婆”有概率执行失败。"
            # 将今天所有拥有老婆的用户的老婆重新随机分配（贤者时间用户不受影响）
            if choice == "impart":
                today_users = []
                harem_users = {}  # {uid: wife_count}
                all_images = []
                protected_users = set()  # 拥有贤者时间的用户
                for u, rec in cfg.items():
                    # 检查是否拥有贤者时间效果
                    if get_user_flag(today, u, "ban_items"):
                        protected_users.add(u)
                        continue
                    if isinstance(rec, dict) and rec.get("harem") and rec.get("date") == today:
                        wives = rec.get("wives", [])
                        if wives:
                            harem_users[u] = len(wives)
                            all_images.extend(wives)
                    elif isinstance(rec, dict) and rec.get("date") == today:
                        wives = rec.get("wives", [])
                        if wives:
                            today_users.append((u, wives[0]))  # 普通用户只有一个老婆
                            all_images.append(wives[0])
                if len(today_users) + len(harem_users) < 2:
                    return True, f"{nick}，何意味？当前持有老婆的用户不足，随机分配未生效。"
                # 随机打乱所有图片
                random.shuffle(all_images)
                idx = 0
                # 先分配给普通用户
                for u, _ in today_users:
                    if idx < len(all_images):
                        # 获取用户信息
                        user_data = cfg.get(u, {})
                        user_nick = user_data.get("nick", f"用户{u}") if isinstance(user_data, dict) else f"用户{u}"
                        cfg[u] = {"wives": [all_images[idx]], "date": today, "nick": user_nick}
                        idx += 1
                # 再分配给开后宫用户，保持原有数量
                for u, count in harem_users.items():
                    if idx + count <= len(all_images):
                        user_data = cfg.get(u, {})
                        user_nick = user_data.get("nick", f"用户{u}") if isinstance(user_data, dict) else f"用户{u}"
                        cfg[u] = {"harem": True, "wives": all_images[idx:idx+count], "date": today, "nick": user_nick}
                        idx += count
                save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
                all_owners = [u for u, _ in today_users] + list(harem_users.keys())
                cancel_msg = await self.cancel_swap_on_wife_change(gid, all_owners)
                msg = "何意味？已将所有今日拥有老婆的用户进行随机分配！"
                if protected_users:
                    msg += f"（拥有贤者时间的用户不受影响）"
                if cancel_msg:
                    msg += f"\n{cancel_msg}"
                return True, msg
            # 执行“换老婆”指令（本次不消耗次数）
            if choice == "do_change_once":
                prev = float(get_user_meta(today, uid, "change_free_prob", 0.0) or 0.0)
                set_user_meta(today, uid, "change_free_prob", 1.0)
                # 执行一次换老婆
                async for _ in self.change_wife(event):
                    pass
                # 恢复之前概率（若之前大于1.0会被限制到1.0）
                set_user_meta(today, uid, "change_free_prob", prev)
                return True, f"{nick}，何意味？你的老婆跑了......"
            # 随机生效两个效果
            if choice == "two_effects":
                effects = ["mute_300", "double_counter", "zero_counter", "change_free_half", "change_fail_half"]
                selected = random.sample(effects, min(2, len(effects)))
                msgs = []
                for eff in selected:
                    if eff == "mute_300":
                        try:
                            await event.bot.set_group_ban(group_id=int(gid), user_id=int(uid), duration=300)
                        except:
                            pass
                        msgs.append("被禁言300秒")
                    elif eff == "double_counter":
                        if random.random() < 0.5:
                            grp = change_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] *= 2
                            grp[uid] = rec
                            save_change_records()
                            msgs.append("换老婆次数翻倍")
                        else:
                            grp = ntr_records.setdefault(gid, {})
                            rec = grp.get(uid, {"date": today, "count": 0})
                            if rec.get("date") != today:
                                rec = {"date": today, "count": 0}
                            rec["count"] *= 2
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
                        current = float(get_user_meta(today, uid, "change_free_prob", 0.0) or 0.0)
                        set_user_meta(today, uid, "change_free_prob", max(current, 0.5))
                        msgs.append("换老婆有概率不消耗次数")
                    elif eff == "change_fail_half":
                        current = float(get_user_meta(today, uid, "change_fail_prob", 0.0) or 0.0)
                        set_user_meta(today, uid, "change_fail_prob", max(current, 0.5))
                        msgs.append("换老婆有概率执行失败")
                return True, f"{nick}，何意味？随机生效两个效果（{', '.join(msgs)}）。"
            # 随机获得一张道具卡
            if choice == "random_item":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                random_item = random.choice(self.item_pool)
                user_items.append(random_item)
                save_item_data()
                return True, f"{nick}，何意味？你获得了道具卡「{random_item}」。"
            # 获得一次抽盲盒的机会
            if choice == "draw_chance":
                set_user_meta(today, uid, "blind_box_extra_draw", True)
                return True, f"{nick}，何意味？你获得了一次额外的抽盲盒机会。"
            # 随机获得两张道具卡
            if choice == "two_items":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.setdefault(uid, [])
                random_items = random.choices(self.item_pool, k=2)
                user_items.extend(random_items)
                save_item_data()
                items_text = "、".join(random_items)
                return True, f"{nick}，何意味？你获得了道具卡：{items_text}。"
            # 今日不能再使用道具卡
            if choice == "ban_items":
                set_user_flag(today, uid, "ban_items", True)
                return True, f"{nick}，何意味？你今天不能再使用道具卡了。"
            # 失去你当前所有的道具卡
            if choice == "lose_all_items":
                today_items = item_data.setdefault(today, {})
                if uid in today_items:
                    lost_count = len(today_items[uid])
                    del today_items[uid]
                    save_item_data()
                    return True, f"{nick}，何意味？你失去了所有道具卡（共{lost_count}张）。"
                return True, f"{nick}，何意味？你失去了所有道具卡（你本来就没有）。"
            if choice == "force_use_item":
                today_items = item_data.setdefault(today, {})
                user_items = today_items.get(uid, [])
                available = [
                    card for card in user_items
                    if card not in self.items_need_target and card != "何意味"
                ]
                if not available:
                    return True, f"{nick}，何意味？你没有可以强制使用的道具卡。"
                forced_card = random.choice(available)
                user_items.remove(forced_card)
                save_item_data()
                forced_success, forced_message = await self.apply_item_effect(forced_card, event, None)
                msg_prefix = f"{nick}，何意味？强制使用了「{forced_card}」。"
                if forced_success and forced_message:
                    return True, f"{msg_prefix}\n{forced_message}"
                return True, msg_prefix
        # 新增道具卡效果
        # ① 白月光：今天获得一次"选老婆"的使用次数
        if name == "白月光":
            add_user_mod(today, uid, "select_wife_uses", 1)
            return True, f"{nick}，你获得了一次「选老婆」的使用次数。"
        # ② 公交车：今天你对其他人使用"交换老婆"指令时无需经过对方同意，强制交换，但你今天无法使用"牛老婆"指令
        if name == "公交车":
            set_user_flag(today, uid, "force_swap", True)
            set_user_flag(today, uid, "ban_ntr", True)
            return True, f"{nick}，公交车已发车！你今天可以强制交换老婆！但代价是......"
        # ③ 病娇：今天你的老婆不会被别人使用"牛老婆"牛走，但当你在有老婆的情况下成功使用"牛老婆"指令牛走别人的老婆时，随机触发事件
        if name == "病娇":
            set_user_flag(today, uid, "landmine_girl", True)
            return True, f"{nick}，你的老婆变成了病娇..."
        # ④ 儒夫：今天你获得10次"打老婆"使用次数
        if name == "儒夫":
            add_user_mod(today, uid, "beat_wife_uses", 10)
            return True, f"{nick}，儒家思想已融入你的血液，你今天获得了10次「打老婆」的使用次数。"
        # ⑤ 熊出没：今天你可以使用"勾引"指令无数次，但每次使用有25%概率被禁言120秒
        if name == "熊出没":
            add_user_mod(today, uid, "seduce_uses", -1)  # -1表示无限
            return True, f"{nick}，熊出没已上线！你今天可以无限使用「勾引」指令"
        # 其他未实现
        return False, f"道具卡「{card_name}」的效果正在开发中，敬请期待~"

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
                # 检查修罗场触发
                if wife_count >= 2:
                    prob = (wife_count - 1) * 0.1
                    if random.random() < prob:
                        # 触发修罗场，失去所有老婆
                        if uid in cfg:
                            del cfg[uid]
                        save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
                path = os.path.join(IMG_DIR, img)
                if img.startswith("http"):
                    chain = [Plain(text), Image.fromURL(img)]
                elif os.path.exists(path):
                    chain = [Plain(text), Image.fromFileSystem(path)]
                else:
                    chain = [Plain(text), Image.fromURL(self.image_base_url + img)]
                try:
                    yield event.chain_result(chain)
                except:
                    yield event.plain_result(text)
                return
        # 开始抽取新老婆
        # 检查用户是否在专属卡池中
        user_keywords = pro_users.get(uid, [])
        
        local_imgs = os.listdir(IMG_DIR)
        if local_imgs:
            # 如果用户在专属卡池中，根据关键词筛选图片
            if user_keywords:
                keywords_lower = [kw.lower() for kw in user_keywords]
                filtered_imgs = [
                    img_name for img_name in local_imgs
                    if any(kw in img_name.lower() for kw in keywords_lower)
                ]
                # 如果筛选后有图片，从筛选结果中选择；否则从全部图片中选择
                img = random.choice(filtered_imgs) if filtered_imgs else random.choice(local_imgs)
            else:
                img = random.choice(local_imgs)
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.image_base_url) as resp:
                        text = await resp.text()
                    all_imgs = text.splitlines()
                    # 如果用户在专属卡池中，根据关键词筛选图片
                    if user_keywords:
                        keywords_lower = [kw.lower() for kw in user_keywords]
                        filtered_imgs = [
                            img_name for img_name in all_imgs
                            if any(kw in img_name.lower() for kw in keywords_lower)
                        ]
                        # 如果筛选后有图片，从筛选结果中选择；否则从全部图片中选择
                        img = random.choice(filtered_imgs) if filtered_imgs else random.choice(all_imgs)
                    else:
                        img = random.choice(all_imgs)
            except:
                    yield event.plain_result("抱歉，今天的老婆获取失败了，请稍后再试~")
                    return
        comp_target = get_user_meta(today, uid, "competition_target", None)
        if comp_target:
            target_wives = get_wives_list(cfg, comp_target, today)
            if target_wives and random.random() < 0.3:
                img = random.choice(target_wives)
        # 统一使用add_wife函数添加老婆
        add_wife(cfg, uid, img, today, nick, is_harem)
        save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
        path = os.path.join(IMG_DIR, img)
        if img.startswith("http"):
            chain = [Plain(text), Image.fromURL(img)]
        elif os.path.exists(path):
            chain = [Plain(text), Image.fromFileSystem(path)]
        else:
            chain = [Plain(text), Image.fromURL(self.image_base_url + img)]
        try:
            yield event.chain_result(chain)
        except:
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
        if rec["count"] >= self.ntr_max:
            yield event.plain_result(
                f"{nick}，你今天已经牛了{self.ntr_max}次啦，明天再来吧~"
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
        final_prob = max(0.0, min(1.0, (self.ntr_possibility or 0.0) + attack_bonus + defense_bonus))
        forced_success = False
        if get_user_meta(today, uid, "next_ntr_guarantee", False):
            forced_success = True
            set_user_meta(today, uid, "next_ntr_guarantee", False)
        if get_user_meta(today, tid, "victim_auto_ntr", False):
            forced_success = True
            add_user_mod(today, tid, "change_extra_uses", 1)
            penalty = int(get_user_meta(today, tid, "ntr_penalty_stack", 0) or 0)
            set_user_meta(today, tid, "ntr_penalty_stack", penalty + 1)
        if forced_success or random.random() < final_prob:
            # 获取目标的老婆（支持开后宫用户）
            target_wives = get_wives_list(cfg, tid, today)
            if not target_wives:
                yield event.plain_result("对方今天还没有老婆可牛哦~")
                return
            wife = random.choice(target_wives)
            # 从目标处移除老婆
            if is_harem_user(cfg, tid):
                cfg[tid]["wives"].remove(wife)
                if len(cfg[tid]["wives"]) == 0:
                    del cfg[tid]
            else:
                del cfg[tid]
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
                    if uid in cfg:
                        del cfg[uid]
                    save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
            save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
            # 检查并取消相关交换请求
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, tid])
            yield event.plain_result(f"{nick}，牛老婆成功！老婆已归你所有，恭喜恭喜~")
            if cancel_msg:
                yield event.plain_result(cancel_msg)
            # 立即展示新老婆
            async for res in self.animewife(event):
                yield res
        else:
            rem = self.ntr_max - rec["count"]
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
                    # 解析出处和角色名，分隔符为!
                    if "!" in name:
                        source, chara = name.split("!", 1)
                        text = f"{owner}的第{idx}个老婆是来自《{source}》的{chara}"
                    else:
                        text = f"{owner}的第{idx}个老婆是{name}"
                # 解析出处和角色名，分隔符为!
                if idx == len(wives):
                    text += f"，共有{len(wives)}个老婆，羡慕吗？"
                else:
                    text += "，"
                path = os.path.join(IMG_DIR, img)
                chain = [
                    Plain(text),
                    (Image.fromURL(img) if img.startswith("http")
                     else (Image.fromFileSystem(path) if os.path.exists(path) else Image.fromURL(self.image_base_url + img))),
                ]
                try:
                    yield event.chain_result(chain)
                except:
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
            path = os.path.join(IMG_DIR, img)
            chain = [
                Plain(text),
                (
                    Image.fromURL(img)
                    if img.startswith("http")
                    else (
                        Image.fromFileSystem(path)
                        if os.path.exists(path)
                        else Image.fromURL(self.image_base_url + img)
                    )
                ),
            ]
            try:
                yield event.chain_result(chain)
            except:
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
        max_change = (self.change_max_per_day or 0) + int(get_user_mod(today, uid, "change_extra_uses", 0))
        if rec["count"] >= max_change:
            yield event.plain_result(
                f"{nick}，你今天已经换了{max_change}次老婆啦，明天再来吧~"
            )
            return
        wives = get_wives_list(cfg, uid, today)
        if not wives:
            yield event.plain_result(f"{nick}，你今天还没有老婆，先去抽一个再来换吧~")
            return
        # 删除旧老婆数据
        if uid in cfg:
            del cfg[uid]
        fail_prob = float(get_user_meta(today, uid, "change_fail_prob", 0.0) or 0.0)
        if fail_prob > 0 and random.random() < fail_prob:
            rec["count"] += 1
            recs[uid] = rec
            save_change_records()
            yield event.plain_result(f"{nick}，修罗场余波未散，明天再来吧......")
            return
        consume = True
        free_prob = float(get_user_meta(today, uid, "change_free_prob", 0.0) or 0.0)
        if free_prob > 0 and random.random() < free_prob:
            consume = False
        free_msg = ""
        if not consume and free_prob > 0:
            free_msg = "（本次未消耗次数）"
        if not is_harem:
            # 普通用户已在上面的else分支删除
            save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
                save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
        save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
        save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
        # 解析出处和角色名
        name = os.path.splitext(img)[0]
        if "!" in name:
            source, chara = name.split("!", 1)
            text = f"{nick}，你选择了来自《{source}》的{chara}作为你的老婆，请好好珍惜哦~"
        else:
            text = f"{nick}，你选择了{name}作为你的老婆，请好好珍惜哦~"
        path = os.path.join(IMG_DIR, img)
        if img.startswith("http"):
            chain = [Plain(text), Image.fromURL(img)]
        elif os.path.exists(path):
            chain = [Plain(text), Image.fromFileSystem(path)]
        else:
            chain = [Plain(text), Image.fromURL(self.image_base_url + img)]
        try:
            yield event.chain_result(chain)
        except:
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
                save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
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
            save_json(os.path.join(CONFIG_DIR, f"{gid}.json"), cfg)
            cancel_msg = await self.cancel_swap_on_wife_change(gid, [uid, target_uid])
            msg = f"{nick}，勾引成功！对方已经拜倒在你的脂包肌下了。"
            if cancel_msg:
                msg += f"\n{cancel_msg}"
            yield event.plain_result(msg)
        else:
            yield event.plain_result(f"{nick}，勾引失败！对方没有注意到你，下次再试试吧~")
