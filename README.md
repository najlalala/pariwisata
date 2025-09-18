# Dashboard Pariwisata Jawa Barat

Web application untuk monitoring dan analisis data pariwisata Jawa Barat dengan Flask backend dan modern responsive UI.

## Features

### Dashboard Analytics
- **Real-time Statistics**: Monitoring kawasan wisata, ODTW, cagar budaya, hotel, restoran, dan pengunjung
- **Growth Analysis**: Perhitungan pertumbuhan year-over-year untuk semua indikator
- **Interactive Charts**: Bar chart pengunjung terbanyak per kabupaten/kota  
- **Ranking System**: Top 5 kabupaten/kota berdasarkan kawasan wisata dan pengunjung
- **KPI Metrics**: Rasio hotel/restoran per kawasan, rata-rata pengunjung, persentase cagar budaya

### Data Management Pages
- **Dashboard**: Overview statistik dan analytics utama
- **Data Wisata**: Detail kawasan wisata, ODTW, dan distribusi per kabupaten/kota
- **Pengunjung & Fasilitas**: Analisis pengunjung nusantara/mancanegara dan fasilitas pendukung

### Modern UI/UX  
- **Collapsible Sidebar**: Navigation dengan smooth animations
- **Responsive Design**: Optimized untuk desktop, tablet, dan mobile
- **Interactive Elements**: Hover effects, smooth transitions, modern cards
- **Year Filter**: Dynamic filtering berdasarkan tahun

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL dengan SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Charts**: Chart.js
- **Data Processing**: Pandas
- **Authentication**: Session-based login system

## Database Schema

### Tables Structure
```sql
kawasan_wisata (tahun, kode_kabupaten_kota, nama_kabupaten_kota, jumlah_kawasan)
odtw (tahun, kode_kabupaten_kota, jenis_odtw, jumlah_odtw)  
cagar_budaya (tahun, kode_kabupaten_kota, nama_kabupaten_kota, jumlah_cagar_budaya)
hotel (tahun, kode_kabupaten_kota, nama_kabupaten_kota, jumlah_hotel)
restoran (tahun, kode_kabupaten_kota, nama_kabupaten_kota, jumlah_usaha)
pengunjung (tahun, kode_kabupaten_kota, nama_kabupaten_kota, jenis_wisatawan, jumlah_pengunjung)
```

## Installation

### Prerequisites
- Python 3.7+
- MySQL Server
- Git

### Setup Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd pariwisata-jabar
```

2. **Install Dependencies**
```bash
pip install flask sqlalchemy mysql-connector-python pandas
```

3. **Database Configuration**
```python
# Update connection string in app.py
engine = create_engine("mysql+mysqlconnector://root:password@localhost/pariwisata_jabar")
```

4. **Create Database**
```sql
CREATE DATABASE pariwisata_jabar;
-- Import your data tables here
```

5. **Run Application**
```bash
python app.py
```

6. **Access Application**
```
http://localhost:5000
```

## Authentication

Default login credentials:
- **Admin**: username: `admin`, password: `password123`  
- **User**: username: `user`, password: `user123`

## File Structure

```
pariwisata-jabar/
├── app.py                    # Main Flask application
├── templates/
│   ├── base.html            # Base template dengan sidebar
│   ├── login.html           # Login page
│   ├── dashboard.html       # Main dashboard
│   ├── wisata.html         # Tourism data page  
│   └── pengunjung.html     # Visitors & facilities page
└── README.md
```

## API Endpoints

```python
GET  /                       # Redirect ke dashboard jika login
GET  /login                  # Login page
POST /login                  # Process login
GET  /logout                 # Logout
GET  /dashboard              # Main dashboard
GET  /dashboard?tahun=2023   # Filter dashboard by year
GET  /wisata                 # Tourism data page
GET  /pengunjung             # Visitors & facilities page
```

## Key Functions

### Dashboard Calculations
```python
# Total aggregations per year
get_total(table, column)     # Sum values untuk tahun tertentu

# Growth calculations  
calc_growth(table, column)   # YoY growth percentage

