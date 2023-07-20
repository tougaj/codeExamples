# Утиліта для вибору посилань з групи сторінок

Після закінчення роботи створює файл посилань `links.txt`, який може використовуватись для завантаження сторінок за допомогою відповідних інструментів, наприклад:

```bash
wget \
	-p \
 	--no-clobber \
 	--convert-links \
 	--html-extension \
 	--restrict-file-names=windows \
	--tries 10 \
	--waitretry 10 \
	--wait 0.5 \
	--input-file links.txt
```
