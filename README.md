# llowCV

[English](README_EN.md)

**Pillow だけで動く、cv2 ライクな軽量画像処理ライブラリ。**

OpenCV + NumPy はエッジデバイスや PyInstaller exe 化で重すぎる。
llowCV は Pillow のみをコア依存とし、cv2 と同じ API 名・引数順・座標系を提供することで移行コストを最小化します。

```python
import llowcv as lcv

img = lcv.imread("input.jpg")
img = lcv.resize(img, (640, 480))
img = lcv.put_text(img, "東京 OK", (10, 30), font="NotoSansJP.ttf", size=24, color=(255, 255, 255))
lcv.imwrite("out.jpg", img)
```

## 特長

| | OpenCV | llowCV |
|---|:---:|:---:|
| コア依存 | OpenCV + NumPy | **Pillow のみ** |
| インストールサイズ | ~100 MB | ~10 MB |
| PyInstaller exe 化 | 困難 | 容易 |
| Raspberry Pi / エッジ | 重い | 軽い |
| cv2 ライク API | — | ✅ |
| 日本語テキスト描画 | 要フォント設定 | TTF 指定のみ |
| リアルタイム処理 | ✅ | 対象外 |

## インストール

```bash
pip install llowcv
```

Matplotlib 表示が必要な場合：

```bash
pip install llowcv[mpl]
```

NumPy / OpenCV との変換 API が必要な場合：

```bash
pip install llowcv[cv2]
```

## カラーフォーマット

llowCV は **RGB を基本フォーマット**として扱います。cv2 の BGR とは異なります。

| mode | 用途 | チャンネル順 |
|---|---|---|
| `"RGB"` | カラー画像（デフォルト） | R, G, B |
| `"RGBA"` | 透過付きカラー | R, G, B, A |
| `"L"` | グレースケール | 輝度のみ |

```python
img = lcv.imread("input.jpg")            # → mode='RGB'
img = lcv.imread("input.png", mode="RGBA")  # → mode='RGBA'（透過チャンネルあり）
img = lcv.imread("input.jpg", mode="L")  # → mode='L' （グレースケール）
```

**BGRA / BGR は直接サポートしていません。** cv2 との受け渡しには変換 API を使います：

```python
# cv2 (BGR ndarray) → llowcv (RGB PIL.Image)
img = lcv.from_cv2(cv2_bgr_array)   # BGR → RGB 自動変換

# llowcv (RGB PIL.Image) → cv2 (BGR ndarray)
arr = lcv.as_cv2(img)                # RGB → BGR 自動変換
```

`alpha_composite` は両方の画像が `mode='RGBA'` である必要があります。`blend` と `composite` は `mode='RGB'` を前提とします。

### チャンネル操作

```python
# R↔B 入れ替え（BGR として読み込んだ画像を RGB に直す、またはその逆）
img = lcv.bgr2rgb(img)    # cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 相当
img = lcv.rgb2bgr(img)    # 同一演算（エイリアス）

# チャンネル分離・合成
r, g, b = lcv.split(img)                  # cv2.split 相当、各チャンネルは mode='L'
img      = lcv.merge([r, g, b])           # cv2.merge 相当
img      = lcv.merge([r, g, b, a], mode="RGBA")  # RGBA 合成も可

# 特定チャンネルだけ取り出す場合は split でインデックス指定
r_channel = lcv.split(img)[0]             # R チャンネルのみ（mode='L'）
```

## API リファレンス

### 画像 I/O

```python
img = lcv.imread("input.jpg")              # RGB で読み込み
img = lcv.imread("input.jpg", mode="L")    # グレースケール
lcv.imwrite("out.png", img)                # 拡張子で自動判別
lcv.imshow(img)                            # OS デフォルトビューアで表示
lcv.imshow(img, backend="mpl")             # Matplotlib で表示（pip install llowcv[mpl]）
lcv.imshow(img, backend="mpl", block=False)  # ノンブロッキング表示（mpl のみ有効）
```

### 変換

