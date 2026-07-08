from django.contrib import messages
from django.utils import timezone
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, render
from .forms import ComplaintForm
from .ai.gemini import send_to_gemini
from django.shortcuts import redirect
from .services import apply_ai_result
from .models import Complaint,ComplaintSupport,Comment,Follow,Notification
from .tasks import analyze_complaint_task
from django.http import HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from accounts.models import Profile
import cloudinary.uploader
# Create your views here.

@login_required
def create_complaint(request):

    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.analysis_status = "Processing"


            voice = request.FILES.get("voice")

            if voice:

                result = cloudinary.uploader.upload(
                    voice,
                    resource_type="video",
                    folder="complaints/voice"
                )

                complaint.voice = result["secure_url"]
                complaint.voice_public_id = result["public_id"]

            complaint.save()

            Follow.objects.create(
                complaint=complaint,
                user=request.user
            )

            analyze_complaint_task(complaint.pk)

            return redirect("complaints:mycomplaint_detail", pk=complaint.pk)

    else:
        form = ComplaintForm()
        

    return render(request, "complaints/complaint.html", {"form": form})

@login_required
def mycomplaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk , user= request.user)
    return render(request, "complaints/mycomplaint_detail.html", {"complaint": complaint})


from django.db.models import Count, Q
@login_required
def mycomplaints(request):
    complaints = Complaint.objects.filter(user=request.user)

    context = {
        "complaints":complaints,
        "total": complaints.count(),
        "processing": complaints.filter(analysis_status="Processing").count(),
        "completed": complaints.filter(analysis_status="Completed").count(),
        "failed": complaints.filter(analysis_status="Failed").count(),
        "invalid": complaints.filter(is_valid=False).count(),
    }

    return render(request, "complaints/mycomplaints.html", context)

@login_required
def delete_complaint(request, pk):
    if request.method == "POST":
        try:
            complaint = Complaint.objects.get(pk=pk, user=request.user)
            print("Deleting image:", complaint.image.public_id)
            print("Deleting voice:", complaint.voice_public_id)
            print(complaint.image.url)
            print(complaint.voice)
            if complaint.voice_public_id:

                response= cloudinary.uploader.destroy(complaint.voice_public_id,resource_type="video")
                print("voice",response)
            
            if complaint.image:
                response = cloudinary.uploader.destroy(
                    complaint.image.public_id,
                    resource_type="image"
                )
                print(response)
                

            Complaint.objects.filter(pk=pk).delete()
            return redirect("complaints:mycomplaints")
        except Complaint.DoesNotExist:
            return HttpResponseNotFound("Complaint not found.")
    else:
        try:
            complaint = Complaint.objects.get(pk=pk)
            return render(request, "complaints/confirm_delete.html", {"complaint": complaint})
        except Complaint.DoesNotExist:
            return HttpResponseNotFound("Complaint not found.")

