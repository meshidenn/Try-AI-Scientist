---
name: personal-issue-ops
description: Try-AI-Scientistの調査・実験・実装をGitHub IssueとPersonalProjectに接続する。継続作業のIssue化提案、既存Issueへの結果記録、横断状態の更新を行うときに使う。
---

# Personal Issue Ops

## 役割

- GitHub Issueは、複数セッションにまたがる作業の目的、完了条件、判断、結果、次の一手の正本とする。
- GitHub Project `PersonalProject` は、Status、Priority、Initiative、Area、Review dateの横断ビューとする。
- Chatは作業セッションであり、Issueなしで自由に開始してよい。Issueは作業開始の必須条件ではない。

## Issue化の提案

次のいずれかになった時点で、Issue化を提案する。

- 複数セッションにまたがる。
- 独立した完了条件、研究上の判断、再開時に必要な背景がある。
- 実験結果・artifact・成果物を後から参照する。
- Status、Priority、Projectへの追加を個別に管理する。

提案には、対象リポジトリ、Issue案、目的、完了条件を含める。Issue作成、Projectへの追加、Status・Priority・Initiative・Review dateの変更、Issueクローズは、明示的な承認後にだけ実行する。

## 作業中と終了時

既存Issueに紐づく作業では、開始、ブロッカー、重要な判断、終了時にIssueへ記録する。終了時は次を残す。

- 実施内容と成果物
- テストまたは実験結果
- 未完了項目と次の一手
- 必要ならStatus変更案

完了条件を満たした根拠がある場合だけDoneを提案する。外部待ちはWaitingと待つ対象、Review dateを記録する。

## 実行順序

`Collect -> Propose -> Approve -> Apply -> Execute -> Record` を守る。提案だけでGitHubの状態を変更しない。コード変更を伴うIssue化が承認された場合は、`git-issue-flow` SkillのIssue・branch・Development連携手順を使う。
