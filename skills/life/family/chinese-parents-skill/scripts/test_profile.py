#!/usr/bin/env python3
"""
profile.py 的自校验测试。纯标准库 unittest，无依赖。

    python3 scripts/test_profile.py           跑全部
    python3 scripts/test_profile.py -v        看每条

为什么必须有这个文件：v0.4 的 README 写着"48 个动力学数值与文档速查表逐一校验一致"，
那是我一次性手验的结果——没有任何机制阻止下一次改公式时把它悄悄改坏。
文档里的每一个数字都是承诺，这里把承诺变成断言。

断言的事实来源：
  references/dimensions.md 第二、五节（锚点向量、相似度算例）
  references/dynamics.md   第一、二、四~七节（六个量、速查表、词条表、7.2 推演）
测试挂了先看是不是文档改了，别急着改测试。
"""

import os
import unittest

import profile as P


# ---------------------------------------------------------------- 文档基准

# dynamics.md 第二节「全锚点速查表」，一个数字都不能差
ANCHOR_DYNAMICS = {
    #              TEMP0  K     D     COOL BOND0 YIELD
    "虎妈虎爸":   (29, 1.43, 0.82, 3, 62, 80),
    "鸡娃家长":   (22, 1.52, 1.02, 3, 74, 70),
    "直升机父母": (20, 1.58, 0.94, 2, 64, 68),
    "佛系家长":   (5,  0.60, 1.16, 7, 85, 29),
    "开明家长": (5,  0.65, 1.26, 7, 91, 34),
    "强势家长": (37, 1.51, 0.68, 3, 50, 89),
    "诈尸式育儿": (18, 1.24, 0.70, 4, 46, 52),   # K 已含诈尸式修正 +0.25
    "丧偶式育儿": (5,  0.61, 0.69, 5, 45, 34),
}

# dimensions.md 第五节算例
SIM_CASE = dict(CTL=75, WRM=55, INV=70, ANX=80, COM=40,
                VAL=45, FIN=50, EXP=85, SOC=40, IND=55)

# dynamics.md 7.2 逐轮：(轮末 TEMP, 轮末 BOND, 累计说服)
DEMO_ROUNDS = [(42, 69, 0), (75, 69, 0), (98, 61, 0), (98, 53, 0), (64, 53, 30)]


class TestKernel(unittest.TestCase):
    """内核常量与基础计算"""

    def test_dims_complete(self):
        self.assertEqual(len(P.DIMS), 10)
        self.assertEqual(set(P.DIMS), set(P.DIM_CN))
        self.assertEqual(set(P.DIMS), set(P.BANDS_4) | set(P.BANDS_3))
        self.assertFalse(set(P.BANDS_4) & set(P.BANDS_3), "一个维度不能同时是 4 档和 3 档")

    def test_anchors_wellformed(self):
        for name, vec in P.ANCHORS.items():
            self.assertEqual(set(vec), set(P.DIMS), f"{name} 维度不全")
            for d, v in vec.items():
                self.assertTrue(0 <= v <= 100, f"{name}.{d}={v} 越界")

    def test_band_boundaries(self):
        # 4 档：0-24 / 25-49 / 50-74 / 75-100
        for v, i in ((0, 0), (24, 0), (25, 1), (49, 1), (50, 2), (74, 2), (75, 3), (100, 3)):
            self.assertEqual(P.band_index("CTL", v), i, f"CTL={v}")
        # 3 档：0-33 / 34-66 / 67-100
        for v, i in ((0, 0), (33, 0), (34, 1), (66, 1), (67, 2), (100, 2)):
            self.assertEqual(P.band_index("VAL", v), i, f"VAL={v}")

    def test_half_up(self):
        # 银行家舍入会给出 0 / 2 / 1.42，这里必须是 1 / 3 / 1.43
        self.assertEqual(P._round(0.5), 1)
        self.assertEqual(P._round(2.5), 3)
        self.assertEqual(P._round2(1.425), 1.43)
        self.assertEqual(P._round2(0.645), 0.65)  # 民主型 K 的真实取值
        # ROUND_HALF_UP 对负数是"远离零"，−0.5 → −1。引擎里所有取整对象
        # （TEMP/BOND/Δ）都先 clamp 到非负，走不到这条分支，钉住行为免得误用。
        self.assertEqual(P._round(-0.5), -1)

    def test_similarity_uses_half_up(self):
        """总差 350 → 65.0，内置 round() 在 .5 边界会偏，这里必须稳定"""
        a = {d: 0 for d in P.DIMS}
        b = {d: 35 for d in P.DIMS}
        self.assertEqual(P.similarity(a, b), 65)
        self.assertEqual(P.similarity(a, a), 100)
        far = {d: 100 for d in P.DIMS}
        self.assertEqual(P.similarity(a, far), 0)