# Ranking queries
top_kawasan                  # Top 5 regions by tourism objects
top_pengunjung              # Top 5 regions by visitors

# KPI calculations
hotel_ratio                 # Hotels per kawasan ratio
restoran_ratio             # Restaurants per kawasan ratio  
avg_pengunjung_per_kawasan # Average visitors per kawasan
cagar_percentage           # Heritage sites percentage
```

### Data Processing
- **Pandas Integration**: SQL queries converted to DataFrames untuk complex analysis
- **Error Handling**: Try-catch blocks dengan user-friendly error messages
- **Session Management**: Login required decorator untuk protected routes
- **Dynamic Filtering**: Year-based data filtering dengan parameter handling

## Dashboard Components

### Statistics Cards
- Objek Wisata dengan growth indicator
- ODTW (Objek Daya Tarik Wisata)  
- Cagar Budaya dengan persentase
- Hotel dan Restoran counts
- Total Pengunjung dalam jutaan

### Charts & Visualizations
- **Bar Chart**: Top kabupaten/kota by visitors menggunakan Chart.js
- **Ranking Tables**: Sortable tables untuk kawasan wisata dan pengunjung
- **Growth Indicators**: Color-coded percentage changes
- **Regional Performance**: Multi-metric comparison

### KPI Dashboard
- Infrastructure ratios (hotel/restoran per kawasan)
- Visitor analytics (average per kawasan)
- Cultural heritage metrics (cagar budaya percentage)
- Growth trend analysis

## Data Sources

Application mengambil data dari 6 tabel utama:
- **kawasan_wisata**: Jumlah kawasan wisata per kabupaten/kota
- **odtw**: Objek Daya Tarik Wisata berdasarkan jenis
- **cagar_budaya**: Situs warisan budaya
- **hotel**: Fasilitas akomodasi
- **restoran**: Fasilitas kuliner  
- **pengunjung**: Data kunjungan wisatawan (nusantara/mancanegara)

## Customization

### Adding New Metrics
```python
# Tambah fungsi calculation baru di dashboard route
new_metric = get_total("table_name", "column_name")

# Update template variables
return render_template("dashboard.html", new_metric=new_metric, ...)
```

### UI Modifications
- Edit CSS variables di `base.html` untuk color schemes
- Modify chart configurations di template scripts
- Customize card layouts dan responsive breakpoints

### Database Extensions
- Add new tables dengan foreign key relationships
- Extend existing queries untuk additional metrics
- Update pandas processing untuk new data sources

## Performance Optimization

- **Connection Pooling**: SQLAlchemy engine dengan connection reuse
- **Query Optimization**: Selective data loading dengan tahun filtering
- **Caching**: Static asset caching dan session management
- **Error Handling**: Graceful degradation pada database errors

## Security Features

- **Session-based Authentication**: Secure user sessions dengan Flask
- **SQL Injection Prevention**: Parameterized queries menggunakan SQLAlchemy text()
- **Input Validation**: Form data validation dan sanitization
- **Error Message Handling**: User-friendly error display tanpa expose system details

## Development

### Running in Development
```bash
export FLASK_ENV=development
python app.py
```

### Database Management
```python
# Helper function untuk raw query results
rows_to_dicts(result)        # Convert SQLAlchemy rows ke dictionaries

# Login decorator
@login_required              # Protect routes yang butuh authentication
```

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push branch (`git push origin feature/new-feature`)  
5. Create Pull Request

## Troubleshooting

### Common Issues
- **Database Connection**: Check MySQL service dan credentials
- **Missing Data**: Verify table structure dan data imports
- **Chart Not Loading**: Check browser console untuk JavaScript errors
- **Login Issues**: Verify session configuration dan user credentials

### Error Logging
Application menggunakan Flask flash messages untuk user feedback:
```python
flash('Error message', 'error')    # Error notifications
flash('Success message', 'success') # Success notifications  
```

**Dashboard Pariwisata Jawa Barat** - Comprehensive tourism data analytics dengan Flask dan modern web technologies.
