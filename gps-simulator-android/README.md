# GPS 模擬器 - Android 應用程式

完整的 Android GPS 模擬應用程式，支援 Google Maps 整合、可拖曳的拉桿控制、方向箭頭和 GPS 模擬移動功能。

## 功能特性

- **Google Maps 整合** — 顯示互動式地圖，支援縮放和平移
- **GPS 模擬控制** — 完整的方向、速度和大小拉桿控制
- **方向指示器** — 半透明箭頭顯示當前方向，自動旋轉
- **GPS 模擬移動** — 自動計算位置變化，模擬車輛按規定速度和方向移動
- **狀態管理** — 實時顯示模擬狀態和位置資訊
- **深色模式支援** — 完整的深色模式適配

## 系統要求

- **Android Studio** 4.0 或更新版本
- **Android SDK** 24 (API 24) 或更新版本
- **Java Development Kit (JDK)** 11 或更新版本
- **Gradle** 7.0 或更新版本

## 構建步驟

### 方法 1: 使用 Android Studio (推薦)

1. **打開 Android Studio**
   - 啟動 Android Studio
   - 選擇 "Open an existing Android Studio project"
   - 選擇此專案目錄

2. **等待 Gradle 同步**
   - Android Studio 將自動下載所有依賴項
   - 等待同步完成（可能需要 5-10 分鐘）

3. **構建應用程式**
   - 選擇 "Build" → "Build Bundle(s) / APK(s)" → "Build APK(s)"
   - 或使用快捷鍵 `Ctrl+F9` (Windows/Linux) 或 `Cmd+F9` (Mac)

4. **找到生成的 APK**
   - APK 檔案位於: `app/build/outputs/apk/debug/app-debug.apk`
   - 或構建完成後，Android Studio 會提示 APK 位置

### 方法 2: 使用命令列

```bash
# 進入專案目錄
cd /path/to/gps-simulator-android

# 清理舊構建
./gradlew clean

# 構建 Debug APK
./gradlew assembleDebug

# 構建 Release APK (需要簽署金鑰)
./gradlew assembleRelease

# APK 將生成在:
# - Debug: app/build/outputs/apk/debug/app-debug.apk
# - Release: app/build/outputs/apk/release/app-release.apk
```

## 安裝到裝置

### 使用 Android Studio

1. 連接 Android 裝置或啟動模擬器
2. 選擇 "Run" → "Run 'app'" 或按 `Shift+F10`
3. 選擇目標裝置
4. 應用程式將自動安裝並啟動

### 使用命令列

```bash
# 安裝 Debug APK
adb install app/build/outputs/apk/debug/app-debug.apk

# 啟動應用程式
adb shell am start -n com.gpssimulator/.ui.MainActivity
```

## 專案結構

```
gps-simulator-android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/gpssimulator/
│   │       │   ├── ui/
│   │       │   │   ├── MainActivity.kt          # 主活動
│   │       │   │   └── ArrowView.kt             # 方向箭頭自訂視圖
│   │       │   ├── data/
│   │       │   │   └── GPSSimulatorState.kt     # 狀態管理
│   │       │   └── utils/
│   │       │       └── GPSCalculator.kt         # GPS 計算工具
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   └── activity_main.xml        # 主佈局
│   │       │   ├── values/
│   │       │   │   ├── colors.xml               # 顏色定義
│   │       │   │   ├── strings.xml              # 字串資源
│   │       │   │   └── themes.xml               # 主題樣式
│   │       │   └── drawable/
│   │       │       ├── status_background.xml    # 狀態提示背景
│   │       │       └── reset_button_background.xml  # 復原按鈕背景
│   │       └── AndroidManifest.xml              # 應用程式清單
│   └── build.gradle                             # 應用模組構建配置
├── build.gradle                                 # 根構建配置
├── settings.gradle                              # 專案設定
├── gradle/
│   └── wrapper/
│       └── gradle-wrapper.properties             # Gradle Wrapper 配置
└── README.md                                    # 本檔案
```

## 核心功能說明

### GPS 計算 (GPSCalculator.kt)

- **calculateNewLocation()** — 根據起始座標、方向和距離計算新座標
- **calculateDistance()** — 根據速度和時間間隔計算移動距離
- **calculateNextLocation()** — 計算下一個 GPS 位置

### 狀態管理 (GPSSimulatorState.kt)

- **SimulationState** — 儲存應用程式狀態（位置、方向、速度等）
- **GPSSimulatorStateManager** — 管理狀態更新和事件

### UI 元件

- **MainActivity** — 主活動，整合地圖、控制拉桿和開關
- **ArrowView** — 自訂視圖，顯示方向指示器

## 權限

應用程式需要以下 Android 權限：

- `ACCESS_FINE_LOCATION` — 精確位置
- `ACCESS_COARSE_LOCATION` — 粗略位置
- `ACCESS_BACKGROUND_LOCATION` — 背景位置存取
- `ACCESS_MOCK_LOCATION` — 允許模擬位置

## Google Maps API 金鑰

應用程式已配置 Google Maps API 金鑰。如需更改，請編輯 `AndroidManifest.xml` 中的：

```xml
<meta-data
    android:name="com.google.android.geo.API_KEY"
    android:value="YOUR_API_KEY_HERE" />
```

## 故障排除

### 構建失敗

**問題**: Gradle 版本不相容
**解決方案**: 確保使用 Gradle 7.0 或更新版本

**問題**: 依賴項下載失敗
**解決方案**: 檢查網路連線，或編輯 `build.gradle` 中的 Maven 倉庫

### 安裝失敗

**問題**: APK 簽署錯誤
**解決方案**: 使用 Debug 版本進行測試

**問題**: 裝置不被識別
**解決方案**: 啟用 USB 偵錯，並安裝 ADB 驅動程式

## 開發環境設定

### 安裝 Android SDK

1. 下載 [Android Studio](https://developer.android.com/studio)
2. 安裝後，打開 SDK Manager
3. 安裝以下元件：
   - Android SDK Platform 31
   - Android SDK Build-Tools 31.0.0
   - Google Play Services

### 設定 JAVA_HOME

```bash
# Linux/Mac
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk

# Windows
set JAVA_HOME=C:\Program Files\Java\jdk-11
```

## 許可證

MIT License

## 支援

如有問題或建議，請提交 Issue 或 Pull Request。