class TestSimilarity(unittest.TestCase):
    """dimensions.md 第五节算例"""

    def test_doc_example(self):
        self.assertEqual(P.similarity(SIM_CASE, P.ANCHORS["虎妈虎爸"]), 85)
        self.assertEqual(P.similarity(SIM_CASE, P.ANCHORS["鸡娃家长"]), 92)

    def test_ranking_and_floor(self):
        ranked = P.rank_anchors(SIM_CASE)
        self.assertEqual(ranked[0]["type"], "鸡娃家长")
        self.assertTrue(all(r["similarity"] >= 55 for r in ranked),
                        "低于 55% 不展示——硬报出来是误导")
        gaps = {g["dim"] for g in ranked[0]["top_gaps"]}
        self.assertIn("FIN", gaps, "文档指明主要差异在经济投入")

    def test_symmetry(self):
        a, b = P.ANCHORS["虎妈虎爸"], P.ANCHORS["佛系家长"]
        self.assertEqual(P.similarity(a, b), P.similarity(b, a))


class TestAnchorDynamics(unittest.TestCase):
    """dynamics.md 第二节速查表，8 锚点 × 6 个量 = 48 个数字"""

    def test_all_48_values(self):
        for name, (t0, k, d, cool, b0, y) in ANCHOR_DYNAMICS.items():
            with self.subTest(anchor=name):
                got = P.dynamics(P.ANCHORS[name])
                self.assertEqual(got["TEMP0"], t0, "TEMP₀")
                self.assertEqual(got["K"], k, "K")
                self.assertEqual(got["D"], d, "D")
                self.assertEqual(got["COOL"], cool, "COOL")
                self.assertEqual(got["BOND0"], b0, "BOND₀")
                self.assertEqual(got["YIELD"], y, "YIELD")

    def test_clamps(self):
        for name in P.ANCHORS:
            dyn = P.dynamics(P.ANCHORS[name])
            self.assertTrue(5 <= dyn["TEMP0"] <= 60, name)
            self.assertTrue(0.6 <= dyn["K"] <= 1.8, name)
            self.assertTrue(0.6 <= dyn["D"] <= 1.4, name)
            self.assertTrue(1 <= dyn["COOL"] <= 10, name)

    def test_cold_parent_temp_cap(self):
        """WRM≤20 且 INV≤20 → TEMP 上限锁 35（反套路第一条）"""
        self.assertEqual(P.dynamics(P.ANCHORS["丧偶式育儿"])["TEMP_CAP"], 35)
        self.assertEqual(P.dynamics(P.ANCHORS["虎妈虎爸"])["TEMP_CAP"], 100)


class TestCouplings(unittest.TestCase):
    """dimensions.md 第七节耦合规则"""

    def _names(self, p):
        return {h["name"] for h in P.hit_couplings(p)}

    def test_zombie_needs_ctl(self):
        """
        丧偶式不该命中诈尸式——这是 v0.4 修过的致命 bug，钉死防回归。
        两者 INV/COM 都极低，区别在 CTL：一个是"不管但会突然接管"，
        一个是"彻底退出"。少了 CTL≥25，丧偶式会被误加 K +0.25。
        """
        self.assertIn("诈尸式", self._names(P.ANCHORS["诈尸式育儿"]))
        self.assertNotIn("诈尸式", self._names(P.ANCHORS["丧偶式育儿"]))
        widow = P.dynamics(P.ANCHORS["丧偶式育儿"])
        self.assertNotIn("诈尸式修正 K +0.25", " ".join(widow["notes"]))

    def test_known_couplings(self):
        self.assertIn("高压无温度", self._names(P.ANCHORS["强势家长"]))
        self.assertIn("爱与成绩挂钩", self._names(P.ANCHORS["虎妈虎爸"]))
        self.assertIn("焦虑变现", self._names(P.ANCHORS["鸡娃家长"]))
        self.assertIn("假民主", self._names(dict(P.ANCHORS["开明家长"], CTL=80, COM=85)))

    def test_extremes_flagged(self):
        """极端维度 = ≥85 或 ≤15。WRM=18 差三分不算，边界不能松"""
        ext = {e["dim"] for e in P.extremes(P.ANCHORS["强势家长"])}
        self.assertEqual(ext, {"CTL", "COM", "VAL", "EXP", "SOC", "IND"})
        self.assertNotIn("WRM", ext, "WRM=18 未达 ≤15，不该混进人格底色")


