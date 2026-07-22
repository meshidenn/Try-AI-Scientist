# Integrated Claim Audit

## Status

統合レポートの数値を`integrated-comparison.json`、exp-001、exp-002の構造化artifactと照合した。

## Supported

- agentic synthetic workloadでFP8+s8がconcurrency 1/2/4の最高throughputだった。
- randomのspec_tokens=4では、±5%判定でFP8が8条件優位、1条件同等、BF16優位0だった。
- acceptance低下なしでもFP8 slowdownが起こる条件が1件あり、acceptance単独原因説は棄却される。

## Guardrails

- 各条件は原則1 runのため、5%未満の差は優劣として扱っていない。
- randomの低depth群と高depth群は実験プロトコルが完全には一致しない。
- production agentへの一般化は未支持。現時点ではFP8+s8はdefault候補であり、確定設定ではない。
- agenticのtotal output token不一致2件はcross-target比較から除外した。

