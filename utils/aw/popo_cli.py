"""
POPO CLI 造数工具

封装 popo-cli 命令，用于测试用例的前置数据准备（造数）。
不替代 UI 操作，仅用于 setup/teardown 中快速准备测试数据。

用法（通过 PPUser.cli 属性访问，uid 自动绑定）:
    # 群组
    tid, name = self.userA.cli.create_team_cli(name="测试群", uid_list=["grp.popoqa67@corp.netease.com"])
    result    = self.userA.cli.invite_member_cli(tid, ["grp.popoqa73@corp.netease.com"])
    result    = self.userA.cli.kick_member_cli(tid, ["grp.popoqa73@corp.netease.com"])
    result    = self.userA.cli.update_team_name_cli(tid, "新群名")

    # 消息（文本/图片/文件 三选一）
    msg  = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", message="文本")
    path = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", image_path="E:/xx.png")
    fname, fpath = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", file_path="E:/xx.pdf")

    # 群消息同理，receiver 换 tid
    msg  = self.userA.cli.send_message_team_cli(tid="8479417", message="文本")

    # 日历
    info = self.userA.cli.create_schedule_cli("会议名", "2026-06-10T14:00:00+08:00", "2026-06-10T15:00:00+08:00", participants=["grp.popoqa67@corp.netease.com"])
    info = self.userA.cli.update_schedule_cli(info["schedule_id"], title="新名称")
    info = self.userA.cli.confirm_schedule_cli(schedule_id, status=1)
    info = self.userA.cli.quit_schedule_cli(schedule_id)
"""
import hashlib
import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

_SUCCESS_STATUS = 1


# ==================== 底层执行 ====================

def _run(args: list) -> dict:
    """
    执行 popo-cli popo <args> 命令，返回业务数据层（data.data.data.data）。
    失败时抛出 RuntimeError。
    """
    cmd = ["popo-cli", "popo"] + args
    logger.info(f"🔧 popo-cli: {' '.join(str(a) for a in cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            shell=True,  # Windows 下 popo-cli 是 .cmd，需要 shell=True
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"popo-cli 超时: {' '.join(str(a) for a in cmd)}")

    raw = (result.stdout or "").strip()
    if not raw:
        raise RuntimeError(f"popo-cli 无输出，stderr: {result.stderr.strip()}")

    try:
        resp = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"popo-cli 返回非 JSON: {raw[:200]}")

    try:
        payload = resp["data"]["data"]["data"]
    except (KeyError, TypeError):
        raise RuntimeError(f"popo-cli 返回结构异常: {raw[:200]}")

    if payload.get("status") != _SUCCESS_STATUS:
        msg = payload.get("message", str(payload))
        raise RuntimeError(f"popo-cli 业务失败: {msg}")

    return payload.get("data") or {}