class TestMoveTables(unittest.TestCase):
    """dynamics.md 4.2 / 4.3 词条表完整性"""

    def test_counts(self):
        self.assertEqual(len(P.TRIGGERS), 21, "雷区表应有 T1–T21")
        self.assertEqual(len(P.COOLERS), 19, "破冰表应有 C1–C19")
        self.assertEqual(list(P.TRIGGERS), [f"T{i}" for i in range(1, 22)])
        self.assertEqual(list(P.COOLERS), [f"C{i}" for i in range(1, 20)])

    def test_shapes(self):
        for mid, (name, line, base, bonuses) in P.TRIGGERS.items():
            self.assertTrue(name and line, mid)
            self.assertTrue(base > 0, f"{mid} 雷区基础值应为正")
            for cond, val in bonuses:
                self.assertTrue(val > 0 and callable(cond), mid)
        for mid, (name, line, base, bonuses, hot) in P.COOLERS.items():
            self.assertTrue(name and line, mid)
            self.assertTrue(base > 0, f"{mid} 破冰基础值以正数存储，取负在计算时做")
            self.assertIsInstance(hot, bool, mid)

    def test_hot_items(self):
        """爆发区仍生效的只有这五条，多一条少一条都会让高温区演错"""
        hot = {m for m, v in P.COOLERS.items() if v[4]}
        self.assertEqual(hot, {"C8", "C13", "C17", "C18", "C19"})

    def test_bonus_takes_max_not_sum(self):
        """T1 对 CTL=72/IND=32 的画像应取 10（IND）而不是 8+10=18"""
        p = dict(P.DEMO_PROFILE)
        self.assertEqual(P._best_bonus(p, P.TRIGGERS["T1"][3]), 10)
        # C13 无条件通用，加成恒为 0
        self.assertEqual(P._best_bonus(p, P.COOLERS["C13"][3]), 0)

    def test_t12_highest_base(self):
        bases = {m: v[2] for m, v in P.TRIGGERS.items()}
        self.assertEqual(max(bases, key=bases.get), "T12", "既成事实基础伤害最高")