@login_required
def toggle_support(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    support, created = ComplaintSupport.objects.get_or_create(complaint=complaint, user=request.user)
    if not created:
        support.delete()
        supported = False
    else:
        supported = True
    
    return JsonResponse({"status": "success", "supports_count": complaint.supports.count(), "supported": supported})

@login_required
def toggle_follow(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if complaint.user==request.user:
        return JsonResponse({"status": "success", "followed": followed})

    follow, created = Follow.objects.get_or_create(complaint=complaint, user=request.user)
    if not created:
        follow.delete()
        followed = False
    else:
        followed = True

    return JsonResponse({"status": "success", "followed": followed})

@login_required
def comment_view(request, pk):
    
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    complaint = get_object_or_404(Complaint, pk=pk)

    comment_text = request.POST.get("comment", "").strip()

    if not comment_text:
        return JsonResponse(
            {
                "status": "error",
                "message": "Comment cannot be empty."
            },
            status=400,
        )

    role = request.user.profile.role

    is_government = True if (role=="Government" or role=="Admin") else False

    comment = Comment.objects.create(
        complaint=complaint,
        user=request.user,
        comment=comment_text,
        is_government= is_government,
    )

    if is_government:
        followers = complaint.followers.all()

        followers = list(followers)

        for follower in followers:
            Notification.objects.create(
                user=follower.user,
                complaint=complaint,
                title="Government Comment",
                message=f"A government official commented on '{complaint.title}'.",
                notification_type="Comment"
            )
    
    return JsonResponse({
        "status": "success",
        "id": comment.id,
        "username": "Anonymous Citizen",
        "comment": comment.comment,
        "created_at": "Just now",
    })

@login_required
def public_dashboard(request):

    complaints = Complaint.objects.filter(is_valid=True,visibility="ANONYMOUS")

    complaints = complaints.exclude(analysis_status="Failed")

    trending_complaints = complaints.filter(created_at__gte = timezone.now() - timezone.timedelta(days=7))

    trending_complaints = trending_complaints.exclude(status="Resolved")


    trending_complaints = trending_complaints.annotate(
        supports_count=Count("supports")
    ).order_by("-supports_count")[:6]

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    department = request.GET.get("department", "").strip()
    status = request.GET.get("status", "").strip()
    severity = request.GET.get("severity", "").strip()
    sort = request.GET.get("sort", "recent")

    if search:
        complaints = complaints.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(department__icontains=search) |
            Q(address__icontains = search) |
            Q(keywords__contains = [search])
        )

    if category:
        complaints = complaints.filter(category=category)

    if department:
        complaints = complaints.filter(department=department)

    if status:
        complaints = complaints.filter(status=status)

    if severity:
        complaints = complaints.filter(severity=severity)

    if sort == "recent":
        complaints = complaints.order_by("-created_at")

    elif sort == "supported":
        complaints = complaints.annotate(
            supports_count=Count("supports")
        ).order_by("-supports_count")

    elif sort == "priority score":
        complaints = complaints.order_by("-priority_score")
    

    paginator = Paginator(complaints,12)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    total_complaints = complaints.count()

    resolved_complaints = complaints.filter(status="Resolved").count()

    progress_complaints = complaints.filter(status="In Progress").count()

    pending_complaints = complaints.filter(status="Pending").count()

    supported_ids = set(
        ComplaintSupport.objects.filter(
            user=request.user
        ).values_list("complaint_id", flat=True)
    )

    follow_ids = set(
        Follow.objects.filter(
            user=request.user
        ).values_list("complaint_id", flat=True)
    )

    for complaint in page_obj:
        complaint.is_supported = complaint.id in supported_ids
        complaint.is_followed = complaint.id in follow_ids

    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "query_params": query_params.urlencode(),
        "trending_complaints": trending_complaints,
        "total_complaints": total_complaints,
        "resolved_complaints": resolved_complaints,
        "progress_complaints": progress_complaints,
        "pending_complaints": pending_complaints,
    }

    return render(request, "complaints/public_dashboard.html", context)

@login_required
def complaint_public_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, is_valid=True)
    supports_count = complaint.supports.count()
    user_supported = False
    user_followed = False
    if request.user.is_authenticated:
        user_supported = ComplaintSupport.objects.filter(complaint=complaint, user=request.user).exists()
        user_followed = Follow.objects.filter(complaint=complaint,user=request.user).exists()
    
    anoy_count = complaint.comments.filter(is_government=False).count()
    
    context = {
        "complaint": complaint,
        "supports_count": supports_count,
        "user_supported": user_supported,
        "user_followed" : user_followed,
        "can_delete" : True if request.user==complaint.user else False,
        "anoy_count": anoy_count,
    }

    return render(request, "complaints/complaint_public_detail.html", context)

@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    )

    unread_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,"complaints/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        }
    )
    

