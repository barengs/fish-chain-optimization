from django.db import models
from users.models import OwnerProfile, CaptainProfile

class Ship(models.Model):
    """Model representing a fishing ship"""
    name = models.CharField(max_length=200, verbose_name="Nama Kapal")
    registration_number = models.CharField(max_length=100, unique=True, verbose_name="Nomor Registrasi")
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE, related_name='ships', verbose_name="Pemilik")
    captain = models.ForeignKey(CaptainProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='ships', verbose_name="Nahkoda")
    length = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Panjang (meter)")  # in meters
    width = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Lebar (meter)")   # in meters
    gross_tonnage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Gross Tonnage")
    year_built = models.IntegerField(blank=True, null=True, verbose_name="Tahun Dibuat")
    home_port = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pelabuhan Asal")
    active = models.BooleanField(default=True, verbose_name="Aktif")  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"
    
    class Meta:
        verbose_name = "Kapal"
        verbose_name_plural = "Kapal"