class TestSimulateDemo(unittest.TestCase):
    """dynamics.md 7.2 五轮完整推演，逐轮对账"""

    @classmethod
    def setUpClass(cls):
        cls.sim = P.simulate(P.DEMO_PROFILE, P.DEMO_MOVES)

    def test_initial_values(self):
        dyn = self.sim["dynamics"]
        self.assertEqual((dyn["TEMP0"], dyn["K"], dyn["D"], dyn["COOL"],
                          dyn["BOND0"], dyn["YIELD"]),
                         (24, 1.30, 0.94, 4, 69, 70))

    def test_round_by_round(self):
        for r, (temp, bond, persuade) in zip(self.sim["rounds"], DEMO_ROUNDS):
            with self.subTest(round=r["n"], move=r["move"]):
                self.assertEqual(r["temp"], temp, "轮末 TEMP")
                self.assertEqual(r["bond"], bond, "轮末 BOND")
                self.assertEqual(r["persuade"], persuade, "累计说服")

    def test_cap_applied(self):
        """第 2、3 轮原始伤害都超 35，必须封顶"""
        r2, r3 = self.sim["rounds"][1], self.sim["rounds"][2]
        self.assertEqual(r2["temp_peak"] - r2["temp_before"], 35)
        self.assertEqual(r3["temp_peak"], 100, "75+35 溢出后 clamp 到 100")

    def test_backfire_in_burst_zone(self):
        """第 4 轮 C2 非[高温]条目，在爆发区失效并反噬 +10，且不计说服"""
        r4 = self.sim["rounds"][3]
        self.assertEqual(r4["temp_peak"], 100)
        self.assertEqual(r4["persuade"], 0, "TEMP≥85 时说的道理她没听见")
        self.assertIn("反噬", " ".join(r4["log"]))

    def test_hot_cooler_rescues(self):
        """第 5 轮 C18 是 [高温] 条目，×1.5 后封顶 −30，说服 +30"""
        r5 = self.sim["rounds"][4]
        self.assertEqual(r5["temp_before"] - r5["temp_peak"], 30)
        self.assertEqual(r5["persuade"], 30)

    def test_settlement(self):
        s = self.sim
        self.assertEqual((s["temp_start"], s["temp_end"]), (24, 64))
        self.assertEqual((s["bond_start"], s["bond_end"]), (69, 50))
        self.assertEqual(s["hot_rounds"], 4, "第 2–5 轮轮末都在 61+")
        self.assertEqual(s["persuade"], 30)
        self.assertEqual(s["verdict"], "不让步")

    def test_worst_move_is_boundary_claim(self):
        """
        文档点名第 3 轮「这是我自己的事」是最贵的一句。
        按 TEMP 升幅算，第 2、3 轮都封顶 35 打平；真正拉开差距的是 BOND。
        """
        self.assertEqual(self.sim["worst_move"]["n"], 3)
        self.assertEqual(self.sim["worst_move"]["move"], "T1")

    def test_alternative_path_from_doc(self):
        """
        7.2 结尾「换个打法」：第 3 轮改用 C14 让渡决定，
        (18 + CTL≥70 加成 10) × 0.94 = 26，说服 26 + 首次让渡 8 = 34
        """
        sim = P.simulate(P.DEMO_PROFILE, ["T21", "T9", "C14"])
        r3 = sim["rounds"][2]
        self.assertEqual(r3["temp_before"] - r3["temp_peak"], 26)
        self.assertEqual(r3["temp"], 45, "75 → 49 → 冷却 −4 → 45，避开爆发区")
        self.assertEqual(sim["persuade"], 34)
        self.assertEqual(sim["bond_end"], 69, "BOND 一分不掉")


