# Overview : Air Piano: Real-Time Finger Detection for Virtual Piano Playing
![image](https://github.com/user-attachments/assets/e79b8cb3-8aac-4a0a-82fd-809f56bf430f)
![image](https://github.com/user-attachments/assets/d6e0a8f4-2c57-4061-905b-9aade72aff38)

## Fomo object detection model development on edge impluse link - 
https://studio.edgeimpulse.com/public/683639/live

## Project demonstration youtube link -
https://youtu.be/-nB3dS6YtFM

Instead of playing a heavy, expensive instrument like a piano, you can wave your hands in the air to create sounds!
Leveraging the Nicla Vision board, we built a system to detect finger movements and turn them into music.
we developed a FOMO-based model to detect these gestures in real time, achieving a validation F1 score of 78.1%. To suit the Nicla Vision’s limited resources, the model was optimized and compressed into a lightweight 56 KB trained.tflite file.
Our pipeline translates detected finger positions into 8 virtual keys, sending serial commands to a connected computer to produce piano sounds. 
This project showcases the successful integration of creativity, machine learning, and embedded systems, delivering an innovative and engaging user experience directly at the edge.
