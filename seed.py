import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question

def seed_data():
    print("Seeding veritabanı başlıyor...")
    
    # 1. Kategorileri Oluştur
    cat_yazilim, _ = Category.objects.get_or_create(name="Yazılım")
    cat_genel, _ = Category.objects.get_or_create(name="Genel Kültür")
    
    # Mevcut soruları temizle (Gerekirse)
    Question.objects.all().delete()
    
    # 2. Yazılım Soruları
    yazilim_sorulari = [
        ("Python'da bir listeye eleman eklemek için hangi metod kullanılır?", "add()", "append()", "insert()", "push()", "B"),
        ("Django framework'ü hangi dilde yazılmıştır?", "Java", "Ruby", "Python", "PHP", "C"),
        ("HTML'in açılımı nedir?", "Hyper Text Markup Language", "High Tech Modern Language", "Hyperlinks and Text Markup Language", "Home Tool Markup Language", "A"),
        ("CSS neyin kısaltmasıdır?", "Computer Style Sheets", "Creative Style System", "Cascading Style Sheets", "Colorful Style Sheets", "C"),
        ("React hangi şirket tarafından geliştirilmiştir?", "Google", "Facebook (Meta)", "Microsoft", "Twitter", "B"),
        ("Aşağıdakilerden hangisi bir ilişkisel veritabanı (RDBMS) değildir?", "PostgreSQL", "MySQL", "MongoDB", "Oracle", "C"),
        ("Git versiyon kontrol sistemini kim kurmuştur?", "Linus Torvalds", "Bill Gates", "Steve Jobs", "Mark Zuckerberg", "A"),
        ("API kelimesinin açılımı nedir?", "Application Programming Interface", "Advanced Program Integration", "Automated Programming Interface", "Application Process Integration", "A"),
        ("JavaScript'te '===' operatörü ne işe yarar?", "Sadece değeri kontrol eder", "Değeri atar", "Hem değeri hem de veri tipini kontrol eder", "Hiçbiri", "C"),
        ("Vue.js'te component'ler arası veri taşımak için yukarıdan aşağıya ne kullanılır?", "Emits", "Props", "State", "Vuex", "B"),
        ("Aşağıdakilerden hangisi bir NoSQL veritabanıdır?", "SQLite", "MariaDB", "Redis", "PostgreSQL", "C"),
        ("Python'da fonksiyon tanımlamak için hangi anahtar kelime kullanılır?", "func", "define", "def", "function", "C"),
        ("Docker'da imaj oluşturmak için kullanılan dosyanın adı nedir?", "Dockerfile", "Docker-compose", "image.txt", "Docker.build", "A"),
        ("Hangi HTTP metodu veri güncellemek için kullanılır?", "GET", "POST", "PUT", "DELETE", "C"),
        ("Bir web sayfasının stilini belirleyen dil hangisidir?", "HTML", "JS", "CSS", "PHP", "C"),
        ("Yapay zeka modelleri genellikle hangi dilde eğitilir?", "C++", "Java", "Python", "C#", "C"),
        ("Aşağıdakilerden hangisi frontend framework'ü değildir?", "Angular", "Vue", "React", "Django", "D"),
        ("Node.js hangi motoru kullanır?", "V8", "SpiderMonkey", "Chakra", "WebKit", "A"),
        ("SQL açılımı nedir?", "Structured Query Language", "Strong Question Language", "Structured Question Language", "System Query Language", "A"),
        ("Bilişimde 'Bug' kelimesi ilk olarak hangi böcek yüzünden çıkmıştır?", "Örümcek", "Güve", "Sinek", "Karınca", "B"),
    ]
    
    for q_text, a, b, c, d, correct in yazilim_sorulari:
        Question.objects.create(
            category=cat_yazilim,
            text=q_text,
            option_a=a,
            option_b=b,
            option_c=c,
            option_d=d,
            correct_option=correct
        )
        
    # 3. Genel Kültür Soruları
    genel_sorulari = [
        ("Dünyanın uydusu nedir?", "Mars", "Güneş", "Ay", "Venüs", "C"),
        ("Türkiye'nin başkenti neresidir?", "İstanbul", "Ankara", "İzmir", "Bursa", "B"),
        ("Hangi gezegen 'Kızıl Gezegen' olarak bilinir?", "Jüpiter", "Satürn", "Mars", "Venüs", "C"),
        ("Mona Lisa tablosunu kim çizmiştir?", "Van Gogh", "Picasso", "Leonardo da Vinci", "Michelangelo", "C"),
        ("Suyun kimyasal formülü nedir?", "CO2", "H2O", "O2", "NaCl", "B"),
    ]
    
    for q_text, a, b, c, d, correct in genel_sorulari:
        Question.objects.create(
            category=cat_genel,
            text=q_text,
            option_a=a,
            option_b=b,
            option_c=c,
            option_d=d,
            correct_option=correct
        )

    print(f"Başarılı! {len(yazilim_sorulari)} Yazılım sorusu ve {len(genel_sorulari)} Genel Kültür sorusu eklendi.")

if __name__ == '__main__':
    seed_data()