class TestSimulateRules(unittest.TestCase):
    """状态机的规则分支"""

    NORMAL = dict(P.DEMO_PROFILE)

    def test_repeat_decay(self):
        """同一条破冰第二次 ×0.5，第三次起 ×0"""
        sim = P.simulate(self.NORMAL, ["C13", "C13", "C13"])
        cuts = [r["temp_before"] - r["temp_peak"] for r in sim["rounds"]]
        self.assertEqual(cuts[0], 8)          # 8 × 0.94 = 7.52 → 8
        self.assertEqual(cuts[1], 4)          # × 0.5 → 3.76 → 4
        self.assertEqual(cuts[2], 0)          # 第三次归零，她听出来了
        self.assertIn("话术", " ".join(sim["rounds"][2]["log"]))

    def test_first_time_bonuses_once(self):
        """C3 首次给期限 +10，第二次不再给"""
        sim = P.simulate(self.NORMAL, ["C3", "C3"])
        logs = [" ".join(r["log"]) for r in sim["rounds"]]
        self.assertIn("首次给出明确期限", logs[0])
        self.assertNotIn("首次给出明确期限", logs[1])

    def test_c14_capped_at_two(self):
        """让渡决定权最多计 2 次"""
        sim = P.simulate(self.NORMAL, ["C14", "C14", "C14"])
        self.assertEqual(sum("让渡决定权" in l for r in sim["rounds"]
                             for l in r["log"]), 2)

    def test_cold_mode(self):
        """BOND≤20：升温系数 ×0，TEMP 上限锁 40，判定走冷让步"""
        sim = P.simulate(self.NORMAL, ["T12", "T2"], bond=15)
        self.assertTrue(all(r["temp"] <= 40 for r in sim["rounds"]))
        self.assertEqual(sim["verdict"], "冷让步")
        self.assertIn("冷处理", " ".join(sim["rounds"][0]["log"]))

    def test_fake_democracy_forced(self):
        """假民主：攒满说服力也强制假让步·条件型"""
        p = dict(self.NORMAL, COM=85, CTL=80)
        sim = P.simulate(p, ["C3", "C7", "C9", "C14", "C16", "C4"])
        self.assertGreaterEqual(sim["persuade"], sim["yield"])
        self.assertEqual(sim["verdict"], "假让步·条件型")

    def test_real_concession(self):
        """低 YIELD + 低温 + 足够 BOND → 真让步"""
        sim = P.simulate(P.ANCHORS["开明家长"], ["C3", "C2", "C7"])
        self.assertLessEqual(sim["temp_end"], 35)
        self.assertGreaterEqual(sim["persuade"], sim["yield"])
        self.assertEqual(sim["verdict"], "真让步")

    def test_anx85_self_heating(self):
        """ANX≥85：轮末不冷却反而 +5，沉默是燃料"""
        p = dict(self.NORMAL, ANX=90)
        sim = P.simulate(p, ["C13", "C13"])
        self.assertIn("灾难化推演", " ".join(sim["rounds"][0]["log"]))
        self.assertEqual(sim["rounds"][0]["cool"], -5)

    def test_c18_fails_on_cold_parent(self):
        """WRM≤24 时 C18 示弱本条失效——她会读成软弱"""
        p = dict(self.NORMAL, WRM=18)
        sim = P.simulate(p, ["C18"])
        self.assertEqual(sim["rounds"][0]["temp_peak"], sim["rounds"][0]["temp_before"])
        self.assertIn("失效", " ".join(sim["rounds"][0]["log"]))

    def test_bond_direct_damage(self):
        """T2 / T14 / T18 无论温度多少都额外扣 BOND −3"""
        for mid in ("T2", "T14", "T18"):
            sim = P.simulate(P.ANCHORS["开明家长"], [mid])
            self.assertLessEqual(sim["bond_end"], sim["bond_start"] - 3, mid)

    def test_guilt_multiplier(self):
        """甜蜜的窒息：BOND 扣减 ×1.5，且 C5/C6/C10 借愧疚要还"""
        p = dict(self.NORMAL, CTL=75, WRM=75)
        sim = P.simulate(p, ["C5"])
        self.assertIn("愧疚", " ".join(sim["rounds"][0]["log"]))
        self.assertLess(sim["bond_end"], sim["bond_start"])

    def test_channel_discount(self):
        """
        非当面升温 ×0.8，微信文字再打八折。
        用 T21 不用 T9——T9 三种渠道都会撞 +35 封顶，测不出差别。
        """
        rise = lambda s: s["rounds"][0]["temp_peak"] - s["rounds"][0]["temp_before"]
        face = rise(P.simulate(self.NORMAL, ["T21"], channel="face"))
        phone = rise(P.simulate(self.NORMAL, ["T21"], channel="phone"))
        wechat = rise(P.simulate(self.NORMAL, ["T21"], channel="wechat"))
        self.assertEqual((face, phone, wechat), (20, 16, 12))

    def test_channel_bond_damage_heavier(self):
        """挂断本身就是伤害：非当面 BOND 扣减 ×1.2"""
        face = P.simulate(self.NORMAL, ["T2"], channel="face")
        phone = P.simulate(self.NORMAL, ["T2"], channel="phone")
        self.assertLess(phone["bond_end"], face["bond_end"])

    def test_temp_never_out_of_range(self):
        """任何画像 × 任何长序列，TEMP/BOND 都不许越界"""
        moves = list(P.TRIGGERS) + list(P.COOLERS)
        for name, vec in P.ANCHORS.items():
            sim = P.simulate(vec, moves)
            for r in sim["rounds"]:
                self.assertTrue(0 <= r["temp"] <= 100, f"{name} 第 {r['n']} 轮 TEMP")
                self.assertTrue(0 <= r["bond"] <= 100, f"{name} 第 {r['n']} 轮 BOND")

    def test_unknown_move_rejected(self):
        with self.assertRaises(ValueError):
            P.simulate(self.NORMAL, ["T99"])

    def test_empty_moves(self):
        sim = P.simulate(self.NORMAL, [])
        self.assertEqual(sim["rounds"], [])
        self.assertEqual(sim["temp_end"], sim["temp_start"])


class TestQuiz(unittest.TestCase):
    """30 题快测"""

    def test_structure(self):
        self.assertEqual(len(P.QUIZ), 30)
        counts = {}
        for dim, q, opts in P.QUIZ:
            self.assertIn(dim, P.DIMS)
            self.assertEqual(len(opts), 4, q)
            self.assertEqual(len(set(opts)), 4, f"选项重复：{q}")
            counts[dim] = counts.get(dim, 0) + 1
        self.assertEqual(set(counts.values()), {3}, "每个维度必须正好 3 题")

    def test_monotonic_extremes(self):
        """全 a 和全 d 必须落在相反两端，否则题目方向写反了"""
        low = P.from_answers("a" * 30)
        high = P.from_answers("d" * 30)
        for d in P.DIMS:
            self.assertLess(low[d], high[d], d)

    def test_answer_length_validated(self):
        with self.assertRaises(ValueError):
            P.from_answers("abc")

    def test_dump_quiz_covers_all(self):
        md = P.dump_quiz()
        for i, (dim, q, opts) in enumerate(P.QUIZ, 1):
            self.assertIn(q, md, f"第 {i} 题没导出")


