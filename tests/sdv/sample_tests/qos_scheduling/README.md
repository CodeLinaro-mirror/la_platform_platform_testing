<!--
  Copyright (C) 2026 The Android Open Source Project
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

# SDV Sample QoS Scheduling Test

## Test Execution

### Atest

```shell
atest SdvQosSchedulingSampleTest
```

### CATBox tests

1. Build catbox: `m catbox`
1. Navigate to CATbox location: `cd out/host/linux-x86/catbox/android-catbox/`
1. Check available test plans for SDV

    ```bash
    ./tools/catbox-tradefed l p | grep sdv
    ```

1. Execute test

   - One device:

    ```bash
    NOTIFY_AS_NATIVE=0.0.0.0:6520 ./tools/catbox-tradefed run commandAndExit \
        sdv-sample-qos-scheduling-test --{device1}serial 0.0.0.0:6520
    ```
