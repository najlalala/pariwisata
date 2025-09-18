from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
from functools import wraps
import pandas as pd

app = Flask(__name__)

engine = create_engine("mysql+mysqlconnector://root:@localhost/pariwisata_jabar")

# User login dummy (untuk demo)
USERS = {
    'admin': 'password123',
    'user': 'user123'
}

# -----------------------------
# Helper
# -----------------------------
def rows_to_dicts(result):
    """Convert SQLAlchemy Row objects ke list of dict"""
    return [dict(row._mapping) for row in result]

def login_required(f):
    """Decorator halaman yang butuh login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logout berhasil!', 'success')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        tahun = request.args.get("tahun", type=int)

        with engine.connect() as conn:
            # Ambil tahun terbaru jika tidak dipilih
            if not tahun:
                tahun_db = conn.execute(text("SELECT MAX(tahun) FROM kawasan_wisata")).scalar()
                tahun = int(tahun_db) if tahun_db else 0

            # --- Total masing-masing data ---            
            def get_total(table, column):
                result = conn.execute(text(f"SELECT SUM({column}) FROM {table} WHERE tahun=:tahun"), {"tahun": tahun}).scalar()
                return float(result or 0)

            total_kawasan = get_total("kawasan_wisata", "jumlah_kawasan")
            total_odtw = get_total("odtw", "jumlah_odtw")
            total_cagar = get_total("cagar_budaya", "jumlah_cagar_budaya")
            total_hotel = get_total("hotel", "jumlah_hotel")
            total_restoran = get_total("restoran", "jumlah_usaha")
            total_pengunjung = get_total("pengunjung", "jumlah_pengunjung")

            # --- Growth per indikator dibanding tahun sebelumnya ---
            def calc_growth(table, column):
                prev = conn.execute(text(f"SELECT SUM({column}) FROM {table} WHERE tahun=:tahun_prev"), {"tahun_prev": tahun-1}).scalar()
                prev = float(prev or 0)
                current = conn.execute(text(f"SELECT SUM({column}) FROM {table} WHERE tahun=:tahun"), {"tahun": tahun}).scalar()
                current = float(current or 0)
                if prev == 0:
                    return 0
                return ((current - prev) / prev) * 100

            kawasan_growth = calc_growth("kawasan_wisata", "jumlah_kawasan")
            cagar_growth = calc_growth("cagar_budaya", "jumlah_cagar_budaya")
            hotel_growth = calc_growth("hotel", "jumlah_hotel")
            restoran_growth = calc_growth("restoran", "jumlah_usaha")
            pengunjung_growth = calc_growth("pengunjung", "jumlah_pengunjung")

            # --- Top 5 kawasan wisata ---
            df = pd.read_sql(text("""
                SELECT nama_kabupaten_kota, SUM(jumlah_kawasan) as total
                FROM kawasan_wisata
                WHERE tahun=:tahun
                GROUP BY nama_kabupaten_kota
                ORDER BY total DESC
                LIMIT 5
            """), conn, params={"tahun": tahun})
            top_kawasan = [{"nama": row["nama_kabupaten_kota"], "total": int(row["total"])} for _, row in df.iterrows()]

            # --- Distribusi kawasan per kab/kota untuk doughnut chart ---
            df_dist = pd.read_sql(text("""
                SELECT nama_kabupaten_kota, SUM(jumlah_kawasan) as total
                FROM kawasan_wisata
                WHERE tahun=:tahun
                GROUP BY nama_kabupaten_kota
            """), conn, params={"tahun": tahun})
            distribution_labels = df_dist["nama_kabupaten_kota"].tolist()
            distribution_values = df_dist["total"].tolist()

            # --- Total pengunjung per tahun untuk line chart ---
            df_wisatawan = pd.read_sql(text("""
                SELECT tahun, SUM(jumlah_pengunjung) as total
                FROM pengunjung
                GROUP BY tahun
                ORDER BY tahun
            """), conn)
            wisatawan_labels = df_wisatawan["tahun"].tolist()
            wisatawan_values = df_wisatawan["total"].tolist()

            # --- Top 5 pengunjung ---
            df_pengunjung = pd.read_sql(text("""
                SELECT nama_kabupaten_kota, SUM(jumlah_pengunjung) as total
                FROM pengunjung
                WHERE tahun=:tahun
                GROUP BY nama_kabupaten_kota
                ORDER BY total DESC
                LIMIT 5
            """), conn, params={"tahun": tahun})
            top_pengunjung = [{"nama": row["nama_kabupaten_kota"], "total": int(row["total"])} for _, row in df_pengunjung.iterrows()]

            # --- KPI tambahan ---
            hotel_ratio = round(total_hotel / total_kawasan, 2) if total_kawasan else 0
            restoran_ratio = round(total_restoran / total_kawasan, 2) if total_kawasan else 0
            avg_pengunjung_per_kawasan = round(total_pengunjung / total_kawasan) if total_kawasan else 0
            cagar_percentage = round((total_cagar / total_kawasan) * 100, 2) if total_kawasan else 0

            # --- Performance index radar chart ---
            df_perf = pd.read_sql(text("""
                SELECT k.nama_kabupaten_kota as nama,
                       SUM(k.jumlah_kawasan) as kawasan,
                       SUM(h.jumlah_hotel) as hotel,
                       SUM(r.jumlah_usaha) as restoran,
                       SUM(c.jumlah_cagar_budaya) as cagar,
                       SUM(p.jumlah_pengunjung) as pengunjung
                FROM kawasan_wisata k
                LEFT JOIN hotel h ON k.nama_kabupaten_kota=h.nama_kabupaten_kota AND h.tahun=k.tahun
                LEFT JOIN restoran r ON k.nama_kabupaten_kota=r.nama_kabupaten_kota AND r.tahun=k.tahun
                LEFT JOIN cagar_budaya c ON k.nama_kabupaten_kota=c.nama_kabupaten_kota AND c.tahun=k.tahun
                LEFT JOIN pengunjung p ON k.nama_kabupaten_kota=p.nama_kabupaten_kota AND p.tahun=k.tahun
                WHERE k.tahun=:tahun
                GROUP BY k.nama_kabupaten_kota
                ORDER BY pengunjung DESC
                LIMIT 5
            """), conn, params={"tahun": tahun})
            regional_performance = df_perf.to_dict(orient="records")

    except Exception as e:
        flash(f"Error mengambil data: {str(e)}", "error")
        tahun = 0
        total_kawasan = total_odtw = total_cagar = total_hotel = total_pengunjung = total_restoran = 0
        top_kawasan = top_pengunjung = distribution_labels = distribution_values = wisatawan_labels = wisatawan_values = regional_performance = []
        kawasan_growth = cagar_growth = hotel_growth = restoran_growth = pengunjung_growth = 0
        hotel_ratio = restoran_ratio = avg_pengunjung_per_kawasan = cagar_percentage = 0

    return render_template(
        "dashboard.html",
        tahun=tahun,
        total_kawasan=total_kawasan,
        total_odtw=total_odtw,
        total_cagar=total_cagar,
        total_hotel=total_hotel,
        total_pengunjung=total_pengunjung,
        total_restoran=total_restoran,
        top_kawasan=top_kawasan,
        top_pengunjung=top_pengunjung,
        visitor_trend_labels=wisatawan_labels,
        visitor_trend_values=wisatawan_values,
        distribution_labels=distribution_labels,
        distribution_values=distribution_values,
        kawasan_growth=kawasan_growth,
        cagar_growth=cagar_growth,
        hotel_growth=hotel_growth,
        restoran_growth=restoran_growth,
        pengunjung_growth=pengunjung_growth,
        hotel_ratio=hotel_ratio,
        restoran_ratio=restoran_ratio,
        avg_pengunjung_per_kawasan=avg_pengunjung_per_kawasan,
        cagar_percentage=cagar_percentage,
        regional_performance=regional_performance
    )



# -----------------------------
# Wisata
# -----------------------------
@app.route('/wisata')
@login_required
def wisata():
    try:
        with engine.connect() as conn:
            kawasan_data = rows_to_dicts(conn.execute(text("""
                SELECT tahun, SUM(jumlah_kawasan) as total_kawasan
                FROM kawasan_wisata 
                GROUP BY tahun 
                ORDER BY tahun
            """)))

            odtw_data = rows_to_dicts(conn.execute(text("""
                SELECT jenis_odtw, SUM(jumlah_odtw) as total
                FROM odtw 
                WHERE tahun = (SELECT MAX(tahun) FROM odtw)
                GROUP BY jenis_odtw
                ORDER BY total DESC
            """)))

            kab_data = rows_to_dicts(conn.execute(text("""
                SELECT k.nama_kabupaten_kota,
                       COALESCE(SUM(k.jumlah_kawasan), 0) as kawasan,
                       COALESCE(SUM(o.jumlah_odtw), 0) as odtw
                FROM kawasan_wisata k
                LEFT JOIN odtw o ON k.kode_kabupaten_kota = o.kode_kabupaten_kota 
                    AND k.tahun = o.tahun
                WHERE k.tahun = (SELECT MAX(tahun) FROM kawasan_wisata)
                GROUP BY k.nama_kabupaten_kota
                ORDER BY kawasan DESC
            """)))

    except Exception as e:
        flash(f'Error mengambil data wisata: {str(e)}', 'error')
        kawasan_data = odtw_data = kab_data = []

    return render_template(
        'wisata.html',
        kawasan_data=kawasan_data,
        odtw_data=odtw_data,
        kab_data=kab_data
    )
# -----------------------------
# Pengunjung
# -----------------------------
@app.route('/pengunjung')
@login_required
def pengunjung():
    try:
        with engine.connect() as conn:
            # Data pengunjung per tahun
            pengunjung_tahun = rows_to_dicts(conn.execute(text("""
                SELECT tahun, 
                       SUM(CASE WHEN jenis_wisatawan LIKE '%nusantara%' THEN jumlah_pengunjung ELSE 0 END) as nusantara,
                       SUM(CASE WHEN jenis_wisatawan LIKE '%mancanegara%' THEN jumlah_pengunjung ELSE 0 END) as mancanegara
                FROM pengunjung 
                GROUP BY tahun 
                ORDER BY tahun
            """)))

            # Top daerah dengan pengunjung terbanyak
            top_daerah = rows_to_dicts(conn.execute(text("""
                SELECT nama_kabupaten_kota, SUM(jumlah_pengunjung) as total
                FROM pengunjung 
                WHERE tahun = (SELECT MAX(tahun) FROM pengunjung)
                GROUP BY nama_kabupaten_kota
                ORDER BY total DESC
            """)))

            # Semua data pengunjung (buat scatter plot)
            pengunjung_all = rows_to_dicts(conn.execute(text("""
                SELECT nama_kabupaten_kota, SUM(jumlah_pengunjung) as total
                FROM pengunjung 
                WHERE tahun = (SELECT MAX(tahun) FROM pengunjung)
                GROUP BY nama_kabupaten_kota
            """)))

            # Semua fasilitas (buat scatter plot)
            fasilitas_data = rows_to_dicts(conn.execute(text("""
                SELECT h.nama_kabupaten_kota,
                    COALESCE(SUM(h.jumlah_hotel), 0) as hotel,
                    COALESCE(SUM(r.jumlah_usaha), 0) as restoran
                FROM hotel h
                LEFT JOIN restoran r ON h.kode_kabupaten_kota = r.kode_kabupaten_kota
                                    AND h.tahun = r.tahun
                WHERE h.tahun = (SELECT MAX(tahun) FROM hotel)
                GROUP BY h.nama_kabupaten_kota
            """)))


    except Exception as e:
        flash(f'Error mengambil data pengunjung: {str(e)}', 'error')
        pengunjung_tahun = top_daerah = fasilitas_data = []

    return render_template(
        'pengunjung.html',
        pengunjung_tahun=pengunjung_tahun,
        top_daerah=top_daerah,
        fasilitas_data=fasilitas_data,
        pengunjung_all=pengunjung_all
    )





# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
