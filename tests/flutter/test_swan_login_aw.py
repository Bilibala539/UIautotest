"""Swan 登录 AW 单元测试：保留业务编排，隔离设备与验证码服务。"""
import os
import unittest
from unittest.mock import Mock, call, patch

from utils.aw.business.swan import SwanBusiness


class SwanLoginAWTest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.aw = SwanBusiness(Mock(platform_name="flutter"))
        self.actions = Mock()
        for name in (
            "accessibility_exists",
            "wait_accessibility",
            "click_accessibility",
            "clear_input",
            "input_text",
            "press_back",
            "relaunch_app",
            "_fetch_sms_code",
        ):
            action = Mock()
            setattr(self.aw, name, action)
            self.actions.attach_mock(action, name)
        self.aw.accessibility_exists.return_value = False
        self.aw.wait_accessibility.return_value = True
        self.aw._fetch_sms_code.return_value = "1234"

    def assert_no_submission(self):
        self.aw.click_accessibility.assert_not_called()
        self.aw.input_text.assert_not_called()
        self.aw.relaunch_app.assert_not_called()
        self.aw._fetch_sms_code.assert_not_called()

    def test_invalid_method_fails_before_device_access(self):
        with self.assertRaises(ValueError):
            self.aw.login(method="unknown")
        self.assertEqual(self.actions.mock_calls, [])

    def test_missing_or_explicit_empty_credentials_do_not_submit(self):
        cases = (
            ({}, {}),
            ({"phone": "13800000000"}, {}),
            ({"phone": "", "password": "secret"}, {"SWAN_PHONE": "13800000000"}),
            ({"phone": "13800000000", "password": ""}, {"SWAN_PASSWORD": "secret"}),
            ({"phone": "  ", "method": "sms"}, {}),
            ({"phone": "13800000000", "password": "  "}, {}),
        )
        for arguments, environment in cases:
            with self.subTest(arguments=arguments), patch.dict(os.environ, environment, clear=True):
                self.actions.reset_mock()
                with self.assertRaises(ValueError):
                    self.aw.login(**arguments)
                self.assert_no_submission()
                self.aw.wait_accessibility.assert_not_called()

    def test_password_login_uses_explicit_or_environment_credentials(self):
        for explicit in (True, False):
            with self.subTest(explicit=explicit):
                self.actions.reset_mock()
                with patch.dict(os.environ, {
                    "SWAN_PHONE": "13800000000",
                    "SWAN_PASSWORD": "environment-password",
                    "SWAN_PACKAGE": "test.swan.package",
                }):
                    if explicit:
                        self.aw.login(" 13900000000 ", " password with spaces ")
                        expected_inputs = [call("13900000000"), call(" password with spaces ")]
                    else:
                        self.aw.login()
                        expected_inputs = [call("13800000000"), call("environment-password")]
                self.assertEqual(self.aw.input_text.call_args_list, expected_inputs)
                self.aw.relaunch_app.assert_called_once_with("test.swan.package")
                self.aw._fetch_sms_code.assert_not_called()
                self.assertEqual(self.aw.click_accessibility.call_args_list, [
                    call(self.aw.KEY_USE_PASSWORD_BUTTON),
                    call(self.aw.KEY_PHONE_FIELD),
                    call(self.aw.KEY_PASSWORD_FIELD),
                    call(self.aw.KEY_AGREEMENT),
                    call(self.aw.KEY_SUBMIT),
                    call(self.aw.KEY_TAB_RECOMMEND),
                ])
                self.aw.wait_accessibility.assert_called_with(self.aw.KEY_TAB_ME, timeout=15.0)
                self.assertLess(
                    self.actions.mock_calls.index(call.relaunch_app("test.swan.package")),
                    self.actions.mock_calls.index(call.click_accessibility(self.aw.KEY_AGREEMENT)),
                )

    def test_sms_login_waits_for_code_page_before_fetching(self):
        with patch.dict(os.environ, {"SWAN_PHONE": "13800000000"}):
            self.aw.login(method="sms", wait_code=7)

        self.aw.relaunch_app.assert_called_once_with("com.swan.network")
        self.aw._fetch_sms_code.assert_called_once_with("13800000000", wait=7)
        self.assertEqual(self.aw.input_text.call_args_list, [call("13800000000"), call("1234")])
        self.assertLess(
            self.actions.mock_calls.index(call.wait_accessibility(self.aw.KEY_CODE_FIELD, timeout=15.0)),
            self.actions.mock_calls.index(call._fetch_sms_code("13800000000", wait=7)),
        )
        self.aw.click_accessibility.assert_called_with(self.aw.KEY_TAB_RECOMMEND)
        self.aw.wait_accessibility.assert_called_with(self.aw.KEY_TAB_ME, timeout=15.0)

    def test_existing_session_returns_home_without_credentials_or_submission(self):
        self.aw.accessibility_exists.return_value = True

        self.aw.login()

        self.aw.click_accessibility.assert_called_once_with(self.aw.KEY_TAB_RECOMMEND)
        self.aw.wait_accessibility.assert_called_once_with(self.aw.KEY_TAB_ME, timeout=15.0)
        self.aw.relaunch_app.assert_not_called()
        self.aw.input_text.assert_not_called()
        self.aw._fetch_sms_code.assert_not_called()

    def test_session_restored_after_relaunch_does_not_submit(self):
        self.aw.accessibility_exists.side_effect = [False, True]

        self.aw.login("13800000000", "secret")

        self.aw.relaunch_app.assert_called_once_with("com.swan.network")
        self.aw.click_accessibility.assert_called_once_with(self.aw.KEY_TAB_RECOMMEND)
        self.aw.input_text.assert_not_called()
        self.aw._fetch_sms_code.assert_not_called()

    def test_missing_login_page_does_not_restart_or_submit(self):
        self.aw.wait_accessibility.return_value = False

        with self.assertRaisesRegex(AssertionError, "login 需要"):
            self.aw.login("13800000000", "secret")

        self.assert_no_submission()

    def test_missing_login_page_after_restart_does_not_submit(self):
        self.aw.wait_accessibility.side_effect = [True, False]

        with self.assertRaisesRegex(AssertionError, "重启后未进入登录页"):
            self.aw.login("13800000000", "secret")

        self.aw.relaunch_app.assert_called_once()
        self.aw.click_accessibility.assert_not_called()
        self.aw.input_text.assert_not_called()

    def test_code_page_timeout_does_not_fetch_or_fill_code(self):
        self.aw.wait_accessibility.side_effect = lambda key, timeout: key != self.aw.KEY_CODE_FIELD

        with self.assertRaisesRegex(AssertionError, "未进入验证码输入页"):
            self.aw.login("13800000000", method="sms")

        self.aw._fetch_sms_code.assert_not_called()
        self.aw.input_text.assert_called_once_with("13800000000")
        self.assertNotIn(call(self.aw.KEY_TAB_RECOMMEND), self.aw.click_accessibility.call_args_list)

    def test_code_fetch_failure_propagates_without_authentication_fallback(self):
        self.aw._fetch_sms_code.side_effect = RuntimeError("OTP service unavailable")

        with self.assertRaisesRegex(RuntimeError, "OTP service unavailable"):
            self.aw.login("13800000000", method="sms")

        self.aw.input_text.assert_called_once_with("13800000000")
        self.assertNotIn(call(self.aw.KEY_USE_PASSWORD_BUTTON), self.aw.click_accessibility.call_args_list)
        self.assertNotIn(call(self.aw.KEY_TAB_RECOMMEND), self.aw.click_accessibility.call_args_list)

    def test_failed_authentication_does_not_return_success_or_try_another_method(self):
        for method in ("password", "sms"):
            with self.subTest(method=method):
                self.actions.reset_mock()
                self.aw.wait_accessibility.side_effect = lambda key, timeout: key != self.aw.KEY_TAB_ME
                with self.assertRaisesRegex(AssertionError, "登录后未进入首页"):
                    self.aw.login("13800000000", "secret", method=method)
                self.assertNotIn(call(self.aw.KEY_TAB_RECOMMEND), self.aw.click_accessibility.call_args_list)
                if method == "password":
                    self.aw._fetch_sms_code.assert_not_called()
                else:
                    self.assertNotIn(call(self.aw.KEY_USE_PASSWORD_BUTTON), self.aw.click_accessibility.call_args_list)

    def test_return_home_failure_propagates(self):
        self.aw.accessibility_exists.return_value = True
        self.aw.wait_accessibility.return_value = False

        with self.assertRaisesRegex(AssertionError, "未回到首页"):
            self.aw.login()

        self.aw.input_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
