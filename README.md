# Speech-to-text-VietNamese-FastSpeech2
Using the FastSpeech 2 model to convert Vietnamese text into speech with a distinctive Central Vietnamese accent
1. Giới thiệu về mô hình FastSpeech2:
  - Các bạn có thể tìm hiểu thông qua việc đọc bài báo này [FastSpeech2 Paper](https://arxiv.org/abs/2006.04558)
  - Hoặc có thể xem video trình bày bằng tiếng Việt của nhóm chúng mình trên [Youtube](https://youtu.be/-n-oN0bqxRo)
2. Kết quả của chúng tôi: 
  - Mô hình có khả năng phân tích và tổng hợp Mel-Spectrogram gần như tương đương với Mel-Spectrogram được sinh ra từ âm thanh gốc. Giọng nói được sinh ra từ các Mel-Spectrogram đó có thể nghe rõ các chữ cái, số, ngày tháng năm.
  - Hình ảnh Mel-Spectrogram được sinh ra từ âm thanh gốc: \
     ![GroundTrustMel](https://github.com/user-attachments/assets/b4c595c0-6774-4ba4-8e2c-7b5a0bc8e464)
    ![trust](https://github.com/user-attachments/assets/377788b1-9a84-40fa-a9d2-4247295dc450)

  - Hình ảnh Mel-Spectrogram được sinh ra từ mô hình: \
    ![SyntheziedMel](https://github.com/user-attachments/assets/73a7ca9e-ec92-47f4-b161-ba0c32ef8717)
  ![syn](https://github.com/user-attachments/assets/4df8e5f2-64d8-4abd-858c-6937bc49b085)
  - Các bạn cũng có thể xem video demo của nhóm chúng mình qua [link youtube này](https://youtu.be/mmN39XVUyDs)
3. Hướng dẫn cài đặt 
