"""
Tools and Code Execution Tests for RB Agent OS.
Verifies controlled code execution, timeouts, file ops, and verification logic.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.code_executor import code_executor
from app.tools.file_ops import file_ops
from app.core.verifier import get_verifier

class TestTools(unittest.TestCase):
    def test_run_python_code_success(self):
        code = "print(2 + 2)"
        res = code_executor.run_python_code(code)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exit_code"], 0)
        self.assertEqual(res["stdout"].strip(), "4")
        self.assertTrue(res["verified"])

    def test_run_python_syntax_error_not_reported_as_success(self):
        code = "print(undefined_variable_name_xyz)"
        res = code_executor.run_python_code(code)
        self.assertEqual(res["status"], "error")
        self.assertNotEqual(res["exit_code"], 0)
        self.assertFalse(res["verified"])
        self.assertIn("NameError", res["stderr"])

    def test_run_python_timeout(self):
        code = "import time; time.sleep(5)"
        res = code_executor.run_python_code(code, timeout=1)
        self.assertEqual(res["status"], "error")
        self.assertFalse(res["verified"])
        self.assertIn("timed out", res["stderr"])

    def test_file_operations_lifecycle(self):
        filename = "test_ops_file.txt"
        content = "RB Agent OS Verified Write Test"

        # 1. Write file
        write_res = file_ops.write_file(filename, content)
        self.assertEqual(write_res["status"], "success")
        self.assertTrue(write_res["verified"])

        # 2. Read file
        read_res = file_ops.read_file(filename)
        self.assertEqual(read_res["status"], "success")
        self.assertEqual(read_res["content"], content)
        self.assertTrue(read_res["verified"])

        # 3. List files
        list_res = file_ops.list_files(".")
        self.assertEqual(list_res["status"], "success")
        names = [f["name"] for f in list_res["files"]]
        self.assertIn(filename, names)

        # 4. Delete file
        del_res = file_ops.delete_file(filename)
        self.assertEqual(del_res["status"], "success")
        self.assertTrue(del_res["verified"])

        # Verify it no longer exists
        read_again = file_ops.read_file(filename)
        self.assertEqual(read_again["status"], "error")

if __name__ == "__main__":
    unittest.main()
