# agent

`.agents/` から参照される共通契約、template、保存形式を置く。

実体のsub-agent定義とskill定義は `.agents/` に置く。このディレクトリは、それらのagent-facingな指示から参照されるrepo固有の仕様を管理する。

方針として、coding agentがすでに得意な一般作業は細かくskill化しすぎない。代わりに、このrepo固有の保存形式、レビュー形式、文献検索、実験ログ、再開ルールを明示する。

## subagents

subagentは `.agents/subagents/` に置く。例: surveyor、experiment-runner、artifact-auditor、paper-reviewer、result-interpreter、claim-auditor、archivist。

subagentは `ai_scientist/runner/` や `ai_scientist/evaluators/` のようなディレクトリと1対1対応するものではない。subagentは研究workflow上の役割であり、必要に応じてrunner、search、evaluators、reviewers、archiveを使う。

subagent間の状態共有は、原則としてproject内のartifactで行う。直接会話だけに依存しないことで、途中再開、人間レビュー、別agentへの引き継ぎをしやすくする。

## skills

skillは `.agents/skills/` に置く。繰り返し使う具体的な手順を定義する。例: literature search、experiment logging、result verification、paper writing。

skillはsubagentに読ませる再利用可能な手順である。coding agentが一般に得意な作業を細かく説明するのではなく、このrepo固有の保存形式、API利用、検証ルール、更新ルールを記述する。
