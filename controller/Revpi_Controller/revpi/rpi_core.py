# ============================== #
# SHARED REVPI INSTANCE
# ============================== #
#
# PENTING:
# Sebelumnya, `revpimodio2.RevPiModIO(...)` dibuat 2x secara terpisah
# (satu di data_provider.py, satu lagi di sensor.py). Ini SALAH.
#
# revpimodio2 mengakses process image RevPi melalui satu device
# (/dev/piControl0) dan menjalankan thread autorefresh sendiri untuk
# setiap instance yang dibuat. Kalau ada 2 instance autorefresh=True
# yang berjalan bersamaan dalam 1 proses, keduanya akan saling
# tarik-menarik membaca/menulis process image di background thread
# masing-masing -> nilai input yang dibaca jadi tidak konsisten
# (kadang benar, kadang basi/stuck), dan output yang ditulis oleh satu
# instance bisa "ketiban" refresh cycle instance yang lain.
#
# Gejala di lapangan: input dashboard (yang lewat jalur langsung
# apply_control_command -> apply_output_state) kelihatan OK, tapi
# input fisik (yang harus dibaca ulang tiap cycle oleh instance lain)
# jadi tidak responsif / tidak konsisten.
#
# FIX: hanya ADA SATU instance RevPiModIO untuk seluruh aplikasi.
# Semua modul (data_provider.py, sensor.py, dll) WAJIB import `rpi`
# dari sini, jangan pernah membuat instance baru.
#
# ============================== #

import revpimodio2

rpi = revpimodio2.RevPiModIO(autorefresh=True)
