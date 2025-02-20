from django.db import models
from .firebase_config import get_db_ref

# Create your models here.

class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    jumlah_uang = models.IntegerField(default=0)
    history = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.nama} - Rp{self.jumlah_uang}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Simpan ke Firebase setiap kali model disimpan
        ref = get_db_ref()
        ref.child('wallets').child(str(self.id)).set({
            'nama': self.nama,
            'jumlah_uang': self.jumlah_uang,
            'history': self.history
        })

    @classmethod
    def from_firebase(cls, firebase_data, wallet_id):
        wallet = cls(
            id=wallet_id,
            nama=firebase_data.get('nama', ''),
            jumlah_uang=firebase_data.get('jumlah_uang', 0),
            history=firebase_data.get('history', '')
        )
        return wallet

