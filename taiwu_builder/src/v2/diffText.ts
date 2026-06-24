// 字符级 LCS 双串 diff：返回两个串各自被切成 "common" / "diff" 段的序列。
// 用于把心法正练 vs 心法逆练的差异部分高亮出来。

export type DiffSeg = { kind: "common" | "diff"; text: string };

export function diffPair(a: string, b: string): { left: DiffSeg[]; right: DiffSeg[] } {
  const m = a.length;
  const n = b.length;
  if (m === 0 || n === 0) {
    return {
      left: a ? [{ kind: "diff", text: a }] : [],
      right: b ? [{ kind: "diff", text: b }] : [],
    };
  }

  // LCS DP（字符级）。注意：极端长文本可能 O(m*n)，但功法文本几十~一百多字符够用。
  const dp: Uint16Array[] = [];
  for (let i = 0; i <= m; i++) dp.push(new Uint16Array(n + 1));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
      else dp[i][j] = dp[i - 1][j] >= dp[i][j - 1] ? dp[i - 1][j] : dp[i][j - 1];
    }
  }

  // 回溯，得到每个字符的标签序列。
  type Op = "match" | "del" | "ins";
  const ops: Op[] = [];
  let i = m;
  let j = n;
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) {
      ops.push("match");
      i--;
      j--;
    } else if (dp[i - 1][j] >= dp[i][j - 1]) {
      ops.push("del");
      i--;
    } else {
      ops.push("ins");
      j--;
    }
  }
  while (i > 0) {
    ops.push("del");
    i--;
  }
  while (j > 0) {
    ops.push("ins");
    j--;
  }
  ops.reverse();

  // 按 op 重组成 left/right 两路段序列；相邻同 kind 合并。
  const left: DiffSeg[] = [];
  const right: DiffSeg[] = [];
  let ai = 0;
  let bi = 0;
  const pushSeg = (arr: DiffSeg[], kind: DiffSeg["kind"], ch: string) => {
    const last = arr[arr.length - 1];
    if (last && last.kind === kind) last.text += ch;
    else arr.push({ kind, text: ch });
  };

  for (const op of ops) {
    if (op === "match") {
      pushSeg(left, "common", a[ai]);
      pushSeg(right, "common", b[bi]);
      ai++;
      bi++;
    } else if (op === "del") {
      pushSeg(left, "diff", a[ai]);
      ai++;
    } else {
      pushSeg(right, "diff", b[bi]);
      bi++;
    }
  }

  return { left, right };
}
