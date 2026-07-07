from django import forms
from .models import Complaint
from PIL import Image
from mutagen import File as MutagenFile

class ComplaintForm(forms.ModelForm):
    voice = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            "id": "id_voice",
            "accept": "audio/*",
            "class": "hidden",
        })
    )
    
    class Meta:
        model=Complaint
        fields=[
            "title","description","image","state","district","address","visibility","latitude","longitude"
        ]
        widgets = {

            "title": forms.TextInput(attrs={
                "class": "w-full border rounded-lg p-2",
                "placeholder": "Enter complaint title"
            }),

            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg p-2",
                "rows": 4,
                "placeholder": "Describe your complaint..."
            }),

            "address": forms.Textarea(attrs={
                "class": "w-full border rounded-lg p-2",
                "rows": 2,
                "placeholder": "Enter the address where the issue is located"
            }),

            "state": forms.TextInput(attrs={
                "class": "w-full border rounded-lg p-2",
                "placeholder": "Select the state where the issue is located"
            }),

            "district": forms.TextInput(attrs={
                "class": "w-full border rounded-lg p-2",
                "placeholder": "Select the district where the issue is located"
            }),

            "visibility": forms.RadioSelect(),

            "image": forms.ClearableFileInput(attrs={
                "class": "hidden", "accept": ".jpg,.jpeg,.png"
            }),

            "voice": forms.ClearableFileInput(attrs={
                "class": "hidden", "accept": "audio/*"
            }),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def clean(self):
        super().clean()
        print(self.files)
        
        data=self.cleaned_data
        image = data.get("image")
        voice = data.get("voice")
        description = data.get("description", "").strip()

        if not image and not voice and not description:
            raise forms.ValidationError(
                "Please provide at least one of: description, image, or voice."
            )

        return data
    
    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        # Maximum 5 MB
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Image must be smaller than 5 MB."
            )

        # Allowed MIME types
        allowed_types = {
            "image/jpeg",
            "image/png",
        }

        if image.content_type not in allowed_types:
            raise forms.ValidationError(
                "Only JPG, JPEG and PNG images are allowed."
            )

        # Verify image
        try:
            image.seek(0)
            img = Image.open(image)
            img.verify()
        except Exception:
            raise forms.ValidationError(
                "Invalid or corrupted image."
            )
        finally:
            image.seek(0)

        return image

    def clean_voice(self):
        voice = self.cleaned_data.get("voice")

        if not voice:
            return voice

        # Maximum 10 MB
        if voice.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "Voice recording must be smaller than 10 MB."
            )

        # Allowed MIME types
        allowed_types = {
            "audio/mpeg",      # mp3
            "audio/wav",
            "audio/x-wav",
            "audio/mp4",       # m4a
            "audio/x-m4a",
            "audio/ogg",
            "audio/webm",
        }

        if voice.content_type not in allowed_types:
            raise forms.ValidationError(
                "Only MP3, WAV, M4A and OGG audio files are allowed."
            )

        # Verify audio
        try:
            if voice.content_type == "audio/webm":
                pass
            else:
                voice.seek(0)
                audio = MutagenFile(voice)

                if audio is None or not hasattr(audio, "info"):
                    raise forms.ValidationError(
                        "Invalid audio file."
                    )

                # Maximum duration: 60 seconds
                if audio.info.length > 60:
                    raise forms.ValidationError(
                        "Voice recording cannot exceed 60 seconds."
                    )

        except forms.ValidationError:
            raise

        except Exception:
            raise forms.ValidationError(
                "Invalid or corrupted audio file."
            )

        finally:
            voice.seek(0)

        return voice