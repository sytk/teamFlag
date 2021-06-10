## Hand tracking
Open Hack U 2020 Online vol.2
### 1. ファイル説明
- `palm_detection_without_custom_op.tflite`（手のひら検出）モデルファイル：[*mediapipe-models*]レポジトリよりダウンロードしました。
- `hand_landmark.tflite`（ランドマーク検出）モデルファイル：[*mediapipe*]レポジトリよりダウンロードしました。
- `anchors.csv`ファイルと`hand_tracker.py`ファイル：[*hand_tracking*]レポジトリよりダウンロードしました。

### 2. 実施方法
```
$ python main.py
```

### requirement
- tensorflow 1.14.0
- opencv 4.4.0.42
- vptree
- scikitlearn