class TestInput(unittest.TestCase):
    """输入解析与缺失维度推断"""

    def test_scores_parsing(self):
        p = P.from_scores("CTL=75, anx=80 ,COM=10")
        self.assertEqual(p, {"CTL": 75, "ANX": 80, "COM": 10})

    def test_scores_clamped(self):
        p = P.from_scores("CTL=999,WRM=-50")
        self.assertEqual(p["CTL"], 100)
        self.assertEqual(p["WRM"], 0)

    def test_scores_rejects_garbage(self):
        for bad in ("CTL", "XXX=50", "CTL=abc"):
            with self.assertRaises(ValueError, msg=bad):
                P.from_scores(bad)

    def test_confidence_three_levels(self):
        """给了 CTL 就能推 COM/IND/SOC；ANX 之外的维度无依据，必须标 blind"""
        p, missing, conf = P.infer_missing({"CTL": 90})
        self.assertEqual(conf["CTL"], "known")
        self.assertEqual(conf["COM"], "inferred")
        self.assertEqual(conf["IND"], "inferred")
        self.assertEqual(conf["FIN"], "blind", "没有任何规则能推出 FIN，不许假装知道")
        self.assertEqual(set(P.DIMS) - {"CTL"}, set(missing))

    def test_no_missing_means_all_known(self):
        full = dict(P.ANCHORS["虎妈虎爸"])
        p, missing, conf = P.infer_missing(full)
        self.assertEqual(missing, [])
        self.assertTrue(all(v == "known" for v in conf.values()))

    def test_inference_direction(self):
        """高控制推出的沟通必须偏低，不能是 50"""
        p, _, _ = P.infer_missing({"CTL": 95})
        self.assertLess(p["COM"], 40)
        self.assertLess(p["IND"], 40)


class TestNoFakeNumbers(unittest.TestCase):
    """
    信息不足时不许输出看起来很专业的假数字。

    只给一个 CTL=90，v0.4 会一脸认真地报"虎妈虎爸 84%"——那 84% 是拿
    六个硬填的 50 算出来的回声。宁可不报。
    """

    ONE_DIM = {"CTL": 90}

    def test_tainted_dynamics_tracked(self):
        _, _, conf = P.infer_missing(self.ONE_DIM)
        bad = P.tainted(conf)
        self.assertIn("TEMP0", bad)
        self.assertIn("ANX", bad["TEMP0"], "TEMP₀ 权重最大的那一维是硬填的")
        self.assertIn("WRM", bad["D"])
        self.assertNotIn("CTL", sum(bad.values(), []), "CTL 是用户给的，不算污染源")

    def test_full_profile_is_clean(self):
        _, _, conf = P.infer_missing(dict(P.ANCHORS["虎妈虎爸"]))
        self.assertEqual(P.tainted(conf), {})
        self.assertEqual(P.blind_dims(conf), [])

    def test_similarity_suppressed(self):
        p, missing, conf = P.infer_missing(self.ONE_DIM)
        self.assertGreaterEqual(len(P.blind_dims(conf)), P.SIM_BLIND_LIMIT)
        out = P.render(p, missing, conf)
        self.assertIn("不报", out)
        self.assertIn("回声", out)
        self.assertNotIn("虎妈虎爸  ", out, "抑制之后不许再出现相似度排名")

    def test_similarity_kept_when_enough_info(self):
        """够 7 维就照常报——抑制的是无依据，不是保守"""
        seven = {d: 60 for d in P.DIMS[:7]}
        p, missing, conf = P.infer_missing(seven)
        self.assertLess(len(P.blind_dims(conf)), P.SIM_BLIND_LIMIT)
        self.assertNotIn("回声", P.render(p, missing, conf))

    def test_advice_suppressed(self):
        """被污染的量不许出读法，基于虚数的建议比不给更危险"""
        p, _, conf = P.infer_missing(self.ONE_DIM)
        advice = P.read_advice(p, P.dynamics(p), P.tainted(conf), conf)
        self.assertTrue(any("撑不起" in a for a in advice))
        self.assertFalse(any("让步阈值" in a for a in advice))

    def test_coupling_verdict_needs_known_dims(self):
        """假民主是定性结论，靠推断值不能下"""
        p, _, conf = P.infer_missing({"CTL": 90})   # COM 由 CTL 推出
        advice = P.read_advice(p, P.dynamics(p), P.tainted(conf), conf)
        self.assertFalse(any("假民主" in a for a in advice))
        full = dict(P.ANCHORS["开明家长"], CTL=80, COM=85)
        advice2 = P.read_advice(full, P.dynamics(full), {},
                                {d: "known" for d in P.DIMS})
        self.assertTrue(any("假民主" in a for a in advice2))

    def test_json_exposes_flags(self):
        _, _, conf = P.infer_missing(self.ONE_DIM)
        self.assertEqual(len(P.blind_dims(conf)), 6)
        self.assertFalse(len(P.blind_dims(conf)) < P.SIM_BLIND_LIMIT)