@login_required
def open_notification(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect(
        "complaints:complaint_public_detail",
        pk=notification.complaint.pk
    )

@login_required
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

    return redirect("complaints:notifications")

def faq(request):
    return render(request,"complaints/faq.html")

@login_required
def govt_dashboard(request):
    if not (
        request.user.is_superuser or
        request.user.profile.role == "Government"
    ):
        return redirect("complaints:public_dashboard")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()

        user = User.objects.filter(username=username).first()

        if not user:
            messages.error(request, "User not found.")
            return redirect("complaints:govt_dashboard")

        if request.user == user:
            messages.info(request, "Your account already has Government access.")
            return redirect("complaints:govt_dashboard")

        profile = Profile.objects.get(user=user)

        if profile.role == "Government":
            messages.info(request, "This user already has Government access.")
        else:
            profile.role = "Government"
            profile.save()
            messages.success(request, f"{username} is now a Government Officer.")

        return redirect("complaints:govt_dashboard")
            
    elif request.method=="GET":
        complaints = Complaint.objects.filter(is_valid=True)

        complaints = complaints.exclude(analysis_status="Failed")

        trending_complaints = complaints.filter(created_at__gte = timezone.now() - timezone.timedelta(days=7))

        trending_complaints = trending_complaints.exclude(status="Resolved")

        trending_complaints = trending_complaints.annotate(
            supports_count=Count("supports")
        ).order_by("-supports_count")[:6]

        search = request.GET.get("search", "").strip()
        category = request.GET.get("category", "").strip()
        department = request.GET.get("department", "").strip()
        status = request.GET.get("status", "").strip()
        severity = request.GET.get("severity", "").strip()
        sort = request.GET.get("sort", "recent")
        visibility= request.GET.get("visibility","")

        if search:
            complaints = complaints.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(department__icontains=search) |
                Q(address__icontains = search) |
                Q(keywords__contains = [search])
            )

        if visibility:
            complaints= complaints.filter(visibility=visibility)

        if category:
            complaints = complaints.filter(category=category)

        if department:
            complaints = complaints.filter(department=department)

        if status:
            complaints = complaints.filter(status=status)

        if severity:
            complaints = complaints.filter(severity=severity)

        if sort == "recent":
            complaints = complaints.order_by("-created_at")

        elif sort == "supported":
            complaints = complaints.annotate(
                supports_count=Count("supports")
            ).order_by("-supports_count")

        elif sort == "severity":
            complaints = complaints.order_by("-priority_score")

        paginator = Paginator(complaints,12)

        page_number = request.GET.get('page')

        page_obj = paginator.get_page(page_number)

        total_complaints = complaints.count()

        resolved_complaints = complaints.filter(status="Resolved").count()

        progress_complaints = complaints.filter(status="In Progress").count()

        pending_complaints = complaints.filter(status="Pending").count()

        pwd_count = complaints.filter(
            department__in=["PWD", "Public Works Department"]
        ).count()
        health_count = complaints.filter(department="Health Department").count()
        water_count = complaints.filter(department="Water Department").count()
        fire_count = complaints.filter(department="Fire Department").count()
        municipal_count = complaints.filter(department="Municipal Corporation").count()
        edu_count = complaints.filter(department="Education Department").count()

        query_params = request.GET.copy()
        query_params.pop("page", None)

        context = {
            "page_obj": page_obj,
            "query_params": query_params.urlencode(),
            "trending_complaints": trending_complaints,
            "total_complaints": total_complaints,
            "resolved_complaints": resolved_complaints,
            "progress_complaints": progress_complaints,
            "pending_complaints": pending_complaints,
            "pwd_count": pwd_count,
            "water_count":water_count,
            "edu_count":edu_count,
            "municipal_count":municipal_count,
            "fire_count":fire_count,
            "health_count":health_count,
        }
        
        return render(request,"complaints/government_dashboard.html",context)

@login_required
def govt_detail_complaint(request,pk):
    if not (
        request.user.is_superuser or
        request.user.profile.role == "Government"
    ):
        return redirect("complaints:public_dashboard")
    
    complaint = get_object_or_404(Complaint, pk=pk, is_valid=True)
    supports_count = complaint.supports.count()
    
    context = {
        "complaint": complaint,
        "supports_count": supports_count,
    }

    return render(request,"complaints/government_complaint_detail.html",context)


