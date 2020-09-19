# Docker Mimari

## Kaynaklar
- https://gokhansengun.com/docker-nedir-nasil-calisir-nerede-kullanilir/
- https://www.ibm.com/cloud/learn/docker
- https://docs.docker.com/engine/docker-overview/
- https://devops.stackexchange.com/questions/447/why-it-is-recommended-to-run-only-one-process-in-a-container
- https://tecadmin.net/tutorial/docker/docker-tutorials/

## Docker vs VM
- Klasik VM

![alt text](https://gokhansengun.com/resource/img/DockerPart1/VirtualMachineArchitecture.png)

    - VMware, Xen, Hyper-V gibi Hypervisor’ler (sanallaştırma platformları), yönettikleri fiziksel veya sanal bilgisayarlar üzerine farklı işletim sistemleri kurulmasına olanak tanımaktadırlar. Günümüzde veri merkezleri (data center) çok büyük oranda sayılan Hypervisor’ler tarafından sanallaştırılmışlardır, Cloud (Bulut) olarak adlandırılan kavramın altyapı kısmını oluşturan geniş veri merkezleri tamamıyla Hypervisor’ler tarafından yönetilmektedir. Hypervisor platformları sayesinde fiziksel olarak işletilen güçlü sunucular, ihtiyaç ölçüsünde farklı işletim sistemleri (kimi zaman hem Windows hem de Linux aynı fiziksel sunucuda) kurularak kolaylıkla işletilebilmektedir. 
    
- Docker 

![image](https://gokhansengun.com/resource/img/DockerPart1/DockerContainerArchitecture.png)

    - LXC’nin Hypervisor’e göre sağladığı avantajların en önemlilerinden birisi aynı işletim sistemi içerisinde sunabilmesidir. Hypervisor bazlı sanal sunucuların hepsinin kendine ait Guest işletim sistemi bulundurması gereklidir, LXC’de ise Container’lar Host’un işletim sistemini kullanırlar yani bir işletim sistemini ortak olarak kullanırlar. 
    
-![docker1](https://gokhansengun.com/resource/img/DockerPart1/DockerOnWindows.svg)

    - Docker temel iki parçadan oluşmaktadır. Birincisi Linux Kernel’la direkt iletişim halinde olan Docker Daemon, ikincisi ise bu Daemon (Motor) ile iletişim kurmamıza olanak tanıyan Docker CLI (Command-Line Interface)’dır. Linux’ta hem Docker Daemon hem de Docker CLI doğal olarak direkt Linux üzerinde koşmaktadır. Windows ve Mac OS X’te ise Docker CLI Windows ve Mac OS X işletim sistemleri üzerinde koşmakta, Docker Daemon ise bu işletim sistemlerinde bir Hypervisor (duruma göre VMware, VirtualBox, Hyperkit, Hyper-V) yardımıyla çalıştırılan Linux üzerinde koşmaktadır.

## Docker Terminoloji

- **Container :**
Docker Daemon tarafından Linux çekirdeği içerisinde birbirinden izole olarak çalıştırılan process’lerin her birine verilen isimdir.

- **Image ve Dockerfile :**
Docker Daemon ile çalıştırılacak Container’ların baz alacağı işletim sistemi veya başka Image’ı, dosya sisteminin yapısı ve içerisindeki dosyaları, koşturacağı programı (veya bazen çok tercih edilmemekle birlikte programları) belirleyen ve içeriği metin bazlı bir Dockerfile (yazımı tam olarak böyle, ne dockerfile ne DockerFile ne de DOCKERFILE) ile belirlenen binary’ye verilen isimdir.

- **Docker Daemon (Docker Engine) :**
Docker ekosistemindeki Hypervisor’ün tam olarak karşılığıdır. Linux Kernel’inde bulunan LXC’nin yerini almıştır. İşlevi Container’ların birbirlerinden izole bir şekilde, Image’larda tanımlarının yapıldığı gibi çalışmaları için gerekli yardım ve yataklığı yani ortamı sağlamaktır. Container’ın bütün yaşam döngüsünü, dosya sistemini, verilen CPU ve RAM sınırlamaları ile çalışması vb bütün karmaşık (işletim sistemine yakın seviyelerdeki) işlerin halledildiği bölümdür.

- **Docker CLI (Command-Line Interface) - Docker İstemcisi :**
Kullanıcının Docker Daemon ile konuşabilmesi için gerekli komut setini sağlar. Registry’den yeni bir Image indirilmesi, Image’dan yeni bir Container ayağa kaldırılması, çalışan Container’ın durdurulması, yeniden başlatılması, Container’lara işlemci ve RAM sınırlarının atanması vb komutların kullanıcıdan alınarak Docker Daemon’e teslim edilmesinden sorumludur.

## Docker’ın Kullanım Alanları ve Çözmeye Aday Olduğu Problemler

- <span style="color:red"> Benim Makinemde Çalışıyor (Works on my Machine) Problemine Çözüm Sağlaması</span>. 

- <span style="color:blue">Geliştirme Ortamı Standardizasyonu Sağlaması</span>. 

- <span style="color:green">Test ve Entegrasyon Ortamı Kurulumu ve Yönetimini Kolaylaştırması</span>. 

- <span style="color:orange">Mikroservis Mimari için Kolay ve Hızlı Bir Şekilde Kullanıma Hazır Hale Getirilebilmesi</span>. 

- <span style="color:purple">Kaynakların Etkili ve Efektif Bir Biçimde Kullanılmasını Sağlaması</span>. 



## Docker CLI - Cheat Sheet

|Komut|Açıklaması|
|:-----|:----------|
|docker images|Lokal registry’de mevcut bulunan Image’ları listeler|
|docker ps|Halihazırda çalışmakta olan Container’ları listeler|
|docker ps -a |Docker Daemon üzerindeki bütün Container’ları listeler|
|docker ps -aq|Docker Daemon üzerindeki bütün Container’ların ID’lerini listeler|
|docker pull <repository_name>/<image_name>:<image_tag>|Belirtilen Image’ı lokal registry’ye indirir. Örnek: docker pull gsengun/jmeter3.0:1.7|
|docker top <container_id>|İlgili Container’da top komutunu çalıştırarak çıktısını gösterir|
docker run -it <image_id|image_name> CMD|Verilen Image’dan terminal’i attach ederek bir Container oluşturur|
docker pause <container_id>|İlgili Container’ı duraklatır|
docker unpause <container_id>|İlgili Container pause ile duraklatılmış ise çalışmasına devam ettirilir|
docker stop <container_id>|İlgili Container’ı durdurur|
docker start <container_id>|İlgili Container’ı durdurulmuşsa tekrar başlatır|
docker rm <container_id>|İlgili Container’ı kaldırır fakat ilişkili Volume’lara dokunmaz|
docker rm -v <container_id>|İlgili Container’ı ilişkili Volume’lar ile birlikte kaldırır|
docker rm -f <container_id>|İlgili Container’ı zorlayarak kaldırır. Çalışan bir Container ancak -f ile kaldırılabilir|
docker rmi <image_id|image_name>|İlgili Image’ı siler|
docker rmi -f <image_id|image_name>|İlgili Image’ı zorlayarak kaldırır, başka isimlerle Tag’lenmiş Image’lar -f ile kaldırılabilir|
docker info|Docker Daemon’la ilgili özet bilgiler verir|
docker inspect <container_id>|İlgili Container’la ilgili detaylı bilgiler verir|
docker inspect <image_id|image_name>|İlgili Image’la ilgili detaylı bilgiler verir|
|docker rm $(docker ps -aq)|Bütün Container’ları kaldırır|
docker stop $(docker ps -aq)|Çalışan bütün Container’ları durdurur|
docker rmi $(docker images -aq)|Bütün Image’ları kaldırır|
docker images -q -f dangling=true|Dangling (taglenmemiş ve bir Container ile ilişkilendirilmemiş) Image’ları listeler|
docker rmi $(docker images -q -f dangling=true)|Dangling Image’ları kaldırır|
docker volume ls -f dangling=true|Dangling Volume’ları listeler|
docker volume rm $(docker volume ls -f dangling=true -q)|Danling Volume’ları kaldırır|
docker logs <container_id>|İlgili Container’ın terminalinde o ana kadar oluşan çıktıyı gösterir|
docker logs -f <container_id>|İlgili Container’ın terminalinde o ana kadar oluşan çıktıyı gösterir ve -f follow parametresi ile o andan sonra oluşan logları da göstermeye devam eder|
docker exec <container_id> <command>|Çalışan bir Container içinde bir komut koşturmak için kullanılır|
docker exec -it <container_id> /bin/bash|Çalışan bir Container içinde terminal açmak için kullanılır. İlgili Image’da /bin/bash bulunduğu varsayımı ile|
docker attach <container_id>|Önceden detached modda -d başlatılan bir Container’a attach olmak için kullanılır|



# markdown cheatsheet

- https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

- https://stackoverflow.com/questions/35465557/how-to-apply-color-in-markdown/35485694
