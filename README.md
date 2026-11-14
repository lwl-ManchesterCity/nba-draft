# NBA 单赛季选秀模拟器

Node.js 运行：`npm install`，`npm run dev` 同时启动前后端（前端 http://127.0.0.1:5188，API 端口 3018）；`npm run build` 后用 `npm run start` 启动生产服务（3018 端口）。`npm run players:fetch` 刷新快照。`npm test` 运行单元测试；启动开发服务后用 `npm run test:ui` 运行浏览器测试，需本机 Chrome。

数据为 ESPN 2024–25、2025–26 赛季枚举中可取得统计、至少一个赛季出场 20 场且场均至少 15 分钟的球员，不保证覆盖全部当季球员；快照记录 404 和失败数。球员球队来自 ESPN 赛季资料；缺失显示破折号。头像来自 ESPN；其权利属于相应权利人，仓库不提供第三方图片或数据的使用授权。

护框是盖帽、篮板和身高构成的代理指标；持球负荷是出手、罚球和失误的每 36 分钟代理，不是官方使用率。复盘中本地胜率是主观规则估计。

阈值使用规格起始值，不为命中率强行调整。当前快照的命中率：持球创造 14.9%、空间 50.0%、护框 21.8%、外线换防 38.6%、组织 30.8%、篮板 22.1%、效率 37.3%。持球创造、护框、篮板低于 30%，因此不参与短板判定；这些阈值旨在识别较突出的能力，不能视为球员没有相应能力。

八维球员对比使用额外赛季快照：BPM 来自 [nba-chemistry 数据集](https://github.com/gh1sung/nba-chemistry/blob/main/data/bpm_2024_25.csv)（项目说明为 Basketball-Reference 数据）；防守时对手命中率及防守出手来自 [NBA 防守投篮追踪缓存](https://github.com/maxhostetter-eng/nba-defensive-shot-tracking-analysis/blob/main/nba_player_defense_cache.csv)。`python3 scripts/import-advanced.py` 按球员姓名和赛季场次匹配，交易球员取合计行；有歧义或未匹配则留空。统计为 304/308 BPM、307/308 防守追踪；数据来自第三方缓存，可能存在来源错误，防守命中率受出手位置和样本量影响。

当前球员池覆盖 2024–25 和 2025–26 常规赛：至少一个赛季出场 20 场且场均 15 分钟。双赛季基本权重分别为 35% 和 65%，不足 20 场的赛季按场次比例降低权重后重新归一化；只出现一个赛季时使用该赛季。得分、篮板、助攻、盖帽、抢断、失误与 PER 为加权赛季值，TS% 使用加权场均得分、出手和罚球出手计算。复盘可展开各赛季原始数据。默认综合排序依照 PER、ESPN 综合评分与上场时间计算，属于数据模型，不是官方能力值。

中锋对位图的“内线战术进攻”使用 [sportsdataverse NBA Synergy 快照](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/nba_stats_synergy)的顺下、低位、空切回合；“篮下防守（追踪）”使用 [NBA 防守追踪缓存](https://github.com/maxhostetter-eng/nba-defensive-shot-tracking-analysis) 的篮下防守命中率差，并不等于协防能力。合并两季时沿用球员赛季权重，有数据的赛季重新归一化；战术每季至少30回合，防守每季至少20场及50次篮下防守出手。当前覆盖分别为301/401、398/401；不同球员可用赛季不同，界面显示样本。刷新数据需 Python 的 pyarrow 后运行 `python3 scripts/import-tracking.py`，遇缺失不填零。

位置图的掩护助攻、干扰投篮、传球干扰和争抢球来自 [NBA Hustle 数据快照](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/nba_stats_hustle)，使用 2024–25 与 2025–26 常规赛。`python3 scripts/import-hustle.py` 需要 pyarrow；以姓名、NBA ID 唯一性与各赛季出场数核验，累计至少20场且出场数与 ESPN 差不超过1场，交易球员按球队行合计。当前匹配 327/401 人；缺失维度不参与评分。数据按实际可用赛季的权重归一化，以每36分钟展示。不同角色基准使用 ESPN G/F/C 三组，不是精确的五位置分组，每项至少20个有效同组样本。

### 追踪数据核对与限制

突破、潜在助攻与防守投篮数据来自 NBA_Lineup202324_Analyzer 的 NBA 统计镜像，文件版本由 `scripts/import-external-tracking.py` 中的 Git blob SHA 固定。导入时按规范化姓名匹配，要求 ESPN 球员池姓名唯一、跨赛季及追踪来源的 NBA ID 唯一；逐赛季常规赛出场数须与 ESPN 相差不超过 1 场。转队时仅在分球队记录的场次总和吻合时合并；不满足条件的赛季不使用，不能当作零。权重按有数据的赛季重新归一，每项保留赛季、样本和原始权重。NBA ID 仍为姓名匹配的候选映射，尚未与官方身份表逐人确认；有数据不等于样本覆盖完整赛季。

当前快照复核：库里、东契奇、文班亚马、哈利伯顿的 ESPN 出场数和得分与对应赛季 ESPN 接口一致；东契奇涉及转队，哈利伯顿仅有一个赛季。该抽查不构成 NBA 官网逐人或逐项数据对账。突破、外线防守等追踪结果仍需官方来源独立验证；球队防守投篮是个人数据推演，不是五人实际共同上场的防守效率。

### 项目声明

本项目为个人学习和非商业用途的非官方篮球选秀模拟器，与 NBA、ESPN、球队及球员无官方关联。球员头像、姓名、球队标识及第三方数据的相关权利归各自权利人所有；标注来源或非商业声明不构成授权，第三方素材的使用和再分发应自行核实许可。