@login_required
def delete_comment(request, pk):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request."
            },
            status=405
        )

    comment_id = request.POST.get("comment_id")

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        complaint_id=pk
    )

    # Allow deletion only by the comment author
    # (or add request.user.is_superuser / Government checks if desired)
    
    if comment.user != request.user and not request.user.is_superuser and request.user.profile.role=="Citizen":
        return JsonResponse(
            {
                "success": False,
                "message": "Permission denied."
            },
            status=403
        )

    comment.delete()

    return JsonResponse(
        {
            "success": True
        }
    )

import json
@login_required
def change_complaint_status(request, pk):

    if request.user.profile.role not in ["Government", "Admin"]:
        return JsonResponse(
            {
                "success": False,
                "message": "Permission denied."
            },
            status=403
        )

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request."
            },
            status=405
        )

    complaint = get_object_or_404(Complaint, pk=pk)

    data = json.loads(request.body)

    status = data.get("status")

    allowed_status = [
        "Pending",
        "In Progress",
        "Resolved",
        "Rejected",
    ]

    if status not in allowed_status:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid status."
            },
            status=400
        )

    complaint.status = status

    complaint.save(update_fields=["status"])

    followers = complaint.followers.all()

    users = list(followers)

    for follow in users:
        Notification.objects.create(
            user=follow.user,
            complaint=complaint,
            title="Complaint Status Updated",
            message=f'"{complaint.title}" is now {complaint.status}.',
            notification_type="Status"
        )

    return JsonResponse(
        {
            "success": True,
            "message": f"Complaint marked as {status}."
        }
    )

@login_required
def manage_officials(request):

    # Only Government officers can access
    if request.user.profile.role == "Citizen":
        messages.error(request, "Permission denied.")
        return redirect("complaints:public_dashboard")

    search = request.GET.get("search", "").strip()

    profiles = Profile.objects.select_related("user").order_by("user__username")

    if search:
        profiles = profiles.filter(
            user__username__icontains=search
        )

    context = {
        "profiles": profiles,
    }

    return render(
        request,
        "complaints/manage_officials.html",
        context,
    )

@login_required
def make_government(request, user_id):

    if request.method != "POST":
        return JsonResponse(
            {
                "success":False,
                "message":"Invalid request."
            },
            status=405
        )

    if request.user.profile.role == "Citizen":
        return JsonResponse(
            {
                "success":False,
                "message":"Permission denied."
            },
            status=403
        )

    profile = get_object_or_404(
        Profile,
        user_id=user_id
    )

    if profile.user == request.user:
        return JsonResponse(
            {
                "success":False,
                "message":"Your account already has Government access."
            }
        )

    if profile.role != "Citizen":
        
        return JsonResponse(
            {
                "success":False,
                "message":"This user is already a Government Official."
            }
        )

    profile.role = "Government"
    profile.save()

    return JsonResponse(
        {
            "success":True,
            "message":"Government access granted successfully."
        }
    )

@login_required
def remove_government(request, user_id):

    if request.method!="POST":
        return JsonResponse(
            {
                "success":False,
                "message":"Invalid request."
            },
            status=405
        )

    if request.user.profile.role == "Citizen":
        return JsonResponse(
            {
                "success":False,
                "message":"Permission denied."
            },
            status=403
        )

    profile = get_object_or_404(
        Profile,
        user_id=user_id
    )

    if profile.user == request.user:
        return JsonResponse(
            {
                "success":False,
                "message":"You cannot remove your own Government access."
            }
        )

    if profile.role == "Citizen":
        return JsonResponse(
            {
                "success":False,
                "message":"This user is already a Citizen."
            }
        )
    
    if profile.role == "Admin":
        return JsonResponse(
            {
                "success":False,
                "message":"You can't remove Admin."
            }
        )

    profile.role = "Citizen"
    profile.save()

    return JsonResponse(
        {
            "success":True,
            "message":"Government access removed successfully."
        }
    )

def guidelines(request):
    return render(request,"complaints/guidelines.html")

def contact(request):
    return render(request,"complaints/contact.html")

def about(request):
    return render(request,"complaints/about.html")