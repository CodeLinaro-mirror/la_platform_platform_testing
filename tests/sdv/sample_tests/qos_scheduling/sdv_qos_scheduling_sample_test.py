# Copyright (C) 2026 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""SDV QoS Scheduling Sample E2E Test"""

import logging
import re
from mobly import asserts
from sdv_test_fw.device.sdv_property import SdvDeviceProperty
from sdv_test_fw.test_execution import sdv_base_test
from sdv_test_fw.test_execution import sdv_test_runner
from sdv_test_fw.verification import polling

class SdvQosSchedulingSampleTest(sdv_base_test.SdvBaseTestClass):

    # Path to the sample's orchestration config on the device.
    SAMPLE_ORCH_CONFIG_PATH = "/etc/orch/vm_qos_scheduling_orch_config.textproto"

    # Threshold for speedup (Elevated vs Normal).
    MIN_SPEEDUP_THRESHOLD = 1.5

    def setup_class(self):
        super().setup_class()
        self.sdv_device = self.get_device("device1")
        self.adb = self.sdv_device.adb()

        # Ensure the device is rooted for setprop and reboot.
        self.adb.root_device()

        # Backup the current orchestrator config path.
        self.original_orch_config = self.adb.prop.get(
            SdvDeviceProperty.ORCHESTRATOR_CONFIG_PATH
        )
        logging.info(f"Original orchestrator config: {self.original_orch_config}")

    def teardown_class(self):
        # If setup_class failed before self.adb was assigned, skip restoring.
        if not hasattr(self, 'adb'):
            super().teardown_class()
            return

        # Ensure the device is rooted before restoring.
        self.adb.root_device()

        # Restore the original orchestrator config and reboot to return to baseline.
        logging.info(f"Restoring orchestrator config to: {self.original_orch_config}")
        self.adb.prop.set(
            SdvDeviceProperty.ORCHESTRATOR_CONFIG_PATH,
            self.original_orch_config
        )
        self.adb.reboot_device()
        super().teardown_class()

    def test_qos_scheduling_performance(self):
        """Verifies that the elevated scheduling profile performs better than the normal profile."""

        self.log_test_info("Starting QoS Scheduling Performance Test")

        # 1. Set the orchestrator configuration path.
        logging.info(f"Setting orchestrator config path to {self.SAMPLE_ORCH_CONFIG_PATH}")
        self.adb.prop.set(
            SdvDeviceProperty.ORCHESTRATOR_CONFIG_PATH,
            self.SAMPLE_ORCH_CONFIG_PATH
        )

        # 2. Reboot the device to apply changes and start services.
        logging.info("Rebooting device to apply orchestration config...")
        self.adb.reboot_device()
        self.adb.wait_for_boot_complete()

        # 3. Observe the logs for performance comparison.
        # Example log: Normal: 11.5M, Elevated: 101.1M (Elevated is 8.80x faster)
        logging.info("Waiting for performance test results in logs...")

        # We wait for the specific comparison log line.
        regex_pattern = r"Normal: .*, Elevated: .* \(Elevated is ([\d.]+)x faster\)"

        # Use polling to wait for the log.
        polling.wait_and_verify_expected_logs(
            self.adb,
            grep_text="Normal:",
            expected_result=regex_pattern,
            timeout=120, # The test runs for 10s, but boot + service startup takes time.
            assert_msg="Could not find performance comparison log in logcat."
        )

        # 4. Extract and validate the speedup ratio.
        logcat_processor = self.adb.advance_logcat()
        comparison_log = logcat_processor.nth_message(1, regex_pattern, regex=True)

        match = re.search(regex_pattern, comparison_log)
        asserts.assert_true(match, f"Failed to parse speedup ratio from log: {comparison_log}")

        speedup_ratio = float(match.group(1))
        logging.info(f"Detected speedup ratio: {speedup_ratio}x")

        asserts.assert_greater_equal(
            speedup_ratio,
            self.MIN_SPEEDUP_THRESHOLD,
            f"Speedup ratio {speedup_ratio}x is below the expected threshold of {self.MIN_SPEEDUP_THRESHOLD}x."
        )

        self.log_test_info("QoS Scheduling Performance Test completed successfully")

if __name__ == "__main__":
    sdv_test_runner.run()