def _run_curl(args: list) -> str:
    """执行 curl.exe 命令，返回 stdout 字符串。"""
    cmd = ["curl.exe"] + args
    logger.info(f"🔧 curl.exe: {' '.join(str(a) for a in cmd[:5])}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        return result.stdout or ""
    except subprocess.TimeoutExpired:
        raise RuntimeError("curl.exe 上传超时")


# ==================== PopoCLI ====================

class PopoCLI:
    """
    POPO CLI 造数客户端。

    通过 PPUser.cli 属性访问时，uid 自动绑定为当前用户。
    也可直接实例化并传入 uid：PopoCLI(uid="xxx@corp.netease.com")
    """

    def __init__(self, uid: str = None):
        self._uid = uid

    def _get_uid(self) -> str:
        """获取当前用户 uid，未绑定时调用 team_current_user_info 动态查询。"""
        if self._uid:
            return self._uid
        data = _run(["team_current_user_info"])
        uid = data.get("uid", "")
        if not uid:
            raise RuntimeError("team_current_user_info 未返回 uid")
        self._uid = uid
        logger.info(f"👤 当前用户 uid: {uid}")
        return uid

    # ==================== 群组 ====================

    def create_team_cli(self, uid_list: list, name: str = None) -> Tuple[str, str]:
        """
        创建群组。

        Args:
            uid_list: 被邀请成员的 uid 列表（不含当前用户自身，创建者自动入群）
            name:     群名，不传则系统自动生成

        Returns:
            (tid: str, name: str)

        Example:
            tid, name = self.userA.cli.create_team_cli(
                name="消息透出测试群",
                uid_list=["grp.popoqa67@corp.netease.com"],
            )
        """
        uid = self._get_uid()
        uid_list_json = json.dumps(uid_list, ensure_ascii=False)
        args = ["team_create", f"uid={uid}", f"uidList={uid_list_json}", "type=1"]
        if name:
            args.append(f"name={name}")
        data = _run(args)
        tid = str(data.get("tid", ""))
        actual_name = data.get("name", name or "")
        pass_num = data.get("passNum", 0)
        logger.info(f"✅ 群组已创建: '{actual_name}' tid={tid} 入群={pass_num}人")
        return tid, actual_name

    def invite_member_cli(self, tid: str, uid_list: list,
                          name: str = None) -> Dict:
        """
        邀请成员加入已有群组。

        Args:
            tid:      群 ID
            uid_list: 被邀请成员的 uid 列表
            name:     群名（可选，用于返回值标注）

        Returns:
            {"tid": str, "name": str, "pass_num": int}
            注：群成员列表/总人数 popo-cli 无对应查询接口，不在返回值中

        Example:
            result = self.userA.cli.invite_member_cli(
                tid="8479417",
                uid_list=["grp.popoqa73@corp.netease.com"],
                name="测试群",
            )
            # result["pass_num"] == 1
        """
        uid_list_json = json.dumps(uid_list, ensure_ascii=False)
        data = _run(["team_invite", f"tid={tid}", f"inviteList={uid_list_json}"])
        pass_num = data.get("passNum", 0)
        logger.info(f"✅ 邀请入群: tid={tid} 入群={pass_num}人")
        return {"tid": tid, "name": name or "", "pass_num": pass_num}

    def kick_member_cli(self, tid: str, uid_list: list,
                        name: str = None) -> Dict:
        """
        从群组移除成员。

        Args:
            tid:      群 ID
            uid_list: 被移除成员的 uid 列表
            name:     群名（可选，用于返回值标注）

        Returns:
            {"tid": str, "name": str, "kicked_uids": list, "kicked_names": list}
            注：剩余成员列表/人数 popo-cli 无对应查询接口，不在返回值中

        Example:
            result = self.userA.cli.kick_member_cli(
                tid="8479417",
                uid_list=["grp.popoqa73@corp.netease.com"],
                name="测试群",
            )
            # result["kicked_names"] == ["grp73"]
        """
        uid_list_json = json.dumps(uid_list, ensure_ascii=False)
        _run(["team_kick_member", f"tid={tid}", f"toUids={uid_list_json}"])

        # 通过 userinfo_search 反查被移除人的姓名
        kicked_names = []
        for uid in uid_list:
            try:
                search_data = _run([
                    "userinfo_search",
                    f"query={uid}", "type=2", "page=0", "pageSize=3", "searchRange=1",
                ])
                persons = search_data.get("search_results", {}).get("person", [])
                if persons:
                    kicked_names.append(persons[0]["content"].get("name", "") or uid)
                else:
                    kicked_names.append(uid)
            except Exception:
                kicked_names.append(uid)

        logger.info(f"✅ 已移除成员: tid={tid} 移除={kicked_names}")
        return {
            "tid": tid,
            "name": name or "",
            "kicked_uids": uid_list,
            "kicked_names": kicked_names,
        }

    def update_team_name_cli(self, tid: str, name: str) -> Dict:
        """
        修改群名。

        Returns:
            {"tid": str, "name": str}

        Example:
            result = self.userA.cli.update_team_name_cli(tid="8479417", name="新群名")
            # result["name"] == "新群名"
        """
        _run(["team_update_team_name", f"tid={tid}", f"tname={name}"])
        logger.info(f"✅ 群名已修改: tid={tid} → '{name}'")
        return {"tid": tid, "name": name}

    # ==================== 消息上传辅助 ====================

    def _upload_image(self, image_path: str) -> str:
        """上传图片到 FP，返回永久 URL。"""
        fp_data = _run(["message_fp_upload_url"])
        upload_url = fp_data.get("uploadUrl", "")
        token = fp_data.get("token", "")
        if not upload_url or not token:
            raise RuntimeError(f"message_fp_upload_url 返回字段缺失: {fp_data}")

        file_size = os.path.getsize(image_path)
        stdout = _run_curl([
            "-s", "-X", "POST", upload_url,
            "-H", f"Authorization: {token}",
            "-H", f"Content-Length: {file_size}",
            "--data-binary", f"@{image_path}",
        ])
        try:
            resp = json.loads(stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"图片上传响应非 JSON: {stdout[:200]}")
        url = resp.get("url", "")
        if not url:
            raise RuntimeError(f"图片上传失败: {stdout[:200]}")
        logger.info(f"✅ 图片已上传: {url}")
        return url

    def _upload_file(self, file_path: str) -> Dict:
        """上传文件到 S3，返回发送消息所需的完整字段 dict。"""
        fname = os.path.basename(file_path)
        fext = os.path.splitext(fname)[1].lstrip(".")
        fsize = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            fhash = hashlib.md5(f.read()).hexdigest()

        # 获取 S3 上传地址
        s3_data = _run(["message_s3_ufile_upload", f"fsize={fsize}", f"fhash={fhash}"])
        upload_url = s3_data.get("url", "")
        object_key = s3_data.get("objectKey", "")
        bucket_name = s3_data.get("bucketName", "")
        if not upload_url:
            raise RuntimeError(f"message_s3_ufile_upload 返回字段缺失: {s3_data}")

        # curl PUT 上传
        stdout = _run_curl(["-s", "-w", "%{http_code}", "-T", file_path, upload_url])
        http_code = stdout.strip()[-3:] if len(stdout) >= 3 else ""
        if http_code != "200":
            raise RuntimeError(f"文件上传失败，HTTP {http_code}: {stdout[:200]}")

        # 上报完成 — fname 写临时文件避免中文乱码
        fname_tmp = os.path.join(tempfile.gettempdir(), "popo_fname.txt")
        with open(fname_tmp, "w", encoding="utf-8") as f:
            f.write(fname)
        try:
            complete_data = _run([
                "message_s3_ufile_upload_complete",
                f"fsize={fsize}", f"fhash={fhash}",
                f"objectKey={object_key}",
                f"fname=@text:{fname_tmp}",
                f"bucketName={bucket_name}",
                "clientType=3",
            ])
        finally:
            try:
                os.unlink(fname_tmp)
            except OSError:
                pass

        ufid = complete_data.get("ufid", "")
        ftype = complete_data.get("ftype", 0)
        logger.info(f"✅ 文件已上传: {fname} ufid={ufid}")
        return {
            "fileID": ufid,
            "md5": fhash,
            "format": fext,
            "artwork": "",
            "size": fsize,
            "type": 3,
            "externType": ftype,
            "objectKey": object_key,
            "name": fname,
        }

    def _do_send_file(self, send_cmd: str, target_arg: str,
                      file_path: str) -> Tuple[str, str]:
        """上传文件并发送，返回 (fname, file_path)。"""
        msg_dict = self._upload_file(file_path)
        fname = msg_dict["name"]

        msg_tmp = os.path.join(tempfile.gettempdir(), "popo_msg.json")
        with open(msg_tmp, "w", encoding="utf-8") as f:
            json.dump(msg_dict, f, ensure_ascii=False, separators=(",", ":"))
        try:
            _run([send_cmd, target_arg,
                  f"message=@text:{msg_tmp}", "msgType=3", "source=AGENT"])
        finally:
            try:
                os.unlink(msg_tmp)
            except OSError:
                pass
        logger.info(f"✅ 文件消息已发送: {fname}")
        return fname, file_path

    # ==================== 消息 ====================

    def send_message_p2p_cli(self, receiver: str, message: str = None,
                             image_path: str = None,
                             file_path: str = None) -> Union[str, Tuple[str, str]]:
        """
        向指定用户发送 P2P 消息（文本 / 图片 / 文件，三选一）。

        Args:
            receiver:   接收方 uid（邮箱格式）
            message:    文本消息内容
            image_path: 本地图片路径（.png / .jpg 等）
            file_path:  本地文件路径

        Returns:
            文本消息 → str（消息内容）
            图片消息 → str（图片路径）
            文件消息 → (filename: str, file_path: str)

        Example:
            msg        = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", message="123")
            path       = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", image_path="E:/shot.png")
            name, path = self.userA.cli.send_message_p2p_cli(receiver="grp.popoqa67@corp.netease.com", file_path="E:/report.pdf")
        """
        if message is not None:
            _run(["message_send_p2p", f"receiver={receiver}",
                  f"message={message}", "source=AGENT"])
            logger.info(f"✅ P2P 文本已发送: receiver={receiver}")
            return message
        elif image_path is not None:
            url = self._upload_image(image_path)
            _run(["message_send_p2p", f"receiver={receiver}",
                  f"message=[img]{url}[/img]", "source=AGENT"])
            logger.info(f"✅ P2P 图片已发送: receiver={receiver}")
            return image_path
        elif file_path is not None:
            return self._do_send_file(
                "message_send_p2p", f"receiver={receiver}", file_path)
        else:
            raise ValueError("message / image_path / file_path 必须三选一")

    def send_message_team_cli(self, tid: str, message: str = None,
                              image_path: str = None,
                              file_path: str = None) -> Union[str, Tuple[str, str]]:
        """
        向群组发送消息（文本 / 图片 / 文件，三选一）。

        Args:
            tid:        群 ID
            message:    文本消息内容
            image_path: 本地图片路径
            file_path:  本地文件路径

        Returns:
            文本消息 → str（消息内容）
            图片消息 → str（图片路径）
            文件消息 → (filename: str, file_path: str)

        Example:
            msg        = self.userA.cli.send_message_team_cli(tid="8479417", message="123")
            name, path = self.userA.cli.send_message_team_cli(tid="8479417", file_path="E:/doc.pdf")
        """
        if message is not None:
            _run(["message_send_team", f"receiver={tid}",
                  f"message={message}", "source=AGENT"])
            logger.info(f"✅ 群文本已发送: tid={tid}")
            return message
        elif image_path is not None:
            url = self._upload_image(image_path)
            _run(["message_send_team", f"receiver={tid}",
                  f"message=[img]{url}[/img]", "source=AGENT"])
            logger.info(f"✅ 群图片已发送: tid={tid}")
            return image_path
        elif file_path is not None:
            return self._do_send_file(
                "message_send_team", f"receiver={tid}", file_path)
        else:
            raise ValueError("message / image_path / file_path 必须三选一")

    # ==================== 日历 ====================

    def _get_schedule_detail(self, schedule_id: int) -> Dict:
        """查询日程详情，返回 detail dict。"""
        return _run(["calendar_schedule_detail", f"scheduleId={schedule_id}"])

    def create_schedule_cli(self, title: str, start_time: str, end_time: str,
                            participants: List[str] = None,
                            location: str = None,
                            content: str = None) -> Dict:
        """
        创建日程/会议。

        Args:
            title:        会议标题
            start_time:   开始时间（ISO-8601，如 '2026-06-10T14:00:00+08:00'）
            end_time:     结束时间（ISO-8601）
            participants: 参与人 uid 列表（可选）
            location:     地点（可选）
            content:      备注（可选）

        Returns:
            {"schedule_id": int, "title": str, "participants": list[str]}

        Example:
            info = self.userA.cli.create_schedule_cli(
                title="项目评审",
                start_time="2026-06-10T14:00:00+08:00",
                end_time="2026-06-10T15:00:00+08:00",
                participants=["grp.popoqa67@corp.netease.com"],
            )
        """
        args = [
            "calendar_schedule_create",
            f"title={title}",
            f"startTime={start_time}",
            f"endTime={end_time}",
        ]
        if participants:
            args.append(f"participants={json.dumps(participants, ensure_ascii=False)}")
        if location:
            args.append(f"location={location}")
        if content:
            args.append(f"content={content}")

        data = _run(args)
        schedule_id = data.get("scheduleId")
        logger.info(f"✅ 日程已创建: '{title}' scheduleId={schedule_id}")
        return {
            "schedule_id": schedule_id,
            "title": title,
            "participants": participants or [],
        }

    def update_schedule_cli(self, schedule_id: int,
                            title: str = None,
                            start_time: str = None,
                            end_time: str = None,
                            add_participants: List[str] = None,
                            remove_participants: List[str] = None,
                            location: str = None,
                            content: str = None) -> Dict:
        """
        修改日程，返回修改后的完整会议信息（操作后自动查询 detail）。

        Returns:
            {"schedule_id": int, "title": str, "start_time": str,
             "end_time": str, "participants": list[{"uid", "name"}]}

        Example:
            info = self.userA.cli.update_schedule_cli(
                schedule_id=109335848,
                title="新会议名",
                start_time="2026-06-10T15:00:00+08:00",
                end_time="2026-06-10T16:00:00+08:00",
            )
        """
        args = ["calendar_schedule_update", f"scheduleId={schedule_id}"]
        if title:
            args.append(f"title={title}")
        if start_time:
            args.append(f"startTime={start_time}")
        if end_time:
            args.append(f"endTime={end_time}")
        if add_participants:
            args.append(f"addParticipants={json.dumps(add_participants, ensure_ascii=False)}")
        if remove_participants:
            args.append(f"removeParticipants={json.dumps(remove_participants, ensure_ascii=False)}")
        if location:
            args.append(f"location={location}")
        if content:
            args.append(f"content={content}")

        _run(args)

        detail = self._get_schedule_detail(schedule_id)
        result = {
            "schedule_id": detail.get("id"),
            "title": detail.get("title", ""),
            "start_time": detail.get("startTime", ""),
            "end_time": detail.get("endTime", ""),
            "participants": [
                {"uid": p["uid"], "name": p.get("name", "")}
                for p in detail.get("participants", [])
            ],
        }
        logger.info(f"✅ 日程已修改: scheduleId={schedule_id} title='{result['title']}'")
        return result

    def confirm_schedule_cli(self, schedule_id: int, status: int) -> Dict:
        """
        接受或拒绝日程邀请（操作前先查询 detail 取日程信息）。

        Args:
            schedule_id: 日程 ID
            status:      1=接受，2=拒绝

        Returns:
            {"schedule_id": int, "title": str,
             "participants": list[{"uid", "name"}]}

        Example:
            info = self.userA.cli.confirm_schedule_cli(schedule_id=109335848, status=1)
        """
        detail = self._get_schedule_detail(schedule_id)
        title = detail.get("title", "")
        participants = [
            {"uid": p["uid"], "name": p.get("name", "")}
            for p in detail.get("participants", [])
        ]

        _run(["calendar_schedule_confirm",
              f"scheduleId={schedule_id}", f"status={status}"])

        action = "接受" if status == 1 else "拒绝"
        logger.info(f"✅ 已{action}日程: '{title}' scheduleId={schedule_id}")
        return {
            "schedule_id": schedule_id,
            "title": title,
            "participants": participants,
        }

    def quit_schedule_cli(self, schedule_id: int) -> Dict:
        """
        退出日程（操作前先查询 detail 取日程名称）。

        Returns:
            {"schedule_id": int, "title": str}

        Example:
            info = self.userA.cli.quit_schedule_cli(schedule_id=109335848)
        """
        detail = self._get_schedule_detail(schedule_id)
        title = detail.get("title", "")

        _run(["calendar_schedule_quit", f"scheduleId={schedule_id}"])
        logger.info(f"✅ 已退出日程: '{title}' scheduleId={schedule_id}")
        return {"schedule_id": schedule_id, "title": title}
