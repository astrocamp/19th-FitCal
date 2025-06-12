from django.core.exceptions import ValidationError
from django.forms import FileInput, HiddenInput, ModelForm, TextInput, TimeInput
from django.forms.widgets import RadioSelect

from .models import Rating, Store


def validate_tax_id(tax_id):
    if not tax_id.isdigit() or len(tax_id) != 8:
        return False

    weights = [1, 2, 1, 2, 1, 2, 4, 1]
    total = 0
    split_7th = False

    for i in range(8):
        product = int(tax_id[i]) * weights[i]
        if i == 6 and tax_id[i] == '7':
            split_7th = True
        if product >= 10:
            product = product // 10 + product % 10
        total += product

    if total % 5 == 0:
        return True

    if split_7th:
        total_adjusted = total - 7 + (1 + 2)
        if total_adjusted % 5 == 0:
            return True

    return False


# class NoLabelClearableFileInput(ClearableFileInput):
#     initial_text = '目前檔案'
#     input_text = '更新檔案'
#     clear_checkbox_label = ''


class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = [
            'name',
            'address',
            'phone_number',
            'tax_id',
            'opening_time',
            'closing_time',
            'cover_image',
            'logo_image',
        ]
        error_messages = {
            'name': {
                'required': '店家名稱不能空白',
            },
            'address': {
                'required': '地址不能空白',
            },
            'phone_number': {
                'required': '電話必須為10位數字',
            },
            'tax_id': {
                'required': '必須為8位數字的有效統編',
            },
            'opening_time': {
                'required': '開店時間不能空白',
            },
            'closing_time': {
                'required': '打烊時間不能空白',
            },
        }

        labels = {
            'name': '店家名稱',
            'address': '地址',
            'phone_number': '行動電話',
            'tax_id': '統編',
            'opening_time': '開店時間',
            'closing_time': '打烊時間',
            'cover_image': '上傳店家封面',
            'logo_image': '上傳店家 Logo',
        }

        widgets = {
            'user': HiddenInput(),
            'cover_image': FileInput(),
            'logo_image': FileInput(),
            'name': TextInput(
                attrs={
                    'placeholder': '格式範例：五倍學院',
                    'required': 'required',
                }
            ),
            'address': TextInput(
                attrs={
                    'placeholder': '格式範例：台北市中正區衡陽路7號5樓',
                    'required': 'required',
                }
            ),
            'tax_id': TextInput(
                attrs={
                    'pattern': r'\d{8}',
                    'title': '必須為8位數字的有效統編',
                    'placeholder': '格式範例：83598406',
                    'required': 'required',
                }
            ),
            'phone_number': TextInput(
                attrs={
                    'pattern': r'09\d{8}',
                    'title': '電話必須為 09 開頭的 10 位數字',
                    'placeholder': '格式範例：0912345678',
                    'required': 'required',
                }
            ),
            'opening_time': TimeInput(attrs={'type': 'time', 'required': 'required'}),
            'closing_time': TimeInput(attrs={'type': 'time', 'required': 'required'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise ValidationError('店家名稱不能空白')
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address.strip():
            raise ValidationError('地址不能空白')
        return address

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit() or len(phone) != 10 or not phone.startswith('09'):
            raise ValidationError('電話必須為 10 位數字，且以 09 開頭')
        return phone

    def clean_tax_id(self):
        tax_id = self.cleaned_data.get('tax_id')
        if not validate_tax_id(tax_id):
            raise ValidationError('請輸入正確的統一編號')
        return tax_id

    def clean_opening_time(self):
        opening_time = self.cleaned_data.get('opening_time')
        if not opening_time:
            raise ValidationError('開店時間不能空白')
        return opening_time

    def clean_closing_time(self):
        closing_time = self.cleaned_data.get('closing_time')
        if not closing_time:
            raise ValidationError('打烊時間不能空白')
        return closing_time


class RatingForm(ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }
        labels = {
            'score': '評分（1~5 分）',
        }
