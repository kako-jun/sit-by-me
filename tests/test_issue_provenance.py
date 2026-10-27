"""Source coverage proves storage; semantic closure requires explicit review."""
import copy
import hashlib
import json
import sys
from unittest.mock import patch

from tests.ledger_test_support import ROOT, YamlFixture
sys.path.insert(0, str(ROOT / "scripts"))
import build_issue_provenance as P


def snapshot(body="前文\n# 作業記録\n実装した。\n# 決定\n「青くする」\n"):
    return {"issues": [
        {"number": 1, "html_url": "https://github.com/kako-jun/sit-by-me/issues/1", "created_at": "2026-01-01", "body": body},
        {"number": 2, "html_url": "https://github.com/kako-jun/sit-by-me/issues/2", "created_at": "2026-01-02", "body": None},
        {"number": 3, "html_url": "https://github.com/kako-jun/sit-by-me/pull/3", "created_at": "2026-01-03", "body": "PR", "pull_request": {"url": "pr"}}],
        "comments": [
            {"id": 11, "issue_url": "https://api.github.com/repos/kako-jun/sit-by-me/issues/1", "html_url": "https://github.com/kako-jun/sit-by-me/issues/1#issuecomment-11", "created_at": "2026-01-04", "body": "コメント"},
            {"id": 12, "issue_url": "https://api.github.com/repos/kako-jun/sit-by-me/issues/3", "html_url": "https://github.com/kako-jun/sit-by-me/pull/3#issuecomment-12", "created_at": "2026-01-04", "body": "PRコメント"}]}


