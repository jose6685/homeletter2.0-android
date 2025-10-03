/*
 * Copyright 2020 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.homeletter.app;



public class Application extends android.app.Application {

  

  @Override
  public void onCreate() {
      super.onCreate();
      try {
          com.google.android.gms.ads.MobileAds.initialize(this);
          // 在開發環境使用測試設備配置，避免無填充造成誤判
          try {
              java.util.List<String> testIds = java.util.Arrays.asList(
                      com.google.android.gms.ads.AdRequest.DEVICE_ID_EMULATOR
              );
              com.google.android.gms.ads.RequestConfiguration config =
                      new com.google.android.gms.ads.RequestConfiguration.Builder()
                              .setTestDeviceIds(testIds)
                              .build();
              com.google.android.gms.ads.MobileAds.setRequestConfiguration(config);
          } catch (Throwable t2) {
              android.util.Log.w("HomeLetter", "MobileAds request configuration failed", t2);
          }
      } catch (Throwable t) {
          android.util.Log.w("HomeLetter", "MobileAds init failed", t);
      }
  }
}
