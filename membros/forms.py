import io

from django import forms
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from .models import Membro
from .validadores import SomenteNumerosMixin

# Permite abrir fotos HEIC (iPhone) além de JPEG, PNG, WebP etc.
register_heif_opener()

DIAS_SEMANA = [
    ('domingo', 'Domingo'),
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
]


class MembroForm(SomenteNumerosMixin, forms.ModelForm):
    dias_culto_checkboxes = forms.MultipleChoiceField(
        choices=DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Quais dias vem no culto"
    )

    class Meta:
        model = Membro
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_casamento': forms.DateInput(attrs={'type': 'date'}),
            'data_batismo': forms.DateInput(attrs={'type': 'date'}),
            'nome_filhos': forms.Textarea(attrs={'rows': 2}),
            'periodo_apoio': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['sexo', 'estado_civil', 'funcao_ministerial']:
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name in ['possui_doenca', 'lider_departamento']:
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name not in ['dias_culto_checkboxes', 'foto']:
                field.widget.attrs.update({'class': 'form-control'})

        if self.instance and hasattr(self.instance, 'dias_culto') and self.instance.dias_culto:
            self.fields['dias_culto_checkboxes'].initial = self.instance.dias_culto.split(',')

    def clean_foto(self):
        """Converte qualquer foto enviada (HEIC, PNG, WebP...) para JPEG."""
        foto = self.cleaned_data.get("foto")
        # só converte quando uma foto nova foi enviada
        if isinstance(foto, UploadedFile):
            img = Image.open(foto)
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
                fundo = Image.new("RGB", img.size, (255, 255, 255))
                fundo.paste(img, mask=img.split()[-1])
                img = fundo
            else:
                img = img.convert("RGB")
            img.thumbnail((1200, 1600))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=88)
            nome = foto.name.rsplit(".", 1)[0] + ".jpg"
            return ContentFile(buffer.getvalue(), name=nome)
        return foto

    def save(self, commit=True):
        instance = super().save(commit=False)
        dias = self.cleaned_data.get('dias_culto_checkboxes')
        instance.dias_culto = ','.join(dias) if dias else ''
        if commit:
            instance.save()
        return instance