class IssueProvenanceTests(YamlFixture):
    def install(self, data=None):
        data = data or snapshot()
        sources, claims = P.build(data, [])
        self.write_table("Issue出典", sources)
        self.write_table("Issue命題", claims)
        path = self.root / "snapshot.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return sources, claims, path

    def verify(self, *arguments):
        return self.cli("verify_domain_ledger.py", *arguments)

    def test_sources_cover_body_empty_body_comments_and_exclude_prs(self):
        sources, claims, path = self.install()
        self.assertEqual({s["出典ID"] for s in sources}, {"ISSUE-1-BODY", "ISSUE-1-C11", "ISSUE-2-BODY"})
        self.assertEqual({c["出典ID"] for c in claims}, {s["出典ID"] for s in sources})
        result = self.verify("--from-json", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sections_retain_preamble_and_every_character(self):
        body = "前文\n\n# 作業記録\n本文\n## 指示\n後の決定\n"
        self.assertEqual("".join(section[3] for section in P.sections(body)), body)
        self.assertEqual(len(P.sections(body)), 3)

    def test_structural_coverage_does_not_pass_semantic_closure(self):
        sources, claims, path = self.install()
        self.assertTrue(all(s["点検状態"] == "自動抽出・要確認" for s in sources))
        result = self.verify("--from-json", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("semantic review pending=3", result.stdout)
        self.assert_rejected(self.verify("--require-reviewed", "--from-json", str(path)), "意味点検未完了")

    def test_confirmed_source_cannot_retain_pending_claim(self):
        self.install()
        self.mutate("Issue出典", lambda rows: rows[0].update(点検状態="確認済み"))
        self.assert_rejected(self.verify(), "確認済み", "命題")

    def test_missing_comment_is_a_source_coverage_failure(self):
        sources, claims, path = self.install()
        self.write_table("Issue出典", [s for s in sources if s["種別"] != "コメント"])
        self.write_table("Issue命題", [c for c in claims if c["出典ID"] != "ISSUE-1-C11"])
        self.assert_rejected(self.verify("--from-json", str(path)), "snapshot")

    def test_source_requires_claim_coverage(self):
        self.install()
        self.write_table("Issue命題", [])
        self.assert_rejected(self.verify(), "命題がない出典")

    def test_claim_source_is_required_and_must_resolve_exactly(self):
        for source in ("", "未決(要確認)", "ISSUE-999-BODY"):
            with self.subTest(source=source):
                self.install()
                self.mutate("Issue命題", lambda rows: rows[0].update(出典ID=source))
                self.assert_rejected(self.verify(), "Issue命題", "出典ID")

    def test_unknown_map_reference_remains_permitted_with_real_source(self):
        self.install()
        self.mutate("Issue命題", lambda rows: rows[0].update(分類="既存台帳参照", 参照先="MAP:未決(要確認)"))
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_orphan_comment_is_rejected(self):
        data = snapshot()
        data["comments"][0]["issue_url"] = "https://api.github.com/repos/kako-jun/sit-by-me/issues/999"
        with self.assertRaises(ValueError):
            P.source_records(data)

    def test_duplicate_source_urls_are_rejected(self):
        self.install()
        self.mutate("Issue出典", lambda rows: rows[1].update(URL=rows[0]["URL"]))
        self.assert_rejected(self.verify(), "URL重複")

    def test_original_and_safe_hashes_are_distinct_after_redaction(self):
        body = "\n".join(["/Users/example/private/file", "/home/example/secret", "~/data/private",
                          "/tmp/session/input", r"C:\Users\example\secret.txt",
                          "~/.codex/sessions/record", "01234567-89ab-cdef-0123-456789abcdef",
                          "ghp_" + "a" * 24])
        sources, claims = P.build(snapshot(body), [])
        source = next(s for s in sources if s["出典ID"] == "ISSUE-1-BODY")
        self.assertEqual(source["本文SHA256"], hashlib.sha256(body.encode()).hexdigest())
        self.assertEqual(source["安全化SHA256"], hashlib.sha256(source["本文"].encode()).hexdigest())
        self.assertNotEqual(source["本文SHA256"], source["安全化SHA256"])
        for secret in ("example", "/tmp/session", "01234567-89ab", "ghp_"):
            self.assertNotIn(secret, source["本文"])
        self.assertTrue(all(not c["原文抜粋"] for c in claims if c["出典ID"] == source["出典ID"]))

    def test_safe_body_tampering_is_rejected(self):
        self.install()
        self.mutate("Issue出典", lambda rows: rows[0].update(本文="改変本文"))
        self.assert_rejected(self.verify(), "本文ハッシュ不一致")

    def test_original_hash_tampering_is_rejected_against_snapshot(self):
        _, _, path = self.install()
        self.mutate("Issue出典", lambda rows: rows[0].update(本文SHA256="0" * 64))
        self.assert_rejected(self.verify("--from-json", str(path)), "snapshotから本文変更")

    def test_redacted_quote_cannot_claim_exact_attribution(self):
        data = snapshot("「/Users/example/secret は残す」")
        decision = {"決定ID": "D1", "決定の要点": "引用", "逐語": "「/Users/example/secret は残す」",
                    "出典URL": data["issues"][0]["html_url"]}
        _, claims = P.build(data, [decision])
        claim = next(c for c in claims if c["決定ID"] == "D1")
        self.assertEqual(claim["帰属"], "話者未確定")
        self.assertEqual(claim["原文抜粋"], "")

    def test_unchanged_hash_preserves_manual_split_claim(self):
        sources, claims, _ = self.install()
        old_sources, old_claims = copy.deepcopy(sources), copy.deepcopy(claims)
        old_sources[0].update(点検状態="確認済み", 備考="手動点検")
        custom = copy.deepcopy(claims[0])
        custom.update(命題ID="ISSUE-1-BODY.CUSTOM", 分類="提案", 備考="【手動】分割")
        self.write_table("Issue出典", old_sources)
        self.write_table("Issue命題", old_claims + [custom])
        with patch.object(P, "LEDGER", self.ledger):
            kept_sources, kept_claims = P.keep_reviewed_rows(copy.deepcopy(sources), copy.deepcopy(claims))
        self.assertEqual(kept_sources[0]["点検状態"], "確認済み")
        self.assertIn(custom, kept_claims)

    def test_changed_body_invalidates_manual_review(self):
        sources, claims, _ = self.install()
        sources[0].update(点検状態="確認済み")
        claims[0].update(分類="提案", 備考="【手動】分類")
        self.write_table("Issue出典", sources)
        self.write_table("Issue命題", claims)
        new_sources, new_claims = P.build(snapshot("変更された本文"), [])
        with patch.object(P, "LEDGER", self.ledger):
            kept_sources, kept_claims = P.keep_reviewed_rows(new_sources, new_claims)
        self.assertEqual(kept_sources[0]["点検状態"], "自動抽出・要確認")
        self.assertNotIn("【手動】", kept_claims[0]["備考"])

    def test_missing_quote_is_not_invented(self):
        data = snapshot("同じ出典だが別の文")
        _, claims = P.build(data, [{"決定ID": "D1", "決定の要点": "引用", "逐語": "「存在しない引用」", "出典URL": data["issues"][0]["html_url"]}])
        claim = next(c for c in claims if c["決定ID"] == "D1")
        self.assertEqual(claim["原文抜粋"], "")
        self.assertEqual(claim["帰属"], "話者未確定")