```python
img = lcv.resize(img, (640, 480))                              # リサイズ
img = lcv.resize(img, (640, 480), interpolation="cubic")       # 補間指定
img = lcv.resize(img, img.size, silent=True)                   # 同サイズ警告を抑制
img = lcv.crop(img, (x, y, w, h))                              # 切り抜き（cv2 準拠 xywh）
img = lcv.rotate(img, 90)                                      # 回転（反時計回り）
img = lcv.rotate(img, 45, expand=True)                         # キャンバス拡大あり
img = lcv.flip(img, 0)                                         # 上下反転
img = lcv.flip(img, 1)                                         # 左右反転
img = lcv.flip(img, -1)                                        # 上下 + 左右
```

補間アルゴリズム: `"nearest"` / `"linear"` (デフォルト) / `"bilinear"` / `"cubic"` / `"bicubic"` / `"lanczos"`

### フィルタ・色変換

```python
img = lcv.blur(img, (5, 5))          # ボックスブラー
img = lcv.blur(img, (1, 1))          # radius=0 の no-op は UserWarning が出る
img = lcv.blur(img, (1, 1), silent=True)  # 警告を抑制
img = lcv.sharpen(img, amount=1.5)   # シャープ（1.0 = 変化なし）
img = lcv.to_gray(img)               # グレースケール変換（mode='L'）
```

### テキスト描画

```python
img = lcv.put_text(
    img,
    text="Hello, 世界",
    org=(10, 40),              # 左下基準（cv2 準拠）
    font="NotoSansJP-Regular.ttf",
    size=32,
    color=(255, 255, 255),
)
```

`org` は cv2.putText と同じ**左下基準**の座標です。フォントは TTF/OTF ファイルパスを直接指定します。

### 合成

```python
out = lcv.blend(img1, img2, alpha=0.5)        # アルファブレンド（0.0=img1, 1.0=img2）
out = lcv.composite(img1, img2, mask)          # マスク合成（mask=0→img1, 255→img2）
out = lcv.alpha_composite(dst, src)            # RGBA アルファ合成
```

### NumPy / OpenCV 変換（opt-in）

`pip install llowcv[cv2]` でインストール後に利用可能：

```python
arr  = lcv.as_cv2(img)    # PIL.Image (RGB) → ndarray (BGR)
img  = lcv.from_cv2(arr)  # ndarray (BGR) → PIL.Image (RGB)
arr  = lcv.as_numpy(img)  # PIL.Image → RGB ndarray
arr  = lcv.to_bgr(arr)    # RGB ndarray → BGR ndarray
```

### カメラ（USB カメラ）

```python
with lcv.Camera(index=0) as cam:
    frame = cam.capture()          # PIL.Image (RGB) を返す
    lcv.imwrite("frame.jpg", frame)
```

Windows は Media Foundation、Linux は v4l2 バックエンドを使用します。

### グローバル設定

```python
# no-op 警告を一括抑制（Silent モード）
lcv.config.warn_noop = False

# 環境変数でも制御可能（0 / false / no / off で無効化）
# LLOWCV_WARN_NOOP=0 python main.py
```

`warn_noop` が有効な場合、以下の操作で `UserWarning` が発生します：
- `resize`: 入力と同サイズを指定
- `blur`: `ksize=(1,1)` など blur がかからない設定
- `imshow`: `pillow` バックエンドで `block=False` を指定

## 設計方針

- **コア依存は Pillow のみ** — NumPy / OpenCV はオプション
- **すべての API は新しい `PIL.Image` を返す** — in-place 変更なし、スレッドセーフ
- **API 名・引数順・座標系は cv2 準拠** — 既存コードの移行コストを最小化
- **Video / GUI / ML は対象外** — リアルタイム処理が必要なら OpenCV を使ってください

## 動作要件

- Python >= 3.10
- Pillow（コア依存）
- matplotlib（`[mpl]` オプション）
- numpy + opencv-python（`[cv2]` オプション）

## ライセンス

MIT License
