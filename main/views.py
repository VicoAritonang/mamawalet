from django.shortcuts import render
from django.http import JsonResponse
from .models import Wallet
from .firebase_config import get_db_ref
from datetime import datetime

# Create your views here.

def show_saldo(request, id):
    try:
        ref = get_db_ref()
        wallet_data = ref.child('wallets').child(str(id)).get()
        
        if wallet_data is None:
            return JsonResponse({
                'error': 'Wallet tidak ditemukan'
            }, status=404)

        data = {
            'nama': wallet_data['nama'],
            'jumlah_uang': wallet_data['jumlah_uang']
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def edit_saldo(request, id, method, nominal):
    try:
        ref = get_db_ref()
        wallet_ref = ref.child('wallets').child(str(id))
        wallet_data = wallet_ref.get()
        
        if wallet_data is None:
            return JsonResponse({
                'error': 'Wallet tidak ditemukan'
            }, status=404)

        if method == 'in':
            new_amount = wallet_data['jumlah_uang'] + nominal
            new_history = wallet_data.get('history', '') + f", {wallet_data['nama']} menerima uang sebesar Rp{nominal} pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            wallet_ref.update({
                'jumlah_uang': new_amount,
                'history': new_history
            })
            
            return JsonResponse({
                'message': 'penambahan sukses'
            })
            
        elif method == 'dec':
            if wallet_data['jumlah_uang'] >= nominal:
                new_amount = wallet_data['jumlah_uang'] - nominal
                new_history = wallet_data.get('history', '') + f", {wallet_data['nama']} mengirim uang sebesar Rp{nominal} pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                wallet_ref.update({
                    'jumlah_uang': new_amount,
                    'history': new_history
                })
                
                return JsonResponse({
                    'message': 'pengurangan sukses'
                })
            else:
                return JsonResponse({
                    'message': 'saldo anda tidak mencukupi'
                })
        
        return JsonResponse({
            'error': 'Method tidak valid'
        }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def add_wallet(request, id, nama):
    try:
        ref = get_db_ref()
        wallet_ref = ref.child('wallets').child(str(id))
        
        # Cek apakah wallet dengan id tersebut sudah ada
        if wallet_ref.get() is not None:
            return JsonResponse({
                'error': 'Wallet dengan ID tersebut sudah ada'
            }, status=400)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        initial_history = f"wallet {nama} dibuat pada {current_time}"
        
        wallet_data = {
            'id': id,
            'nama': nama,
            'jumlah_uang': 0,
            'history': initial_history
        }
        
        wallet_ref.set(wallet_data)
        
        return JsonResponse({
            'message': 'Wallet berhasil dibuat',
            'data': wallet_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def transfer(request, pengirim, penerima, nominal):
    try:
        ref = get_db_ref()
        
        # Mengambil data wallet pengirim dan penerima
        wallet_pengirim_ref = ref.child('wallets').child(str(pengirim))
        wallet_penerima_ref = ref.child('wallets').child(str(penerima))
        
        wallet_pengirim = wallet_pengirim_ref.get()
        wallet_penerima = wallet_penerima_ref.get()
        
        # Cek apakah kedua wallet ada
        if not wallet_pengirim or not wallet_penerima:
            return JsonResponse({
                'error': 'Wallet pengirim atau penerima tidak ditemukan'
            }, status=404)
        
        # Cek saldo pengirim
        if wallet_pengirim['jumlah_uang'] >= nominal:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update saldo dan history pengirim
            new_saldo_pengirim = wallet_pengirim['jumlah_uang'] - nominal
            new_history_pengirim = wallet_pengirim.get('history', '') + f", mengirim uang sejumlah Rp{nominal} kepada {wallet_penerima['nama']} pada {current_time}"
            
            wallet_pengirim_ref.update({
                'jumlah_uang': new_saldo_pengirim,
                'history': new_history_pengirim
            })
            
            # Update saldo dan history penerima
            new_saldo_penerima = wallet_penerima['jumlah_uang'] + nominal
            new_history_penerima = wallet_penerima.get('history', '') + f", mendapatkan uang sebesar Rp{nominal} dari {wallet_pengirim['nama']} pada {current_time}"
            
            wallet_penerima_ref.update({
                'jumlah_uang': new_saldo_penerima,
                'history': new_history_penerima
            })
            
            return JsonResponse({
                'message': 'Transfer berhasil',
                'data': {
                    'pengirim': wallet_pengirim['nama'],
                    'penerima': wallet_penerima['nama'],
                    'nominal': nominal
                }
            })
        else:
            return JsonResponse({
                'message': 'saldo anda tidak cukup'
            })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def history(request, id):
    try:
        ref = get_db_ref()
        wallet_ref = ref.child('wallets').child(str(id))
        wallet_data = wallet_ref.get()
        
        if wallet_data is None:
            return JsonResponse({
                'error': 'Wallet tidak ditemukan'
            }, status=404)

        return JsonResponse({
            'nama': wallet_data['nama'],
            'history': wallet_data.get('history', '')
        })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def clear_database(request):
    try:
        ref = get_db_ref()
        # Menghapus semua data di root database
        ref.delete()
        
        return JsonResponse({
            'message': 'Database berhasil dibersihkan'
        })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def delete_wallet(request, id):
    try:
        ref = get_db_ref()
        wallet_ref = ref.child('wallets').child(str(id))
        
        if wallet_ref.get() is None:
            return JsonResponse({
                'error': 'Wallet tidak ditemukan'
            }, status=404)
            
        wallet_ref.delete()
        
        return JsonResponse({
            'message': f'Wallet dengan id {id} berhasil dihapus'
        })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)