class TestRender(unittest.TestCase):
    """输出不许崩，也不许把 ?? 藏起来"""

    def test_render_full(self):
        p, missing, conf = P.infer_missing(dict(P.ANCHORS["强势家长"]))
        out = P.render(p, missing, conf)
        self.assertIn("中国式家长维度画像", out)
        self.assertIn("强势家长", out)

    def test_render_marks_blind(self):
        p, missing, conf = P.infer_missing({"CTL": 90})
        out = P.render(p, missing, conf)
        self.assertIn("??", out)
        self.assertIn("一律作废", out)

    def test_render_sim(self):
        out = P.render_sim(P.simulate(P.DEMO_PROFILE, P.DEMO_MOVES))
        for token in ("【建档】", "【结算】", "判定：", "最贵的一句"):
            self.assertIn(token, out)

    def test_list_moves(self):
        out = P.list_moves(P.DEMO_PROFILE)
        self.assertIn("T21", out)
        self.assertIn("C19", out)

    def test_all_anchors_render(self):
        for name, vec in P.ANCHORS.items():
            with self.subTest(anchor=name):
                P.render(dict(vec), [], {d: "known" for d in P.DIMS})
                P.render_sim(P.simulate(vec, ["T9", "C13", "C18"]))


class TestQuirksDoc(unittest.TestCase):
    """神人家长魔怔案例集不是普通文案，是 AI 学'无逻辑情绪输出'的训练数据。

    这份文件最容易在'顺手精简'时被砍成几句标语——一旦砍了，AI 又会
    回到用因果连贯框架演神人家长的老毛病。这里把'有足够多的模板和案例'
    钉成结构断言，删减会当场挂。
    """

    DOC = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "references", "quirks.md"
    )

    def setUp(self):
        with open(self.DOC, encoding="utf-8") as fh:
            self.text = fh.read()

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.DOC), "references/quirks.md 缺失")

    def test_meta_features_present(self):
        # 元认知必须点明'无逻辑 / 无因果 / 纯情绪输出'，否则就不是在教 AI 反逻辑
        self.assertIn("无逻辑", self.text)
        self.assertIn("无因果", self.text)
        self.assertIn("纯情绪输出", self.text)

    def test_enough_templates(self):
        # 第二节 17 种奇葩思维模板 + 大量场景章节，给 AI 足够的'套路库'
        self.assertGreaterEqual(self.text.count("### "), 95,
                                "思维模板/场景章节数偏少，疑似被精简")

    def test_enough_cases(self):
        # 第三节按场景铺开的案例，每条带【原话】；要'各种各样'，数量不能塌
        self.assertGreaterEqual(self.text.count("**【原话】**"), 110,
                                "魔怔案例数偏少，AI 学不到足够多样性")
        self.assertGreaterEqual(self.text.count("**【情境】**"), 110,
                                "魔怔案例情境数偏少")
        # 每条案例都要解释'神人在哪'，这是教 AI 识别无逻辑的关键
        self.assertGreaterEqual(self.text.count("**【神人在哪】**"), 110,
                                "缺'神人在哪'分析，案例只是语录不是教材")


if __name__ == "__main__":
    unittest.main(verbosity=2)
