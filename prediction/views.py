from django.shortcuts import render,redirect,get_object_or_404
from authentication.views import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.files.storage import default_storage
from authentication.models import User  # Import your custom User model
from django.core.files.storage import FileSystemStorage
from .ml_model import predict_image
from .models import Detection, History 
from django.conf import settings
from datetime import datetime
import cv2
import os
from PIL import Image
import numpy as np
import base64
from io import BytesIO


@login_required
def predict_view(request):
    file_extension = None
    user_uid = request.session.get("user_uid")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not user_uid:
        return HttpResponse("Unauthorized: No user session found", status=401)

    user = User.objects.get(firebase_id=user_uid) 
    
    if not user:
        return HttpResponse("User not found in database", status=401)

    history_records = History.objects.filter(user=user).order_by("-timestamp")

    if request.method == 'POST' and request.FILES.get("uploaded_file"):
        uploaded_file = request.FILES["uploaded_file"]
        

        upload_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "uploads"))
        prediction_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "predictions",user_uid))

        os.makedirs(prediction_storage.location, exist_ok=True)

        file_path = upload_storage.save(uploaded_file.name, uploaded_file)
        file_url = upload_storage.url(file_path)


        file_extension = uploaded_file.name.split(".")[-1].lower()
        grad_cam_images = []

        #image prediction
        if file_extension in ["jpg", "jpeg", "png", "webp"]:
            image = Image.open(upload_storage.path(file_path)).convert('RGB')
            label, confidence, grad_cam = predict_image(image)
        
            is_real = label == 'Real'
            confidence = round(confidence * 100 if is_real else (1 - confidence) * 100, 2)  

            grad_cam_filename = f"gradcam_{timestamp}.png"
            with open(os.path.join(prediction_storage.location, grad_cam_filename), "wb") as f:
                grad_cam.save(f)

            grad_cam_path = f"predictions/{user_uid}/{grad_cam_filename}"    

            # Save detection to database  # NEW CODE
            detection = Detection.objects.create(
                user=user,
                file=uploaded_file,
                file_type="image",
                prediction=is_real,
                confidence_score=confidence,
                grad_cam=[grad_cam_path]
            )

            # Save history record  # NEW CODE
            History.objects.create(user=user, prediction=detection)
            history_records = History.objects.filter(user=user).order_by("-timestamp")

            return redirect('predict_result', detection_id=detection.detection_id)
            
            # Video Prediction
        elif file_extension in ["mp4", "avi", "mov"]:
            video_name = os.path.splitext(uploaded_file.name)[0]
            video_path = upload_storage.path(file_path)
            cap = cv2.VideoCapture(video_path)
            success, frame_count = True, 0

            predictions = []  # Store labels
            confidence_scores = []  # Store confidence values
            grad_cam_images = []  # Store Grad-CAM images

            video_prediction_dir = os.path.join(settings.MEDIA_ROOT, "predictions",user_uid, video_name)
            os.makedirs(video_prediction_dir, exist_ok=True)

            while success and frame_count < 10:  # Process up to 10 frames
                success, frame = cap.read()
                if success:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)

                    label, confidence, grad_cam = predict_image(image)  # Use the same function

                    # Store predictions
                    predictions.append(label)
                    confidence_scores.append(confidence)

                    # Save Grad-CAM image
                    grad_cam_filename = f"frame_{frame_count}.jpg"
                    grad_cam_absolute_path = os.path.join(video_prediction_dir, grad_cam_filename)
                    
                    with open(grad_cam_absolute_path,"wb") as f:
                        grad_cam.save(f)

                    grad_cam_path = f"predictions/{user_uid}/{video_name}/{grad_cam_filename}"
                    grad_cam_images.append(grad_cam_path)

                    frame_count += 1

            cap.release()

            # **Final Video Classification**
            if predictions:
                # Majority voting for label
                final_label = max(set(predictions), key=predictions.count)

                # Average confidence
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                is_real = final_label == "Real"
                avg_confidence = round(avg_confidence * 100 if is_real else (1 - avg_confidence) * 100, 2)

            else:
                final_label = "Unknown"
                avg_confidence = 0
                is_real = False    


            # Save detection to database  # NEW CODE
            detection = Detection.objects.create(
                user=user,
                file=uploaded_file,
                file_type="video",
                prediction=is_real,
                confidence_score=avg_confidence,
                grad_cam= grad_cam_images
            )

            # Save history record  # NEW CODE
            History.objects.create(user=user, prediction=detection)

            history_records = History.objects.filter(user=user).order_by("-timestamp")
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(history_records)
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

            return redirect('predict_result', detection_id=detection.detection_id)
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(history_records)
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    return render(request, "prediction/predict.html",{"history":history_records})

@login_required
def predict_result_view(request, detection_id):
    user_uid = request.session.get("user_uid")
    user = User.objects.get(firebase_id=user_uid)

    detection = Detection.objects.get(detection_id=detection_id)
    history_records = History.objects.filter(user=user).order_by("-timestamp")
    
    return render(request, "prediction/predict.html", {
        "file_url": detection.file.url,
        "label": "Real" if detection.prediction else "Fake",
        "confidence": detection.confidence_score,
        'user_uid':user_uid,
        "grad_cam_images": detection.grad_cam if detection.grad_cam else [],
        "history": history_records,
        "MEDIA_URL": settings.MEDIA_URL
    })

@login_required
def predict_from_history(request, record_id):
    user_uid = request.session.get("user_uid")
    user = User.objects.get(firebase_id=user_uid)
    record = get_object_or_404(History, id=record_id)
    history_records = History.objects.filter(user=user).order_by("-timestamp")
    detection = Detection.objects.get(detection_id=record.prediction_id)
    return render(request, "prediction/predict.html", {
        "file_url": detection.file.url,
        "label": "Real" if detection.prediction else "Fake",
        "confidence": detection.confidence_score,
        'user_uid':user_uid,
        "grad_cam_images": detection.grad_cam if detection.grad_cam else [],
        "history": history_records,
        "MEDIA_URL": settings.MEDIA_URL
    })