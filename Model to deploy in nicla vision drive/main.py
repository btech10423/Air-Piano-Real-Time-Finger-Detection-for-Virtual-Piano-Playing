import sensor, image, time, ml, math, uos, gc, pyb

# Initialize USB serial communication
vcp = pyb.USB_VCP()

# Camera setup
sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))       # Set 240x240 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.

# Load the model and labels
try:
   
    net = ml.Model("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

# Colors for drawing detections
colors = [
    (255,   0,   0),
    (  0, 255,   0),
    (255, 255,   0),
    (  0,   0, 255),
    (255,   0, 255),
    (  0, 255, 255),
    (255, 255, 255),
]

# Threshold for detections
min_confidence = 0.5
threshold_list = [(math.ceil(min_confidence * 255), 255)]

# Piano setup
num_keys = 8
image_width = 240
key_width = image_width / num_keys 
press_threshold = 1000  # Adjusting based on testing (area in pixels)
piano_active = False
prev_key = None

# FOMO post-processing function
def fomo_post_process(model, inputs, outputs):
    ob, oh, ow, oc = model.output_shape[0]
    x_scale = inputs[0].roi[2] / ow
    y_scale = inputs[0].roi[3] / oh
    scale = min(x_scale, y_scale)
    x_offset = ((inputs[0].roi[2] - (ow * scale)) / 2) + inputs[0].roi[0]
    y_offset = ((inputs[0].roi[3] - (ow * scale)) / 2) + inputs[0].roi[1]
    l = [[] for i in range(oc)]
    for i in range(oc):
        img = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = img.find_blobs(
            threshold_list, x_stride=1, y_stride=1, area_threshold=1, pixels_threshold=1
        )
        for b in blobs:
            rect = b.rect()
            x, y, w, h = rect
            score = (
                img.get_statistics(thresholds=threshold_list, roi=rect).l_mean() / 255.0
            )
            x = int((x * scale) + x_offset)
            y = int((y * scale) + y_offset)
            w = int(w * scale)
            h = int(h * scale)
            l[i].append((x, y, w, h, score))
    return l

clock = time.clock()
while True:
    clock.tick()
    img = sensor.snapshot()
    
    # Runing inference
    detections = net.predict([img], callback=fomo_post_process)
    
    # Check for "Start" gesture to activate piano
    for i, detection_list in enumerate(detections):
        if labels[i] == "Start":
            for det in detection_list:
                if det[4] > 0.5 and not piano_active:
                    piano_active = True
                    vcp.write("WELCOME\n".encode())
                    break
    
    # If piano is active, check for "Index" gesture to play keys
    if piano_active:
        index_detected = False
        for i, detection_list in enumerate(detections):
            if labels[i] == "index":
                if detection_list:
                    det = detection_list[0] 
                    x, y, w, h, score = det
                    if score > 0.5:
                        index_detected = True
                        center_x = x + w // 2
                        area = w * h
                        key = min(int(center_x / key_width), num_keys - 1)
                        if area < press_threshold:
                            if prev_key != key:
                                if prev_key is not None:
                                    vcp.write(f"RELEASE {prev_key}\n".encode())
                                vcp.write(f"PLAY {key}\n".encode())
                                prev_key = key
                        else:
                            if prev_key is not None:
                                vcp.write(f"RELEASE {prev_key}\n".encode())
                                prev_key = None
                break
        
        # If no "Index" detection, release any pressed key
        if not index_detected and prev_key is not None:
            vcp.write(f"RELEASE {prev_key}\n".encode())
            prev_key = None
    
    # Draw rectangles for all detections above threshold
    for i, detection_list in enumerate(detections):
        if i == 0: continue
        for x, y, w, h, score in detection_list:
            if score > 0.5:
                img.draw_rectangle(x, y, w, h, color=colors[i % len(colors)])
    
    print(clock.fps(), "fps")